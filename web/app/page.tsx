import Link from "next/link";
import { listDatasets } from "@/lib/data";

export default async function Home() {
  const datasets = await listDatasets();

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
        Analyses
      </h2>
      {datasets.length === 0 ? (
        <p className="mt-4 rounded-lg border border-dashed border-neutral-300 p-6 text-sm text-neutral-500 dark:border-neutral-700">
          No exported data yet. Run the pipeline through{" "}
          <code className="font-mono">scripts/export_web.py</code>, then reload.
        </p>
      ) : (
        <ul className="mt-4 space-y-2">
          {datasets.flatMap(({ company, axes }) =>
            axes.map((axis) => (
              <li key={`${company}/${axis}`}>
                <Link
                  href={`/${company}/${axis}`}
                  className="group flex items-baseline justify-between rounded-lg border border-neutral-200 px-4 py-3 transition-colors hover:border-neutral-400 dark:border-neutral-800 dark:hover:border-neutral-600"
                >
                  <span>
                    <span className="font-medium capitalize">{company}</span>
                    <span className="text-neutral-400"> / </span>
                    <span className="capitalize">{axis}</span>
                  </span>
                  <span className="text-sm text-neutral-400 transition-transform group-hover:translate-x-0.5">
                    &rarr;
                  </span>
                </Link>
              </li>
            ))
          )}
        </ul>
      )}
    </main>
  );
}
