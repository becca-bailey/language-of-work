import { promises as fs } from "fs";
import path from "path";

export interface PowerSeriesPoint {
  year: number;
  value: number;
  norm: number;
}

export interface PowerCompanySeries {
  id: string;
  displayName: string;
  series: PowerSeriesPoint[];
}

export interface PowerMetric {
  id: string;
  label: string;
  benefits: "workers" | "management" | "optimism";
  note: string;
  series: PowerSeriesPoint[];
  perCompany: PowerCompanySeries[];
}

export interface PowerEvent {
  year: number;
  date: string;
  label: string;
  kind: string;
}

export interface PowerCase {
  company: string;
  date: string;
  title: string;
  shift: string;
  quotes: string[];
  source: string;
}

export interface PowerStory {
  story: string;
  title: string;
  subtitle: string;
  thesis: string;
  companies: string[];
  companiesNote: string;
  power: { label: string; caveat: string; series: PowerSeriesPoint[] };
  metrics: PowerMetric[];
  cases: PowerCase[];
  events: PowerEvent[];
}

export async function loadPowerStory(): Promise<PowerStory | null> {
  try {
    const raw = await fs.readFile(
      path.join(process.cwd(), "public", "data", "stories", "power.json"),
      "utf-8"
    );
    return JSON.parse(raw) as PowerStory;
  } catch {
    return null;
  }
}
