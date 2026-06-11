import type { PhraseTerm } from "./data";

export interface StoryYearPoint {
  year: number;
  /** Embedding-derived presence share (performance story). */
  fractionPresent?: number;
  /** Share of chunks in an active DEI register (DEI story, careers source). */
  activeShare?: number;
  /** Share of chunks in the meritocracy register (DEI story, careers source). */
  meritocracyShare?: number;
  /** Signed inclusion − meritocracy projection (DEI story). */
  netScore?: number | null;
  /** Register counts for this year (DEI story, careers source). */
  registers?: Record<string, number>;
  topkMean: number;
  nChunks: number;
  thin: boolean;
}

export type StoryMetricKey = "fractionPresent" | "activeShare" | "netScore";

export interface StoryCompanySeries {
  id: string;
  displayName: string;
  years: StoryYearPoint[];
}

export interface StorySourceData {
  coverageStart: number;
  companies: StoryCompanySeries[];
}

export interface StoryHighlight {
  id: string;
  stance: string;
  stanceLabel: string;
  stanceNote: string;
  company: string;
  displayName: string;
  year: number;
  source: string;
  text: string;
  heading?: string;
  score: number;
}

export interface StoryTimelineQuote {
  year: number;
  register: string;
  text: string;
  heading?: string;
  score: number;
}

export interface StoryTimeline {
  company: string;
  displayName: string;
  quotes: StoryTimelineQuote[];
}

export interface StoryData {
  story: string;
  title: string;
  metric: string;
  metricLabel: string;
  sources: Record<string, StorySourceData>;
  lexicons: Record<string, (PhraseTerm & { company?: string })[]>;
  highlights?: StoryHighlight[];
  timelines?: StoryTimeline[];
}

export function metricValue(
  point: StoryYearPoint,
  key: StoryMetricKey
): number | null {
  const v = point[key];
  return typeof v === "number" ? v : null;
}

export function industryMeanByYear(
  companies: StoryCompanySeries[],
  year: number,
  key: StoryMetricKey = "fractionPresent"
): number | null {
  const values = companies
    .map((c) => {
      const point = c.years.find((y) => y.year === year);
      return point ? metricValue(point, key) : null;
    })
    .filter((v): v is number => v !== null);
  if (!values.length) return null;
  return values.reduce((a, b) => a + b, 0) / values.length;
}

export function allYears(companies: StoryCompanySeries[]): number[] {
  const years = new Set<number>();
  for (const c of companies) {
    for (const y of c.years) years.add(y.year);
  }
  return [...years].sort((a, b) => a - b);
}
