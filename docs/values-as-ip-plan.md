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

## The mission this study serves

> The relevant question is not "why does culture decay?" but, following Doctorow's inversion of
> enshittification, **"what prevents cultural enshittification — and what happens to the language of
> values when those forces erode?"**

Cultural decay is the default under market pressure, not the anomaly. A workplace culture does not
stay good because leaders care about it; it stays good while specific **counterforces** hold the
default back — a tight labor market that gives workers bargaining power, competition for talent and
reputation, the founder's still-personal stake, and (rarely) regulation or organized labor. When
those counterforces erode, the culture enshittifies regardless of stated intentions. The
millennial-era bet — that better intentions, training, DEI metrics, and committees would hold the
tide — worked only while the labor market made it cheap to mean it. This study is about what is
left, and what the *language* does, after that power recedes.

**Values-as-IP is the lens, not a competing theory.** Codifying values into intellectual property —
a trademarked "Way," a founder-authored Creed, a productized culture, a controlled nominal commons —
is precisely the move available to leaders *once the live counterforces are gone*. The codified
canon is durable in a way the conditions that produced it were not, so it persists, frozen, while
practice drifts beneath it. That is why a firm can "appear not to live up to its values more over
time": the canon is fixed at the moment of codification, the counterforces keep eroding, and the gap
between the two is what the instrument measures. Codification does not cause the decay; it **outlives
the conditions that made the values real, and masks their erosion.**

So the two pathways are two things that happen to codified values once the counterforces recede:
- **Pathway A (ossification, Menlo):** the canon becomes inert liturgy and the claimed impact
  relocates to an unverified replication market (object→meta). Decay shows up as *drift away from
  the work*, not as conflict.
- **Pathway B (weaponization, Automattic):** the canon stays fixed while the now-defensible asset is
  turned outward — the mission-register collapses into a rights-register under stress. Decay shows up
  as *the values being enforced against people* rather than lived.

**Scope guard.** The frozen protocol (H1–H6) measures the *symptom* — canon drift, conduct
divergence, the canon↔worker gap. It does not yet measure the counterforces themselves (labor-market
slack, competition, founder tenure, organizing). Treat the counterforces as the **interpretive
layer** for now: where a public, datable proxy exists (e.g. the 2022–2024 tech-labor-market
inversion against Automattic's 2024 rupture; Menlo's founder tenure and firm size against its canon
freeze), annotate the timeline with it as context, never as a measured variable. Turning a
counterforce into a measured covariate is a deliberate, separately-registered extension (see Phase 4
note) — not a silent edit to the frozen predictions.

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

### Phase 1a findings (run 2026-06-19) — both anchors VIABLE
Ran `explore_sources.py` (hn + books) for both anchors. Verdict and what it changed:
- **Automattic — strongly viable.** Exact-phrase `"Automattic"` ≈ 3,379 HN items (2008→2025);
  the 2024 rupture window is densely covered with rights-register material (cease-and-desist,
  trademark transfer to the Foundation, "8% license fee," the Alignment Offer, "Paranoia and Fear
  Inside Automattic"). Canon = the Creed (web), not a book — books register is naturally minor for
  Pathway B; *The Year Without Pants* (Berkun, 2013) is a usable insider account.
- **Menlo — viable but small worker-N.** `"Menlo Innovations"` ≈ 37 HN items, qualitatively
  on-point (a 2012 comment: people are *"paying to learn the Menlo Way"* — the H4 relocation signal
  in the wild). Report worker results as ranges/trajectories; supplement with Reddit/Indeed when
  those fetchers land. Codification anchors **confirmed** (Open Library): *Joy, Inc.* 2013,
  *Chief Joy Officer* 2018.
- **Tooling findings folded into the plan:** (1) keyless Google Books is dead (quota 0) → books now
  via **Open Library**; (2) HN Algolia `nbHits` overcounts via loose token matching — *quote* the
  phrase (`"Automattic"` 317,927→3,379) and trust ranked samples, not totals; (3) generic case
  terms collide with the world (bare `Menlo Way` ≈ Menlo Park) → use disambiguated/quoted queries;
  (4) empty press/legal rows in the maps are **tooling gaps** (news.py/courts.py unbuilt), not data
  gaps — both registers are clearly populated (HN already surfaces the docket and press coverage).
- **Worker-source access reality (2026):** keyless APIs are closing. Google Books → quota 0; Reddit
  `.json` → HTML block (needs OAuth). Ladder for the worker register: keyless-and-open (HN Algolia,
  Open Library) → OAuth where required (Reddit) → **lawful manual-ingest** for ToS-restricted
  sources (Glassdoor/Indeed via `ingest_manual_html.py`), never auto-scrape. Worker records carry a
  `subtype` (employee / visitor / community / review) so reliability is a weight, not a label.

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

#### Phase 2 progress (run 2026-06-23) — both axes built + circularity-clean + face-valid
- **Both axes built** → `axes/built/{object_meta,mission_rights}.json` (8 sentences/pole, corporate
  voice). `build_axes.py` was extended to run the **circularity check on the Project-3 firm/canon
  subset** (`register=="firm"`) since there is no DEI-style `mission_brand` classification here —
  `circularity_check` embeds those chunks cache-first, so no classify/embed prerequisite.
- **Lexical-leakage fix (important).** First drafts embedded firms' *verbatim* canon — "democratize
  publishing" (Automattic), "the way we work"/"ripples" (Menlo/Sheridan). That would make H4/H5
  partly tautological (a chunk scores its pole by lexical identity, not concept) and break H6 cross-
  case comparability. Poles were **genericized to the concept, not the slogan**; the YAML headers
  record this constraint. Re-running, both axes now produce **0 circularity flags** against *both*
  anchors' canon (incl. Automattic's actual mission text vs. the mission pole — the leakage test).
- **Face validity confirmed** (projection of firm chunks, both cases): mission_rights puts the Creed
  + "value impact not time" at the mission pole and WordPress trademark-enforcement language at the
  rights pole; object_meta puts "we make products for people" at object and, on Menlo, the
  productized **"factory tours… gone virtual"** at meta — the H4 impact-relocation signal in situ.
- **Still open in Phase 2:** hand-labeled validation sample (`label_sample.py`→`validate.py`); the
  §6 register-confound procedure for H2 (worker-register poles); and the Project-3 classification
  step (no `classifications.json` yet — `embed_chunks.py` still assumes the DEI label set).

### Phase 3 — Per-case measurement (branches by pathway)
- **Both anchors:** H1 (capture under stress, event-anchored `mission_rights` classification in
  windows around dated conflict events) and H2 (the gap — discovery corpus where available, public
  fallback otherwise).
- **Menlo (A):** H3 (canon drift — axis-position variance/cumulative drift of the canon subset
  pre/post codification vs. controls) and H4 (object→meta migration aligned to codification date +
  an audit of every impact claim: is the denominator story-consumption or practice-adoption?).
- **Automattic (B):** H5 (low canon drift co-occurring with high conduct divergence) — hold canon
  drift against event-anchored conduct/tactical classification; worker↔firm lead-lag.
- **Counterforce annotation (interpretive, not a hypothesis):** on each case's timeline, overlay the
  public, datable counterforce proxies that the mission frame points to — e.g. the 2022–2024 tech
  labor-market inversion (layoffs, loss of worker bargaining power) against Automattic's 2024
  rupture; Menlo's founder tenure and static firm size against its post-2013 canon freeze. These are
  context for reading the measured gap, explicitly flagged as un-modeled. Do **not** fit, weight, or
  test them here — that is the Phase 4 extension.
- Output: per-case result sheet, one page per applicable hypothesis, disconfirming-check applied
  honestly, with the counterforce overlay as a clearly-labeled context band.

### Phase 4 — Fork test + (later) comparison set
- **Evaluate H6** on the two anchors: did each case's frozen pathway classification match its
  observed signature? A misclassification is the most informative outcome — report prominently.
- Only after the fork holds on the anchors, expand to the comparison set (Basecamp/37signals,
  Gravity, Patagonia; Zappos/Buffer pending viability). Each is variance/replication, not new
  theory.
- Plot the 2-D space **canon-drift × conduct-divergence**; assemble the typology
  (frozen / drift / ruptured / founder-collapse / influence-real-then-ruptured / mixed).
- **Counterforces-as-variable extension (separately registered, only if the fork holds).** This is
  where the mission's core question becomes a measurement rather than an annotation: take a datable
  counterforce proxy (labor-market slack, competitive pressure, founder tenure, organizing/union
  events) and test whether the canon↔practice gap *widens as the counterforce erodes*. It needs its
  own frozen pre-registration — new constructs, new disconfirming results — because it adds variables
  the current H1–H6 do not contain. Flagged here so it is built deliberately, not smuggled into the
  anchor analysis.

### Phase 5 — Presentation (The Pudding model)
Scrollama + D3, reusing the existing `web/` export pattern (`export_web.py` →
`web/public/data/`). The narrative opens on the mission question — *what holds a culture in place,
and what happens to its stated values when that grip loosens?* — and frames codification as what
remains after the holding force is gone. Core scenes, with **Scene 3 carrying the thesis**: Menlo's
flat canon line with no conduct to contradict it, beside Automattic's flat canon line *with an
erupting conduct trace diverging beneath it* — the same frozen canon, two ways for the practice to
leave it behind. Where a counterforce proxy exists, render it as a receding band beneath the canon
line so the viewer reads the gap *opening as the force erodes*. Then the typology map.

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
- `sources/reddit.py` — Reddit worker testimony. **Keyless `.json` is blocked** (Reddit serves the
  HTML app shell to unauthenticated/datacenter clients); built for app-only **OAuth**
  (`REDDIT_CLIENT_ID`/`REDDIT_CLIENT_SECRET`) and degrades with an actionable message when creds are
  absent. Every record tagged `source=reddit` + `subtype=community` + provenance (subreddit, score,
  num_comments) — reliability handled as metadata to weight/filter, not a discard flag.
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
**Causal-frame risk (new, from the mission reframe):** the instrument measures the *symptom* (canon
drift, conduct divergence, the gap), not the *cause* (eroding counterforces). Do not let the
narrative claim that codification *causes* decay, or that an eroding labor market *caused* a measured
gap — the counterforce layer is annotation until separately registered (Phase 4). State the
mechanism as "codification outlives and masks the conditions," and keep the measured claims to what
the axes actually show. Selection bias (controls + frozen pre-registration are the counterweight); "no documented
adoption" ≠ "no adoption" (keep H4's claim narrow); worker-corpus sampling skew (report ranges/
trajectories, never point estimates); **register confound (the biggest technical risk — H2 only)**;
active litigation + named individuals (Automattic/WP Engine, Patagonia/Pattie Gonia, Gravity's
founder — stay on the documented public record, label all allegations as allegations, take no
position on merits, treat discovery as contested); survivorship (all anchors survived — a boundary
on generalization).
