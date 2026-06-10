#!/usr/bin/env python
"""Step 8: validation — ground truth, LLM cross-check, axis robustness.

1. Ground truth: does altruism peak near 2014? Is the control axis decoupled
   (low correlation between altruism and control year series)?
2. LLM pairwise tournament: judge model compares evidence quotes between year
   pairs (randomized order, temperature 0), Bradley-Terry ranking, compared
   against the embedding ranking (Spearman).
3. Perturbation: leave-one-sentence-out per pole, confirm the year ranking
   holds (Spearman vs full axis).

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


def quotes_text(quotes: dict, axis: str, year: int, max_chunks: int = 3) -> str:
    items = quotes[axis][str(year)][:max_chunks]
    return "\n".join(f"- {q['text']}" for q in items)


def ground_truth_check(scores: pd.DataFrame) -> dict:
    alt = scores[scores["axis"] == "altruism"].sort_values("year")
    ctrl = scores[scores["axis"] == "control"].sort_values("year")
    peak_year = int(alt.loc[alt["zscore"].idxmax(), "year"])
    merged = alt.merge(ctrl, on="year", suffixes=("_alt", "_ctrl"))
    r, p = pearsonr(merged["raw_topk_mean_alt"], merged["raw_topk_mean_ctrl"])
    return {
        "altruism_peak_year": peak_year,
        "peak_within_2014_pm2": abs(peak_year - 2014) <= 2,
        "altruism_control_correlation": round(float(r), 3),
        "correlation_p": round(float(p), 3),
        "control_decoupled": bool(abs(r) < 0.5),
    }


def bradley_terry(years: list[int], wins: dict[tuple[int, int], int], iters: int = 200) -> dict[int, float]:
    """Simple MM fit of Bradley-Terry strengths from pairwise win counts."""
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


def tournament(quotes: dict, years: list[int], n_pairs: int, seed: int) -> dict:
    rng = random.Random(seed)
    all_pairs = [(a, b) for i, a in enumerate(years) for b in years[i + 1:]]
    pairs = rng.sample(all_pairs, min(n_pairs, len(all_pairs)))
    client = Anthropic()
    wins: dict[tuple[int, int], int] = {}
    judgments = []
    for a, b in pairs:
        flip = rng.random() < 0.5  # randomize presentation order
        first, second = (b, a) if flip else (a, b)
        prompt = TOURNAMENT_QUESTION.format(
            a=quotes_text(quotes, "altruism", first),
            b=quotes_text(quotes, "altruism", second),
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


def write_report(cdir, results: dict) -> None:
    gt, pert = results["ground_truth"], results["perturbation"]
    lines = [
        "# Validation report (M6 review gate)", "",
        "## 1. Ground truth",
        f"- Altruism peak year: **{gt['altruism_peak_year']}** "
        f"({'PASS' if gt['peak_within_2014_pm2'] else 'FAIL'} vs 2014 +/- 2)",
        f"- Altruism-control correlation: {gt['altruism_control_correlation']} "
        f"({'decoupled: PASS' if gt['control_decoupled'] else 'coupled: INVESTIGATE'})", "",
        "## 2. LLM pairwise tournament",
    ]
    if "tournament" in results:
        lines += [
            f"- Embedding-vs-LLM ranking agreement (Spearman): "
            f"**{results['tournament_spearman']}**",
            f"- {len(results['tournament']['judgments'])} pairwise judgments "
            f"(see validation.json)", "",
        ]
    else:
        lines += ["- Skipped (--skip-tournament)", ""]
    lines += [
        "## 3. Axis-sentence perturbation",
        f"- Min Spearman across leave-one-out: **{pert['min_spearman']}** "
        f"({'PASS' if pert['robust'] else 'FRAGILE — review phrase sets'})",
        f"- Mean: {pert['mean_spearman']}", "",
        "Disagreements between checks are case studies, not silent overrides — "
        "investigate the chunks before believing or discarding the finding.",
    ]
    (cdir / "validation_report.md").write_text("\n".join(lines) + "\n")


def main(company: str, n_pairs: int, seed: int, skip_tournament: bool) -> None:
    cdir = company_dir(company)
    scores = pd.read_parquet(cdir / "axis_scores.parquet")
    quotes = read_json(cdir / "evidence_quotes.json")

    results: dict = {"ground_truth": ground_truth_check(scores)}
    print(f"Ground truth: {results['ground_truth']}")

    if not skip_tournament:
        alt = scores[scores["axis"] == "altruism"].sort_values("year")
        years = alt["year"].tolist()
        print(f"Tournament over {len(years)} years, {n_pairs} pairs:")
        results["tournament"] = tournament(quotes, years, n_pairs, seed)
        emb_rank = alt.set_index("year")["zscore"]
        llm_rank = pd.Series({int(y): s for y, s in results["tournament"]["strengths"].items()})
        rho, _ = spearmanr(emb_rank.sort_index(), llm_rank.sort_index())
        results["tournament_spearman"] = round(float(rho), 3)
        print(f"Embedding-vs-LLM Spearman: {results['tournament_spearman']}")

    print("Perturbation check...")
    results["perturbation"] = perturbation_check(company)
    print(f"Min Spearman: {results['perturbation']['min_spearman']}")

    write_json(cdir / "validation.json", results)
    write_report(cdir, results)
    print(f"Wrote {cdir / 'validation_report.md'} — review it (manual step M6)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    parser.add_argument("--n-pairs", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-tournament", action="store_true")
    args = parser.parse_args()
    main(args.company, args.n_pairs, args.seed, args.skip_tournament)
