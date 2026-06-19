# The Language of Work — Project 3

## "When Values Become Intellectual Property"

A multi-case extension of the careers-page-archaeology instrument. This document is the
**operational plan**: it maps the case-study design (see the master design doc / §1–§8 of the
proposal) onto the existing codebase, marks what is reused versus new, and sequences the work
**anchors-first**. It is deliberately not the registered protocol — that frozen artifact is the
first deliverable (Phase 0), and it owns the actual a-priori pathway classifications and H1–H6
predictions.

Anchor cases: **Menlo Innovations** (Pathway A — ossification) and **Automattic** (Pathway B —
weaponization). Comparison set deferred until the fork is proven on the two anchors.

---

## 0. Relationship to the existing instrument

Project 2 (the DEI sub-study) is the structural template. Almost all scaffolding transfers:

| New-study need | Reuse | New work |
|---|---|---|
| Two new axes: `object_meta`, `mission_rights` | `generate_axis_candidates.py` → `build_axes.py` → `axes/*.yaml` | curate poles in corporate register (§7) |
| Event/stance classification (H1, H5) | `dei_stance.py` pattern: discrete classes, hand-label gate, `agreement_report`, surviving `*_overrides.json` | new label set + event-window aggregation |
| Register classification (§6) | `classify_dei_register.py` pattern | worker-register poles + cross-check |
| Canon-vs-second-corpus on same axes (H2) | `embed_investor.py` → `score_dei_investor.py` pattern | worker corpus replaces investor filings |
| Per-case config, MANUAL GATEs | `CompanyProfile`, README gate convention | per-case profiles, canon tagging |
| Chunk → classify → embed → score | **reused wholesale, unchanged** | normalize every source into the chunk record |
| **Data fetching** | — | **rebuilt: a diversified, purpose-specific source layer (§2). Do *not* reuse the CDX careers-sweep path.** |

### Design principle: diverge at fetch, converge at chunk
The DEI study had essentially one fetch path — a Wayback CDX sweep of careers URLs — plus SEC
EDGAR as a second corpus. This population can't be served that way: the evidence lives in a
*book*, a *Creed*, *worker reviews*, *trademark filings*, and a *litigation docket*, each with its
own access method, register, and provenance. So the architecture splits:

- **Fetch diverges.** One small, single-purpose fetcher per source type (§2), each casting as wide
  as its source allows. This is also where exploration happens — we pull broadly first, then decide
  what's worth keeping.
- **Everything downstream converges.** Every fetcher normalizes its output into the *same* chunk
  record the existing pipeline already consumes, so `extract_chunks` → `classify` → `embed` →
  `score` run unchanged regardless of where the text came from. The register/role/provenance of
  each record is carried as metadata, not as a separate code path.

Concretely this retires the single `url_patterns.json` + CDX-domain-sweep assumption. **Empirical
note (2026-06-11):** the IA **CDX search API** timed out on every query from this environment
(290–485 s; domain *and* prefix), while web.archive.org itself served in ~0.12 s. The Wayback
**Availability API** (`/wayback/available?url=…&timestamp=…`, per-URL, cheap) is the resilient path
for known canon artifacts; reserve CDX for narrow, capped, retried discovery only.

**Three things the DEI analogy hides** — these are where the real engineering and risk live:

1. **Population mismatch.** The instrument was built for public, large firms with deep Wayback
   careers archives + SEC filings as the second corpus. The anchors are private/small. Menlo's
   canon is a *book + tour pages*, not a careers archive. **Corpus viability is the binding
   constraint** — measure it before building anything (Phase 1a below).
2. **Worker-register confound is new.** DEI's second corpus was investor filings —
   corporate-vs-corporate, clean subtraction. Only **H2 crosses registers** (canon vs. worker).
   `object_meta` and `mission_rights` are firm-internal (corporate-vs-corporate, safe). Keep this
   line bright; do not treat H2 as "just like investor filings."
3. **Codification-date sourcing is new.** `fetch_filings.py` targets SEC EDGAR; trademark
   filing/registration dates come from USPTO **TSDR** — a different source. Phase 0 needs a small
   fetcher or manual lookup.

---

## 1. Phasing (resequenced: freeze + feasibility before any building)

### Phase 0 — Freeze the protocol (pure writing, no data) — **do first**
The a-priori pathway classification + dated H1–H6 predictions are the only thing that makes H6
falsifiable, and they require no corpus. Deliverable: a dated, frozen
`docs/values-as-ip-protocol.md` containing, per case:
- construct definition + **codification date(s)** (TSDR filing/registration, book pub date,
  paid-tour/workshop launch, foundation/trust formation);
- frozen **Pathway A / B / bridge** classification;
- H1–H6 predictions with each one's stated disconfirming result;
- the two controls: (a) un-codified small firm with strong un-branded culture; (b) a falsification
  probe — any codified firm with a *documented, named* adopter.
Once written, this file is append-only. Changes go in a dated changelog at the bottom.

### Phase 1a — Wide source exploration + feasibility probe (cheap, gates everything)
This is the "pull as widely as possible" step, and it doubles as the viability gate. For Menlo and
Automattic only, before committing to full corpus construction:
- `uv run scripts/explore_sources.py --case menlo` (and `automattic`) — fans out across *every*
  registered source (§2), per-source, and writes `data/<case>/source_map.md`: count, date range,
  and a handful of sample URLs/snippets per source, grouped by register (firm / press / worker /
  legal). This generalizes the old CDX `discover` into a multi-source census.
- The probe is deliberately shallow and capped (small `limit`, short timeout, retries) — it answers
  "does enough text exist, in each register, across the relevant years?" not "fetch it all."
- **Decision gate:** if a case's canon isn't recoverable, or worker-N ≈ 0, or a register is empty,
  the case set changes *before* sunk cost. Record the verdict + the `source_map.md` summary in the
  protocol changelog.

### Phase 1b — Anchor corpus construction (Menlo, Automattic)
Run the per-source fetchers (§2) for the sources that cleared the Phase-1a gate, each normalizing
into the shared chunk record. Three register-distinct, timestamped corpora per case:
1. **Firm self-description (longitudinal)** — for *known* canon URLs (the Creed, tour/"Way" pages,
   about/mission), resolve snapshots via the Wayback **Availability API** per URL per target date,
   not a CDX domain sweep; supplement with a live-site fetch of artifacts that still exist. Book
   canon comes via the books fetcher (metadata + pub date + lawful short excerpts/paraphrase).
   **Tag the `canon` subset separately** (mission/Creed/"Way") via a `canon` flag + per-case
   `canon_overrides.json` — H3/H5 operate on the canon, not all firm text.
2. **Press & legitimation** — news, awards, B-school cases, conference/podcast descriptions.
3. **Worker testimony** — Glassdoor/Indeed/Blind/Reddit/HN/ex-employee writeups. Document sampling
   asymmetries (self-selection, review-bombing, small-N, survivorship); record N and date coverage.
- **Automattic discovery bonus corpus** (Pathway B): produced internal comms (Slack/email) give a
  register-confound-free H2 measure (same authors, internal vs. external). Treat per §8 of the
  design — active litigation, allegations-as-allegations, contested-until-adjudicated. **H2 must
  not depend on it alone**: keep a public-record fallback path.
- Output: per-case corpus manifest (date coverage, source counts, canon tagging, caveats).

### Phase 2 — Instrument extension & validation
- Build **both** new axes (§7) via `build_axes.py`:
  - `object_meta` — object pole (building product / serving clients / craft / end user) ↔ meta pole
    (being a teachable model / the Way / movement / "sharing" / "ripples"). Serves H4.
  - `mission_rights` — mission pole ("democratize publishing," "save the home planet") ↔ rights pole
    ("protect goodwill," "infringement," "license," "consistent enforcement"). Serves H1, H5.
  - Both poles in corporate voice, 6–10 sentences, register cancels in subtraction. Run the
    `build_axes.py` circularity check.
- **Resolve the §6 register confound for H2 only**, in preference order: (1) relative positioning
  vs. each corpus's own baseline; (2) register-matched poles (build worker-register poles, verify
  axis direction is stable across registers); (3) Haiku stance cross-check independent of the
  embedding projection. If the gap survives all three it is a stance gap; if it collapses, H2 is
  allowed to fail and we report "no measurable gap."
- Re-validate the full axis inventory against a hand-labeled sample drawn from *these* corpora
  (`label_sample.py` → `validate.py` pattern).
- Output: validated axis set + register-bridging procedure + confusion stats.

### Phase 3 — Per-case measurement (branches by pathway)
- **Both anchors:** H1 (capture under stress, event-anchored `mission_rights` classification in
  windows around dated conflict events) and H2 (the gap — discovery corpus where available, public
  fallback otherwise).
- **Menlo (A):** H3 (canon drift — axis-position variance/cumulative drift of the canon subset
  pre/post codification vs. controls) and H4 (object→meta migration aligned to codification date +
  an audit of every impact claim: is the denominator story-consumption or practice-adoption?).
- **Automattic (B):** H5 (low canon drift co-occurring with high conduct divergence) — hold canon
  drift against event-anchored conduct/tactical classification; worker↔firm lead-lag.
- Output: per-case result sheet, one page per applicable hypothesis, disconfirming-check applied
  honestly.

### Phase 4 — Fork test + (later) comparison set
- **Evaluate H6** on the two anchors: did each case's frozen pathway classification match its
  observed signature? A misclassification is the most informative outcome — report prominently.
- Only after the fork holds on the anchors, expand to the comparison set (Basecamp/37signals,
  Gravity, Patagonia; Zappos/Buffer pending viability). Each is variance/replication, not new
  theory.
- Plot the 2-D space **canon-drift × conduct-divergence**; assemble the typology
  (frozen / drift / ruptured / founder-collapse / influence-real-then-ruptured / mixed).

### Phase 5 — Presentation (The Pudding model)
Scrollama + D3, reusing the existing `web/` export pattern (`export_web.py` →
`web/public/data/`). Core scenes, with **Scene 3 carrying the thesis**: Menlo's flat canon line
with no conduct to contradict it, beside Automattic's flat canon line *with an erupting conduct
trace diverging beneath it*. Then the typology map.

---

## 2. New code, concretely (anchors-first slice)

### 2.1 The source layer — `src/lowork/sources/` (the part that diverges from DEI)
One module per source type, each single-purpose and casting as wide as the source allows. The
contract is narrow: every fetcher returns an iterable of **`SourceRecord`** and writes raw payloads
to disk for reproducibility. It does *not* chunk, classify, or score — that's the shared downstream.

- `sources/base.py` — the `SourceRecord` schema and a **registry** so `explore_sources.py` can
  enumerate and fan out over all sources. Fields: `source` (e.g. `wayback`, `hn`), `register`
  (`firm` / `press` / `worker` / `legal`), `role`/author hint, `url`, `observed_date` (when the
  text was *of*, for the timeline), `fetched_at`, `raw_path`, `text`, `provenance`. `register` and
  `observed_date` are what let the converged pipeline stay one code path.
- `sources/wayback_url.py` — **Availability-API** resolver: given a known URL + target dates, return
  the nearest snapshot(s) and fetch via the `id_` raw flag. Per-URL, cheap, retried. (Replaces the
  CDX domain sweep, which is unusable here — see §0 note.)
- `sources/cdx_discover.py` — narrow, capped, retried CDX discovery for *finding* unknown canon URLs
  only; strict timeout, small `limit`, never a domain sweep. Exploration aid, not the fetch path.
- `sources/live.py` — current live-site fetch (Trafilatura) for canon artifacts that still exist
  (the Creed, tour/"Way" pages). Captures the present-day canon endpoint.
- `sources/books.py` — Google Books API + publisher pages: book pub dates (a codification anchor)
  and lawful short excerpts / front-matter / publisher copy + paraphrase. No full text.
- `sources/news.py` — press & legitimation, date-ranged and wide: GDELT DOC API (free, good for
  volume-over-time and the rupture windows), plus targeted awards / B-school / conference / podcast
  description pulls.
- `sources/hn.py` — Hacker News Algolia API ("working at X" / company threads) — the master plan's
  blessed worker source; full corpus, date-filterable.
- `sources/reddit.py` — Reddit public JSON / API where accessible; supplementary worker source,
  flagged for post-2023 API limits.
- `sources/glassdoor.py` — **stub + caution only.** Scraping violates ToS; use academic datasets or
  manual capture if at all. Do not build the study around it.
- `sources/trademarks.py` — USPTO **TSDR** lookup for trademark filing/registration dates
  (codification anchors). Small; manual fallback into the protocol if the API is fussy.
- `sources/courts.py` — **CourtListener / RECAP** for the WP Engine docket and any discovery on the
  public record. Gated behind the §8 legal cautions (active litigation, allegations-as-allegations).

### 2.2 Orchestration & the rest
- `scripts/explore_sources.py --case <name>` — fan out over the registry (capped), write
  `data/<case>/source_map.md` (the Phase-1a census). The wide-exploration entry point.
- `scripts/fetch_case.py --case <name> --sources <list>` — run the chosen fetchers for real,
  normalize into the shared chunk pipeline.
- `data/<case>/sources.json` — replaces `url_patterns.json`: per-case source config (known canon
  URLs, search terms, subreddits, docket IDs, date windows) consumed by the fetchers.
- `axes/object_meta.yaml`, `axes/mission_rights.yaml` (+ `axes/candidates/`, `axes/built/`).
- Canon tagging: a `canon` boolean on chunk records + `data/<case>/canon_overrides.json`
  (mirrors the DEI override mechanism so it survives re-classification).
- `src/lowork/register.py` (or extend the DEI register module) — worker-register poles + the
  three-step §6 cross-check, scoped to H2.
- `scripts/classify_register_shift.py` — event-windowed `mission_rights` classification (H1/H5),
  modeled on `classify_dei_register.py` but aggregating around dated events, not calendar years.

## 3. Standing risks (carry from §8 of the design)
Selection bias (controls + frozen pre-registration are the counterweight); "no documented
adoption" ≠ "no adoption" (keep H4's claim narrow); worker-corpus sampling skew (report ranges/
trajectories, never point estimates); **register confound (the biggest technical risk — H2 only)**;
active litigation + named individuals (Automattic/WP Engine, Patagonia/Pattie Gonia, Gravity's
founder — stay on the documented public record, label all allegations as allegations, take no
position on merits, treat discovery as contested); survivorship (all anchors survived — a boundary
on generalization).
