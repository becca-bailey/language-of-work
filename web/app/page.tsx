import Link from "next/link";
import { listDatasets } from "@/lib/data";
import { getAxisContent } from "@/lib/content";

export default async function Home() {
  const datasets = await listDatasets();
  const axes = [...new Set(datasets.flatMap((d) => d.axes))].sort();

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
        <li>
          <Link
            href="/stories/performance"
            className="group flex items-baseline justify-between gap-4 rounded-lg border border-indigo-200 bg-indigo-50/50 px-4 py-3 transition-colors hover:border-indigo-400 dark:border-indigo-900 dark:bg-indigo-950/30 dark:hover:border-indigo-700"
          >
            <span>
              <span className="font-medium">Performance Language</span>
              <span className="mt-0.5 block text-sm text-neutral-500 dark:text-neutral-400">
                Did the hardcore turn follow Twitter? When did hustle language peak?
              </span>
            </span>
            <span className="text-sm text-neutral-400 transition-transform group-hover:translate-x-0.5">
              &rarr;
            </span>
          </Link>
        </li>
        <li>
          <Link
            href="/stories/dei"
            className="group flex items-baseline justify-between gap-4 rounded-lg border border-indigo-200 bg-indigo-50/50 px-4 py-3 transition-colors hover:border-indigo-400 dark:border-indigo-900 dark:bg-indigo-950/30 dark:hover:border-indigo-700"
          >
            <span>
              <span className="font-medium">DEI Language</span>
              <span className="mt-0.5 block text-sm text-neutral-500 dark:text-neutral-400">
                Industry-wide adoption and retraction — careers pages vs investor filings.
              </span>
            </span>
            <span className="text-sm text-neutral-400 transition-transform group-hover:translate-x-0.5">
              &rarr;
            </span>
          </Link>
        </li>
      </ul>

      <h2 className="mt-12 text-sm font-medium uppercase tracking-wide text-neutral-500">
        Topics
      </h2>
      {axes.length === 0 ? (
        <p className="mt-4 rounded-lg border border-dashed border-neutral-300 p-6 text-sm text-neutral-500 dark:border-neutral-700">
          No exported data yet. Run the pipeline through{" "}
          <code className="font-mono">scripts/export_web.py</code>, then reload.
        </p>
      ) : (
        <ul className="mt-4 space-y-2">
          {axes.map((axis) => {
            const content = getAxisContent(axis);
            return (
              <li key={axis}>
                <Link
                  href={`/${axis}`}
                  className="group flex items-baseline justify-between gap-4 rounded-lg border border-neutral-200 px-4 py-3 transition-colors hover:border-neutral-400 dark:border-neutral-800 dark:hover:border-neutral-600"
                >
                  <span>
                    <span className="font-medium">{content.title}</span>
                    <span className="mt-0.5 block text-sm text-neutral-500 dark:text-neutral-400">
                      {content.teaser}
                    </span>
                  </span>
                  <span className="text-sm text-neutral-400 transition-transform group-hover:translate-x-0.5">
                    &rarr;
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </main>
  );
}
