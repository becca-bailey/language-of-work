import { promises as fs } from "fs";
import path from "path";
import type { StoryData } from "./storyTypes";

export type {
  StoryCompanySeries,
  StoryData,
  StorySourceData,
  StoryYearPoint,
} from "./storyTypes";
export { allYears, industryMeanByYear } from "./storyTypes";

const STORIES_DIR = path.join(process.cwd(), "public", "data", "stories");

export async function loadStory(slug: string): Promise<StoryData | null> {
  try {
    const raw = await fs.readFile(path.join(STORIES_DIR, `${slug}.json`), "utf-8");
    return JSON.parse(raw) as StoryData;
  } catch {
    return null;
  }
}
