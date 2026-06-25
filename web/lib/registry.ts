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
  {
    id: "values-as-ip",
    name: "Values as Intellectual Property",
    blurb:
      "What happens to the language of values once a culture is codified into ownable assets — a creed, a trademarked “Way,” a controlled commons.",
  },
];

export const STORIES: StoryMeta[] = [
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
    slug: "values-as-ip",
    title: "When Values Become Intellectual Property",
    teaser:
      "Automattic's codified canon holds at the mission pole while its conduct language turns toward rights and enforcement.",
    study: "values-as-ip",
  },
  {
    slug: "menlo",
    title: "The Menlo Way",
    teaser:
      "A company codified and broadcast a humane culture more than almost anyone — and its influence never propagated. Durable language, boutique impact.",
    study: "values-as-ip",
  },
];

export function storiesByStudy(): { study: StudyMeta; stories: StoryMeta[] }[] {
  return STUDIES.map((study) => ({
    study,
    stories: STORIES.filter((s) => s.study === study.id),
  })).filter((group) => group.stories.length > 0);
}
