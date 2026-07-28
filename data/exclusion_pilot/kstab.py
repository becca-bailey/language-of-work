"""k-stability check for the shared-concept gender ranking.

Cluster at k=50/80/120 and follow TRACER SENTENCES (one unmistakable sentence
per headline concept). For each k, report the stats of the cluster each tracer
lands in: mean z, n, committed companies (>=2 sentences), gate pass. If the
headline concepts keep their scores across k, the ranking is not a k artifact.
"""
import json
import sys
from collections import Counter

sys.path.insert(0, "src")

import numpy as np
from scipy.cluster.vq import kmeans2

from lowork.embeddings import EmbeddingStore

story = json.load(open("astro/src/data/stories/gender-language.json"))
rows = []
for c in story["columns"]:
    for it in c["items"]:
        rows.append((c["name"], it["t"], it["z"]))

store = EmbeddingStore()
E = np.stack(store.embed([r[1] for r in rows]))
E = E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)

TRACERS = {
    "severance / earned seat": "generous severance package",
    "write it up, don't chat it down": "chat it down",
    "candor / direct feedback": "willingly receive and give feedback",
    "autonomy / anti top-down": "not to seek to please their boss",
    "excellence through effort": "most of us have to put in considerable effort",
    "dream team": "comprise the dream team",
    "bold innovation": "explore bold ideas and embrace the unknown",
    "remote / flexible work": "all full-time employees can work remote",
    "collaboration / mutual support": "take care of each other, have fun together",
    "DEI commitment": "improving workforce representation and creating an inclusive",
    "pay equity": "maintain pay equity",
    "ERGs": "Equality Groups are employee-led",
    "women-in-tech stats (reporting)": "global women tech hires increased",
}

trace_ix = {}
for name, sub in TRACERS.items():
    hits = [i for i, r in enumerate(rows) if sub.lower() in r[1].lower()]
    if not hits:
        print(f"!! tracer not found: {name} ({sub})")
        continue
    trace_ix[name] = hits[0]

MIN_PER_COMPANY, MIN_COMPANIES = 2, 3

results = {}
for K in (50, 80, 120):
    cents, labels = kmeans2(E, K, minit="++", seed=0)
    n_pass = 0
    for k in range(K):
        idx = np.where(labels == k)[0]
        if len(idx) < 30:
            continue
        cos = Counter(rows[i][0] for i in idx)
        if sum(1 for n in cos.values() if n >= MIN_PER_COMPANY) >= MIN_COMPANIES:
            n_pass += 1
    results[K] = {}
    for name, ti in trace_ix.items():
        k = labels[ti]
        idx = np.where(labels == k)[0]
        cos = Counter(rows[i][0] for i in idx)
        zs = np.array([rows[i][2] for i in idx])
        committed = sum(1 for n in cos.values() if n >= MIN_PER_COMPANY)
        results[K][name] = (zs.mean(), zs.std() / np.sqrt(len(idx)), len(idx),
                            committed, committed >= MIN_COMPANIES and len(idx) >= 30)
    print(f"k={K}: {n_pass} clusters pass the gate")

print(f"\n{'concept':34s}" + "".join(f"  k={K}: z (n, cos, gate)   " for K in (50, 80, 120)))
for name in trace_ix:
    line = f"{name:34s}"
    for K in (50, 80, 120):
        z, se, n, nco, ok = results[K][name]
        line += f"  {z:+.2f}±{se:.2f} ({n:3d},{nco:2d},{'pass' if ok else 'FAIL'})"
    print(line)
