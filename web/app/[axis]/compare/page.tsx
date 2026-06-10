import Link from "next/link";
import { notFound } from "next/navigation";
import CompareChart from "@/components/CompareChart";
import { loadAxis, loadCompaniesManifest } from "@/lib/data";
import { getAxisContent } from "@/lib/content";

export default async function ComparePage({
  params,
}: {
  params: Promise<{ axis: string }>;
}) {
  const { axis } = await params;
  const manifest = await loadCompaniesManifest();
  const companyIds = manifest
    .filter((c) => c.axes.includes(axis))
    .map((c) => c.id);

  if (companyIds.length < 2) notFound();

  const datasets = await Promise.all(
    companyIds.map((id) => loadAxis(id, axis))
  );
  const valid = datasets.filter((d): d is NonNullable<typeof d> => d !== null);
  if (valid.length < 2) notFound();

  const content = getAxisContent(axis);

  const series = valid.map((d) => ({
    company: d.company,
    displayName: d.displayName ?? d.company,
    points: d.years.map((y) => ({
      year: y.year,
      zscore: y.zscore,
      thin: y.thin,
    })),
  }));

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-12">
      <Link
        href={`/${axis}`}
        className="text-sm text-neutral-500 transition-colors hover:text-neutral-800 dark:hover:text-neutral-200"
      >
        &larr; {content.title}
      </Link>
      <h1 className="mt-4 text-2xl font-semibold tracking-tight">
        Compare: {content.title}
      </h1>
      <p className="mt-2 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
        Side-by-side trajectories for {valid.map((d) => d.displayName ?? d.company).join(", ")}.
        Each line is z-scored within its own company — compare shapes, not absolute magnitudes.
      </p>
      <div className="mt-8">
        <CompareChart series={series} axisName={axis} />
      </div>
      <ul className="mt-8 space-y-2 border-t border-neutral-200 pt-6 dark:border-neutral-800">
        {valid.map((d) => (
          <li key={d.company}>
            <Link
              href={`/${axis}/${d.company}`}
              className="text-sm text-indigo-600 hover:underline dark:text-indigo-400"
            >
              {d.displayName ?? d.company} — full detail &rarr;
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
