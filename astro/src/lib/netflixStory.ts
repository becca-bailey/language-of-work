import { promises as fs } from "fs";
import path from "path";
import { STORIES_DIR } from "./dataDir";

export interface NetflixAdopter {
  company: string;
  displayName: string;
  year: number;
  verbatim: boolean;
  example: string;
  score: number | null;
}

export interface NetflixEcho {
  company: string;
  displayName: string;
  year: number;
  example: string;
  score: number;
}

export interface NetflixConcept {
  id: string;
  label: string;
  tier: "lift" | "netflix_only" | "generic";
  originYear: number | null;
  adopters: NetflixAdopter[];
  echoes?: NetflixEcho[];
}

export interface NetflixEvolutionRow {
  concept: string;
  firstYear: number;
  lastYear: number;
  present: number[];
  retired: boolean;
}

export interface NetflixStory {
  story: string;
  title: string;
  subtitle: string;
  thesis: string;
  deckQuotes: { label: string; text: string }[];
  propagation: {
    originYear: number;
    note: string;
    concepts: NetflixConcept[];
  };
  objectivity: {
    scanned: number;
    claim: number;
    metricCredible: number;
    claimPct: number;
    smokingGun: string;
    finding: string;
  };
  objectivityMatrix: {
    concept: string;
    claims: boolean;
    metric: boolean;
    eval: string;
  }[];
  implicitExplicit: { explicit: string; implicit: string }[];
  netflixEvolution: {
    years: number[];
    rows: NetflixEvolutionRow[];
    headline: string;
  };
}

export async function loadNetflixStory(): Promise<NetflixStory | null> {
  try {
    const raw = await fs.readFile(
      path.join(STORIES_DIR, "netflix-culture.json"),
      "utf-8"
    );
    return JSON.parse(raw) as NetflixStory;
  } catch {
    return null;
  }
}
