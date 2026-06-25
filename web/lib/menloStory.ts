import { promises as fs } from "fs";
import path from "path";

export interface MenloIdealismYear {
  year: number;
  era: string;
  idealism: number;
  zscore: number;
  nSentences: number;
  thin: boolean;
  topQuote: { text: string; heading: string };
}

export interface MenloEra {
  era: string;
  fromYear: number;
  toYear: number;
  idealism: number;
  nSentences: number;
  years: number[];
}

export interface MenloCohortSeries {
  id: string;
  displayName: string;
  years: { year: number; zscore: number }[];
}

export interface MenloPhrase {
  term: string;
  first_year: number;
  last_year: number;
  count: number;
  max_score: number;
  example: string;
}

export interface MenloEvent {
  date: string;
  label: string;
  kind: string;
  source?: string;
}

export interface MenloAudit {
  counts: Record<string, number>;
  namedAdopterCredible: number;
  namedAdopterNote: string;
  finding: string;
  guardrail: string;
}

export interface MenloOutsiderQuote {
  year: number;
  text: string;
  url: string;
}

export interface MenloStory {
  story: string;
  title: string;
  subtitle: string;
  thesis: string;
  idealism: {
    metricLabel: string;
    note: string;
    series: MenloIdealismYear[];
    eraSummary: MenloEra[];
    cohort: MenloCohortSeries[];
  };
  brandedLanguage: Record<string, MenloPhrase[]>;
  events: MenloEvent[];
  annotations: { label: string; kind: string; source?: string }[];
  impactAudit: MenloAudit;
  outsiderView: MenloOutsiderQuote[];
}

export async function loadMenloStory(): Promise<MenloStory | null> {
  try {
    const raw = await fs.readFile(
      path.join(process.cwd(), "public", "data", "stories", "menlo.json"),
      "utf-8"
    );
    return JSON.parse(raw) as MenloStory;
  } catch {
    return null;
  }
}
