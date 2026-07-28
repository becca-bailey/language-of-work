"""Export the judged shared-concept ranking as JSON for the dot-plot viz.

Reclusters (deterministic, k=80 seed=0), joins data/exclusion_pilot/
concept_judgments.json, keeps coherent culture_concepts + DEI values_commitment
clusters, applies the membership floor (>=3 companies with >=2 sentences each),
and emits per-concept: name, mean z, se, n, committed companies, top
contributors, and example sentences (2 central + masc/fem extremes).
"""
import json
import re
import sys
from collections import Counter

sys.path.insert(0, "src")

import numpy as np
from scipy.cluster.vq import kmeans2

from lowork.embeddings import EmbeddingStore

story = json.load(open("astro/src/data/stories/gender-language.json"))
rows = []  # (company, text, z, year)
for c in story["columns"]:
    for it in c["items"]:
        rows.append((c["name"], it["t"], it["z"], it.get("y")))

store = EmbeddingStore()
E = np.stack(store.embed([r[1] for r in rows]))
E = E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)
cents, labels = kmeans2(E, 80, minit="++", seed=0)

# Pole decomposition (docs/anti-feminine-measurements.md): per-sentence
# closeness to each pole centroid separately, z-scored over gender-mention-
# free sentences. mz high = masc-coded by APPROACH; fz low = by AVOIDANCE.
from lowork.gender_axis import GENDER_PAIRS, _norm

masc_c = _norm(_norm(np.stack(store.embed([m for m, _ in GENDER_PAIRS]))).mean(axis=0))
fem_c = _norm(_norm(np.stack(store.embed([f for _, f in GENDER_PAIRS]))).mean(axis=0))

judged = {r["k"]: r for r in json.load(open("data/exclusion_pilot/concept_judgments.json"))}

# Dominance cap (Becca 2026-07-24, revised same day): concepts where one
# company supplies >40% of sentences are EXCLUDED from the chart — their
# cross-company matches are often weak (fixed-cadence cycles = 58% Basecamp).
# This also drops severance/high-bar-hiring (74% Netflix); that concept's
# home is the Netflix propagation story, not this ranking.
MIN_PER_COMPANY, MIN_COMPANIES, MAX_SHARE = 2, 3, 0.40

# Becca 2026-07-24: score concepts on sentences WITHOUT explicit gender
# mentions — "women in tech" has no "men in tech" counterpart, so explicit
# mentions inflate the feminine pole asymmetrically. Raw all-sentence score
# kept as zAll for reference. Same regex as the unit chart's annotation layer.
GENDERED = re.compile(
    r"\b(man|men|woman|women|he|she|him|her|hers|his|himself|herself|male|female|"
    r"boys?|girls?|fathers?|mothers?|sons?|daughters?|dads?|moms?|brothers?|sisters?|"
    r"husbands?|wives|wife|kings?|queens?|gender|maternity|paternity|lgbtq?\+?|"
    r"boyfriends?|girlfriends?|alumnae|latinas?)\b", re.I)
MIN_CLEAN = 30

m_raw, f_raw = E @ masc_c, E @ fem_c
clean_all = np.array([not GENDERED.search(r[1]) for r in rows])
m_mu, m_sd = m_raw[clean_all].mean(), m_raw[clean_all].std()
f_mu, f_sd = f_raw[clean_all].mean(), f_raw[clean_all].std()
mz_all = (m_raw - m_mu) / m_sd
fz_all = (f_raw - f_mu) / f_sd

out = []
set_aside = Counter()
for k, j in judged.items():
    keep = (j["category"] == "culture_concept" and j["coherent"]) or \
           j.get("dei_kind") == "values_commitment"
    if not keep:
        if j["category"] == "dei_program_reporting":
            set_aside["diversity-reporting"] += 1
        elif j["category"] == "corporate_pr":
            set_aside["press-release / product marketing"] += 1
        elif j["category"] == "navigation_boilerplate":
            set_aside["navigation / boilerplate"] += 1
        else:
            set_aside["incoherent"] += 1
        continue
    idx = np.where(labels == k)[0]
    z_all = float(np.mean([rows[i][2] for i in idx]))
    n_gendered = sum(1 for i in idx if GENDERED.search(rows[i][1]))
    idx = np.array([i for i in idx if not GENDERED.search(rows[i][1])])
    if len(idx) < MIN_CLEAN:
        print(f"  mostly explicit gender mentions, drops [{k}] {j.get('shared_name', j['name'])} "
              f"({n_gendered}/{n_gendered + len(idx)} gendered, zAll {z_all:+.2f})")
        set_aside["mostly explicit gender mentions"] += 1
        continue
    cos = Counter(rows[i][0] for i in idx)
    committed = [co for co, n in cos.items() if n >= MIN_PER_COMPANY]
    if len(committed) < MIN_COMPANIES:
        print(f"  floor drops [{k}] {j.get('shared_name', j['name'])}")
        set_aside["below the sharing floor"] += 1
        continue
    zs = np.array([rows[i][2] for i in idx])
    sims = E[idx] @ cents[k]
    order = np.argsort(-sims)
    ex = lambda i: {"co": rows[idx[i]][0], "t": rows[idx[i]][1][:220],
                    "z": round(float(rows[idx[i]][2]), 2), "y": rows[idx[i]][3]}
    # Becca's ruling 2026-07-24: tooltip shows the most RELEVANT matches (nearest
    # the concept's center), not masc/fem extremes. Prefer distinct companies so
    # the examples also show the sharing, not one company's phrasing three times.
    picked, seen_cos = [], set()
    for i in order:
        if rows[idx[i]][0] in seen_cos:
            continue
        picked.append(int(i))
        seen_cos.add(rows[idx[i]][0])
        if len(picked) == 3:
            break
    for i in order:  # backfill if <3 distinct companies
        if len(picked) == 3:
            break
        if int(i) not in picked:
            picked.append(int(i))
    top_co, top_n = cos.most_common(1)[0]
    if top_n / len(idx) > MAX_SHARE:
        print(f"  cap drops [{k}] {j.get('shared_name', j['name'])} "
              f"({top_co} {top_n / len(idx):.0%})")
        set_aside["one company over the 40% cap"] += 1
        continue
    out.append({
        "k": int(k),
        "name": j.get("shared_name", j["name"]).lower(),
        "dei": j.get("dei_kind") == "values_commitment",
        "z": round(float(zs.mean()), 3),
        "se": round(float(zs.std() / np.sqrt(len(idx))), 3),
        "n": int(len(idx)),
        "nCos": len(committed),
        "topCos": [[co, n] for co, n in cos.most_common(4)],
        "topShare": round(top_n / len(idx), 2),
        "diffuse": bool(j.get("diffuse")),
        "zAll": round(z_all, 3),
        "mz": round(float(mz_all[idx].mean()), 3),
        "fz": round(float(fz_all[idx].mean()), 3),
        "nGendered": int(n_gendered),
        "examples": [ex(i) for i in picked],
    })

out.sort(key=lambda r: -r["z"])
doc = {"setAside": dict(set_aside), "concepts": out}
for path in ("astro/src/data/stories/gender-concepts.json",
             "data/exclusion_pilot/concept_viz.json"):
    json.dump(doc, open(path, "w"), ensure_ascii=False, indent=1)
    print(f"{len(out)} concepts -> {path}")
print("set aside:", dict(set_aside))
