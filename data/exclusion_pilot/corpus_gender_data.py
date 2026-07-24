"""All-corpus gender unit-chart data: every company, careers register only."""
import json
import sys

sys.path.insert(0, "scripts")
sys.path.insert(0, "src")

import numpy as np
import importlib

tcp = importlib.import_module("track_culture_propagation")
from lowork.embeddings import EmbeddingStore

store = EmbeddingStore()
BASE = "/private/tmp/claude-501/-Users-becca-language-of-work/e2c0efc4-d008-4c43-8e4a-b72bd44154b2/scratchpad/exclusion_pilot/"
CAP = 480

def norm(v):
    return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-9)

PAIRS = [("man","woman"),("men","women"),("he","she"),("him","her"),("his","hers"),
         ("himself","herself"),("male","female"),("boy","girl"),("father","mother"),
         ("son","daughter"),("brother","sister"),("husband","wife"),("uncle","aunt"),
         ("king","queen"),("grandfather","grandmother"),("gentleman","lady")]
M = norm(np.stack(store.embed([m for m, _ in PAIRS])))
F = norm(np.stack(store.embed([f for _, f in PAIRS])))
axis = norm(norm(M - F).mean(axis=0))

def proj(texts):
    return norm(np.stack(store.embed(texts))) @ axis

def company_unique(co):
    seen = {}
    for y, s in tcp.company_sentences(co):
        k = s.lower().strip()
        if k not in seen or y < seen[k][0]:
            seen[k] = (y, s)
    return sorted(seen.values())

BASELINE = ["google","amazon","meta","palantir","coinbase","netflix","shopify","stripe",
            "airbnb","snap","hubspot","gitlab","github","basecamp","salesforce",
            "starbucks","uber","apple","nvidia","engine"]
all_sents = {co: company_unique(co) for co in tcp.COMPANIES}
pool = np.concatenate([proj([s for _, s in all_sents[co]]) for co in BASELINE if all_sents.get(co)])
mu, sd = pool.mean(), pool.std()
print(f"baseline: mean {mu:+.4f} sd {sd:.4f}")

from lowork.company import CompanyProfile

cols = []
for co in tcp.COMPANIES:
    sents = all_sents.get(co) or []
    if not sents:
        print(f"  ! {co}: no sentences — skipped")
        continue
    sampled = False
    if len(sents) > CAP:
        idx = sorted(set(np.linspace(0, len(sents) - 1, CAP).round().astype(int)))
        sents = [sents[i] for i in idx]
        sampled = True
    z = (proj([s for _, s in sents]) - mu) / sd
    order = np.argsort(-z)
    items = [{"z": round(float(z[i]), 2), "y": sents[i][0], "t": sents[i][1][:220]} for i in order]
    nm = sum(1 for i in items if i["z"] >= 0.5)
    nf = sum(1 for i in items if i["z"] <= -0.5)
    cols.append({"name": CompanyProfile.load(co).display_name, "register": "careers",
                 "n": len(items), "sampled": sampled,
                 "mascPct": round(100 * nm / len(items)), "femPct": round(100 * nf / len(items)),
                 "meanZ": round(float(z.mean()), 2), "note": "", "items": items})

out = {"generated": "2026-07-23", "baselineN": int(len(pool)),
       "mu": round(float(mu), 4), "sd": round(float(sd), 4), "cap": CAP, "columns": cols}
with open(BASE + "corpus_gender_data.json", "w") as f:
    json.dump(out, f)
for c in sorted(cols, key=lambda c: -c["mascPct"]):
    print(f"{c['name']:14s} n={c['n']:4d} masc {c['mascPct']:3d}% / fem {c['femPct']:3d}%  meanZ {c['meanZ']:+.2f}")
