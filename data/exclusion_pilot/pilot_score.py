"""Pilot: does 'exclusionary language' separate the hypothesized cohort?

Six draft sub-concepts of the anti-recruiting register, scored across every
corpus company (cached embeddings) plus the freshly captured ramp/flock/
doordash texts and the post-Elon X 'hardcore ultimatum' canon probe.
Output: per-company max-sim + hit counts per sub-concept -> cohort separation.
"""
import sys

sys.path.insert(0, "scripts")
sys.path.insert(0, "src")

import numpy as np
import importlib

tcp = importlib.import_module("track_culture_propagation")
from lowork.embeddings import EmbeddingStore
from lowork.sentences import split_sentences

BASE = "/private/tmp/claude-501/-Users-becca-language-of-work/e2c0efc4-d008-4c43-8e4a-b72bd44154b2/scratchpad/exclusion_pilot/"

SUBCONCEPTS = {
    "not_for_everyone": [
        "Our culture is not for everyone — and that's okay.",
        "We don't expect this to be the perfect place for everyone.",
        "This job is not for most people.",
    ],
    "intensity_warning": [
        "We'll be honest: working here is intense.",
        "Sounds intense? It is.",
        "You'll work harder and at a faster pace than you ever have.",
    ],
    "anti_pitch": [
        "Here's a letter persuading you not to apply.",
        "You probably shouldn't work here.",
        "Before you apply, let us talk you out of it.",
    ],
    "best_work_fastest_pace": [
        "You'll be pushed to do the best work of your career, at the fastest pace of your career.",
        "The best work of your life starts here.",
    ],
    "elite_misfits": [
        "We hire brilliant misfits, not normal people.",
        "We work on hard problems with hardcore people.",
        "Maybe you're not 'most people.'",
    ],
    "earned_seat": [
        "Every seat must be earned here.",
        "Only exceptional performance earns you a place on this team.",
    ],
}

store = EmbeddingStore()
vecs = {n: tcp._norm(np.stack(store.embed(a))) for n, a in SUBCONCEPTS.items()}

def sentences_from_file(path):
    text = open(path).read()
    return [(2026, s.strip()) for s in split_sentences(text) if len(s.strip().split()) >= 5]

# X post-Elon: careers page is a JS shell; the register lives in the Nov 2022
# "Twitter 2.0" ultimatum (canon, widely published). Probe with its core lines.
X_CANON = [(2022, "Going forward, to build a breakthrough Twitter 2.0 and succeed in an increasingly competitive world, we will need to be extremely hardcore."),
           (2022, "This will mean working long hours at high intensity."),
           (2022, "Only exceptional performance will constitute a passing grade.")]

extra = {
    "ramp*": sentences_from_file(BASE + "ramp_live.txt"),
    "flock*": sentences_from_file(BASE + "flock_live.txt"),
    "doordash*": sentences_from_file(BASE + "doordash_2023.txt"),
    "x-post-elon*": X_CANON,
}

companies = [c for c in tcp.COMPANIES]
rows = []
for co in companies + list(extra):
    if co in extra:
        sents = extra[co]
    else:
        seen = {}
        for y, s in tcp.company_sentences(co):
            k = s.lower().strip()
            if k not in seen or y < seen[k][0]:
                seen[k] = (y, s)
        sents = sorted(seen.values())
    if not sents:
        continue
    E = tcp._norm(np.stack(store.embed([s for _, s in sents])))
    row = {"company": co, "n": len(sents)}
    total_hits = 0
    best_overall = 0.0
    for name, A in vecs.items():
        sims = (A @ E.T).max(axis=0)
        hits = int((sims >= 0.5).sum())
        row[name] = f"{float(sims.max()):.2f}/{hits}"
        total_hits += hits
        best_overall = max(best_overall, float(sims.max()))
    row["hits_per_100"] = round(100 * total_hits / len(sents), 1)
    row["best"] = round(best_overall, 2)
    rows.append(row)

rows.sort(key=lambda r: -r["hits_per_100"])
cols = ["company", "n", "hits_per_100", "best"] + list(SUBCONCEPTS)
print(" | ".join(f"{c:>22s}" if c == "company" else f"{c:>8s}"[:24] for c in cols))
for r in rows:
    print(" | ".join(f"{str(r.get(c, '')):>22s}" if c == "company" else f"{str(r.get(c, '')):>8s}" for c in cols))

# strongest individual matches, for the memo
print("\nTop individual sentences (any sub-concept >= 0.6):")
for co in companies + list(extra):
    sents = extra.get(co) or []
    if not sents and co in companies:
        seen = {}
        for y, s in tcp.company_sentences(co):
            k = s.lower().strip()
            if k not in seen or y < seen[k][0]:
                seen[k] = (y, s)
        sents = sorted(seen.values())
    if not sents:
        continue
    E = tcp._norm(np.stack(store.embed([s for _, s in sents])))
    for name, A in vecs.items():
        sims = (A @ E.T).max(axis=0)
        for i in np.argsort(-sims)[:2]:
            if sims[i] >= 0.6:
                y, s = sents[i]
                print(f"  {float(sims[i]):.2f} {name:22s} {co:12s} {y} | {s[:90]}")
