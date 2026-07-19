import { promises as fs } from "fs";
import path from "path";
import { DATA_DIR } from "./dataDir";

export interface EvidenceQuote {
  text: string;
  heading: string;
  score: number;
}

export interface YearScore {
  year: number;
  zscore: number;
  rawTopkMean: number;
  nChunks: number;
  kUsed: number;
  thin: boolean;
  carriedForwardFrac: number | null;
  quotes: EvidenceQuote[];
}

export interface AxisData {
  company: string;
  displayName?: string;
  axis: string;
  years: YearScore[];
}

export interface CompanyManifestEntry {
  id: string;
  displayName: string;
  axes: string[];
}

export async function loadAxis(
  company: string,
  axis: string
): Promise<AxisData | null> {
  try {
    const raw = await fs.readFile(
      path.join(DATA_DIR, company, `${axis}.json`),
      "utf-8"
    );
    const parsed = JSON.parse(raw) as AxisData & {
      years?: YearScore[];
      levels?: { sentence?: { years: YearScore[] }; chunk?: { years: YearScore[] } };
    };
    // Current: flat sentence-level export. Legacy: nested levels object.
    if (parsed.years) return parsed;
    const years =
      parsed.levels?.sentence?.years ?? parsed.levels?.chunk?.years ?? [];
    return { company: parsed.company, axis: parsed.axis, years };
  } catch {
    return null;
  }
}

export async function loadCompaniesManifest(): Promise<CompanyManifestEntry[]> {
  try {
    const raw = await fs.readFile(
      path.join(DATA_DIR, "companies.json"),
      "utf-8"
    );
    const parsed = JSON.parse(raw) as { companies: CompanyManifestEntry[] };
    return parsed.companies ?? [];
  } catch {
    return listDatasetsLegacy();
  }
}

async function listDatasetsLegacy(): Promise<CompanyManifestEntry[]> {
  try {
    const companies = await fs.readdir(DATA_DIR);
    const out: CompanyManifestEntry[] = [];
    for (const company of companies) {
      const stat = await fs.stat(path.join(DATA_DIR, company));
      if (!stat.isDirectory()) continue;
      const files = await fs.readdir(path.join(DATA_DIR, company));
      const axes = files
        .filter((f) => f.endsWith(".json"))
        .map((f) => f.replace(/\.json$/, ""))
        .filter((a) => a !== "control");
      if (axes.length)
        out.push({
          id: company,
          displayName: company.charAt(0).toUpperCase() + company.slice(1),
          axes,
        });
    }
    return out;
  } catch {
    return [];
  }
}

export async function listDatasets(): Promise<CompanyManifestEntry[]> {
  return loadCompaniesManifest();
}

export async function loadAxisForCompanies(
  companyIds: string[],
  axis: string
): Promise<(AxisData | null)[]> {
  return Promise.all(companyIds.map((id) => loadAxis(id, axis)));
}

export interface DeiYearScore {
  year: number;
  inclusionTopkMean: number;
  inclusionMean: number;
  inclusionMax: number;
  inclusionFractionPresent: number;
  nChunks: number;
  kUsed: number;
  thin: boolean;
  registers: Record<string, number>;
  controlTopkMean: number | null;
  inclusionQuotes: EvidenceQuote[];
}

export interface DeiData {
  company: string;
  displayName?: string;
  axis: string;
  years: DeiYearScore[];
  phrases: {
    terms: PhraseTerm[];
    high_scoring_sentences: { id: string; year: number; text: string; score: number }[];
    lexicons?: {
      inclusion?: PhraseTerm[];
      civilizational?: PhraseTerm[];
    };
  };
}

export interface PhraseTerm {
  term: string;
  first_year: number;
  last_year: number;
  max_score: number;
  example: string;
}

export async function loadDei(company: string): Promise<DeiData | null> {
  try {
    const raw = await fs.readFile(
      path.join(DATA_DIR, company, "dei.json"),
      "utf-8"
    );
    return JSON.parse(raw) as DeiData;
  } catch {
    return null;
  }
}

export interface SynthesisSection {
  heading: string;
  body: string;
}

export interface SynthesisData {
  company: string;
  displayName?: string;
  headline: string | null;
  identity?: string | null;
  fit?: string | null;
  sections: SynthesisSection[];
  model: string;
  promptVersion: number;
  facetsUsed: string[];
  generatedAt: string;
}

export interface FingerprintAxis {
  axis: string;
  label: string;
  zscore: number;
  recentZscore: number;
  recentYear: number;
  nYears: number;
}

export interface FingerprintData {
  company: string;
  displayName?: string;
  axes: FingerprintAxis[];
}

// Per-company values fingerprint: one summary z-score per axis (vs. peers),
// written by scripts/export_web.py. Returns null when not yet generated.
export async function loadFingerprint(
  company: string
): Promise<FingerprintData | null> {
  try {
    const raw = await fs.readFile(
      path.join(DATA_DIR, "fingerprints", `${company}.json`),
      "utf-8"
    );
    return JSON.parse(raw) as FingerprintData;
  } catch {
    return null;
  }
}

// AI narrative precomputed by scripts/synthesize_company.py. Lives outside the
// per-company export dir (synthesis/<company>.json) so it isn't part of its own
// pipeline input set. Returns null when no narrative has been generated.
export async function loadSynthesis(
  company: string
): Promise<SynthesisData | null> {
  try {
    const raw = await fs.readFile(
      path.join(DATA_DIR, "synthesis", `${company}.json`),
      "utf-8"
    );
    return JSON.parse(raw) as SynthesisData;
  } catch {
    return null;
  }
}

export function compareableAxes(
  companies: CompanyManifestEntry[]
): string[] {
  const counts = new Map<string, number>();
  for (const c of companies) {
    for (const axis of c.axes) {
      if (axis === "control") continue;
      counts.set(axis, (counts.get(axis) ?? 0) + 1);
    }
  }
  return [...counts.entries()]
    .filter(([, n]) => n >= 2)
    .map(([axis]) => axis)
    .sort();
}
