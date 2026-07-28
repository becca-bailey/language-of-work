"""Split the 13 dei_program_reporting clusters: values/commitment language
(belongs in the culture-concept ranking) vs metrics/event reporting (set
aside). Updates data/exclusion_pilot/concept_judgments.json in place with a
`dei_kind` field."""
import json
import sys
from collections import Counter

sys.path.insert(0, "src")

import numpy as np
from anthropic import Anthropic

from lowork.config import CLASSIFIER_MODEL
from lowork.embeddings import EmbeddingStore

story = json.load(open("astro/src/data/stories/gender-language.json"))
rows = []
for c in story["columns"]:
    for it in c["items"]:
        rows.append((c["name"], it["t"], it["z"]))

store = EmbeddingStore()
E = np.stack(store.embed([r[1] for r in rows]))
E = E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)

from scipy.cluster.vq import kmeans2

cents, labels = kmeans2(E, 80, minit="++", seed=0)

path = "data/exclusion_pilot/concept_judgments.json"
recs = json.load(open(path))

SYSTEM = """You are given a sample of sentences from company careers/culture pages, all on diversity & inclusion topics. Decide which kind dominates the cluster:

- "values_commitment": statements of belief, principle, or cultural commitment — how the company says its culture works or should work ("everyone belongs here", "we strive to create a workplace where all feel seen", "we advocate for equal rights"). First-person, present-tense culture claims.
- "metrics_reporting": representation statistics, percentages, report citations, program/event/ERG coverage written as news or accounting ("women tech hires increased to 25.7%", "the group co-hosts AmazeCon").

Pick the kind that covers the majority of the sample."""

TOOL = {
    "name": "record_kind",
    "input_schema": {
        "type": "object",
        "properties": {
            "kind": {"type": "string", "enum": ["values_commitment", "metrics_reporting"]},
            "reason": {"type": "string"},
        },
        "required": ["kind", "reason"],
    },
}

client = Anthropic()
for r in recs:
    if r["category"] != "dei_program_reporting":
        continue
    k = r["k"]
    idx = np.where(labels == k)[0]
    sims = E[idx] @ cents[k]
    order = np.argsort(-sims)
    sample_ix = list(order[:8]) + list(order[8::max(1, len(idx) // 6)][:4])
    sample = [rows[idx[j]][1][:200] for j in sample_ix]
    resp = client.messages.create(
        model=CLASSIFIER_MODEL, max_tokens=300, temperature=0,
        system=SYSTEM, tools=[TOOL],
        tool_choice={"type": "tool", "name": "record_kind"},
        messages=[{"role": "user", "content": json.dumps({"sample": sample}, ensure_ascii=False)}],
    )
    j = next(b for b in resp.content if b.type == "tool_use").input
    r["dei_kind"] = j["kind"]
    print(f"  [{k:2d}] {j['kind']:18s} z={r['mean_z']:+.2f} n={r['n']:3d}  {r['name']}")

json.dump(recs, open(path, "w"), ensure_ascii=False, indent=1)

print("\n=== FINAL RANKING: culture concepts + DEI values language ===")
kept = [r for r in recs if
        (r["category"] == "culture_concept" and r["coherent"])
        or r.get("dei_kind") == "values_commitment"]
for r in sorted(kept, key=lambda r: -r["mean_z"]):
    tag = "DEI" if r.get("dei_kind") else "   "
    print(f"{r['mean_z']:+.2f}±{r['se']:.2f} n={r['n']:3d} {r['n_co']:2d} cos {tag}  {r['name']}")
