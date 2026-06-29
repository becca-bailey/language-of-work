import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const essays = defineCollection({
  loader: glob({ pattern: "**/*.mdx", base: "./src/content/essays" }),
  schema: z.object({
    title: z.string(),
    teaser: z.string().optional(),
    subtitle: z.string().optional(),
    // Shown in production only when true; otherwise a draft (dev-only).
    published: z.boolean().optional(),
  }),
});

const stories = defineCollection({
  loader: glob({ pattern: "**/*.mdx", base: "./src/content/stories" }),
  schema: z.object({
    title: z.string(),
    subtitle: z.string().optional(),
    thesis: z.string().optional(),
    // Homepage hub metadata (was registry.ts): which study it belongs to, the
    // listing teaser, sort order, and draft/published gating.
    study: z.string(),
    teaser: z.string(),
    order: z.number().default(0),
    published: z.boolean().optional(),
  }),
});

export const collections = { essays, stories };
