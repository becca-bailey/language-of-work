/**
 * Single source of truth for the stories the site presents, grouped by study.
 *
 * A "study" is a research project (its own cases, axes, and method); a "story"
 * is a curated narrative under /stories/[slug]. The homepage hub renders from
 * this registry so adding a story is a one-line edit here, not a page rewrite.
 * The generic axis explorer lives separately under /explore/[axis].
 */

export interface StudyMeta {
  id: string;
  name: string;
  blurb: string;
}

export interface StoryMeta {
  slug: string; // route under /stories/
  title: string;
  teaser: string;
  study: string; // StudyMeta.id
}

export const STUDIES: StudyMeta[] = [
  {
    id: "careers",
    name: "Careers-Page Archaeology",
    blurb:
      "How companies describe themselves as employers over time, measured along embedding-based semantic axes built from archived careers pages.",
  },
];

export const STORIES: StoryMeta[] = [
  {
    slug: "power",
    title: "Culture is downstream of power",
    teaser:
      "Worker-serving language (DEI) tracks worker power and collapses when it falls; the management-serving substrate (performance) never moves.",
    study: "careers",
  },
  {
    slug: "dei",
    title: "DEI Language",
    teaser: "Industry-wide adoption, retraction, and counter-programming on careers pages.",
    study: "careers",
  },
  {
    slug: "altruism",
    title: "Changing the World",
    teaser: 'When did idealistic "change the world" copy peak — and who still sounds that way?',
    study: "careers",
  },
  {
    slug: "netflix-culture",
    title: "A Team, Not a Family",
    teaser:
      "Netflix's 2009 culture deck, the model it spread (narrowly to Coinbase, broadly by convergence), and the scoreboard that isn't there.",
    study: "careers",
  },
  {
    slug: "culture-fit",
    title: "Who is a culture fit?",
    teaser:
      "Who belongs at each company, in their careers pages' own words — from belonging-first to an explicit elite filter.",
    study: "careers",
  },
];

export function storiesByStudy(): { study: StudyMeta; stories: StoryMeta[] }[] {
  return STUDIES.map((study) => ({
    study,
    stories: STORIES.filter((s) => s.study === study.id),
  })).filter((group) => group.stories.length > 0);
}
