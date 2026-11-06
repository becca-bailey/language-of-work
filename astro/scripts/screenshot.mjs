/* Deterministic chart screenshots for essays and before/after comparisons.

   Serves the built site (astro preview), renders each target element at a
   fixed viewport and 2x scale, and writes PNGs to ../reports/. Run:

     npm run build && npm run screenshot

   Figure ids come from the <Figure id=...> wrappers on the story pages.
   Add entries to TARGETS as more figures land; append ?variant=article to
   a path for the stripped (hint/table/source-free) version. */

import { spawn } from "node:child_process";
import { mkdirSync } from "node:fs";
import { chromium } from "playwright";

const PORT = 4322; // off the dev-server port so the two never collide
const OUT_DIR = new URL("../../reports/", import.meta.url).pathname;
const PAD = 24; // whitespace around each captured element, in CSS px
const TARGETS = [
  // netflix-culture
  { path: "/stories/netflix-culture", selector: "#deck-quotes", out: "netflix_deck_quotes_web.png" },
  { path: "/stories/netflix-culture", selector: "#lineage-stacked", out: "netflix_lineage_stacked_web.png" },
  { path: "/stories/netflix-culture", selector: "#lineage-timeline", out: "netflix_lineage_timeline_web.png" },
  { path: "/stories/netflix-culture", selector: "#adopter-ranking", out: "netflix_adopter_ranking_web.png" },
  { path: "/stories/netflix-culture?variant=article", selector: "#lineage-stacked", out: "netflix_lineage_stacked_article.png" },
];

const preview = spawn("npx", ["astro", "preview", "--port", String(PORT)], {
  cwd: new URL("..", import.meta.url).pathname,
  stdio: ["ignore", "inherit", "inherit"],
});

async function waitForServer(url, tries = 40) {
  for (let i = 0; i < tries; i++) {
    try {
      const res = await fetch(url);
      if (res.ok) return;
    } catch {}
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error(`preview server never came up at ${url}`);
}

try {
  await waitForServer(`http://localhost:${PORT}/`);
  mkdirSync(OUT_DIR, { recursive: true });
  const browser = await chromium.launch();
  // Tall viewport so every chart sits fully in view: clip coordinates stay
  // viewport-relative and no mid-capture resize retriggers ParentSize.
  const page = await browser.newPage({
    viewport: { width: 1200, height: 4000 },
    deviceScaleFactor: 2,
    colorScheme: "light",
  });
  for (const t of TARGETS) {
    await page.goto(`http://localhost:${PORT}${t.path}`, { waitUntil: "networkidle" });
    const el = page.locator(t.selector);
    await el.waitFor();
    await page.waitForTimeout(400); // let fonts + hydration settle
    // clip = element box expanded by PAD so the page background frames it
    const box = await el.boundingBox();
    if (!box) throw new Error(`no bounding box for ${t.selector}`);
    await page.screenshot({
      path: `${OUT_DIR}${t.out}`,
      clip: {
        x: Math.max(0, box.x - PAD),
        y: Math.max(0, box.y - PAD),
        width: box.width + PAD * 2,
        height: box.height + PAD * 2,
      },
    });
    console.log(`wrote reports/${t.out}`);
  }
  await browser.close();
} finally {
  preview.kill();
}
