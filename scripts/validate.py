#!/usr/bin/env python
"""Step 8: validation — ground truth, LLM cross-check, axis robustness.

Writes data/<company>/validation_report.md + validation.json (M6 review gate).
"""

from __future__ import annotations

import argparse
import random

import numpy as np
import pandas as pd
from anthropic import Anthropic
from scipy.stats import pearsonr, spearmanr

from lowork.axes import AxisDef, build_axis, project, topk_mean
from lowork.company import CompanyProfile, ValidationHypothesis
from lowork.config import AXES_DIR, JUDGE_MODEL, TOP_K, company_dir
from lowork.embeddings import EmbeddingStore
from lowork.io import read_json, write_json

TOURNAMENT_QUESTION = (
    "Below are mission/brand chunks from a company's careers page in two different "
    "years, labeled A and B. Which set expresses more idealistic, world-improving "
    "framing — work as social good rather than commercial success?\n\n"
    "SET A:\n{a}\n\nSET B:\n{b}\n\n"
    "Answer with exactly one letter: A or B."
)

EARLY_YEARS = list(range(2005, 2014))


def quotes_text(quotes: dict, axis: str, year: int, level: str = "chunk", max_items: int = 3) -> str:
    axis_q = quotes[axis]
    if "chunk" in axis_q:
        items = axis_q[level][str(year)][:max_items]
    else:
        items = axis_q[str(year)][:max_items]
    return "\n".join(f"- {q['text']}" for q in items)


def ground_truth_check(
    scores: pd.DataFrame,
    level: str = "chunk",
    *,
    validation: ValidationHypothesis | None = None,
) -> dict:
    alt = scores[(scores["axis"] == "altruism") & (scores["level"] == level)].sort_values("year")
    ctrl = scores[(scores["axis"] == "control") & (scores["level"] == level)].sort_values("year")
    peak_year = int(alt.loc[alt["zscore"].idxmax(), "year"])
    merged = alt.merge(ctrl, on="year", suffixes=("_alt", "_ctrl"))
    r, p = pearsonr(merged["raw_topk_mean_alt"], merged["raw_topk_mean_ctrl"])
    result = {
        "level": level,
        "altruism_peak_year": peak_year,
        "altruism_control_correlation": round(float(r), 3),
        "correlation_p": round(float(p), 3),
        "control_decoupled": bool(abs(r) < 0.5),
    }
    if validation:
        result["expected_peak"] = validation.expected_altruism_peak
        result["peak_tolerance"] = validation.tolerance
        result["peak_within_expected"] = (
            abs(peak_year - validation.expected_altruism_peak) <= validation.tolerance
        )
    else:
        result["peak_within_expected"] = None
    return result


def bradley_terry(years: list[int], wins: dict[tuple[int, int], int], iters: int = 200) -> dict[int, float]:
    strength = {y: 1.0 for y in years}
    total_wins = {y: 0 for y in years}
    opponents: dict[int, list[int]] = {y: [] for y in years}
    for (a, b), w in wins.items():
        total_wins[a] += w
        opponents[a] += [b] * w
        opponents[b] += [a] * w
    for _ in range(iters):
        new = {}
        for y in years:
            denom = sum(1.0 / (strength[y] + strength[o]) for o in opponents[y])
            new[y] = total_wins[y] / denom if denom else 1e-9
        norm = sum(new.values())
        strength = {y: v / norm for y, v in new.items()}
    return strength


def tournament(quotes: dict, years: list[int], n_pairs: int, seed: int, level: str = "chunk") -> dict:
    rng = random.Random(seed)
    all_pairs = [(a, b) for i, a in enumerate(years) for b in years[i + 1:]]
    pairs = rng.sample(all_pairs, min(n_pairs, len(all_pairs)))
    client = Anthropic()
    wins: dict[tuple[int, int], int] = {}
    judgments = []
    for a, b in pairs:
        flip = rng.random() < 0.5
        first, second = (b, a) if flip else (a, b)
        prompt = TOURNAMENT_QUESTION.format(
            a=quotes_text(quotes, "altruism", first, level=level),
            b=quotes_text(quotes, "altruism", second, level=level),
        )
        resp = client.messages.create(
            model=JUDGE_MODEL, max_tokens=5, temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = resp.content[0].text.strip().upper()[:1]
        winner = first if answer == "A" else second
        loser = second if winner == first else first
        wins[(winner, loser)] = wins.get((winner, loser), 0) + 1
        judgments.append({"pair": [a, b], "winner": winner})
        print(f"  {a} vs {b} -> {winner}")
    strengths = bradley_terry(years, wins)
    return {"judgments": judgments, "strengths": {str(y): s for y, s in strengths.items()}}


def embedding_vs_llm(scores: pd.DataFrame, tournament_result: dict, level: str) -> float:
    alt = scores[(scores["axis"] == "altruism") & (scores["level"] == level)].sort_values("year")
    emb_rank = alt.set_index("year")["zscore"]
    llm_rank = pd.Series({int(y): s for y, s in tournament_result["strengths"].items()})
    rho, _ = spearmanr(emb_rank.sort_index(), llm_rank.sort_index())
    return round(float(rho), 3)


def early_year_agreement(scores: pd.DataFrame, tournament_result: dict) -> dict:
    """Compare chunk vs sentence embedding rankings to LLM on early years."""
    years = [y for y in EARLY_YEARS if str(y) in tournament_result["strengths"]]
    if len(years) < 3:
        return {"note": "insufficient early-year tournament coverage"}
    llm = pd.Series({int(y): tournament_result["strengths"][str(y)] for y in years})
    out = {}
    for level in ("chunk", "sentence"):
        alt = scores[(scores["axis"] == "altruism") & (scores["level"] == level)]
        emb = alt[alt["year"].isin(years)].set_index("year")["zscore"]
        if len(emb) >= 3:
            rho, _ = spearmanr(emb.sort_index(), llm.sort_index())
            out[f"{level}_vs_llm_spearman"] = round(float(rho), 3)
    return out


def perturbation_check(company: str) -> dict:
    store = EmbeddingStore()
    axis = AxisDef.from_yaml(AXES_DIR / "altruism.yaml")
    df = pd.read_parquet(company_dir(company) / "embeddings.parquet")
    mission = df[df["label"] == "mission_brand"].reset_index(drop=True)
    embeddings = np.stack(mission["embedding"].tolist())

    def year_series(axis_vec: np.ndarray) -> pd.Series:
        scores = project(embeddings, axis_vec)
        out = {}
        for year, group_idx in mission.groupby("year").groups.items():
            mean, _, _ = topk_mean(scores[np.asarray(group_idx)], TOP_K)
            out[int(year)] = mean
        return pd.Series(out).sort_index()

    base = year_series(build_axis(store, axis))
    correlations = []
    for i in range(len(axis.pole_a)):
        rho, _ = spearmanr(base, year_series(build_axis(store, axis, drop_a=i)))
        correlations.append({"dropped": f"A{i}: {axis.pole_a[i]}", "spearman": round(float(rho), 3)})
    for i in range(len(axis.pole_b)):
        rho, _ = spearmanr(base, year_series(build_axis(store, axis, drop_b=i)))
        correlations.append({"dropped": f"B{i}: {axis.pole_b[i]}", "spearman": round(float(rho), 3)})
    rhos = [c["spearman"] for c in correlations]
    return {"per_sentence": correlations, "min_spearman": min(rhos),
            "mean_spearman": round(sum(rhos) / len(rhos), 3), "robust": min(rhos) >= 0.8}


def _peak_line(gt: dict) -> str:
    peak = gt["altruism_peak_year"]
    if gt.get("expected_peak") is not None:
        exp = gt["expected_peak"]
        tol = gt.get("peak_tolerance", 2)
        status = "PASS" if gt.get("peak_within_expected") else "FAIL"
        return f"- Altruism peak year: **{peak}** ({status} vs {exp} +/- {tol})"
    return f"- Altruism peak year: **{peak}** (no hypothesis configured)"


def write_report(cdir, results: dict, profile: CompanyProfile) -> None:
    gt = results["ground_truth_chunk"]
    gt_sent = results.get("ground_truth_sentence", {})
    pert = results["perturbation"]
    lines = [
        f"# Validation report: {profile.display_name}", "",
        "## 1. Ground truth (chunk level)",
        _peak_line(gt),
        f"- Altruism-control correlation: {gt['altruism_control_correlation']} "
        f"({'decoupled: PASS' if gt['control_decoupled'] else 'coupled: INVESTIGATE'})", "",
    ]
    if gt_sent:
        lines += [
            "## 1b. Ground truth (sentence level)",
            _peak_line(gt_sent),
            f"- Altruism-control correlation: {gt_sent['altruism_control_correlation']}", "",
        ]
    lines += ["## 2. LLM pairwise tournament"]
    if "tournament" in results:
        lines += [
            f"- Chunk embedding-vs-LLM Spearman: **{results['tournament_spearman_chunk']}**",
            f"- Sentence embedding-vs-LLM Spearman: **{results.get('tournament_spearman_sentence', 'n/a')}**",
            f"- {len(results['tournament']['judgments'])} pairwise judgments", "",
        ]
        early = results.get("early_year_agreement", {})
        if early:
            lines += ["### Early-year agreement (2005-2013)", ""]
            for k, v in early.items():
                lines.append(f"- {k}: {v}")
            lines.append("")
    else:
        lines += ["- Skipped (--skip-tournament)", ""]
    lines += [
        "## 3. Axis-sentence perturbation",
        f"- Min Spearman across leave-one-out: **{pert['min_spearman']}** "
        f"({'PASS' if pert['robust'] else 'FRAGILE'})",
        f"- Mean: {pert['mean_spearman']}", "",
    ]
    if profile.validation and profile.validation.notes:
        lines += ["## 4. Data expansion notes", ""]
        lines += [f"- {note}" for note in profile.validation.notes]
        lines += ["", "Disagreements are case studies, not silent overrides.", ""]
    else:
        lines += ["Disagreements are case studies, not silent overrides.", ""]
    (cdir / "validation_report.md").write_text("\n".join(lines) + "\n")


def main(company: str, n_pairs: int, seed: int, skip_tournament: bool) -> None:
    profile = CompanyProfile.load(company)
    validation = profile.validation
    cdir = company_dir(company)
    scores = pd.read_parquet(cdir / "axis_scores.parquet")
    quotes = read_json(cdir / "evidence_quotes.json")

    results: dict = {
        "ground_truth_chunk": ground_truth_check(scores, "chunk", validation=validation),
        "ground_truth_sentence": ground_truth_check(scores, "sentence", validation=validation),
    }
    print(f"Ground truth (chunk): {results['ground_truth_chunk']}")
    print(f"Ground truth (sentence): {results['ground_truth_sentence']}")

    if not skip_tournament:
        alt_years = scores[(scores["axis"] == "altruism") & (scores["level"] == "chunk")]["year"].tolist()
        print(f"Tournament over {len(alt_years)} years, {n_pairs} pairs:")
        results["tournament"] = tournament(quotes, alt_years, n_pairs, seed, level="chunk")
        results["tournament_spearman_chunk"] = embedding_vs_llm(scores, results["tournament"], "chunk")
        results["tournament_spearman_sentence"] = embedding_vs_llm(scores, results["tournament"], "sentence")
        results["early_year_agreement"] = early_year_agreement(scores, results["tournament"])
        print(f"Chunk vs LLM: {results['tournament_spearman_chunk']}")
        print(f"Sentence vs LLM: {results['tournament_spearman_sentence']}")
        print(f"Early years: {results['early_year_agreement']}")

    print("Perturbation check...")
    results["perturbation"] = perturbation_check(company)
    print(f"Min Spearman: {results['perturbation']['min_spearman']}")

    write_json(cdir / "validation.json", results)
    write_report(cdir, results, profile)
    print(f"Wrote {cdir / 'validation_report.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    parser.add_argument("--n-pairs", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-tournament", action="store_true")
    args = parser.parse_args()
    main(args.company, args.n_pairs, args.seed, args.skip_tournament)
