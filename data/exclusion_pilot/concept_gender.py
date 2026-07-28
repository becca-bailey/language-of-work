"""Shared concepts ranked on the gender axis.

Cluster every corpus sentence (careers register, all companies) in embedding
space; a cluster counts as a SHARED CONCEPT if it appears in >=5 companies
with no single company contributing more than 40% (guards against one
company's house voice masquerading as a shared idea). Rank shared concepts
by mean gender z. Explicit gender mentions and personal names are INCLUDED
(Becca's ruling 2026-07-24: talking about men more than women counts).
"""
import json
import sys
from collections import Counter

sys.path.insert(0, "src")

import numpy as np

from lowork.embeddings import EmbeddingStore

story = json.load(open("astro/src/data/stories/gender-language.json"))
rows = []  # (company, text, z)
for c in story["columns"]:
    for it in c["items"]:
        rows.append((c["name"], it["t"], it["z"]))
print(f"{len(rows)} sentences, {len(story['columns'])} companies")

store = EmbeddingStore()
E = np.stack(store.embed([r[1] for r in rows]))
E = E / (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)

K = 80
try:
    from sklearn.cluster import KMeans

    km = KMeans(n_clusters=K, n_init=4, random_state=0).fit(E)
    labels, cents = km.labels_, km.cluster_centers_
    print("clusterer: sklearn KMeans")
except ImportError:
    from scipy.cluster.vq import kmeans2

    cents, labels = kmeans2(E, K, minit="++", seed=0)
    print("clusterer: scipy kmeans2")

# Becca's rulings 2026-07-24: shared = >=3 companies each contributing >=2
# sentences (membership floor kills single-stray admissions), NO dominance
# cap (concentration is an artifact of corpus-size imbalance; report
# top_share as metadata instead).
MIN_N, MIN_COMPANIES, MIN_PER_COMPANY = 30, 3, 2

shared, house = [], []
for k in range(K):
    idx = np.where(labels == k)[0]
    if len(idx) < MIN_N:
        continue
    cos = Counter(rows[i][0] for i in idx)
    top_co, top_n = cos.most_common(1)[0]
    top_share = top_n / len(idx)
    zs = np.array([rows[i][2] for i in idx])
    sims = E[idx] @ cents[k]
    central = [rows[idx[j]] for j in np.argsort(-sims)[:3]]
    hi = rows[idx[int(np.argmax(zs))]]
    lo = rows[idx[int(np.argmin(zs))]]
    rec = dict(
        k=k, n=len(idx), n_co=len(cos), top_co=top_co, top_share=top_share,
        mean_z=zs.mean(), se=zs.std() / np.sqrt(len(idx)),
        companies=cos.most_common(5), central=central, hi=hi, lo=lo,
    )
    n_committed = sum(1 for n in cos.values() if n >= MIN_PER_COMPANY)
    (shared if n_committed >= MIN_COMPANIES else house).append(rec)

shared.sort(key=lambda r: -r["mean_z"])


def show(r):
    cos = ", ".join(f"{c}:{n}" for c, n in r["companies"])
    print(f"\n[{r['k']:2d}] z={r['mean_z']:+.2f}±{r['se']:.2f}  n={r['n']}  "
          f"{r['n_co']} companies (top {r['top_co']} {r['top_share']:.0%})  [{cos}]")
    for co, t, z in r["central"]:
        print(f"    c {z:+.2f} {co}: {t[:110]}")
    print(f"    ^ {r['hi'][2]:+.2f} {r['hi'][0]}: {r['hi'][1][:110]}")
    print(f"    v {r['lo'][2]:+.2f} {r['lo'][0]}: {r['lo'][1][:110]}")


print(f"\n=== SHARED CONCEPTS (>= {MIN_COMPANIES} companies w/ >= {MIN_PER_COMPANY} "
      f"sentences each, no dominance cap; {len(shared)} pass; ranked masc -> fem) ===")
for r in shared:
    show(r)

print(f"\n=== NOT SHARED (fails membership floor; {len(house)} excluded) ===")
for r in sorted(house, key=lambda r: -r["mean_z"])[:12]:
    cos = ", ".join(f"{c}:{n}" for c, n in r["companies"][:3])
    print(f"  z={r['mean_z']:+.2f} n={r['n']:4d} top={r['top_co']} {r['top_share']:.0%} [{cos}]"
          f"  e.g. {r['central'][0][1][:80]}")
