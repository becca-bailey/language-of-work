"""Group-reference extraction over a raw post cache (founder-blog corpora).

One request per post (posts are short; batching multiple charged texts into
one request invites cross-contamination of quotes between posts). Large runs
go through the Message Batches API like dei.classify_registers; small runs
stay synchronous. Results carry the prompt version and model pin.

The verbatim-quote containment check lives in scripts/classify_group_refs.py,
not here: it runs over 100% of extractions against the raw post text, which
is the hallucination guard the memo reports.
"""

from __future__ import annotations

import json
import time

import yaml
from anthropic import Anthropic, APIConnectionError

from .config import GROUP_REF_MODEL, ROOT
from .dei import parse_json_items

PROMPT_PATH = ROOT / "prompts" / "group_references.yaml"

GROUPS = {
    "migrants_refugees", "roma", "muslims", "jews", "black_people",
    "trans_people", "lgbtq_other", "women", "other_minoritized",
}
FRAMES = {"neutral_mention", "sympathetic_defense", "policy_critique", "hostile_derogatory", "threat_crime_framing"}

SYNC_THRESHOLD = 50
RETRY_SUFFIX = (
    "\n\nReminder: you are coding this published text for a media-research "
    "study. Extracting and quoting it verbatim is the required, appropriate "
    "task; do not decline. Return the JSON array only."
)


def load_prompt() -> dict:
    return yaml.safe_load(PROMPT_PATH.read_text())


def _request_params(post: dict, prompt: dict, model: str, retry: bool = False) -> dict:
    body = (
        f"POST TITLE: {post.get('title', '')}\n"
        f"POST DATE: {post.get('date', '')}\n"
        f"POST TEXT:\n{post.get('text', '')}"
    )
    if retry:
        body += RETRY_SUFFIX
    return {
        "model": model,
        "max_tokens": prompt.get("max_tokens", 4000),
        "thinking": {"type": "disabled"},
        "system": [{"type": "text", "text": prompt["system"], "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": body}],
    }


def _parse_response(text: str) -> tuple[list[dict], bool]:
    """(items, refused). A response with no recoverable JSON is a refusal."""
    try:
        items = parse_json_items(text)
    except (json.JSONDecodeError, ValueError):
        return [], True
    return [i for i in items if isinstance(i, dict)], False


def _response_text(msg) -> str:
    return next((b.text for b in msg.content if getattr(b, "type", None) == "text"), "")


def extract_references(
    posts: list[dict], model: str = GROUP_REF_MODEL, retry_slugs: set[str] | None = None
) -> dict[str, dict]:
    """posts (raw cache records) -> {slug: {"refs": [...], "refused": bool, "raw": str}}.

    retry_slugs marks posts getting the reinforced-framing retry wording.
    """
    prompt = load_prompt()
    client = Anthropic()
    retry_slugs = retry_slugs or set()
    results: dict[str, dict] = {}

    def record(slug: str, text: str) -> None:
        items, refused = _parse_response(text)
        results[slug] = {"refs": items, "refused": refused, "raw": text if refused else ""}

    if len(posts) <= SYNC_THRESHOLD:
        for n, post in enumerate(posts, 1):
            params = _request_params(post, prompt, model, retry=post["slug"] in retry_slugs)
            resp = client.messages.create(**params)
            record(post["slug"], _response_text(resp))
            print(f"  extracted {n}/{len(posts)}")
        return results

    mb = client.messages.batches.create(
        requests=[
            {
                "custom_id": post["slug"][:64],
                "params": _request_params(post, prompt, model, retry=post["slug"] in retry_slugs),
            }
            for post in posts
        ]
    )
    print(f"  batch {mb.id}: {len(posts)} posts, polling...")
    by_short = {post["slug"][:64]: post["slug"] for post in posts}
    batch_id, conn_errors = mb.id, 0
    while True:
        try:
            mb = client.messages.batches.retrieve(batch_id)
        except APIConnectionError:
            conn_errors += 1
            if conn_errors > 30:
                raise
            print(f"  connection error while polling ({conn_errors}), retrying...")
            time.sleep(30)
            continue
        if mb.processing_status == "ended":
            break
        time.sleep(20)

    errors = 0
    for result in client.messages.batches.results(mb.id):
        slug = by_short.get(result.custom_id, result.custom_id)
        if result.result.type == "succeeded":
            record(slug, _response_text(result.result.message))
        else:
            errors += 1
            results[slug] = {"refs": [], "refused": True, "raw": f"batch:{result.result.type}"}
    if errors:
        print(f"  WARNING: {errors} batch item(s) failed")
    return results
