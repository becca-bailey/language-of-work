import Link from "next/link";
import { storiesByStudy } from "@/lib/registry";

export default function Home() {
  const groups = storiesByStudy();

  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-6 py-16">
      <p className="font-mono text-xs uppercase tracking-[0.2em] text-neutral-500">
        The Language of Work
      </p>
      <h1 className="mt-2 text-3xl font-semibold tracking-tight">
        How companies talk about work
      </h1>
      <p className="mt-4 max-w-prose text-neutral-600 dark:text-neutral-400">
        A set of studies measuring the language companies use about themselves —
        as employers, as missions, as cultures — and how it shifts over time,
        tracked as movement along embedding-based semantic axes.
      </p>

      {groups.map(({ study, stories }) => (
        <section key={study.id} className="mt-12">
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
            {study.name}
          </h2>
          <p className="mt-2 max-w-prose text-sm text-neutral-500 dark:text-neutral-400">
            {study.blurb}
          </p>
          <ul className="mt-4 space-y-2">
            {stories.map((story) => (
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
        </section>
      ))}
    </main>
  );
}
