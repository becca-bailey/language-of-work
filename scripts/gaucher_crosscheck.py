#!/usr/bin/env python
"""Dictionary-count cross-check of the gender axis (instrument path, step 2).

Scores the exact sentence set behind astro/src/data/stories/gender-language.json
with the published masculine/feminine word lists from Gaucher, Friesen & Kay
(2011, JPSP, doi 10.1037/a0022530), Appendix A, then correlates the per-company
dictionary rates with the embedding-axis results. Two instruments, no shared
failure mode: the dictionary knows nothing about embedding geometry, the axis
was never told which content words are gendered.

Scoring per the paper: a company's masculine score is the percentage of its
total words matching the masculine list (feminine likewise); asterisks accept
any letters/hyphens/numbers after the stem, bare words match exactly.

Writes docs/gaucher-crosscheck.md. Read-only with respect to story data.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from lowork.config import WEB_DATA_DIR

from track_culture_propagation import company_sentences

MASCULINE = """active adventurous aggress* ambitio* analy* assert* athlet* autonom*
boast* challeng* compet* confident courag* decide decisive decision* determin*
dominant domina* force* greedy headstrong hierarch* hostil* impulsive
independen* individual* intellect* lead* logic masculine objective opinion
outspoken persist principle* reckless stubborn superior self-confiden*
self-sufficien* self-relian*""".split()

FEMININE = """affectionate child* cheer* commit* communal compassion* connect*
considerate cooperat* depend* emotiona* empath* feminine flatterable gentle
honest interpersonal interdependen* interpersona* kind kinship loyal* modesty
nag nurtur* pleasant* polite quiet* respon* sensitiv* submissive support*
sympath* tender* together* trust* understand* warm* whin* yield*""".split()

# Broad stems most likely to fire on ungendered careers boilerplate
# ("leading provider", "responsibilities", "committed to", "childcare").
# Dropped in the sensitivity variant to see how much they drive the result.
BROAD_STEMS = {"lead*", "respon*", "commit*", "depend*", "child*",
               "individual*", "analy*", "connect*", "decision*", "principle*"}

TOKEN = re.compile(r"[a-z]+(?:[-'][a-z]+)*")


def compile_lists(entries: list[str]) -> list[tuple[str, re.Pattern]]:
    pats = []
    for e in entries:
        stem = e.rstrip("*")
        body = re.escape(stem) + (r"[a-z0-9-]*" if e.endswith("*") else "")
        pats.append((e, re.compile(rf"^{body}$")))
    return pats


def score(tokens: list[str], pats: list[tuple[str, re.Pattern]],
          hits: Counter, examples: Counter) -> int:
    n = 0
    for t in tokens:
        for entry, pat in pats:
            if pat.match(t):
                n += 1
                hits[entry] += 1
                examples[t] += 1
                break
    return n


def unique_sentences(co: str) -> list[str]:
    # Mirrors export_gender_story.unique_sentences (dedup lowercase, keep text).
    seen: dict[str, str] = {}
    for y, s in company_sentences(co):
        k = s.lower().strip()
        if k not in seen:
            seen[k] = s
    return list(seen.values())


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    return float((ra @ rb) / np.sqrt((ra @ ra) * (rb @ rb)))


def main(drop_broad: bool = False) -> dict:
    story = json.loads((WEB_DATA_DIR / "stories" / "gender-language.json").read_text())
    masc_entries = [e for e in MASCULINE if not (drop_broad and e in BROAD_STEMS)]
    fem_entries = [e for e in FEMININE if not (drop_broad and e in BROAD_STEMS)]
    masc_pats, fem_pats = compile_lists(masc_entries), compile_lists(fem_entries)

    rows = []
    stem_hits_m, stem_hits_f = Counter(), Counter()
    word_hits_m, word_hits_f = Counter(), Counter()
    for col in story["columns"]:
        co = col["company"]
        tokens = [t for s in unique_sentences(co) for t in TOKEN.findall(s.lower())]
        nm = score(tokens, masc_pats, stem_hits_m, word_hits_m)
        nf = score(tokens, fem_pats, stem_hits_f, word_hits_f)
        total = len(tokens)
        rows.append({
            "company": col["name"], "words": total,
            "dictMascPct": 100 * nm / total, "dictFemPct": 100 * nf / total,
            "dictNet": 100 * (nm - nf) / total,
            "embedMascPct": col["mascPct"], "embedFemPct": col["femPct"],
            "embedMeanZ": col["meanZ"],
        })

    arr = lambda k: np.array([r[k] for r in rows])
    stats = {
        "net_vs_meanZ": spearman(arr("dictNet"), arr("embedMeanZ")),
        "masc_vs_mascPct": spearman(arr("dictMascPct"), arr("embedMascPct")),
        "fem_vs_femPct": spearman(arr("dictFemPct"), arr("embedFemPct")),
    }
    return {"rows": rows, "stats": stats,
            "stems": {"masc": stem_hits_m, "fem": stem_hits_f},
            "words": {"masc": word_hits_m, "fem": word_hits_f}}


def fmt_memo(full: dict, sens: dict) -> str:
    rows = sorted(full["rows"], key=lambda r: -r["dictNet"])
    lines = [
        "# Gaucher dictionary cross-check (instrument path step 2)",
        "",
        "Generated by scripts/gaucher_crosscheck.py. Word lists: Gaucher, Friesen &",
        "Kay 2011 (JPSP), Appendix A. Same sentence set as the published story data",
        "(astro/src/data/stories/gender-language.json). Scores are % of total words,",
        "per the paper; their real-world job-ad baseline was ~1% per list, their",
        "experimental ads 7-8%.",
        "",
        "## Agreement (Spearman, n=%d companies)" % len(rows),
        "",
        "| comparison | full dictionary | broad stems dropped* |",
        "|---|---|---|",
    ]
    for key, label in [("net_vs_meanZ", "dictionary net (masc−fem) vs axis meanZ"),
                       ("masc_vs_mascPct", "dictionary masc%% vs axis mascPct"),
                       ("fem_vs_femPct", "dictionary fem%% vs axis femPct")]:
        lines.append(f"| {label.replace('%%', '%')} | "
                     f"{full['stats'][key]:.3f} | {sens['stats'][key]:.3f} |")
    lines += [
        "",
        "*broad stems dropped: " + ", ".join(sorted(BROAD_STEMS)),
        "",
        "## Per-company (sorted by dictionary net score)",
        "",
        "| company | words | dict masc% | dict fem% | net | axis mascPct | axis meanZ |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['company']} | {r['words']:,} | {r['dictMascPct']:.2f} | "
                     f"{r['dictFemPct']:.2f} | {r['dictNet']:+.2f} | "
                     f"{r['embedMascPct']} | {r['embedMeanZ']:+.2f} |")
    lines += ["", "## What the counts are made of (top stems, full dictionary)", ""]
    for side in ("masc", "fem"):
        top = ", ".join(f"{s} ({n:,})" for s, n in full["stems"][side].most_common(12))
        lines.append(f"- **{side}**: {top}")
    lines += ["", "Top matched surface words:", ""]
    for side in ("masc", "fem"):
        top = ", ".join(f"{w} ({n:,})" for w, n in full["words"][side].most_common(15))
        lines.append(f"- **{side}**: {top}")
    lines += [
        "",
        "## Reading notes",
        "",
        "- The dictionary is blind to embedding geometry; the axis was never told",
        "  which content words are gendered. Agreement between them is therefore",
        "  independent validation of the ranking; divergences show what each",
        "  instrument sees that the other cannot (the dictionary catches single",
        "  words out of context, the axis reads whole-sentence register).",
        "- False-positive pressure is real and documented above: lead* matches",
        "  'leading provider', respon* matches 'responsibilities', child* matches",
        "  childcare-benefits copy. The sensitivity column shows the correlation",
        "  with those stems removed.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    full = main(drop_broad=False)
    sens = main(drop_broad=True)
    memo = fmt_memo(full, sens)
    out = Path(__file__).resolve().parent.parent / "docs" / "gaucher-crosscheck.md"
    out.write_text(memo)
    print(memo)
    print(f"Wrote {out}")
