"""Shared types and constants for the drift-monitor tutorial.

Everything in this module is deterministic and dependency-light (dataclasses +
stdlib only) so it is safe to import from *both* the workflow and the activities.
The workflow sandbox forbids non-determinism, so keep it that way — no network,
no clocks, no numpy here.

The domain: watch a company's *live* careers page over time and notice when its
language drifts along the project's semantic axes (altruism, performance, …).
This is `language-of-work`'s thesis run forward in real time instead of
reconstructed from the Wayback Machine.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --- Temporal wiring ---------------------------------------------------------

TASK_QUEUE = "drift-monitor"

# The axes we score each fetch against. Every name here must have a built vector
# at ../axes/built/<name>.json (real mode) — the fake scorer ignores the vector
# and just needs the names. Kept short for a tutorial; add more freely.
SCORED_AXES: tuple[str, ...] = (
    "altruism",
    "performance",
    "techno_optimism",
    "craft",
    "inclusion",
)

# Defaults for a *tutorial* cadence — seconds, so you see the loop turn over in
# real time. A real deployment would poll weekly (e.g. 7 * 24 * 3600).
DEFAULT_POLL_SECONDS = 30
DEFAULT_REMIND_SECONDS = 20  # re-ping cadence while a review sits unconfirmed
DEFAULT_DRIFT_THRESHOLD = 0.05  # min |Δscore| on an axis to count as real drift

# History whose length we let a single workflow run accumulate before calling
# continue-as-new. Keeps event history bounded on an unbounded (forever) loop.
MAX_POLLS_PER_RUN = 50


# --- Data carried across activity / workflow / signal boundaries -------------
# All of these cross the network as JSON (Temporal's default data converter),
# so every field is a plain JSON-serializable scalar / list / dict.


@dataclass
class MonitorParams:
    """The full, self-contained state of one company's monitor.

    This is both the workflow *argument* and what we hand to `continue_as_new`,
    so it must capture everything needed to resume: the loop carries no hidden
    state across runs beyond this object.
    """

    company: str
    poll_seconds: int = DEFAULT_POLL_SECONDS
    remind_seconds: int = DEFAULT_REMIND_SECONDS
    threshold: float = DEFAULT_DRIFT_THRESHOLD
    # Rolling state, updated in place across polls and continue-as-new:
    last_hash: str | None = None
    last_scores: dict[str, float] = field(default_factory=dict)
    iteration: int = 0


@dataclass
class FetchResult:
    company: str
    url: str
    fetched_at: str  # ISO-8601, stamped inside the activity (never in the workflow)
    html: str
    content_hash: str  # sha256 of the extracted text; the change-detection key


@dataclass
class ScoreInput:
    company: str
    url: str
    timestamp: str
    html: str


@dataclass
class ScoreResult:
    scores: dict[str, float]  # axis name -> top-k mean projection


@dataclass
class AxisDrift:
    axis: str
    old: float
    new: float
    delta: float  # new - old


@dataclass
class DriftReport:
    company: str
    url: str
    detected_at: str
    drifts: list[AxisDrift]
    note: str = ""


@dataclass
class Decision:
    confirmed: bool
    note: str = ""


# --- Pure drift math (deterministic; unit-testable without Temporal) ---------


def significant_drifts(
    old: dict[str, float], new: dict[str, float], threshold: float
) -> list[AxisDrift]:
    """Axes whose score moved by at least `threshold` since the last fetch.

    The first time we ever score a company `old` is empty, so nothing is
    "drift" — we're just establishing the baseline. Drift is only meaningful
    against a prior reading.
    """
    if not old:
        return []
    out: list[AxisDrift] = []
    for axis, new_val in new.items():
        if axis not in old:
            continue
        delta = new_val - old[axis]
        if abs(delta) >= threshold:
            out.append(AxisDrift(axis=axis, old=old[axis], new=new_val, delta=delta))
    # Largest movement first — most interesting drift at the top of the report.
    out.sort(key=lambda d: abs(d.delta), reverse=True)
    return out
