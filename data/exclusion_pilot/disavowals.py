"""Measurement B: what companies say no to — and its gender coding.

Exclusionary culture copy is structurally DISAVOWAL: "we are not a family",
"no rules", "not your cushy nine-to-fiver" each reject a way of working. This
measures the rejection directly:

  1. candidates: corpus sentences with negation/contrast markers (~1k)
  2. judge (Haiku, temp 0, forced tool): does the sentence disavow a way of
     working / kind of workplace / kind of person? If yes, extract the
     DISAVOWED thing as a short neutral phrase ("being a family", "having
     rules", "a comfortable easy job")
  3. score each disavowed phrase on the bipolar gender axis (z against the
     frozen 20-company baseline)

Prediction (Becca 2026-07-24): disavowed content skews feminine-coded — the
"anti-feminine" measurement as rhetoric rather than geometry.
Incremental: judgments cached by sentence hash in
data/exclusion_pilot/disavowal_judgments.json.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, "src")

import numpy as np

from anthropic import Anthropic

from lowork.config import CLASSIFIER_MODEL
from lowork.embeddings import EmbeddingStore
from lowork.gender_axis import build_axis, project

NEG = re.compile(r"\b(not|no|never|isn't|aren't|don't|won't|doesn't|didn't|nor|"
                 r"without|nothing|nobody|rather than|instead of)\b|n['']t\b", re.I)

story = json.load(open("astro/src/data/stories/gender-language.json"))
mu, sd = story["mu"], story["sd"]
cands = []
for c in story["columns"]:
    for it in c["items"]:
        if NEG.search(it["t"]):
            cands.append({"co": c["name"], "t": it["t"], "z": it["z"], "y": it.get("y")})
print(f"{len(cands)} candidates")

CACHE = "data/exclusion_pilot/disavowal_judgments.json"
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
key = lambda t: hashlib.sha1(t.encode()).hexdigest()[:16]

SYSTEM = """You analyze sentences from company careers/culture pages that contain negation. Decide for each whether it DISAVOWS something about working at the company — rejects a way of working, a kind of workplace, a kind of person, or an expectation ("we are not a family", "no rules", "this isn't a cushy job", "we don't hire jerks").

NOT disavowals: negations about products/customers/business ("no hidden fees"), factual descriptions ("you don't need an account"), negations inside supportive promises ("you'll never be left without support"), or idioms with nothing rejected.

For each disavowal, state the DISAVOWED thing as a short neutral noun phrase (2-8 words) naming what is being rejected, with no negation in it: "we are not a family" -> "being a family"; "no rules" -> "rules and processes"; "this isn't your cushy corporate nine-to-fiver" -> "a comfortable, easy job". Phrase it the way its defenders would, not dismissively."""

TOOL = {
    "name": "record_disavowals",
    "input_schema": {
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "disavowal": {"type": "boolean"},
                        "rejected": {"type": "string",
                                     "description": "neutral phrase; empty if not a disavowal"},
                    },
                    "required": ["id", "disavowal"],
                },
            }
        },
        "required": ["results"],
    },
}

todo = [c for c in cands if key(c["t"]) not in cache]
print(f"{len(todo)} to judge ({len(cands) - len(todo)} cached)")
client = Anthropic()
BATCH = 25
for b in range(0, len(todo), BATCH):
    batch = todo[b:b + BATCH]
    payload = [{"id": key(c["t"]), "company": c["co"], "sentence": c["t"]} for c in batch]
    resp = client.messages.create(
        model=CLASSIFIER_MODEL, max_tokens=3000, temperature=0,
        system=SYSTEM, tools=[TOOL],
        tool_choice={"type": "tool", "name": "record_disavowals"},
        messages=[{"role": "user", "content": json.dumps({"sentences": payload}, ensure_ascii=False)}],
    )
    got = {r["id"]: r for r in next(x for x in resp.content if x.type == "tool_use").input["results"]}
    for c in batch:
        r = got.get(key(c["t"]))
        if r is None:
            continue
        cache[key(c["t"])] = {"disavowal": bool(r["disavowal"]),
                              "rejected": (r.get("rejected") or "").strip()}
    if (b // BATCH) % 10 == 0:
        print(f"  judged {min(b + BATCH, len(todo))}/{len(todo)}")
        json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=1)
json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=1)

dis = []
for c in cands:
    j = cache.get(key(c["t"]))
    if j and j["disavowal"] and j["rejected"]:
        dis.append({**c, "rejected": j["rejected"]})
print(f"{len(dis)} disavowals extracted")

store = EmbeddingStore()
axis = build_axis(store)
pz = (project(store, axis, [d["rejected"] for d in dis]) - mu) / sd
for d, z in zip(dis, pz):
    d["rejectedZ"] = round(float(z), 3)

dis.sort(key=lambda d: d["rejectedZ"])
json.dump(dis, open("data/exclusion_pilot/disavowals.json", "w"), ensure_ascii=False, indent=1)

rz = np.array([d["rejectedZ"] for d in dis])
sz = np.array([d["z"] for d in dis])
corpus_mean = 0.17  # gender-mention-free corpus mean z (genre analysis)
print(f"\nrejected-content gender z: mean {rz.mean():+.2f} (corpus sentences ~{corpus_mean:+.2f})")
print(f"  fem-coded (<=-0.5): {(rz <= -0.5).mean():.0%}   masc-coded (>=+0.5): {(rz >= 0.5).mean():.0%}")
print(f"disavowing SENTENCES themselves: mean z {sz.mean():+.2f}")
print("\nmost feminine-coded rejections:")
for d in dis[:10]:
    print(f"  {d['rejectedZ']:+.2f} rejects «{d['rejected']}»  — {d['co']}: {d['t'][:80]}")
print("\nmost masculine-coded rejections:")
for d in dis[-10:]:
    print(f"  {d['rejectedZ']:+.2f} rejects «{d['rejected']}»  — {d['co']}: {d['t'][:80]}")
