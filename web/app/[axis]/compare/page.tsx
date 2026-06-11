import Link from "next/link";
import { notFound } from "next/navigation";
import CompareChart from "@/components/CompareChart";
import { loadAxis, loadCompaniesManifest, loadDei } from "@/lib/data";
import { DEI_EVENTS } from "@/lib/events";
import { getAxisContent } from "@/lib/content";
import RegisterShareCompare from "@/components/RegisterShareCompare";

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

  const content = getAxisContent(axis);

  const series =
    axis === "dei"
      ? (
          await Promise.all(companyIds.map((id) => loadDei(id)))
        )
          .filter((d): d is NonNullable<typeof d> => d !== null)
          .map((d) => ({
            company: d.company,
            displayName: d.displayName ?? d.company,
            points: d.years.map((y) => ({
              year: y.year,
              zscore: y.inclusionTopkMean,
              thin: y.thin,
            })),
          }))
      : (
          await Promise.all(companyIds.map((id) => loadAxis(id, axis)))
        )
          .filter((d): d is NonNullable<typeof d> => d !== null)
          .map((d) => ({
            company: d.company,
            displayName: d.displayName ?? d.company,
            points: d.years.map((y) => ({
              year: y.year,
              zscore: y.zscore,
              thin: y.thin,
            })),
          }));

  if (series.length < 2) notFound();
  const valid = series;

  const deiDatasets =
    axis === "dei"
      ? (await Promise.all(companyIds.map((id) => loadDei(id)))).filter(
          (d): d is NonNullable<typeof d> => d !== null
        )
      : [];

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
        Side-by-side trajectories for {valid.map((d) => d.displayName).join(", ")}.
        {axis === "dei"
          ? " Raw inclusion cosine — comparable across companies; near-zero means absent."
          : " Each line is z-scored within its own company — compare shapes, not absolute magnitudes."}
      </p>
      <div className="mt-8">
        <CompareChart
          series={series}
          axisName={axis}
          events={axis === "dei" ? DEI_EVENTS : undefined}
        />
      </div>
      {axis === "dei" && deiDatasets.length >= 2 && (
        <div className="mt-12">
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
            Register fingerprint
          </h2>
          <p className="mt-1 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
            What kind of DEI language each company uses — normalized share of
            register-classified chunks (excluding absent).
          </p>
          <div className="mt-4">
            <RegisterShareCompare datasets={deiDatasets} />
          </div>
        </div>
      )}
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
