/**
 * Study metadata + the homepage hub grouping.
 *
 * A "study" is a research project (its own cases, axes, and method); a "story"
 * is a curated narrative under /stories/[slug]. Stories themselves now live
 * entirely in the `stories` content collection (MDX frontmatter carries title,
 * teaser, study, order, published) — adding a story is just dropping an MDX
 * file, same as essays. This module only holds the study-level metadata the
 * collection can't, and groups the collection by study for the homepage.
 */
import { getCollection } from "astro:content";
import { isVisible } from "./visibility";

export interface StudyMeta {
  id: string;
  name: string;
  blurb: string;
}

export const STUDIES: StudyMeta[] = [
  {
    id: "careers",
    name: "Careers-Page Archaeology",
    blurb:
      "How companies describe themselves as employers over time, measured along embedding-based semantic axes built from archived careers pages.",
  },
];

/** Published stories (all in dev; published-only in prod), in display order. */
export async function visibleStories() {
  return (await getCollection("stories", (s) => isVisible(s.data.published))).sort(
    (a, b) => a.data.order - b.data.order
  );
}

export async function storiesByStudy() {
  const stories = await visibleStories();
  return STUDIES.map((study) => ({
    study,
    stories: stories.filter((s) => s.data.study === study.id),
  })).filter((group) => group.stories.length > 0);
}
