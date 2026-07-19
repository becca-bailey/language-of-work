"""The drift-monitor workflow — one long-lived instance per company.

This is the heart of the tutorial and the part that genuinely needs Temporal.
It's an *entity workflow*: it starts once per company and runs "forever",
sleeping between polls, surviving worker restarts, and holding human-in-the-loop
state (a pending review) durably across those restarts.

Concepts on display, each mapped to a line below:
  * Timers            — `workflow.wait_condition(..., timeout=...)` between polls
  * Activity retries  — RetryPolicy on the fetch (live sites are flaky)
  * Signals           — poll_now / confirm_drift mutate state from outside
  * Queries           — status / pending_review read state without side effects
  * continue_as_new   — bounds event history on an unbounded loop
  * Determinism       — no clocks/imports here; all I/O is in activities

The workflow code must be deterministic (it is replayed from history on
recovery), so it imports activities only through the sandbox pass-through and
never touches the network, the filesystem, or the wall clock directly.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import (
        fetch_careers_page,
        notify_human,
        persist_report,
        score_axes,
    )
    from shared import (
        MAX_POLLS_PER_RUN,
        Decision,
        DriftReport,
        FetchResult,
        MonitorParams,
        ScoreInput,
        ScoreResult,
        significant_drifts,
    )


@workflow.defn
class CompanyDriftMonitor:
    def __init__(self) -> None:
        self._params: MonitorParams | None = None
        self._poll_now = False
        self._pending: DriftReport | None = None
        self._decision: Decision | None = None
        self._last_checked: str | None = None

    # --- signals: outside events that steer the running workflow -------------

    @workflow.signal
    def poll_now(self) -> None:
        """Force an immediate poll instead of waiting out the timer."""
        self._poll_now = True

    @workflow.signal
    def confirm_drift(self, confirmed: bool, note: str = "") -> None:
        """Human's verdict on the pending drift review."""
        self._decision = Decision(confirmed=confirmed, note=note)

    # --- queries: read state without mutating anything -----------------------

    @workflow.query
    def status(self) -> dict:
        p = self._params
        return {
            "company": p.company if p else None,
            "iteration": p.iteration if p else 0,
            "last_hash": p.last_hash if p else None,
            "last_scores": p.last_scores if p else {},
            "last_checked": self._last_checked,
            "awaiting_review": self._pending is not None,
        }

    @workflow.query
    def pending_review(self) -> dict | None:
        if self._pending is None:
            return None
        return {
            "company": self._pending.company,
            "detected_at": self._pending.detected_at,
            "drifts": [
                {"axis": d.axis, "old": d.old, "new": d.new, "delta": d.delta}
                for d in self._pending.drifts
            ],
        }

    # --- the run loop --------------------------------------------------------

    @workflow.run
    async def run(self, params: MonitorParams) -> None:
        self._params = params
        polls_this_run = 0

        while True:
            await self._wait_for_next_poll(params.poll_seconds)

            fetch = await self._fetch(params.company)
            self._last_checked = fetch.fetched_at
            params.iteration += 1

            if fetch.content_hash != params.last_hash:
                await self._handle_change(params, fetch)

            polls_this_run += 1
            # Restart with fresh (short) history once we've accumulated enough
            # events. State is fully captured in `params`, so this is seamless.
            if polls_this_run >= MAX_POLLS_PER_RUN:
                workflow.continue_as_new(params)

    async def _wait_for_next_poll(self, poll_seconds: int) -> None:
        """Sleep until the next poll, but wake early on a poll_now signal."""
        try:
            await workflow.wait_condition(
                lambda: self._poll_now, timeout=timedelta(seconds=poll_seconds)
            )
        except asyncio.TimeoutError:
            pass  # normal path: the poll interval elapsed
        self._poll_now = False

    async def _fetch(self, company: str) -> FetchResult:
        return await workflow.execute_activity(
            fetch_careers_page,
            company,
            start_to_close_timeout=timedelta(seconds=60),
            heartbeat_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                backoff_coefficient=2.0,
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=5,  # then surface the failure rather than loop forever
            ),
        )

    async def _handle_change(self, params: MonitorParams, fetch: FetchResult) -> None:
        """Content changed since last poll: re-score and, if it drifted, gate on
        a human before committing it to the timeline."""
        result: ScoreResult = await workflow.execute_activity(
            score_axes,
            ScoreInput(
                company=fetch.company,
                url=fetch.url,
                timestamp=fetch.fetched_at,
                html=fetch.html,
            ),
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        drifts = significant_drifts(params.last_scores, result.scores, params.threshold)

        # Always advance the baseline to the latest reading, drift or not.
        params.last_hash = fetch.content_hash
        params.last_scores = result.scores

        if not drifts:
            return  # changed text, but no axis moved enough to be interesting

        report = DriftReport(
            company=fetch.company,
            url=fetch.url,
            detected_at=fetch.fetched_at,
            drifts=drifts,
        )
        await self._review_and_persist(params, report)

    async def _review_and_persist(
        self, params: MonitorParams, report: DriftReport
    ) -> None:
        """Human-in-the-loop gate: notify, then block on a confirm signal, with a
        timer that re-notifies while the review sits unanswered."""
        self._pending = report
        self._decision = None
        await workflow.execute_activity(
            notify_human, args=[report, False], start_to_close_timeout=timedelta(seconds=30)
        )

        while self._decision is None:
            try:
                await workflow.wait_condition(
                    lambda: self._decision is not None,
                    timeout=timedelta(seconds=params.remind_seconds),
                )
            except asyncio.TimeoutError:
                await workflow.execute_activity(
                    notify_human,
                    args=[report, True],
                    start_to_close_timeout=timedelta(seconds=30),
                )

        decision = self._decision
        self._pending = None
        self._decision = None

        if decision.confirmed:
            report.note = decision.note
            await workflow.execute_activity(
                persist_report, report, start_to_close_timeout=timedelta(seconds=30)
            )
