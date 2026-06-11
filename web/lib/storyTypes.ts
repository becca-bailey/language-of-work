import type { PhraseTerm } from "./data";

export interface StoryEnvelopeQuote {
  text: string;
  heading?: string;
  register?: string | null;
  stanceDiff?: number;
  inclusion?: number;
  meritocracy?: number;
  salience?: number;
  stanceProjection?: number;
}

export interface StoryQuoteRef {
  text: string;
  heading?: string;
  score: number;
}

export interface StoryPeakPresent {
  company: string;
  displayName: string;
  peakYear: number;
  peakZscore: number;
  peakQuote: StoryQuoteRef | null;
  latestYear: number;
  latestZscore: number;
  latestQuote: StoryQuoteRef | null;
}

export interface StoryYearQuote {
  company: string;
  displayName: string;
  year: number;
  text: string;
  heading?: string;
  score: number;
  zscore: number;
}

export interface StoryYearPoint {
  year: number;
  /** Z-scored within company (altruism and similar axes). */
  zscore?: number;
  /** Control-axis z-score for the same year. */
  controlZscore?: number | null;
  /** Embedding-derived presence share (performance story). */
  fractionPresent?: number;
  /** Share of chunks in an active DEI register (DEI story, careers source). */
  activeShare?: number;
  /** Share of chunks in the meritocracy register (DEI story, careers source). */
  meritocracyShare?: number;
  /** Share of chunks in the civilizational_mission register. */
  civilizationalShare?: number;
  /** Combined meritocracy + civilizational_mission share. */
  counterShare?: number;
  /** Signed inclusion − meritocracy projection (DEI story). */
  netScore?: number | null;
  /** Stance envelope extrema (inclusion − meritocracy per chunk). */
  stanceMax?: number;
  stanceMin?: number;
  stanceMean?: number;
  /** Topical salience: max(inclusion, meritocracy) top-k mean. */
  salienceTopkMean?: number;
  /** Fraction of chunk texts new vs prior year. */
  textChurn?: number;
  stanceMaxQuote?: StoryEnvelopeQuote | null;
  stanceMinQuote?: StoryEnvelopeQuote | null;
  stanceCounterQuote?: StoryEnvelopeQuote | null;
  /** Bipolar DEI stance axis projection. */
  bipolarTopkMean?: number;
  bipolarMax?: number;
  bipolarMin?: number;
  /** Register counts for this year (DEI story, careers source). */
  registers?: Record<string, number>;
  topkMean: number;
  nChunks: number;
  thin: boolean;
}

export type StoryMetricKey =
  | "fractionPresent"
  | "activeShare"
  | "netScore"
  | "salienceTopkMean"
  | "zscore";

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

export interface StoryCompanyEnvelope {
  company: string;
  displayName: string;
  years: StoryYearPoint[];
}

export interface StoryStanceYear {
  year: number;
  counts: Record<string, number>;
  shares: Record<string, number>;
  nChunks: number;
}

export interface StoryStancePresence {
  company: string;
  displayName: string;
  years: StoryStanceYear[];
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
  envelopes?: StoryCompanyEnvelope[];
  stancePresence?: StoryStancePresence[];
  peakPresent?: StoryPeakPresent[];
  yearQuotes?: StoryYearQuote[];
}

export function metricValue(
  point: StoryYearPoint,
  key: StoryMetricKey
): number | null {
  const v = point[key];
  return typeof v === "number" && !Number.isNaN(v) ? v : null;
}

export function peakYearForSeries(years: StoryYearPoint[]): StoryYearPoint | null {
  const scored = years.filter((y) => typeof y.zscore === "number");
  if (!scored.length) return null;
  return scored.reduce((best, y) =>
    (y.zscore ?? -Infinity) > (best.zscore ?? -Infinity) ? y : best
  );
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
