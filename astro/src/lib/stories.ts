import { promises as fs } from "fs";
import path from "path";
import type { StoryData } from "./storyTypes";
import { STORIES_DIR } from "./dataDir";

export type {
  StoryCompanySeries,
  StoryData,
  StorySourceData,
  StoryYearPoint,
} from "./storyTypes";
export { allYears, industryMeanByYear } from "./storyTypes";


/** Axes with a dedicated story page — topic/compare routes redirect here. */
export const STORY_SLUGS: Record<string, string> = {
  dei: "/stories/dei",
  altruism: "/stories/altruism",
};

export function storyPathForAxis(axis: string): string | undefined {
  return STORY_SLUGS[axis];
}

export async function loadStory(slug: string): Promise<StoryData | null> {
  try {
    const raw = await fs.readFile(path.join(STORIES_DIR, `${slug}.json`), "utf-8");
    return JSON.parse(raw) as StoryData;
  } catch {
    return null;
  }
}
