"""Project-3 content classifier: isolate the canon subset, drop junk.

Register (firm/worker/press/legal) is already tagged at fetch and the axes do the
measurement, so this classifier has a narrow job: within the corpus, mark which
chunks are the firm's *codified values canon* (H3/H5 operate on canon, not all
firm text) and which are junk to exclude from embedding/scoring. Everything else
substantive is on_topic. Mirrors the dei_stance.py pattern: pinned Haiku,
temperature 0, hand-label gate via agreement_report (reused from classify.py).
"""

from __future__ import annotations

import json

from anthropic import Anthropic

from .classify import agreement_report  # label-agnostic; reused
from .config import CANON_LABELS, CLASSIFIER_MODEL

__all__ = ["classify_canon", "agreement_report", "SYSTEM_PROMPT"]

SYSTEM_PROMPT = """You classify text chunks gathered for a study of company values over time.

The chunks come from many sources: a company's own pages and blog posts, archived
snapshots, employee/community discussion (e.g. Hacker News), press coverage, and
legal/trademark documents. Each chunk is tagged with a `register`:
firm | worker | press | legal.

Assign exactly one label per chunk:

- canon: the COMPANY'S OWN codified statement of its mission, values, culture,
  guiding principles, or signature method — text that reads like a creed,
  manifesto, "our values", "the way we work", a mission statement, or a founder's
  articulation of what the company believes and stands for. The durable, quotable
  values text. Firm/founder voice only.
- on_topic: any other SUBSTANTIVE, relevant content — firm product/service/process
  or job descriptions, employee bios, worker testimony about working at or dealing
  with the company, press or community discussion of the company and its conduct,
  and trademark/license/policy/legal prose. Real prose with meaning that is simply
  not the codified values canon.
- junk: navigation menus, link/button lists, cookie banners, page chrome, code
  snippets, encoding artifacts, off-topic tangents (discussion NOT about this
  company), or fragments with no substantive content.

Tie-breakers:
1. canon is reserved for the company's OWN articulation of its mission/values/
   culture/method. A worker, journalist, or commenter describing, quoting, or
   praising the culture is on_topic, not canon. A chunk whose register is worker,
   press, or legal is NEVER canon — only firm-register text can be canon.
2. Recruiting copy, benefits, job/role descriptions, employee bios, company
   history or origin stories, and aspirational product copy ("we build products
   people love") are on_topic — NOT canon — even in firm voice. Canon is the
   explicit values/mission/principles/creed text itself, not the material around it.
3. A signature working method is canon ONLY when it is a named, codified "way"
   presented as the company's own (e.g. "the X Way", a manifesto). A descriptive
   walkthrough of how the company happens to build or operate ("our development
   process", "how we work") is on_topic.
4. An essay, blog post, or comment thread ABOUT values or creeds — discussing,
   advocating, or reflecting on whether a company should have one — is on_topic,
   not canon, even in firm/founder voice. Canon is the codified values statement
   itself, never commentary about the idea of one.
5. Trademark policy, license terms, and legal/enforcement prose are on_topic
   (substantive and relevant) — neither canon nor junk.
6. If a chunk mixes a codified values statement with bios/nav/other text, label it
   canon only if the values statement is the DOMINANT content; otherwise on_topic
   (or junk if mostly chrome/fragments).
7. Off-topic content — generic tech talk, unrelated news, discussion not about this
   company — is junk even when it is substantive prose.

Respond with a JSON array, one object per chunk, in input order:
[{"id": "<chunk id>", "label": "<label>"}]
Use only the labels above. Respond with the JSON array only."""

BATCH_SIZE = 25


def _classify_batch(client, model: str, batch: list[dict]) -> dict[str, str]:
    """Classify one batch -> {chunk_id: label}.

    The model occasionally omits chunks from its JSON array; those would
    otherwise vanish silently (results are keyed by returned id). Re-request the
    omitted subset once, then loudly default any still-missing chunk to junk.
    Unknown/garbled labels also fall back to junk (the safe exclusion)."""
    out: dict[str, str] = {}
    pending = batch
    for _ in range(2):
        payload = [
            {
                "id": c["chunk_id"],
                "register": c.get("register", ""),
                "heading": c.get("heading", ""),
                "text": c["text"],
            }
            for c in pending
        ]
        resp = client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=0,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
        )
        text = resp.content[0].text.strip()
        if text.startswith("```"):
            text = text.strip("`").removeprefix("json").strip()
        for item in json.loads(text):
            label = item["label"]
            if label not in CANON_LABELS:
                label = "junk"
            out[item["id"]] = label
        pending = [c for c in pending if c["chunk_id"] not in out]
        if not pending:
            break

    if pending:
        dropped = [c["chunk_id"] for c in pending]
        print(f"  WARNING: model omitted {len(dropped)} chunks after retry; defaulting to junk: {dropped}")
        for c in pending:
            out[c["chunk_id"]] = "junk"
    return out


def classify_canon(chunks: list[dict], model: str = CLASSIFIER_MODEL) -> dict[str, str]:
    """Classify chunks -> {chunk_id: label}. Batched, temperature 0.

    Passes each chunk's `register` so the model can apply the canon-only-from-firm
    rule. See _classify_batch for omitted/garbled-label handling."""
    client = Anthropic()
    results: dict[str, str] = {}

    for i in range(0, len(chunks), BATCH_SIZE):
        results.update(_classify_batch(client, model, chunks[i : i + BATCH_SIZE]))
        print(f"  classified {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)}")

    return results
