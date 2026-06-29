/**
 * Draft/published gating for stories and essays.
 *
 * A piece is shown in production only when `published: true`. Anything else
 * (published: false, or the flag omitted) is a draft: it renders under
 * `astro dev` so you can preview it locally, but is excluded from the
 * production build (`astro build`, which is what Netlify runs).
 *
 * `import.meta.env.DEV` is true under `astro dev` and false under `astro build`
 * (including Netlify deploy previews) — so drafts are strictly local.
 */
export const showDrafts = import.meta.env.DEV;

export function isVisible(published?: boolean): boolean {
  return published === true || showDrafts;
}
