import { promises as fs } from "fs";
import path from "path";

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

export type ScoreLevel = "chunk" | "sentence";

export interface AxisData {
  company: string;
  axis: string;
  levels: Partial<Record<ScoreLevel, { years: YearScore[] }>>;
}

const DATA_DIR = path.join(process.cwd(), "public", "data");

export async function loadAxis(
  company: string,
  axis: string
): Promise<AxisData | null> {
  try {
    const raw = await fs.readFile(
      path.join(DATA_DIR, company, `${axis}.json`),
      "utf-8"
    );
    const parsed = JSON.parse(raw) as AxisData & { years?: YearScore[] };
    // backward compat: old flat format
    if (!parsed.levels && parsed.years) {
      return {
        company: parsed.company,
        axis: parsed.axis,
        levels: { chunk: { years: parsed.years } },
      };
    }
    return parsed;
  } catch {
    return null;
  }
}

export async function listDatasets(): Promise<
  { company: string; axes: string[] }[]
> {
  try {
    const companies = await fs.readdir(DATA_DIR);
    const out = [];
    for (const company of companies) {
      const stat = await fs.stat(path.join(DATA_DIR, company));
      if (!stat.isDirectory()) continue;
      const files = await fs.readdir(path.join(DATA_DIR, company));
      const axes = files
        .filter((f) => f.endsWith(".json"))
        .map((f) => f.replace(/\.json$/, ""))
        .filter((a) => a !== "control");
      if (axes.length) out.push({ company, axes });
    }
    return out;
  } catch {
    return [];
  }
}
