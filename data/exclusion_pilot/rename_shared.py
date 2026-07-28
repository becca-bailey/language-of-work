"""Re-name kept clusters from COMPANY-BALANCED samples.

The first naming pass sampled by pure centrality, so a cluster dominated by
one company got named for that company's phrasing ("written communication
over chat") even though the sentences other companies contribute are broader
(generic communication advice). Here the judge sees the nearest sentence per
distinct company and must name the idea actually shared across them —
and flag the cluster as diffuse if that sample no longer expresses one idea.
Adds shared_name/diffuse to data/exclusion_pilot/concept_judgments.json.
"""
import json
import sys
from collections import Counter

sys.path.insert(0, "src")

import numpy as np
from scipy.cluster.vq import kmeans2

from anthropic import Anthropic

from lowork.config import CLASSIFIER_MODEL
from lowork.embeddings import EmbeddingStore

story = json.load(open("astro/src/data/stories/gender-language.json"))
rows = [(c["name"], it["t"], it["z"]) for c in story["columns"] for it in c["items"]]
store = EmbeddingStore()
E = np.stack(store.embed([r[1] for r in rows]))
E = E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)
cents, labels = kmeans2(E, 80, minit="++", seed=0)

path = "data/exclusion_pilot/concept_judgments.json"
recs = json.load(open(path))

SYSTEM = """You name ideas shared across companies. You receive sentences from several companies' careers/culture pages, all drawn from one embedding cluster: the most representative sentence from EACH company (labeled), most-representative company first.

Return:
- name: a 2-6 word noun phrase for the idea these companies actually SHARE. Name only what covers the cross-company sample — if only one company's sentences express a specific idea and the rest are broader, name the broader idea. Never name one company's slogan.
- diffuse: true if no single idea plausibly covers a majority of the companies' sentences (they merely share tone or topic area).
- reason: one short sentence."""

TOOL = {
    "name": "record_name",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "diffuse": {"type": "boolean"},
            "reason": {"type": "string"},
        },
        "required": ["name", "diffuse", "reason"],
    },
}

MIN_PER_COMPANY, MIN_COMPANIES = 2, 3
client = Anthropic()

for r in recs:
    keep = (r["category"] == "culture_concept" and r["coherent"]) or \
           r.get("dei_kind") == "values_commitment"
    if not keep:
        continue
    k = r["k"]
    idx = np.where(labels == k)[0]
    cos = Counter(rows[i][0] for i in idx)
    if sum(1 for n in cos.values() if n >= MIN_PER_COMPANY) < MIN_COMPANIES:
        continue
    sims = E[idx] @ cents[k]
    order = np.argsort(-sims)
    sample, seen = [], set()
    for j in order:
        co = rows[idx[j]][0]
        if co in seen:
            continue
        seen.add(co)
        sample.append({"company": co, "sentence": rows[idx[j]][1][:200]})
        if len(sample) == 10:
            break
    resp = client.messages.create(
        model=CLASSIFIER_MODEL, max_tokens=300, temperature=0,
        system=SYSTEM, tools=[TOOL],
        tool_choice={"type": "tool", "name": "record_name"},
        messages=[{"role": "user", "content": json.dumps({"sample": sample}, ensure_ascii=False)}],
    )
    j = next(b for b in resp.content if b.type == "tool_use").input
    r["shared_name"], r["diffuse"] = j["name"], j["diffuse"]
    flag = "DIFFUSE" if j["diffuse"] else "ok"
    marker = "" if j["name"].lower() == r["name"].lower() else "  (was: " + r["name"] + ")"
    print(f"  [{k:2d}] {flag:7s} z={r['mean_z']:+.2f}  {j['name']}{marker}")

json.dump(recs, open(path, "w"), ensure_ascii=False, indent=1)
