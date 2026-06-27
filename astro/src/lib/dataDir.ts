import path from "path";

/**
 * Single source of truth for where the Python pipeline writes its JSON.
 *
 * The data is NOT duplicated into the Astro project. Loaders point at the
 * canonical `web/public/data` (sibling to this `astro/` project). `astro build`
 * runs with cwd = the astro project root, so we resolve one level up into `web`.
 *
 * Cutover (Phase 4) is a one-line change here once Python repoints its output.
 */
export const DATA_DIR = path.resolve(process.cwd(), "..", "web", "public", "data");

export const STORIES_DIR = path.join(DATA_DIR, "stories");
