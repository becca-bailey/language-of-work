"""Generate JSON for the gender-coding unit chart prototype.

Columns = careers-register companies (mission_brand sentences, deduped, whole
corpus; uniform-by-year sample if > CAP) + canon documents. Every sentence gets
a gender-axis z-score vs the pooled 20-company corpus distribution (frozen
baseline so cohort columns don't move the yardstick).
"""
import json
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

# frozen baseline: the 20 pre-exclusion companies
BASELINE = ["google","amazon","meta","palantir","coinbase","netflix","shopify","stripe",
            "airbnb","snap","hubspot","gitlab","github","basecamp","salesforce",
            "starbucks","uber","apple","nvidia","engine"]
pool = []
for co in BASELINE:
    sents = company_unique(co)
    if sents:
        pool.append(proj([s for _, s in sents]))
mu, sd = np.concatenate(pool).mean(), np.concatenate(pool).std()
print(f"baseline: mean {mu:+.4f} sd {sd:.4f}")

def sample_by_year(sents, cap):
    if len(sents) <= cap:
        return sents, False
    idx = np.linspace(0, len(sents) - 1, cap).round().astype(int)
    return [sents[i] for i in sorted(set(idx))], True

def column(name, sents, register, note=""):
    if not sents:
        return None
    sents, sampled = sample_by_year(sents, CAP)
    z = (proj([s for _, s in sents]) - mu) / sd
    order = np.argsort(-z)
    items = [{"z": round(float(z[i]), 2), "y": sents[i][0], "t": sents[i][1][:220]} for i in order]
    nm = sum(1 for i in items if i["z"] >= 0.5)
    nf = sum(1 for i in items if i["z"] <= -0.5)
    return {"name": name, "register": register, "n": len(items), "sampled": sampled,
            "mascPct": round(100 * nm / len(items)), "femPct": round(100 * nf / len(items)),
            "meanZ": round(float(z.mean()), 2), "note": note, "items": items}

cols = []
CAREERS = [("netflix", "Netflix"), ("coinbase", "Coinbase"), ("engine", "Engine"),
           ("palantir", "Palantir"), ("spacex", "SpaceX"), ("anduril", "Anduril"),
           ("ramp", "Ramp")]
for co, label in CAREERS:
    c = column(label, company_unique(co), "careers")
    if c:
        cols.append(c)
    else:
        print(f"  ! {co}: no embedded sentences yet — skipped")
c = column("Basecamp", company_unique("basecamp"), "control",
           "anti-intensity control; manifesto voice")
if c:
    cols.append(c)

def md_sentences(path, year):
    body = open(path).read().split("---")[-1]
    return [(year, s.strip()) for s in split_sentences(body) if len(s.strip().split()) >= 5]

canon = [
    ("Netflix deck '09", "data/netflix/canon/culture_deck_2009.md", 2009, ""),
    ("Coinbase essays", "data/coinbase/canon/mission_focused_2020.md", 2020, "mission-focused post"),
    ("Coinbase culture doc", "data/coinbase/canon/culture_at_coinbase.md", 2023, ""),
    ("X ultimatum '22", "data/x/canon/fork_in_the_road_2022.md", 2022, "'fork in the road' email"),
    ("Anduril campaign", "data/anduril/canon/dontworkatanduril_2024.md", 2024, "#DontWorkAtAnduril"),
]
for label, path, year, note in canon:
    try:
        c = column(label, md_sentences(path, year), "canon", note)
        if c:
            cols.append(c)
    except FileNotFoundError:
        print(f"  ! missing canon {path}")

out = {"generated": "2026-07-23", "baselineN": int(sum(len(p) for p in pool)),
       "mu": round(float(mu), 4), "sd": round(float(sd), 4), "cap": CAP, "columns": cols}
with open(BASE + "unit_chart_data.json", "w") as f:
    json.dump(out, f)
careers_cols = [c for c in cols if c["register"] == "careers"]
print(f"wrote {len(cols)} columns; careers columns present: {[c['name'] for c in careers_cols]}")
