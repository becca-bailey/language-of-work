import path from "path";

/**
 * Single source of truth for where the Python pipeline writes its JSON.
 *
 * Post-cutover (Phase 4) the export scripts write into this Astro project
 * (`lowork.config.WEB_DATA_DIR` → `astro/src/data`) so the whole site deploys
 * from `astro/` with no sibling dependency. `astro build` runs with cwd = the
 * astro project root, so we resolve into `src/data`.
 */
export const DATA_DIR = path.resolve(process.cwd(), "src", "data");

export const STORIES_DIR = path.join(DATA_DIR, "stories");
