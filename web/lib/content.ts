export interface AxisContent {
  /** Display title for the axis, e.g. "Altruism". */
  title: string;
  /** One-line teaser shown on the home page topic list. */
  teaser: string;
  /** 1-2 paragraphs of editorial framing for the topic landing page. */
  framing: string[];
  /** Optional extra summary line shown under the findings. */
  summary?: string;
}

const CONTENT: Record<string, AxisContent> = {
  altruism: {
    title: "Altruism",
    teaser:
      "Which companies said they were changing the world — and did that early optimism fade?",
    framing: [
      "Which companies said they were changing the world? Did their early tech-industry optimism change over time?",
      "This axis contrasts idealistic, world-improving language with commercially pragmatic language, measured on archived careers pages. Each year's score is the projection of mission and brand sentences onto the contrast axis, z-scored within company — so it tracks how a company's own emphasis shifts, not how lofty it sounds compared to anyone else.",
    ],
    summary:
      "Scores are relative within each company; compare the shapes of trajectories, not absolute levels.",
  },
  dei: {
    title: "DEI Language",
    teaser:
      "When did diversity and inclusion language appear on careers pages — and who retracted it?",
    framing: [
      "When did each company first add substantive DEI language to their careers pages? Which shifted from explicit demographic commitments to vague aspirational framing — and who retracted language after 2023?",
      "Early patterns suggest at least three distinct responses to the DEI era — adopt-and-retract, adopt-and-quiet, and never-adopt or counter-program — but as archive coverage fills in (especially post-2018 SPA-era pages), these stories may change. Inclusion intensity is raw cosine to an inclusion pole; register breakdown shows what kind of language appears.",
      "A separate civilizational lexicon tracks vocabulary like \"the West\" descriptively — when it first and last appeared on careers pages. Many readers understand this language as coded; the analysis reports timing, not intent.",
    ],
    summary:
      "Absence of language is a real data point. Careers-page scope only — not annual letters or press. Compare register fingerprints, not just intensity lines.",
  },
};

/** Returns editorial content for an axis, with a generic fallback so new axes don't crash. */
export function getAxisContent(slug: string): AxisContent {
  const entry = CONTENT[slug];
  if (entry) return entry;
  const title = slug.charAt(0).toUpperCase() + slug.slice(1);
  return {
    title,
    teaser: `How ${title.toLowerCase()} language on careers pages shifted over time.`,
    framing: [
      `Movement along the ${title.toLowerCase()} contrast axis, measured on archived careers pages and z-scored within each company.`,
    ],
  };
}
