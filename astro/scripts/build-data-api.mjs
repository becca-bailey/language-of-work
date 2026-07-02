/**
 * Static JSON "API" builder.
 *
 * Mirrors every JSON file under `src/data/` (the single source of truth written
 * by the Python export scripts) into `public/data/`, which Astro copies verbatim
 * into `dist/`. Netlify then serves them at `/data/**` with the CORS headers set
 * in `netlify.toml`, so a separate site (e.g. the personal website) can fetch the
 * same data instead of copying files that drift out of sync.
 *
 * Also emits `public/data/index.json` — a manifest with a `schemaVersion` so
 * consumers can detect drift, plus the company/story lists and every file path.
 *
 * Runs before `astro build` (see package.json). `public/data/` is generated and
 * gitignored.
 */
import { cp, mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Bump when the shape of any exported JSON changes in a breaking way.
const SCHEMA_VERSION = 1;

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const srcDir = path.join(root, "src", "data");
const outDir = path.join(root, "public", "data");

/** Recursively collect JSON file paths relative to `dir`. */
async function collectJson(dir, base = dir) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await collectJson(full, base)));
    } else if (entry.isFile() && entry.name.endsWith(".json")) {
      files.push(path.relative(base, full));
    }
  }
  return files.sort();
}

async function main() {
  // Fresh mirror so deletes in src/data propagate.
  await rm(outDir, { recursive: true, force: true });
  await mkdir(outDir, { recursive: true });
  await cp(srcDir, outDir, {
    recursive: true,
    filter: (src) => {
      // Copy directories and .json files only.
      return !src.endsWith(".DS_Store");
    },
  });

  const files = await collectJson(srcDir);
  const companies = JSON.parse(
    await readFile(path.join(srcDir, "companies.json"), "utf8")
  ).companies;
  const stories = files
    .filter((f) => f.startsWith("stories/") && f.endsWith(".json"))
    .map((f) => path.basename(f, ".json"));

  const manifest = {
    schemaVersion: SCHEMA_VERSION,
    generatedAt: new Date().toISOString(),
    companies,
    stories,
    files,
  };
  await writeFile(
    path.join(outDir, "index.json"),
    JSON.stringify(manifest, null, 2)
  );

  console.log(
    `[build-data-api] mirrored ${files.length} JSON files → public/data/ (schemaVersion ${SCHEMA_VERSION})`
  );
}

main().catch((err) => {
  console.error("[build-data-api] failed:", err);
  process.exit(1);
});
