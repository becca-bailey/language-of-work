"""Which genres of careers copy are most masculine/feminine-coded?

Every corpus sentence (explicit gender mentions excluded) is assigned to its
best-matching genre (embedding, floor 0.35) and to any exclusion sub-concept
it clears (>=0.5), then genres are ranked by mean gender-axis z.
"""
import re
import sys

sys.path.insert(0, "scripts")
sys.path.insert(0, "src")

import numpy as np
import importlib

tcp = importlib.import_module("track_culture_propagation")
from lowork.embeddings import EmbeddingStore
from lowork.gender_axis import build_axis, project

store = EmbeddingStore()
axis = build_axis(store)

GENDERED = re.compile(
    r"\b(man|men|woman|women|he|she|him|her|hers|his|himself|herself|male|female|"
    r"boys?|girls?|fathers?|mothers?|sons?|daughters?|dads?|moms?|brothers?|sisters?|"
    r"husbands?|wives|wife|kings?|queens?|gender|maternity|paternity|lgbtq?\+?|"
    r"boyfriends?|girlfriends?|alumnae|latinas?)\b", re.I)

GENRES = {
    "exclusion / not-good-enough": [
        "We are not for everyone — you probably shouldn't work here.",
        "Working here is intense; you'll be pushed harder than ever, and that's not for most people.",
        "Every seat must be earned; only exceptional performance is a passing grade.",
    ],
    "intensity / performance": [
        "We are a high-performance team with relentlessly high standards.",
        "We move fast, work hard, and hold a high bar for results.",
    ],
    "mission / change the world": [
        "Our mission is to change the world and have a lasting impact on humanity.",
        "We are solving the most important problems of our time.",
    ],
    "craft / engineering": [
        "We care deeply about the craft of building great software.",
        "Engineers here work on hard technical problems at scale.",
    ],
    "founder / bio / leadership": [
        "Our founder and chief executive leads the company's strategy.",
        "Before starting the company, our CEO built and sold two startups.",
    ],
    "benefits / perks": [
        "We offer health insurance, retirement plans, and generous paid time off.",
        "Free meals, wellness stipends, and commuter benefits for every employee.",
    ],
    "family / caregiving": [
        "We support employees and their families with childcare and family leave.",
        "Caregivers get the flexibility and support they need.",
    ],
    "wellbeing / balance": [
        "We care about your wellbeing and a healthy work-life balance.",
        "Take the time you need to rest, recharge, and take care of yourself.",
    ],
    "belonging / inclusion": [
        "Everyone belongs here — we build an inclusive culture where all feel welcome.",
        "Our employee resource groups build community and celebrate our differences.",
    ],
    "community / collaboration": [
        "We support each other and collaborate closely as one team.",
        "A warm, supportive community of colleagues who help each other grow.",
    ],
    "growth / learning": [
        "You'll learn constantly and grow your career with mentorship and training.",
        "We invest in your professional development.",
    ],
    "veterans / military": [
        "We hire veterans and value their military service and leadership.",
        "Those who served their country bring discipline and mission focus.",
    ],
    "product / commerce": [
        "Our platform helps businesses save time and money.",
        "Customers use our products every day to run their companies.",
    ],
}

def norm(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-9)

gvecs = {g: norm(np.stack(store.embed(a))) for g, a in GENRES.items()}
excl = {n: norm(np.stack(store.embed(c["anchors"]))) for n, c in
        importlib.import_module("track_culture_propagation").CONCEPTS.items()} if False else {}

# exclusion sub-concepts from the pilot
SUB = {
    "not_for_everyone": ["Our culture is not for everyone — and that's okay.",
                          "We don't expect this to be the perfect place for everyone.",
                          "This job is not for most people."],
    "intensity_warning": ["We'll be honest: working here is intense.",
                           "Sounds intense? It is.",
                           "You'll work harder and at a faster pace than you ever have."],
    "anti_pitch": ["Here's a letter persuading you not to apply.",
                    "You probably shouldn't work here.",
                    "Before you apply, let us talk you out of it."],
    "elite_misfits": ["We hire brilliant misfits, not normal people.",
                       "We work on hard problems with hardcore people.",
                       "Maybe you're not 'most people.'"],
    "earned_seat": ["Every seat must be earned here.",
                     "Only exceptional performance earns you a place on this team."],
}
svecs = {s: norm(np.stack(store.embed(a))) for s, a in SUB.items()}

# corpus sentences + gender z (frozen baseline mu/sd from the story export)
import json
story = json.load(open("astro/src/data/stories/gender-language.json"))
mu, sd = story["mu"], story["sd"]

rows = []  # (z, genre, subconcept?, co, text)
for c in story["columns"]:
    co = c["name"]
    texts = [it["t"] for it in c["items"] if not GENDERED.search(it["t"])]
    zs = [it["z"] for it in c["items"] if not GENDERED.search(it["t"])]
    if not texts:
        continue
    E = norm(np.stack(store.embed(texts)))
    gsims = {g: (E @ A.T).max(axis=1) for g, A in gvecs.items()}
    ssims = {s: (E @ A.T).max(axis=1) for s, A in svecs.items()}
    gnames = list(GENRES)
    gm = np.stack([gsims[g] for g in gnames])
    best_g = gm.argmax(axis=0)
    best_gv = gm.max(axis=0)
    for i, t in enumerate(texts):
        genre = gnames[best_g[i]] if best_gv[i] >= 0.35 else None
        subs = [s for s in SUB if ssims[s][i] >= 0.5]
        rows.append((zs[i], genre, subs, co, t))

print(f"{len(rows)} sentences (explicit gender mentions excluded)")
pooled = np.array([r[0] for r in rows])
print(f"pooled mean z {pooled.mean():+.2f}")

print("\n=== GENRE RANKING (mean gender z; + = masculine-coded) ===")
from collections import defaultdict
by_g = defaultdict(list)
for z, g, s, co, t in rows:
    by_g[g or "(unassigned)"].append(z)
for g, zs in sorted(by_g.items(), key=lambda kv: -np.mean(kv[1])):
    zs = np.array(zs)
    print(f"  {np.mean(zs):+.2f}  n={len(zs):5d}  {g}")

print("\n=== EXCLUSION SUB-CONCEPTS (the performative register) ===")
by_s = defaultdict(list)
for z, g, subs, co, t in rows:
    for s in subs:
        by_s[s].append((z, co, t))
allx = [x for v in by_s.values() for x in v]
if allx:
    print(f"  {np.mean([x[0] for x in allx]):+.2f}  n={len(allx):5d}  ALL exclusion-register sentences pooled")
for s, v in sorted(by_s.items(), key=lambda kv: -np.mean([x[0] for x in kv[1]])):
    zs = np.array([x[0] for x in v])
    print(f"  {zs.mean():+.2f}  n={len(v):5d}  {s}")
    for z, co, t in sorted(v, key=lambda x: -x[0])[:2]:
        print(f"           {z:+.2f} {co}: {t[:95]}")
