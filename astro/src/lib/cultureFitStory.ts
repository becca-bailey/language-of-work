import { promises as fs } from "fs";
import path from "path";
import { STORIES_DIR } from "./dataDir";

export interface CultureFitCard {
  id: string;
  displayName: string;
  summary: string;
  quotes: { year: number; text: string }[];
}

export interface CultureFitStory {
  story: string;
  title: string;
  subtitle: string;
  intro: string;
  caveat: string;
  cards: CultureFitCard[];
}

export async function loadCultureFitStory(): Promise<CultureFitStory | null> {
  try {
    const raw = await fs.readFile(
      path.join(STORIES_DIR, "culture-fit.json"),
      "utf-8"
    );
    return JSON.parse(raw) as CultureFitStory;
  } catch {
    return null;
  }
}
