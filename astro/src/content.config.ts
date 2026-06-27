import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const essays = defineCollection({
  loader: glob({ pattern: "**/*.mdx", base: "./src/content/essays" }),
  schema: z.object({
    title: z.string(),
    teaser: z.string().optional(),
    subtitle: z.string().optional(),
    draft: z.boolean().optional(),
  }),
});

export const collections = { essays };
