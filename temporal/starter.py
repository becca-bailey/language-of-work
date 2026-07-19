"""Client CLI: start a monitor, poke it, answer its reviews, read its state.

This is how you (or a scheduler, or a web backend) interact with a running
workflow from *outside* the worker. Each subcommand maps to one Temporal client
call — start, signal, or query.

Examples:
    python starter.py start google                 # begin monitoring
    python starter.py poll google                  # force an immediate check
    python starter.py status google                # query current state
    python starter.py review google                # show a pending drift review
    python starter.py confirm google --yes         # accept the drift -> timeline
    python starter.py confirm google --no          # reject it
"""

from __future__ import annotations

import argparse
import asyncio
import json

from temporalio.client import Client

from shared import (
    DEFAULT_DRIFT_THRESHOLD,
    DEFAULT_POLL_SECONDS,
    DEFAULT_REMIND_SECONDS,
    TASK_QUEUE,
    MonitorParams,
)
from workflows import CompanyDriftMonitor

TEMPORAL_TARGET = "localhost:7233"


def workflow_id(company: str) -> str:
    # Stable, one-per-company id. Starting the same company twice is a no-op
    # (reject-duplicate), which is exactly what an entity workflow wants.
    return f"drift-monitor-{company}"


async def _client() -> Client:
    return await Client.connect(TEMPORAL_TARGET)


async def cmd_start(args) -> None:
    client = await _client()
    params = MonitorParams(
        company=args.company,
        poll_seconds=args.poll_seconds,
        remind_seconds=args.remind_seconds,
        threshold=args.threshold,
    )
    handle = await client.start_workflow(
        CompanyDriftMonitor.run,
        params,
        id=workflow_id(args.company),
        task_queue=TASK_QUEUE,
    )
    print(f"Started monitor for '{args.company}' (workflow id: {handle.id})")
    print("Tip: run the worker (python worker.py) if you haven't yet.")


async def cmd_poll(args) -> None:
    client = await _client()
    handle = client.get_workflow_handle(workflow_id(args.company))
    await handle.signal(CompanyDriftMonitor.poll_now)
    print(f"Sent poll_now to '{args.company}'.")


async def cmd_status(args) -> None:
    client = await _client()
    handle = client.get_workflow_handle(workflow_id(args.company))
    state = await handle.query(CompanyDriftMonitor.status)
    print(json.dumps(state, indent=2))


async def cmd_review(args) -> None:
    client = await _client()
    handle = client.get_workflow_handle(workflow_id(args.company))
    pending = await handle.query(CompanyDriftMonitor.pending_review)
    if pending is None:
        print(f"No pending review for '{args.company}'.")
        return
    print(json.dumps(pending, indent=2))


async def cmd_confirm(args) -> None:
    client = await _client()
    handle = client.get_workflow_handle(workflow_id(args.company))
    confirmed = args.yes and not args.no
    await handle.signal(CompanyDriftMonitor.confirm_drift, args=[confirmed, args.note])
    verb = "confirmed" if confirmed else "rejected"
    print(f"Drift {verb} for '{args.company}'.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_start = sub.add_parser("start", help="start monitoring a company")
    p_start.add_argument("company")
    p_start.add_argument("--poll-seconds", type=int, default=DEFAULT_POLL_SECONDS)
    p_start.add_argument("--remind-seconds", type=int, default=DEFAULT_REMIND_SECONDS)
    p_start.add_argument("--threshold", type=float, default=DEFAULT_DRIFT_THRESHOLD)
    p_start.set_defaults(func=cmd_start)

    p_poll = sub.add_parser("poll", help="force an immediate poll")
    p_poll.add_argument("company")
    p_poll.set_defaults(func=cmd_poll)

    p_status = sub.add_parser("status", help="query current state")
    p_status.add_argument("company")
    p_status.set_defaults(func=cmd_status)

    p_review = sub.add_parser("review", help="show the pending drift review, if any")
    p_review.add_argument("company")
    p_review.set_defaults(func=cmd_review)

    p_confirm = sub.add_parser("confirm", help="accept or reject a pending drift")
    p_confirm.add_argument("company")
    p_confirm.add_argument("--yes", action="store_true", help="confirm the drift")
    p_confirm.add_argument("--no", action="store_true", help="reject the drift")
    p_confirm.add_argument("--note", default="", help="optional note stored with the report")
    p_confirm.set_defaults(func=cmd_confirm)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()
