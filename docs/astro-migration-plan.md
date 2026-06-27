# Astro migration plan

Move the web frontend from Next.js (`web/`) to Astro (`astro/`), built in parallel in
the same repo, cutting over to Netlify when at parity. The Python data pipeline does not
change.

## Why this is low-risk

- The Next app is already `output: "export"` — **there is no runtime server.** Every page
  is static HTML, every data loader is a build-time `fs` read of `public/data/*.json`. We
  are swapping one static-site builder for another, not removing a backend.
- No client-side data fetching anywhere — JSON is inlined at build, never served.
- The interactive pieces are already isolated React components (visx); Astro renders React
  to static HTML by default and hydrates only the islands we mark.
- Deploy target Netlify + static output = no adapter, just `netlify.toml`.

## Stack decisions (settled)

- **Astro + `@astrojs/react`** (React 19) — reuse the existing `.tsx` components as islands.
- **Tailwind v4 via `@tailwindcss/vite`** (the Vite plugin) — NOT the deprecated
  `@astrojs/tailwind` integration (that's v3-era). Copy `globals.css` as-is.
- **Content collections (MDX) for essays only.** Data stories stay fs-JSON + a React
  island; they're component-driven, not prose.
- **Pure static Netlify** — no `@astrojs/netlify` adapter. `netlify.toml`: base `astro`,
  publish `astro/dist`. Replicate `trailingSlash: true` and test deep-link direct loads
  (the 404 class already hit once on Vercel).
- **Do not duplicate data.** Point Astro loaders at the canonical Python-output dir via a
  single `DATA_DIR` constant. Leave Python writing to `web/public/data` until cutover, so
  the Next app keeps working in parallel; cutover is then a one-line path change.
- **Drop `web/AGENTS.md`** (the "modified Next.js" note) — it appears to be a scaffold
  artifact and is moot once we leave Next.

## The component buckets (decides hydration directive)

| bucket | examples | directive |
|---|---|---|
| Static `viewBox` SVG / markup | BenefitsChart, MaterialDEIChart, AuditBarChart, NetflixObjectivityMatrix, NetflixEvolutionStrip, tables/quote blocks | **none** (renders to HTML, zero JS) |
| ParentSize + tooltip / state | PowerCultureChart, DEIStoryExplorer, AltruismStoryExplorer, NetflixStoryExplorer, AxisExplorer, DeiExplorer, CompareChart | **island** — `client:only="react"` likely (see risk) |

Rule of thumb when porting: uses `ParentSize`/`useState`/`@visx/tooltip` → island; pure
`viewBox` SVG → static. **Hydrate at the top-level explorer boundary — one island per
story** — so React context stays intact; don't split internals.

## Main technical risk: visx `ParentSize`

`ParentSize` measures with a ResizeObserver: server renders 0-width, client measures →
**SSR hydration mismatch.** For interactive charts, prefer **`client:only="react"`** to
skip the mismatched SSR pass (cost: blank until hydrate — fine for charts). Static
`viewBox` charts have no `ParentSize` and render fine server-side. **Phase 0 resolves
`client:visible` vs `client:only` empirically.**

## Phases

### Phase 0 — spike (HARD GO / NO-GO, before any bulk porting)
Scaffold a throwaway `astro/`, wire `@astrojs/react` + `@tailwindcss/vite`, copy
`globals.css`, the layout, `registry.ts`, and `powerStory.ts`. Build **one** page with:
- **PowerCultureChart** (ParentSize + tooltip + toggle) as an island, and
- **BenefitsChart** (static `viewBox` SVG) with no directive.

Confirm end-to-end: builds; Tailwind applies; the interactive chart hydrates correctly
(decide `client:visible` vs `client:only`); the static chart ships zero JS; deploys to a
**Netlify preview**; **deep-link direct load** of the page works with `trailingSlash`.
If this one page works, the other ~26 components are rote. If it doesn't, stop and rethink.

### Phase 1 — home + the 6 data stories (product-first)
- `src/layouts/Layout.astro` (port `layout.tsx`: fonts, metadata, dark-mode, globals).
- `index.astro` from `registry.ts` (studies + Essays section).
- Per-story `.astro` pages (`/stories/<slug>`) — each loads its JSON in frontmatter and
  renders its top-level explorer as one island. Port the loaders (`*Story.ts`, `stories.ts`,
  `events.ts`, etc.) pointing at `DATA_DIR`.
- Port the components each story needs (most are rote; bucket per the table above).
- `404.astro` from `not-found.tsx`.

### Phase 2 — essays → MDX content collection (the authoring win)
- `src/content/essays/*.mdx` + `[slug].astro` renderer.
- Convert `culture-without-power` from the TSX scaffold to MDX: prose in Markdown, the viz
  (NetflixConceptTree, ObjectivityMatrix, EvolutionStrip, AuditBarChart, PowerCultureChart,
  the Coinbase diff, deck quotes) embedded as components/islands inline. This is the
  ergonomic payoff — you write prose, drop a chart mid-paragraph.

### Phase 3 — `/explore` dynamic routes (lowest priority)
`/explore/[axis]`, `/[axis]/[company]`, `/[axis]/compare` via `getStaticPaths` (the Astro
equivalent of `generateStaticParams`) sourced from the data. Most plumbing, least-used
surface — do last.

### Phase 4 — cutover
- Repoint the Python exports' output dir from `web/public/data` → the Astro location
  (one place: `lowork.config` / the export scripts), and flip the Astro `DATA_DIR` constant.
- `netlify.toml` → build `astro`, publish `astro/dist`. Verify full route parity +
  deep-links on a preview, then promote.
- Retire `web/` (keep in git history).

## Unknowns to verify (mostly in Phase 0)
- React 19 under current `@astrojs/react` version.
- Tailwind v4 via `@tailwindcss/vite` in Astro.
- `ParentSize` hydration → `client:visible` vs `client:only`.
- Deep-link 404 behavior on Netlify with `trailingSlash`.

## Rough sizing
Phase 0 ~half day · Phase 1 ~1–2 days (mechanical × 6 stories) · Phase 2 ~half day ·
Phase 3 ~half day · Phase 4 ~half day. ~3–4 focused days, gated on the Phase 0 spike.

## What does NOT change
The Python pipeline, the data, the analysis, `registry.ts`, and the React component logic.
This is a shell-and-routing swap with an essay-authoring upgrade.
