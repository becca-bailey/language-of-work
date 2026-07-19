"""The worker: connects to the Temporal server and runs workflows + activities.

A worker is a plain process that long-polls a task queue. You can run several
(for scale / redundancy); Temporal load-balances tasks across them. Kill this
process mid-review and restart it — the monitor resumes exactly where it was,
pending human review intact. That's the durability the tutorial is about.

Run:  python worker.py
"""

from __future__ import annotations

import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from activities import (
    fetch_careers_page,
    notify_human,
    persist_report,
    score_axes,
)
from shared import TASK_QUEUE
from workflows import CompanyDriftMonitor

TEMPORAL_TARGET = "localhost:7233"


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
    client = await Client.connect(TEMPORAL_TARGET)

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[CompanyDriftMonitor],
        activities=[
            fetch_careers_page,
            score_axes,
            notify_human,
            persist_report,
        ],
    )
    logging.info(f"Worker up on task queue '{TASK_QUEUE}' (Ctrl-C to stop)")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
