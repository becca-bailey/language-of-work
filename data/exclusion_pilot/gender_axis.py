"""Gender-coding axis discovery (Kozlowski/Taddy/Evans 2019 method).

Axis = normalized mean of normalized difference vectors over PURE gender-term
pairs (man-woman, he-she, ...). No intuition words in the poles — "hardcore"
etc. are projected, not assumed. Projection = cosine(text, axis); positive =
masculine-coded (male terms are the first element of each pair).

Steps:
 1. Build axis in the SAME embedding space as the corpus (EmbeddingStore).
 2. Known-answer test: stereotype-male vs stereotype-female occupation words
    and sentences must separate cleanly, or stop.
 3. Project the exclusion lexicon (falsifiable-intuition test).
 4. Project corpus mission_brand sentences per company (within-register, per
    Becca's genre-confound caution) + pilot cohort documents; z-score against
    the pooled corpus-sentence distribution.
"""
import sys

sys.path.insert(0, "scripts")
sys.path.insert(0, "src")

import numpy as np
import importlib

tcp = importlib.import_module("track_culture_propagation")
from lowork.embeddings import EmbeddingStore
from lowork.sentences import split_sentences

store = EmbeddingStore()
BASE = "/private/tmp/claude-501/-Users-becca-language-of-work/e2c0efc4-d008-4c43-8e4a-b72bd44154b2/scratchpad/exclusion_pilot/"

PAIRS = [
    ("man", "woman"), ("men", "women"), ("he", "she"), ("him", "her"),
    ("his", "hers"), ("himself", "herself"), ("male", "female"),
    ("boy", "girl"), ("father", "mother"), ("son", "daughter"),
    ("brother", "sister"), ("husband", "wife"), ("uncle", "aunt"),
    ("king", "queen"), ("grandfather", "grandmother"), ("gentleman", "lady"),
]

def norm(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-9)

male = norm(np.stack(store.embed([m for m, _ in PAIRS])))
female = norm(np.stack(store.embed([f for _, f in PAIRS])))
diffs = norm(male - female)
axis = norm(diffs.mean(axis=0))

# pair coherence: every pair's diff should point the same way
coh = diffs @ axis
print(f"axis built from {len(PAIRS)} pairs; diff-coherence min/mean = {coh.min():.2f}/{coh.mean():.2f}")

def proj(texts):
    return norm(np.stack(store.embed(texts))) @ axis

# ---- 2. known-answer test ----
male_stereo = ["infantry soldier", "quarterback", "lumberjack", "auto mechanic",
               "construction foreman", "fighter pilot", "wrestler"]
female_stereo = ["kindergarten teacher", "nurse", "ballerina", "babysitter",
                 "midwife", "cheerleader", "seamstress"]
neutral = ["accountant", "the weather today", "a wooden table", "spreadsheet software"]
pm, pf, pn = proj(male_stereo), proj(female_stereo), proj(neutral)
print("\nKNOWN-ANSWER (word level):")
print(f"  male-stereo   mean {pm.mean():+.3f}  range [{pm.min():+.3f},{pm.max():+.3f}]")
print(f"  female-stereo mean {pf.mean():+.3f}  range [{pf.min():+.3f},{pf.max():+.3f}]")
print(f"  neutral       mean {pn.mean():+.3f}")
sep = pm.min() > pf.max()
print(f"  clean separation (male.min > female.max): {sep}")

sent_m = ["The infantry platoon stormed the objective before dawn.",
          "He spent the weekend rebuilding the truck's transmission."]
sent_f = ["The kindergarten teacher comforted the crying child.",
          "She spent the afternoon arranging flowers for the bridal shower."]
print("  sentence-level:", [f"{x:+.3f}" for x in proj(sent_m)], "vs", [f"{x:+.3f}" for x in proj(sent_f)])

# ---- 3. exclusion lexicon: falsifiable-intuition test ----
lexicon = ["hardcore", "relentless", "intense", "intensity", "battle", "warrior",
           "mission", "dominate", "aggressive", "hustle", "grind", "builders",
           "misfits", "high performance", "raise the bar", "move fast",
           "brilliant", "excellence", "empathy", "care", "community",
           "belonging", "collaborative", "supportive", "wellbeing", "nurture",
           "inclusive", "work-life balance", "psychological safety", "kind"]
pl = proj(lexicon)
print("\nEXCLUSION LEXICON projections (+" + " = masculine-coded):")
for w, s in sorted(zip(lexicon, pl), key=lambda x: -x[1]):
    print(f"  {s:+.3f}  {w}")

# ---- 4. corpus discovery: per-company mission_brand sentences ----
print("\nCORPUS (mission_brand sentences, z vs pooled corpus):")
comp_sents = {}
for co in tcp.COMPANIES:
    seen = {}
    for y, s in tcp.company_sentences(co):
        k = s.lower().strip()
        if k not in seen or y < seen[k][0]:
            seen[k] = (y, s)
    if seen:
        comp_sents[co] = sorted(seen.values())

pool_scores = []
per_co = {}
for co, sents in comp_sents.items():
    sc = proj([s for _, s in sents])
    per_co[co] = sc
    pool_scores.append(sc)
pool = np.concatenate(pool_scores)
mu, sd = pool.mean(), pool.std()
print(f"  pooled: n={len(pool)} mean={mu:+.4f} sd={sd:.4f}")

COHORT = {"netflix", "coinbase", "engine", "palantir"}
rows = sorted(per_co.items(), key=lambda kv: -kv[1].mean())
for co, sc in rows:
    tag = " <== cohort" if co in COHORT else ""
    print(f"  {co:12s} n={len(sc):4d}  mean z={float((sc.mean()-mu)/sd*np.sqrt(len(sc))):+6.1f} (per-sent z {float((sc.mean()-mu)/sd):+.2f}){tag}")

# ---- pilot documents (the escalation tiers) ----
print("\nPILOT DOCUMENTS (per-sentence mean z):")
docs = {
    "netflix deck 2009": open("data/netflix/canon/culture_deck_2009.md").read(),
    "coinbase mission essay 2020": open("data/coinbase/canon/mission_focused_2020.md").read().split("---")[-1],
    "engine culture memo 2025": open("data/engine/manual_html/20260723_culture-memo.html").read(),
    "ramp careers 2026": open(BASE + "ramp_live.txt").read(),
    "flock careers 2026": open(BASE + "flock_live.txt").read(),
    "x ultimatum 2022": "Going forward, to build a breakthrough Twitter 2.0 and succeed in an increasingly competitive world, we will need to be extremely hardcore. This will mean working long hours at high intensity. Only exceptional performance will constitute a passing grade.",
    "spacex careers line": "SpaceX is like Special Forces; we do the missions that others think are impossible.",
    "anduril campaign": "It's hard work, on hard problems, on hard mode. If that isn't for you, then Anduril isn't the place for you. We don't hire engineers. We recruit believers.",
    "basecamp control": "We value a calm company and deliberate, concerted effort. We're not for everyone, wait, actually we are calm.",
}
import trafilatura
for name, raw in docs.items():
    text = trafilatura.extract(raw) if raw.strip().startswith("<") else raw
    if not text:
        text = raw
    sents = [s for s in split_sentences(text) if len(s.split()) >= 5]
    if not sents:
        continue
    sc = proj(sents)
    print(f"  {name:30s} n={len(sents):3d}  per-sent z {float((sc.mean()-mu)/sd):+.2f}")
