# Careers-page drift monitor — a Temporal tutorial

A small, self-contained app for learning [Temporal](https://temporal.io) against
a problem that's actually shaped like Temporal's strengths — and that's close to
the `language-of-work` research.

**The idea:** `language-of-work` reconstructs how companies' careers-page
language shifted *historically*, from the Wayback Machine, as a batch pipeline.
This monitor runs the same thesis **forward in real time**: it watches a
company's *live* careers page, and when the language drifts along the project's
semantic axes (altruism, performance, techno-optimism, …), it flags it for you
to confirm and appends it to a timeline.

Why this needs Temporal (when the batch pipeline doesn't): the work here is
**continuous, scheduled, flaky at the network edge, and human-in-the-loop** —
exactly the shape where durable execution earns its keep. Each concept maps to
one real part of the problem:

| Temporal concept | Where it shows up |
|---|---|
| **Schedules / timers** | poll each company on an interval (`wait_condition(timeout=…)`) |
| **Activity retries + heartbeat** | live-page fetches are flaky, unlike the cached batch pull |
| **Long-lived entity workflow + `continue_as_new`** | one durable monitor per company, running "forever" |
| **Signals** | your human "confirm this drift" gate — durable across restarts |
| **Queries** | read a monitor's state without disturbing it |
| **Determinism / sandbox** | workflow logic replays on recovery; all I/O is in activities |

## Files

| File | Role |
|---|---|
| `shared.py` | dataclasses + pure drift math; safe to import anywhere |
| `activities.py` | the impure work: fetch, score, notify, persist (real **and** fake modes) |
| `workflows.py` | `CompanyDriftMonitor` — the durable per-company loop |
| `worker.py` | process that runs workflows + activities off the task queue |
| `starter.py` | client CLI: start / poll / status / review / confirm |
| `fixtures/*.txt` | editable "live pages" for offline fake mode |
| `output/*.jsonl` | confirmed-drift timeline (gitignored) |

## Quickstart (fake mode — no API keys, no network)

Fake mode is the default whenever `OPENAI_API_KEY` is unset, so this runs fully
offline. You'll need three terminals.

**1. Install deps and start a Temporal dev server.**

```bash
cd temporal
pip install -r requirements.txt          # temporalio + httpx

# Easiest server (no Docker): the Temporal CLI
#   https://docs.temporal.io/cli
temporal server start-dev                 # gRPC :7233, Web UI http://localhost:8233
# ...or Docker instead:  docker compose up  (UI on :8080)
```

**2. Run a worker** (terminal 2):

```bash
cd temporal
python worker.py
```

**3. Start a monitor and drive it** (terminal 3):

```bash
cd temporal
python starter.py start google            # begins the durable loop
python starter.py status google           # query its state (baseline scores)
```

The first poll just records a baseline. Now **simulate a drift**: edit
`fixtures/google.txt` — swap the idealistic mission copy for hard
performance-and-results language — then force a poll:

```bash
python starter.py poll google             # re-fetch now instead of waiting
python starter.py review google           # see the pending drift review
python starter.py confirm google --yes    # accept it -> output/google_timeline.jsonl
```

Watch the worker log: you'll see the drift detected, a reminder fire if you wait,
and the confirmed report appended to the timeline.

### See the durability

Start a monitor, trigger a drift so a review is **pending**, then **kill the
worker** (Ctrl-C) before confirming. Restart `python worker.py`. Run
`python starter.py review google` — the pending review is still there. The
workflow state (including the human gate it was blocked on) survived the process
dying. That's the whole point.

## Real mode (uses the project's actual embeddings + axes)

Real mode fetches the live careers page, chunks + embeds it with `lowork`
(cache-first, so re-scoring unchanged text is free), and projects onto the
prebuilt axis vectors in `../axes/built/`.

```bash
# from the repo root, so lowork is importable:
uv sync
export OPENAI_API_KEY=...                  # real mode auto-enables when this is set
cd temporal && python worker.py
```

Live URLs are in `CAREERS_URLS` in `activities.py` (google, netflix, stripe,
airbnb out of the box — add your own). Force fake mode anytime with
`DRIFT_FAKE=1` even if a key is set.

## Tuning

`starter.py start` flags (all optional):

- `--poll-seconds` (default 30) — poll cadence; a real deploy would use days
- `--remind-seconds` (default 20) — re-notify cadence while a review is unanswered
- `--threshold` (default 0.05) — min |Δscore| on an axis to count as drift

## Extracting this into its own repo

This folder is deliberately self-contained. To make it a standalone repo:

```bash
cp -r temporal ~/drift-monitor && cd ~/drift-monitor
git init && git add -A && git commit -m "Drift monitor (from language-of-work tutorial)"
```

It will run **fake mode** immediately with no other changes — fake mode has zero
dependency on the parent project.

Only **real mode** couples to `language-of-work`, in two spots, both already made
portable:

1. **`lowork` import** (chunking + embeddings). Outside this repo you'd `pip
   install` the `lowork` package (or vendor the couple of modules you use). If
   it's missing, real mode raises a clear message telling you to install it or
   use fake mode — it never crashes cryptically.
2. **Axis vectors** at `../axes/built/*.json`. Override the location with the
   `DRIFT_AXES_DIR` env var, or copy the `axes/built/` JSONs alongside the
   folder. (They're small.)

So: nothing to rewrite — moving out is a copy plus, if you want real scoring,
installing `lowork` and pointing `DRIFT_AXES_DIR` at the axis vectors.

> Note: I couldn't create this as a separate GitHub repo directly — this session
> is scoped to the `language-of-work` repo — so it lives here under `temporal/`.
> The steps above are all it takes to lift it out whenever you want.

## Where to go next

- Replace the entity-loop-with-a-timer with a **Temporal Schedule** and compare
  the two patterns.
- Make `notify_human` a real Slack/email activity and watch retries in the UI.
- Fan out: `starter.py start` for every company in `../pipeline.yaml`.
- Add a `@workflow.query` that returns the full in-memory drift history.
