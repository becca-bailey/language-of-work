"""Measurement A: pole decomposition — approach vs avoidance.

The bipolar axis conflates "close to masculinity" with "far from femininity"
by construction. Here every sentence gets TWO scores: similarity to the
masculine pole centroid and to the feminine pole centroid, each z-scored over
the corpus (gender-mention-free sentences, consistent with the story
instrument). A group can then be masculine-coded two ways:
  approach   — unusually close to the masculine pole (high mz)
  avoidance  — unusually far from the feminine pole (low fz)
Hypothesis (Becca 2026-07-24): exclusion-register copy is masculine-coded by
AVOIDANCE — not closer to masculinity than intensity/boldness copy, but
farther from femininity.
"""
import json
import re
import sys
from collections import defaultdict

sys.path.insert(0, "src")

import numpy as np

from lowork.embeddings import EmbeddingStore
from lowork.gender_axis import GENDER_PAIRS, _norm

GENDERED = re.compile(
    r"\b(man|men|woman|women|he|she|him|her|hers|his|himself|herself|male|female|"
    r"boys?|girls?|fathers?|mothers?|sons?|daughters?|dads?|moms?|brothers?|sisters?|"
    r"husbands?|wives|wife|kings?|queens?|gender|maternity|paternity|lgbtq?\+?|"
    r"boyfriends?|girlfriends?|alumnae|latinas?)\b", re.I)

store = EmbeddingStore()
masc_c = _norm(_norm(np.stack(store.embed([m for m, _ in GENDER_PAIRS]))).mean(axis=0))
fem_c = _norm(_norm(np.stack(store.embed([f for _, f in GENDER_PAIRS]))).mean(axis=0))

story = json.load(open("astro/src/data/stories/gender-language.json"))
rows = [(c["name"], it["t"], it["z"]) for c in story["columns"] for it in c["items"]
        if not GENDERED.search(it["t"])]
E = _norm(np.stack(store.embed([r[1] for r in rows])))
m_raw, f_raw = E @ masc_c, E @ fem_c
mz = (m_raw - m_raw.mean()) / m_raw.std()
fz = (f_raw - f_raw.mean()) / f_raw.std()
print(f"{len(rows)} gender-mention-free sentences; corr(m,f) = {np.corrcoef(m_raw, f_raw)[0,1]:.3f}")

# groups: exclusion register (pilot sub-concept anchors), matched masc-coded
# comparisons (intensity, boldness), fem-coded, neutral
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
excl_anchors = _norm(np.stack(store.embed([a for v in SUB.values() for a in v])))
excl_sim = (E @ excl_anchors.T).max(axis=1)
is_excl = excl_sim >= 0.5

COMPARE = {
    "intensity/high-bar": ["We are a high-performance team with relentlessly high standards.",
                            "We move fast, work hard, and hold a high bar for results."],
    "boldness/ambition": ["We explore bold ideas and embrace the unknown.",
                           "Success requires us to be bold and ambitious."],
    "candor/feedback": ["You willingly receive and give feedback with candor.",
                         "We give each other direct, honest feedback."],
    "belonging/inclusion": ["Everyone belongs here — we build an inclusive culture where all feel welcome.",
                             "We create a workplace where everyone feels seen, heard, and valued."],
    "care/wellbeing": ["We care about your wellbeing and a healthy work-life balance.",
                        "We take care of each other and support each other."],
}
groups = {"exclusion register": is_excl}
for gname, anchors in COMPARE.items():
    A = _norm(np.stack(store.embed(anchors)))
    groups[gname] = ((E @ A.T).max(axis=1) >= 0.5) & ~is_excl

zs = np.array([r[2] for r in rows])
groups["all masc-coded (z>=+0.5)"] = (zs >= 0.5) & ~is_excl
groups["all fem-coded (z<=-0.5)"] = zs <= -0.5
groups["neutral band"] = (zs > -0.5) & (zs < 0.5)

print(f"\n{'group':28s} {'n':>5s} {'bipolar z':>10s} {'masc-pole mz':>13s} {'fem-pole fz':>12s}")
res = {}
for g, mask in groups.items():
    n = int(mask.sum())
    if n == 0:
        continue
    res[g] = dict(n=n, z=float(zs[mask].mean()),
                  mz=float(mz[mask].mean()), fz=float(fz[mask].mean()))
    r = res[g]
    print(f"{g:28s} {n:5d} {r['z']:+10.2f} {r['mz']:+13.2f} {r['fz']:+12.2f}")

json.dump(res, open("data/exclusion_pilot/pole_decomposition.json", "w"), indent=1)
print("\nsaved data/exclusion_pilot/pole_decomposition.json")
