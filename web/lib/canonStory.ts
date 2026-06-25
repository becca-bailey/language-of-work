import { promises as fs } from "fs";
import path from "path";

export interface CanonYearPoint {
  year: number;
  value: number;
  n: number;
  thin: boolean;
}

export interface CanonSeries {
  id: "canon" | "conduct";
  label: string;
  years: CanonYearPoint[];
}

export interface CanonBand {
  mean: number;
  lo: number;
  hi: number;
  n: number;
}

export interface CanonEvent {
  id: string;
  label: string;
  year: number;
  description?: string;
}

export interface CanonQuote {
  year: number;
  text: string;
  heading: string;
  score: number;
}

export interface CanonCase {
  company: string;
  displayName: string;
  canonBand: CanonBand;
  series: CanonSeries[];
  events: CanonEvent[];
  rightsQuotes: CanonQuote[];
  missionQuotes: CanonQuote[];
}

export interface CanonStoryData {
  story: string;
  title: string;
  axis: string;
  poleHigh: string;
  poleLow: string;
  metricLabel: string;
  cases: CanonCase[];
}

const STORIES_DIR = path.join(process.cwd(), "public", "data", "stories");

export async function loadCanonStory(): Promise<CanonStoryData | null> {
  try {
    const raw = await fs.readFile(path.join(STORIES_DIR, "values-as-ip.json"), "utf-8");
    return JSON.parse(raw) as CanonStoryData;
  } catch {
    return null;
  }
}
