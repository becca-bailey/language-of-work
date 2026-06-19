# Project 3 — Registered Protocol (FROZEN)

**Status:** DRAFT pending final freeze. Becomes append-only once (a) codification dates are
verified against primary sources and (b) the two controls are confirmed. See "Open items before
freeze" at the bottom. After freeze, the body is immutable; all changes go in the dated changelog.

**Protocol authored:** 2026-06-11
**Measurement may not begin until:** this file is marked FROZEN and committed.

This is the pre-registration the design (§4 Phase 0, §8) requires. Its sole job is to fix
predictions *before* any corpus is measured, so H6 (firm-type → pathway) is falsifiable. Anchors
only; the comparison set is registered separately if/when the fork holds.

---

## 1. Construct

**Values-as-IP codification:** the datable point at which a firm's workplace/social values stop
being an internal practice and become a defensible, monetizable asset — a trademarked methodology,
a founder-authored canon, a productized culture, or control of a nominal commons. Codification
dates are the before/after anchors.

---

## 2. Cases, codification dates, and FROZEN pathway classification

> ⚠️ Dates marked **[verify]** are from background knowledge and MUST be confirmed against the
> cited primary source (USPTO TSDR for marks; publisher record for books) before freeze. Do not
> freeze a wrong anchor.

### Menlo Innovations — **Pathway A (ossification)** [FROZEN]
- *Joy, Inc.: How We Built a Workplace People Love*, Richard Sheridan — **2013** [verify: Penguin/
  Portfolio publisher record].
- *Chief Joy Officer*, Sheridan — **2018** [verify].
- "The Menlo Way" — wordmark; **filing/registration date [verify via USPTO TSDR]**.
- Paid factory tours / workshops productized — **launch date [verify]** (predates the books;
  this is the productization-of-culture anchor).
- **Primary codification anchor for analysis:** 2013 (*Joy, Inc.*), with the tour/trademark
  productization as a secondary, earlier anchor.
- *Type within pathway:* Frozen — brand-as-product small firm; canon expected inert, claimed
  impact relocated to an unverified replication market.

### Automattic — **Pathway B (weaponization)** [FROZEN]
- The Automattic Creed — founder-authored canon; **date of codification [verify]**.
- WordPress trademark — held by the WordPress Foundation; Automattic holds a commercial license;
  the Foundation/commons-stewardship structure **[verify dates: Foundation formation 2010; mark
  registration via TSDR]**.
- **Rupture anchor:** September 2024 WP Engine feud; WP Engine v. Automattic/Mullenweg litigation
  filed **October 2024** [verify exact filing date, N.D. Cal.]; the "Alignment Offer" employee
  exodus, **October 2024** [verify].
- *Type within pathway:* Influence-real-then-ruptured — distributed-work replication genuinely
  cleared and WordPress powers a large share of the web (so the rupture is NOT impact-relocation),
  yet the values brand ruptured via the mark.

---

## 3. Controls (register before freeze; see open items)
- **(a) Un-codified small firm, strong un-branded culture** — CANDIDATE PENDING. Requirement: a
  small firm with a strong internal culture that never wrote the book, trademarked a "Way," or
  productized tours. Selecting this is a judgment call reserved for confirmation; do not fabricate.
- **(b) Falsification probe — codified firm with a *documented, named* adopter.** CANDIDATE
  PENDING. Strong candidate: the **Spotify "squads/tribes" model** — codified and openly named by
  many adopting organizations (and even disowned by Spotify), so the replication market
  demonstrably cleared. This is the case that should make H4 *fail by design*, proving H4 is a
  narrow claim, not a hypocrisy detector.

---

## 4. Predictions (per hypothesis × case) — FROZEN on freeze

Directional, with the disconfirming result restated. "Canon" = the tagged mission/Creed/"Way"
subset, not all firm text.

### H1 — Capture under stress (both anchors)
- **Menlo:** weak/absent — no mark-vs-mission conflict event of force; register stays in
  mission/meta. *(H1 is largely a Pathway-B phenomenon; near-null for Menlo is expected, not a
  failure.)*
- **Automattic:** **strong.** In windows around Sept–Oct 2024, firm/founder language shifts from
  mission-register ("democratize publishing") toward rights-register ("trademark," "infringement,"
  "license," "consistent enforcement," "protect"). *Disconfirmed if* Automattic resolves the
  mission–mark conflict in favor of the mission, or language stays in mission-register through it.

### H2 — The gap (both anchors)
- **Menlo:** canon↔worker gap is **large and widens gradually** post-2013. *Disconfirmed if* small,
  or narrows as the brand matures.
- **Automattic:** gap **opens sharply at the 2024 rupture**, cleanest via the same-author discovery
  corpus (internal vs. external), with a public-record fallback. *Disconfirmed if* small, or
  narrows.

### H3 — Canon ossification (Pathway A: Menlo)
- **Menlo:** canon shows **lower diachronic drift post-2013** than matched un-codified control (3a)
  and than its own pre-2013 baseline, even across the 2020 COVID virtual pivot. *Disconfirmed if*
  the canon drifts as much as the control, or tracks external shocks the way un-codified language
  does.

### H4 — Impact relocation (Pathway A: Menlo)
- **Menlo:** post-2013 self-description migrates **object→meta** (away from the consulting work,
  toward culture-as-teachable-model); reported "impact" denominators are story-consumption (tour
  visitors, book sales, reach), not documented practice-adoption. *Disconfirmed if* self-
  description stays object-level, OR Menlo can name documented organizations that rebuilt on the
  model (the replication market clears). *Expected to FAIL for the Spotify-model control (3b) —
  that failure is the point.*

### H5 — Liturgical canon, divergent conduct (Pathway B: Automattic)
- **Automattic:** **low canon drift co-occurring with high conduct divergence** — the Creed stays
  fixed as liturgy while tactical conduct/communications around 2024 sit at the rights pole and
  diverge from it. *Disconfirmed if* under stress the canon itself is revised to match conduct, OR
  conduct stays consistent with the canon.

### H6 — Firm type predicts pathway (the fork)
- **Prediction:** Menlo (brand-as-product small firm) → Pathway A signature (low canon drift +
  object→meta relocation, no weaponized conduct). Automattic (infrastructure/competitive-IP) →
  Pathway B signature (low canon drift + high conduct divergence, mark weaponized). *Disconfirmed
  if* Menlo weaponizes, or Automattic ossifies-and-relocates rather than weaponizing — either
  misclassification means firm type is not the conditioning variable.

---

## 5. Planned analyses (fixed before measurement)
- Axes: `object_meta`, `mission_rights` (built per §7 of the design, `build_axes.py`, circularity
  check). Canon drift = axis-position variance + cumulative drift of the canon subset across
  Wayback snapshots. Conduct divergence = event-windowed `mission_rights` classification of
  tactical comms. H2 = canon-vs-worker signed per-axis distance under the §6 three-step confound
  control (relative positioning → register-matched poles → Haiku stance cross-check); H2 may fail.
- Event windows: ±N months around each dated rupture (N fixed at freeze).
- Worker-corpus stats reported as ranges/trajectories, never point estimates.

---

## Open items before freeze
1. Verify all **[verify]** dates (USPTO TSDR for marks; publisher records for books; PACER/court
   record for the WP Engine filing). Replace each with a sourced date.
2. Confirm the two controls (§3) — name (3a), confirm (3b).
3. Fix N for the event window (§5).
4. Confirm the Phase-1a feasibility verdict (corpus viability) before committing to both anchors.

## Changelog (append-only after freeze)
- 2026-06-11 — Protocol drafted (anchors only). Not yet frozen; open items outstanding.
