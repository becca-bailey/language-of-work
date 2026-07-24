#!/usr/bin/env python
"""Axis validation — ground truth, LLM cross-check, axis robustness.

Altruism-only for now: the ground-truth peak check, LLM pairwise tournament,
and perturbation test all run on the altruism axis (axis_separation_check is
the exception — it compares axis pairs, currently craft vs performance).
Not a pipeline stage; run manually per company. Distinct from
`pipeline.py validate`, which asserts config/coverage invariants.

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

TOURNAMENT_TEMPLATE = (
    "Below are mission/brand chunks from a company's careers page in two different "
    "years, labeled A and B. {question}\n\n"
    "SET A:\n{a}\n\nSET B:\n{b}\n\n"
    "Answer with exactly one letter: A or B."
)

# Judge questions per axis. Circularity discipline: each names the concept
# without reusing the axis's pole phrases (see axes/*.yaml), so the LLM ranks
# years independently of the embedding construction. Single common words
# ("quality", "intense") are unavoidable; multiword pole phrases are not.
AXIS_TOURNAMENTS = {
    "altruism": (
        "Which set expresses more idealistic, world-improving "
        "framing — work as social good rather than commercial success?"
    ),
    "performance": (
        "Which set describes a more demanding, high-pressure work culture — "
        "one that stresses elite talent, relentless effort, and tough "
        "performance expectations?"
    ),
    "craft": (
        "Which set leans more toward patient, careful workmanship — treating "
        "the finished product's quality and permanence as the point — rather "
        "than shipping quickly and improving through rapid revision?"
    ),
}

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


def tournament(
    quotes: dict, years: list[int], n_pairs: int, seed: int,
    level: str = "chunk", axis: str = "altruism",
) -> dict:
    question = AXIS_TOURNAMENTS[axis]
    rng = random.Random(seed)
    all_pairs = [(a, b) for i, a in enumerate(years) for b in years[i + 1:]]
    pairs = rng.sample(all_pairs, min(n_pairs, len(all_pairs)))
    client = Anthropic()
    wins: dict[tuple[int, int], int] = {}
    judgments = []
    for a, b in pairs:
        flip = rng.random() < 0.5
        first, second = (b, a) if flip else (a, b)
        prompt = TOURNAMENT_TEMPLATE.format(
            question=question,
            a=quotes_text(quotes, axis, first, level=level),
            b=quotes_text(quotes, axis, second, level=level),
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


def embedding_vs_llm(
    scores: pd.DataFrame, tournament_result: dict, level: str, axis: str = "altruism"
) -> float:
    alt = scores[(scores["axis"] == axis) & (scores["level"] == level)].sort_values("year")
    emb_rank = alt.set_index("year")["zscore"]
    llm_rank = pd.Series({int(y): s for y, s in tournament_result["strengths"].items()})
    # Intersect: the ranking may cover years the tournament never saw
    # (e.g. years resurrected by a corpus/methodology change after the run).
    common = emb_rank.index.intersection(llm_rank.index).sort_values()
    rho, _ = spearmanr(emb_rank.loc[common], llm_rank.loc[common])
    return round(float(rho), 3)


CONFIDENT_MARGIN_Z = 1.0   # |Δz| at/above which the embedding is "confident"
AGREEMENT_GATE = 0.8       # primary gate: duel agreement on confident pairs


def pairwise_agreement(
    scores: pd.DataFrame, judgments: list[dict], level: str = "chunk", axis: str = "altruism"
) -> dict:
    """Duel-level agreement between stored judge decisions and the CURRENT
    embedding ranking — the PRIMARY tournament statistic (2026-07-21).

    Robust at small pair budgets where Bradley-Terry+Spearman is schedule-luck
    noise (bootstrap sd ≈0.13 at 40 pairs; google's 0.52-vs-gate was aggregation
    noise over 24 years at ~3 games/year, while duel agreement was 88%). The
    margin split is the signature check: two instruments sharing real signal
    agree strongly on confident pairs and dissolve toward a coin flip on close
    ones. Judgments are reusable data — this recomputes against whatever the
    current ranking is, no new judge calls.
    """
    z = scores[(scores["axis"] == axis) & (scores["level"] == level)].set_index("year")["zscore"]
    rows = []
    for j in judgments:
        a, b = j["pair"]
        if a not in z.index or b not in z.index:
            continue
        emb_winner = a if z[a] > z[b] else b
        rows.append((abs(z[a] - z[b]), emb_winner == j["winner"]))
    if not rows:
        return {"n": 0}
    conf = [h for m, h in rows if m >= CONFIDENT_MARGIN_Z]
    close = [h for m, h in rows if m < CONFIDENT_MARGIN_Z]
    return {
        "n": len(rows),
        "agreement": round(sum(h for _, h in rows) / len(rows), 3),
        "n_confident": len(conf),
        "confident_agreement": round(sum(conf) / len(conf), 3) if conf else None,
        "n_close": len(close),
        "close_agreement": round(sum(close) / len(close), 3) if close else None,
        "confident_margin_z": CONFIDENT_MARGIN_Z,
    }


def games_per_year(judgments: list[dict]) -> float:
    years = {y for j in judgments for y in j["pair"]}
    return round(2 * len(judgments) / len(years), 1) if years else 0.0


def early_year_agreement(
    scores: pd.DataFrame, tournament_result: dict, axis: str = "altruism"
) -> dict:
    """Compare chunk vs sentence embedding rankings to LLM on early years."""
    years = [y for y in EARLY_YEARS if str(y) in tournament_result["strengths"]]
    if len(years) < 3:
        return {"note": "insufficient early-year tournament coverage"}
    llm = pd.Series({int(y): tournament_result["strengths"][str(y)] for y in years})
    out = {}
    for level in ("chunk", "sentence"):
        alt = scores[(scores["axis"] == axis) & (scores["level"] == level)]
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


CONTROL_COUPLING_GATE = 0.5   # |r| below this = decoupled (matches ground_truth_check)
POOL_SIZE_R_GATE = 0.5        # r(topk, log n) above this on axis AND control = pool-size suspect


def control_decoupling_check(scores: pd.DataFrame, level: str = "chunk") -> list[dict]:
    """Placebo check for every axis, not just altruism (extended 2026-07-21).

    Coupling with the values-neutral control axis flags composition-driven
    trends. The log(n) correlation separates the two confounds control can't
    distinguish alone: adaptive top-k mechanically rises with pool size on ANY
    axis (order-statistic inflation), vs a genuine logistics/office mix shift.
    If the axis AND control both track log(n), suspect pool size; if the axis
    couples with control but neither tracks n, suspect mix shift.
    """
    ctrl = scores[(scores["axis"] == "control") & (scores["level"] == level)]
    if ctrl.empty:
        return []
    ctrl = ctrl.dropna(subset=["raw_topk_mean"]).set_index("year")
    out = []
    for axis in sorted(scores["axis"].unique()):
        if axis == "control":
            continue
        ax = (scores[(scores["axis"] == axis) & (scores["level"] == level)]
              .dropna(subset=["raw_topk_mean"]).set_index("year"))
        common = ax.index.intersection(ctrl.index)
        if len(common) < 4:
            continue
        a, c = ax.loc[common], ctrl.loc[common]
        r, p = pearsonr(a["raw_topk_mean"], c["raw_topk_mean"])
        logn = np.log(a["n_chunks"].astype(float))
        if logn.nunique() > 1:
            r_n_axis, _ = pearsonr(a["raw_topk_mean"], logn)
            r_n_ctrl, _ = pearsonr(c["raw_topk_mean"], logn)
        else:
            r_n_axis = r_n_ctrl = float("nan")
        coupled = abs(r) >= CONTROL_COUPLING_GATE
        if not coupled:
            diagnosis = "decoupled"
        elif r_n_axis >= POOL_SIZE_R_GATE and r_n_ctrl >= POOL_SIZE_R_GATE:
            diagnosis = "pool_size_suspect"
        else:
            diagnosis = "mix_shift_suspect"
        out.append({
            "axis": axis, "level": level, "n_years": len(common),
            "control_r": round(float(r), 3), "control_p": round(float(p), 3),
            "r_topk_vs_logn": round(float(r_n_axis), 3) if r_n_axis == r_n_axis else None,
            "control_r_topk_vs_logn": round(float(r_n_ctrl), 3) if r_n_ctrl == r_n_ctrl else None,
            "diagnosis": diagnosis,
        })
    return out


AXIS_SEPARATION_PAIRS = [("craft", "performance")]


def axis_separation_check(company: str) -> list[dict]:
    """Verify paired axes measure distinct concepts, not the same one twice.

    Year-aggregated topk means co-move with composition (values talk waxes and
    wanes together across a page's life), so this operates below aggregation:
    cosine between the built axis vectors, and Pearson over per-chunk
    projections. High chunk-level r in a single company can still be topical
    (e.g. Basecamp's work-philosophy chunks score up on every work-culture
    axis); the vector cosine is the concept-level verdict.
    """
    df = pd.read_parquet(company_dir(company) / "embeddings.parquet")
    mission = df[df["label"] == "mission_brand"]
    embeddings = np.stack(mission["embedding"].tolist())
    out = []
    for a, b in AXIS_SEPARATION_PAIRS:
        paths = [AXES_DIR / "built" / f"{n}.json" for n in (a, b)]
        if not all(p.exists() for p in paths):
            continue
        va, vb = (np.asarray(read_json(p)["vector"]) for p in paths)
        cos = float(va @ vb)
        r, p_val = pearsonr(project(embeddings, va), project(embeddings, vb))
        out.append({
            "axes": [a, b],
            "vector_cosine": round(cos, 3),
            "chunk_r": round(float(r), 3),
            "chunk_p": round(float(p_val), 3),
            "n_chunks": len(mission),
            "separated": bool(abs(cos) < 0.5 and abs(r) < 0.6),
        })
    return out


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
    def _agreement_lines(agr: dict | None, judgments: list[dict]) -> list[str]:
        out = []
        if agr and agr.get("n"):
            ca = agr.get("confident_agreement")
            gate = "PASS" if (ca or 0) >= AGREEMENT_GATE else "INVESTIGATE"
            ca_s = f"{ca:.0%} ({agr['n_confident']} pairs)" if ca is not None else "n/a"
            cl = agr.get("close_agreement")
            cl_s = f"{cl:.0%} ({agr['n_close']})" if cl is not None else "n/a"
            out.append(f"- Duel agreement (PRIMARY): **{agr['agreement']:.0%}** of {agr['n']}; "
                       f"confident |Δz|≥{agr['confident_margin_z']}: **{ca_s}** — {gate}; close: {cl_s}")
        gpy = games_per_year(judgments)
        note = "" if gpy >= 10 else f" (≈{gpy} games/yr; BT ranking needs ~10 to be stable)"
        return out + [f"- Spearman is the timeline-shape statistic, secondary{note}"]

    lines += ["## 2. LLM pairwise tournament"]
    if "tournament" in results:
        lines += _agreement_lines(results.get("tournament_agreement"),
                                  results["tournament"]["judgments"])
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
    for axis, t in results.get("tournaments", {}).items():
        lines += [f"### {axis} tournament"]
        lines += _agreement_lines(t.get("agreement"), t["tournament"]["judgments"])
        lines += [
            f"- Chunk embedding-vs-LLM Spearman: **{t['spearman_chunk']}**",
            f"- Sentence embedding-vs-LLM Spearman: **{t['spearman_sentence']}**",
            f"- {len(t['tournament']['judgments'])} pairwise judgments", "",
        ]
    lines += [
        "## 3. Axis-sentence perturbation",
        f"- Min Spearman across leave-one-out: **{pert['min_spearman']}** "
        f"({'PASS' if pert['robust'] else 'FRAGILE'})",
        f"- Mean: {pert['mean_spearman']}", "",
    ]
    sep = results.get("axis_separation", [])
    if sep:
        lines += ["## 4. Axis separation", ""]
        for s in sep:
            verdict = "PASS" if s["separated"] else "OVERLAP: INVESTIGATE"
            lines.append(
                f"- {s['axes'][0]} vs {s['axes'][1]}: vector cosine {s['vector_cosine']}, "
                f"chunk-level r={s['chunk_r']} (n={s['n_chunks']}) — {verdict}"
            )
        lines.append("")
    ctrl = results.get("control_decoupling", [])
    if ctrl:
        lines += ["## 5. Control decoupling (all axes, chunk level)", "",
                  "| axis | r vs control | r(topk, log n) | diagnosis |",
                  "|---|---|---|---|"]
        for d in ctrl:
            mark = {"decoupled": "PASS",
                    "pool_size_suspect": "POOL-SIZE: top-k inflation, fix estimator",
                    "mix_shift_suspect": "MIX-SHIFT: composition change, read trend cautiously"}[d["diagnosis"]]
            lines.append(f"| {d['axis']} | {d['control_r']} | {d['r_topk_vs_logn']} | {mark} |")
        lines.append("")
    if profile.validation and profile.validation.notes:
        lines += ["## 6. Data expansion notes", ""]
        lines += [f"- {note}" for note in profile.validation.notes]
        lines += ["", "Disagreements are case studies, not silent overrides.", ""]
    else:
        lines += ["Disagreements are case studies, not silent overrides.", ""]
    (cdir / "validation_report.md").write_text("\n".join(lines) + "\n")


def main(company: str, n_pairs: int | None, seed: int, skip_tournament: bool,
         axes: list[str], backfill_agreement: bool = False) -> None:
    profile = CompanyProfile.load(company)
    validation = profile.validation
    cdir = company_dir(company)
    scores = pd.read_parquet(cdir / "axis_scores.parquet")
    quotes = read_json(cdir / "evidence_quotes.json")

    # Merge into any existing validation.json so a per-axis run doesn't clobber
    # sections it didn't recompute (the M6 gate reads the altruism keys).
    results: dict = read_json(cdir / "validation.json") if (cdir / "validation.json").exists() else {}
    results["ground_truth_chunk"] = ground_truth_check(scores, "chunk", validation=validation)
    results["ground_truth_sentence"] = ground_truth_check(scores, "sentence", validation=validation)
    print(f"Ground truth (chunk): {results['ground_truth_chunk']}")
    print(f"Ground truth (sentence): {results['ground_truth_sentence']}")

    if backfill_agreement:
        # Recompute agreement + spearman from STORED judgments against the
        # current ranking. Judgments are fixed data; the comparison target
        # moves with the methodology. No judge calls.
        if "tournament" in results:
            tour = results["tournament"]
            results["tournament_agreement"] = pairwise_agreement(
                scores, tour["judgments"], "chunk", "altruism")
            results["tournament_spearman_chunk"] = embedding_vs_llm(scores, tour, "chunk", "altruism")
            results["tournament_spearman_sentence"] = embedding_vs_llm(scores, tour, "sentence", "altruism")
            print(f"[altruism] backfilled agreement: {results['tournament_agreement']}")
        for axis, t in results.get("tournaments", {}).items():
            t["agreement"] = pairwise_agreement(scores, t["tournament"]["judgments"], "chunk", axis)
            t["spearman_chunk"] = embedding_vs_llm(scores, t["tournament"], "chunk", axis)
            t["spearman_sentence"] = embedding_vs_llm(scores, t["tournament"], "sentence", axis)
            print(f"[{axis}] backfilled agreement: {t['agreement']}")
        write_json(cdir / "validation.json", results)
        write_report(cdir, results, profile)
        print(f"Wrote {cdir / 'validation_report.md'} (backfill)")
        return

    if not skip_tournament:
        for axis in axes:
            if axis not in AXIS_TOURNAMENTS:
                raise SystemExit(f"no tournament question defined for axis '{axis}' "
                                 f"(have: {', '.join(AXIS_TOURNAMENTS)})")
            years = scores[(scores["axis"] == axis) & (scores["level"] == "chunk")]["year"].tolist()
            # Default budget scales with year count: BT standings need ~10
            # games/year to escape schedule luck (fixed 40 over 24 years was
            # ~3 games/year — the google lesson). Explicit --n-pairs overrides.
            n_pairs_eff = n_pairs or min(5 * len(years), len(years) * (len(years) - 1) // 2)
            print(f"[{axis}] tournament over {len(years)} years, {n_pairs_eff} pairs:")
            tour = tournament(quotes, years, n_pairs_eff, seed, level="chunk", axis=axis)
            agr = pairwise_agreement(scores, tour["judgments"], "chunk", axis=axis)
            sp_chunk = embedding_vs_llm(scores, tour, "chunk", axis=axis)
            sp_sent = embedding_vs_llm(scores, tour, "sentence", axis=axis)
            early = early_year_agreement(scores, tour, axis=axis)
            if axis == "altruism":  # legacy output shape, unchanged
                results["tournament"] = tour
                results["tournament_agreement"] = agr
                results["tournament_spearman_chunk"] = sp_chunk
                results["tournament_spearman_sentence"] = sp_sent
                results["early_year_agreement"] = early
            else:
                results.setdefault("tournaments", {})[axis] = {
                    "tournament": tour,
                    "agreement": agr,
                    "spearman_chunk": sp_chunk,
                    "spearman_sentence": sp_sent,
                    "early_year_agreement": early,
                }
            print(f"[{axis}] duel agreement (PRIMARY): {agr}")
            print(f"[{axis}] chunk vs LLM: {sp_chunk}")
            print(f"[{axis}] sentence vs LLM: {sp_sent}")
            print(f"[{axis}] early years: {early}")

    print("Perturbation check...")
    results["perturbation"] = perturbation_check(company)
    print(f"Min Spearman: {results['perturbation']['min_spearman']}")

    results["axis_separation"] = axis_separation_check(company)
    for s in results["axis_separation"]:
        print(f"Axis separation {s['axes']}: cosine {s['vector_cosine']}, "
              f"chunk r={s['chunk_r']} -> {'PASS' if s['separated'] else 'OVERLAP'}")

    results["control_decoupling"] = control_decoupling_check(scores, "chunk")
    for d in results["control_decoupling"]:
        print(f"Control decoupling {d['axis']}: r={d['control_r']} "
              f"r(topk,logn)={d['r_topk_vs_logn']} -> {d['diagnosis']}")

    write_json(cdir / "validation.json", results)
    write_report(cdir, results, profile)
    print(f"Wrote {cdir / 'validation_report.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    parser.add_argument("--n-pairs", type=int, default=None,
                        help="pairs per tournament (default: 5 x n_years, capped at all pairs)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-tournament", action="store_true")
    parser.add_argument("--backfill-agreement", action="store_true",
                        help="recompute duel agreement + spearman from stored judgments "
                             "against the current ranking; no judge calls")
    parser.add_argument(
        "--axes", default="altruism",
        help="Comma-separated axes to run tournaments for "
             f"(available: {', '.join(AXIS_TOURNAMENTS)})",
    )
    args = parser.parse_args()
    main(args.company, args.n_pairs, args.seed, args.skip_tournament,
         [a.strip() for a in args.axes.split(",") if a.strip()],
         backfill_agreement=args.backfill_agreement)
