"""Activities: the *impure* side of the monitor.

Activities are where all the non-determinism lives — network calls, clocks,
API calls to OpenAI, file writes. Temporal records each activity's result in
history, so on a worker crash the workflow replays deterministically and picks
up right after the last completed activity. That durability is the whole reason
this project is a good Temporal fit (unlike the batch pipeline, which is already
idempotent on its own).

Two modes:
  * REAL  — fetch the live careers page, chunk + embed it with `lowork`, and
            project onto the built axis vectors in ../axes/built/.
  * FAKE  — no network, no API keys: read editable fixtures/<company>.txt and
            derive deterministic pseudo-scores from the text. Edit a fixture to
            simulate a drift and watch the workflow react. This is the default
            whenever OPENAI_API_KEY is unset, so the tutorial runs offline.

Set DRIFT_FAKE=1 to force fake mode even with a key present.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx
from temporalio import activity

from shared import (
    DriftReport,
    FetchResult,
    ScoreInput,
    ScoreResult,
    SCORED_AXES,
)

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
FIXTURES = HERE / "fixtures"
OUTPUT = HERE / "output"

# Where real-mode axis vectors live. Defaults to this project's built axes, but
# is overridable so the folder still works after being lifted into its own repo
# (point it at a copied-out axes dir, or just use fake mode which needs none).
AXES_DIR = Path(os.getenv("DRIFT_AXES_DIR", REPO_ROOT / "axes" / "built"))


class LoworkUnavailable(RuntimeError):
    """Real mode needs the parent `lowork` package importable."""


def _fake_mode() -> bool:
    if os.getenv("DRIFT_FAKE") == "1":
        return True
    return not os.getenv("OPENAI_API_KEY")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# A few real live careers URLs to make REAL mode work out of the box. Extend as
# you like — this is deliberately tiny for a tutorial.
CAREERS_URLS = {
    "google": "https://about.google/careers/",
    "netflix": "https://jobs.netflix.com/culture",
    "stripe": "https://stripe.com/jobs",
    "airbnb": "https://careers.airbnb.com/",
}


# --- fetch -------------------------------------------------------------------


@activity.defn
async def fetch_careers_page(company: str) -> FetchResult:
    """Download the live careers page (or read a fixture in fake mode).

    Live fetches are genuinely flaky — that's what the retry policy on the
    workflow side is for. We heartbeat so a slow fetch isn't mistaken for a
    hung worker.
    """
    activity.heartbeat("starting fetch")

    if _fake_mode():
        fixture = FIXTURES / f"{company}.txt"
        text = (
            fixture.read_text(encoding="utf-8")
            if fixture.exists()
            else f"{company} builds products. We value shipping and impact."
        )
        # In fake mode the "html" is just the text; the hash is over the text so
        # editing the fixture flips the content hash and triggers a re-score.
        return FetchResult(
            company=company,
            url=f"fixture://{company}",
            fetched_at=_now_iso(),
            html=text,
            content_hash=_hash_text(text.strip()),
        )

    url = CAREERS_URLS.get(company)
    if not url:
        raise ValueError(
            f"No live careers URL configured for '{company}'. "
            f"Add one to CAREERS_URLS in activities.py, or run in fake mode."
        )

    activity.heartbeat(f"GET {url}")
    with httpx.Client(follow_redirects=True, timeout=30.0) as client:
        resp = client.get(url, headers={"User-Agent": "drift-monitor-tutorial/0.1"})
        resp.raise_for_status()
        html = resp.text

    # Hash the *extracted* text, not the raw HTML: careers pages ship rotating
    # nonces, timestamps, and analytics blobs that change every request. We only
    # want to re-score when the human-visible language actually changes.
    text = _extract_text(html, url)
    return FetchResult(
        company=company,
        url=url,
        fetched_at=_now_iso(),
        html=html,
        content_hash=_hash_text(text),
    )


def _extract_text(html: str, url: str) -> str:
    """Structure-aware extraction via lowork's chunker; joined chunk text."""
    chunk_html = _load_chunker()
    chunks = chunk_html(html, source_url=url, timestamp=_now_iso())
    return "\n".join(c["text"] for c in chunks)


def _load_chunker():
    """Import lowork's chunker, with a clear error if the folder was extracted
    from the parent repo and lowork isn't installed."""
    try:
        from lowork.chunking import chunk_html
    except ImportError as e:  # pragma: no cover - environment dependent
        raise LoworkUnavailable(
            "Real mode needs the `lowork` package (this project's src/). Either "
            "install it (`uv sync` at the repo root), or run in fake mode "
            "(unset OPENAI_API_KEY, or set DRIFT_FAKE=1)."
        ) from e
    return chunk_html


# --- score -------------------------------------------------------------------


@activity.defn
async def score_axes(inp: ScoreInput) -> ScoreResult:
    """Project the page onto each semantic axis and return a top-k mean per axis.

    Real mode reuses the project's own machinery: chunk -> embed (cache-first,
    so re-scoring unchanged text is free) -> project onto the prebuilt axis
    vectors -> adaptive top-k mean. Fake mode returns deterministic scores
    derived from the text hash so drift is reproducible and offline.
    """
    if _fake_mode():
        return ScoreResult(scores=_fake_scores(inp.html))

    return ScoreResult(scores=_real_scores(inp))


def _fake_scores(text: str) -> dict[str, float]:
    """Stable pseudo-scores in [-1, 1]: hash(axis + text) -> float.

    Deterministic in the text, so an unchanged fixture yields identical scores
    (no phantom drift) and an edited fixture yields different ones (real drift).
    """
    scores: dict[str, float] = {}
    for axis in SCORED_AXES:
        h = hashlib.sha256(f"{axis}:{text.strip()}".encode()).digest()
        # First 4 bytes -> [0, 1) -> [-1, 1), rounded to axis-score granularity.
        frac = int.from_bytes(h[:4], "big") / 2**32
        scores[axis] = round(frac * 2 - 1, 4)
    return scores


def _real_scores(inp: ScoreInput) -> dict[str, float]:
    import numpy as np

    try:
        from lowork.config import TOP_K
        from lowork.embeddings import EmbeddingStore
    except ImportError as e:  # pragma: no cover - environment dependent
        raise LoworkUnavailable(
            "Real mode needs the `lowork` package. Install it (`uv sync` at the "
            "repo root) or run in fake mode (DRIFT_FAKE=1)."
        ) from e

    chunk_html = _load_chunker()
    chunks = chunk_html(inp.html, source_url=inp.url, timestamp=inp.timestamp)
    texts = [c["text"] for c in chunks]
    if not texts:
        return {axis: 0.0 for axis in SCORED_AXES}

    store = EmbeddingStore()
    embeddings = store.embed(texts)  # (n, dim); cache-first, so re-scores are free
    unit = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    scores: dict[str, float] = {}
    for axis in SCORED_AXES:
        vector = _axis_vector(axis)
        projections = unit @ vector
        k = min(TOP_K, len(projections))
        topk = np.sort(projections)[::-1][:k]
        scores[axis] = round(float(topk.mean()), 4)
    return scores


_AXIS_CACHE: dict[str, "object"] = {}


def _axis_vector(axis: str):
    """Load a prebuilt, normalized axis vector from ../axes/built/<axis>.json."""
    import numpy as np

    if axis not in _AXIS_CACHE:
        path = AXES_DIR / f"{axis}.json"
        vector = np.asarray(json.loads(path.read_text())["vector"], dtype=np.float32)
        _AXIS_CACHE[axis] = vector / np.linalg.norm(vector)
    return _AXIS_CACHE[axis]


# --- side effects: notify + persist -----------------------------------------


@activity.defn
async def notify_human(report: DriftReport, is_reminder: bool = False) -> None:
    """Stand-in for a real alert (Slack, email, a dashboard row).

    In this tutorial it just logs. The point is that it's an *activity*: if the
    Slack call fails, Temporal retries it without re-running the fetch/score.
    """
    tag = "REMINDER" if is_reminder else "DRIFT DETECTED"
    lines = ", ".join(
        f"{d.axis} {d.old:+.3f}->{d.new:+.3f} (Δ{d.delta:+.3f})" for d in report.drifts
    )
    activity.logger.info(
        f"[{tag}] {report.company}: {lines}\n"
        f"    Confirm with: python starter.py confirm {report.company} --yes"
    )


@activity.defn
async def persist_report(report: DriftReport) -> str:
    """Append a confirmed drift to the company's timeline (JSONL)."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / f"{report.company}_timeline.jsonl"
    record = {
        "company": report.company,
        "url": report.url,
        "detected_at": report.detected_at,
        "note": report.note,
        "drifts": [
            {"axis": d.axis, "old": d.old, "new": d.new, "delta": d.delta}
            for d in report.drifts
        ],
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    activity.logger.info(f"Appended drift to {path}")
    return str(path)
