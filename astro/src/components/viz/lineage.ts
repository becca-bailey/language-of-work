import { loadStory } from "@/lib/stories";

export interface Adopter {
  displayName: string;
  year: number;
  verbatim?: boolean;
  example?: string;
  score?: number | null;
}
export interface Echo {
  displayName: string;
  year: number;
  example: string;
  score: number;
}
export interface Concept {
  id: string;
  label: string;
  tier: string;
  originYear?: number | null;
  originQuote?: string | null;
  adopters: Adopter[];
  echoes?: Echo[];
}

// Shared data prep for the two lineage visualizations (LineageStacked = which language
// matches best; LineageTimeline = when it was adopted). Drops the generic
// (industry-convergence) concepts, keeps only concepts with a Netflix origin quote.
export async function lineageConcepts(): Promise<Concept[]> {
  const data = await loadStory("netflix-culture");
  const concepts = ((data as any)?.propagation?.concepts ?? []) as Concept[];
  return concepts
    .filter((c) => c.tier !== "generic" && c.originQuote)
    .map((c) => ({
      ...c,
      adopters: (c.adopters ?? []).filter((a) => a.example),
      echoes: c.echoes ?? [],
    }));
}

export const maxScore = (c: Concept): number =>
  Math.max(
    0,
    ...c.adopters.map((a) => a.score ?? 0),
    ...(c.echoes ?? []).map((e) => e.score),
  );
