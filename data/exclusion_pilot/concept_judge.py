"""Name + type every shared-concept cluster, then rank CULTURE CONCEPTS only.

Same deterministic clustering as concept_gender.py (kmeans2 seed=0, k=80).
A Haiku judge sees each cluster's central + spread sample and returns a short
name and a category; the gender ranking is then re-cut to culture concepts so
diversity-REPORT boilerplate, press releases, and navigation junk stop
competing with actual shared ideas. No dominance cap (Becca's ruling); gate is
>=3 companies only.
"""
import json
import sys
from collections import Counter

sys.path.insert(0, "src")
sys.path.insert(0, "scripts")

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

K = 80
cents, labels = kmeans2(E, K, minit="++", seed=0)

MIN_N, MIN_COMPANIES = 30, 3

CATEGORIES = (
    "culture_concept",       # a shared idea about how work/culture/hiring is done
    "dei_program_reporting", # diversity stats, report numbers, program/event coverage
    "corporate_pr",          # press releases, product/business marketing, news
    "navigation_boilerplate",# links, job listings, UI copy, legal
    "incoherent_mixed",      # no single idea holds the cluster together
)

SYSTEM = """You are labeling clusters of sentences drawn from company careers pages and culture documents. For each cluster you receive a sample of member sentences (most-central first) and the distribution of companies contributing.

Return for the cluster:
- name: a 2-6 word noun phrase naming the shared idea (e.g. "candor and direct feedback", "written communication over chat"). Name the IDEA, not the companies.
- category: exactly one of
  * culture_concept — the sentences share a recognizable idea about how work, hiring, performance, or culture is done
  * dei_program_reporting — diversity statistics, representation numbers, program/event/ERG coverage written as reporting
  * corporate_pr — press releases, partnership announcements, product or business marketing
  * navigation_boilerplate — links, job listings, awards lists, UI or legal copy
  * incoherent_mixed — no single idea plausibly covers the sample
- coherent: true only if >=70% of the sample fits your name."""

TOOL = {
    "name": "record_cluster",
    "description": "Record the cluster's name and category.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "category": {"type": "string", "enum": list(CATEGORIES)},
            "coherent": {"type": "boolean"},
            "reason": {"type": "string", "description": "one short sentence"},
        },
        "required": ["name", "category", "coherent", "reason"],
    },
}

client = Anthropic()
out = []
for k in range(K):
    idx = np.where(labels == k)[0]
    if len(idx) < MIN_N:
        continue
    cos = Counter(rows[i][0] for i in idx)
    if len(cos) < MIN_COMPANIES:
        continue
    zs = np.array([rows[i][2] for i in idx])
    sims = E[idx] @ cents[k]
    order = np.argsort(-sims)
    sample_ix = list(order[:8]) + list(order[8::max(1, len(idx) // 6)][:4])
    sample = [{"company": rows[idx[j]][0], "sentence": rows[idx[j]][1][:200]}
              for j in sample_ix]
    resp = client.messages.create(
        model=CLASSIFIER_MODEL,
        max_tokens=500,
        temperature=0,
        system=SYSTEM,
        tools=[TOOL],
        tool_choice={"type": "tool", "name": "record_cluster"},
        messages=[{"role": "user", "content": json.dumps(
            {"companies": dict(cos.most_common()), "n_sentences": int(len(idx)),
             "sample": sample}, ensure_ascii=False)}],
    )
    block = next(b for b in resp.content if b.type == "tool_use")
    j = block.input
    top_co, top_n = cos.most_common(1)[0]
    hi = rows[idx[int(np.argmax(zs))]]
    lo = rows[idx[int(np.argmin(zs))]]
    central = rows[idx[order[0]]]
    out.append(dict(k=k, n=int(len(idx)), n_co=len(cos), top_co=top_co,
                    top_share=top_n / len(idx), mean_z=float(zs.mean()),
                    se=float(zs.std() / np.sqrt(len(idx))),
                    name=j["name"], category=j["category"],
                    coherent=j["coherent"], reason=j["reason"],
                    central=central, hi=hi, lo=lo))
    print(f"  [{k:2d}] {j['category']:22s} {'ok ' if j['coherent'] else 'INC'} "
          f"z={zs.mean():+.2f} n={len(idx):3d}  {j['name']}")

json.dump([{**r, "central": list(r["central"]), "hi": list(r["hi"]),
            "lo": list(r["lo"])} for r in out],
          open("data/exclusion_pilot/concept_judgments.json", "w"),
          ensure_ascii=False, indent=1)

print("\n=== CULTURE CONCEPTS ONLY (coherent; ranked masc -> fem) ===")
kept = [r for r in out if r["category"] == "culture_concept" and r["coherent"]]
for r in sorted(kept, key=lambda r: -r["mean_z"]):
    print(f"\n{r['mean_z']:+.2f}±{r['se']:.2f} n={r['n']:3d} "
          f"{r['n_co']:2d} cos (top {r['top_co']} {r['top_share']:.0%})  {r['name']}")
    print(f"    c {r['central'][2]:+.2f} {r['central'][0]}: {r['central'][1][:105]}")
    print(f"    ^ {r['hi'][2]:+.2f} {r['hi'][0]}: {r['hi'][1][:105]}")
    print(f"    v {r['lo'][2]:+.2f} {r['lo'][0]}: {r['lo'][1][:105]}")

print("\n=== SET ASIDE ===")
for r in sorted(out, key=lambda r: r["category"]):
    if not (r["category"] == "culture_concept" and r["coherent"]):
        print(f"  {r['category']:22s} {'ok ' if r['coherent'] else 'INC'} "
              f"z={r['mean_z']:+.2f} n={r['n']:3d}  {r['name']}")
