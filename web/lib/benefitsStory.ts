import { promises as fs } from "fs";
import path from "path";

export interface BenefitsPoint {
  year: number;
  share: number;
  count: number;
  smoothed: number;
}

export interface BenefitsCategory {
  id: string;
  label: string;
  deiSignal: boolean;
  series: BenefitsPoint[];
  total: number;
  firstYear: number | null;
  peakYear: number | null;
}

export interface MaterialDEIComponent {
  id: string;
  label: string;
  total: number;
}

export interface MaterialDEI {
  label: string;
  blurb: string;
  components: MaterialDEIComponent[];
  series: BenefitsPoint[];
  total: number;
}

export interface BenefitsStory {
  story: string;
  title: string;
  subtitle: string;
  intro: string;
  caveat: string;
  years: number[];
  totalsByYear: Record<string, number>;
  categories: BenefitsCategory[];
  materialDEI: MaterialDEI;
}

export async function loadBenefitsStory(): Promise<BenefitsStory | null> {
  try {
    const raw = await fs.readFile(
      path.join(process.cwd(), "public", "data", "stories", "benefits.json"),
      "utf-8"
    );
    return JSON.parse(raw) as BenefitsStory;
  } catch {
    return null;
  }
}
