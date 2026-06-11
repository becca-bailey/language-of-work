import Link from "next/link";

const STORIES = [
  {
    slug: "dei",
    title: "DEI Language",
    teaser:
      "Industry-wide adoption, retraction, and counter-programming on careers pages.",
  },
  {
    slug: "altruism",
    title: "Changing the World",
    teaser:
      "When did idealistic \"change the world\" copy peak — and who still sounds that way?",
  },
] as const;

export default function Home() {
  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-6 py-16">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-neutral-500">
        The Language of Work
      </p>
      <h1 className="mt-2 text-3xl font-semibold tracking-tight">
        Careers Page Archaeology
      </h1>
      <p className="mt-4 max-w-prose text-neutral-600 dark:text-neutral-400">
        How companies describe themselves as employers over time, measured as
        movement along embedding-based semantic axes built from archived
        careers pages.
      </p>

      <h2 className="mt-12 text-sm font-medium uppercase tracking-wide text-neutral-500">
        Stories
      </h2>
      <ul className="mt-4 space-y-2">
        {STORIES.map((story) => (
          <li key={story.slug}>
            <Link
              href={`/stories/${story.slug}`}
              className="group flex items-baseline justify-between gap-4 rounded-lg border border-indigo-200 bg-indigo-50/50 px-4 py-3 transition-colors hover:border-indigo-400 dark:border-indigo-900 dark:bg-indigo-950/30 dark:hover:border-indigo-700"
            >
              <span>
                <span className="font-medium">{story.title}</span>
                <span className="mt-0.5 block text-sm text-neutral-500 dark:text-neutral-400">
                  {story.teaser}
                </span>
              </span>
              <span className="text-sm text-neutral-400 transition-transform group-hover:translate-x-0.5">
                &rarr;
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
