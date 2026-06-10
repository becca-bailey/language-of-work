import Link from "next/link";
import { notFound } from "next/navigation";
import {
  compareableAxes,
  loadAxis,
  loadCompaniesManifest,
  type AxisData,
} from "@/lib/data";
import { getAxisContent } from "@/lib/content";

interface Finding {
  company: string;
  displayName: string;
  sentence: string;
  peakYear: number;
  latestYear: number;
  yearsCovered: number;
}

function computeFinding(
  data: AxisData,
  displayName: string,
  axisTitle: string
): Finding | null {
  const years = [...data.years].sort((a, b) => a.year - b.year);
  if (years.length === 0) return null;

  const peak = years.reduce((best, y) => (y.zscore > best.zscore ? y : best));
  const latest = years[years.length - 1];
  const delta = latest.zscore - peak.zscore;
  const axisLabel = axisTitle.toLowerCase();

  let sentence: string;
  if (years.length === 1) {
    sentence = `${displayName} has only one measured year (${latest.year}), so there's no trend yet.`;
  } else if (peak.year === latest.year) {
    sentence = `${displayName}'s ${axisLabel} language peaked in ${peak.year} — the most recent year measured — so it's still at its high point.`;
  } else if (delta > -0.25) {
    sentence = `${displayName}'s ${axisLabel} language peaked in ${peak.year} and has held roughly steady since.`;
  } else {
    const drop = Math.abs(delta);
    const qualifier = drop >= 1 ? "declined sharply" : "declined";
    sentence = `${displayName}'s ${axisLabel} language peaked in ${peak.year} and has ${qualifier} since (${delta.toFixed(1)}σ by ${latest.year}).`;
  }

  return {
    company: data.company,
    displayName,
    sentence,
    peakYear: peak.year,
    latestYear: latest.year,
    yearsCovered: years.length,
  };
}

export default async function TopicPage({
  params,
}: {
  params: Promise<{ axis: string }>;
}) {
  const { axis } = await params;
  const manifest = await loadCompaniesManifest();
  const companies = manifest.filter((c) => c.axes.includes(axis));
  if (companies.length === 0) notFound();

  const content = getAxisContent(axis);
  const canCompare = compareableAxes(manifest).includes(axis);

  const findings = (
    await Promise.all(
      companies.map(async (c) => {
        const data = await loadAxis(c.id, axis);
        return data ? computeFinding(data, c.displayName, content.title) : null;
      })
    )
  ).filter((f): f is Finding => f !== null);

  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-6 py-12">
      <Link
        href="/"
        className="text-sm text-neutral-500 transition-colors hover:text-neutral-800 dark:hover:text-neutral-200"
      >
        &larr; All topics
      </Link>
      <h1 className="mt-4 text-3xl font-semibold tracking-tight">
        {content.title}
      </h1>
      {content.framing.map((paragraph, i) => (
        <p
          key={i}
          className={
            i === 0
              ? "mt-4 max-w-prose text-lg text-neutral-700 dark:text-neutral-300"
              : "mt-3 max-w-prose text-sm text-neutral-600 dark:text-neutral-400"
          }
        >
          {paragraph}
        </p>
      ))}

      {findings.length > 0 && (
        <>
          <h2 className="mt-12 text-sm font-medium uppercase tracking-wide text-neutral-500">
            Findings
          </h2>
          <ul className="mt-4 space-y-3">
            {findings.map((f) => (
              <li
                key={f.company}
                className="rounded-lg border border-neutral-200 px-4 py-3 dark:border-neutral-800"
              >
                <p className="text-sm text-neutral-800 dark:text-neutral-200">
                  {f.sentence}
                </p>
                <p className="mt-1 font-mono text-xs text-neutral-400">
                  peak {f.peakYear} &middot; latest {f.latestYear} &middot;{" "}
                  {f.yearsCovered} years covered
                </p>
              </li>
            ))}
          </ul>
          {content.summary && (
            <p className="mt-4 max-w-prose text-xs text-neutral-500">
              {content.summary}
            </p>
          )}
        </>
      )}

      {canCompare && (
        <Link
          href={`/${axis}/compare`}
          className="group mt-10 flex items-baseline justify-between rounded-lg border border-indigo-200 bg-indigo-50/50 px-4 py-3 transition-colors hover:border-indigo-400 dark:border-indigo-900 dark:bg-indigo-950/30 dark:hover:border-indigo-700"
        >
          <span className="font-medium">Compare all companies</span>
          <span className="text-sm text-neutral-400 transition-transform group-hover:translate-x-0.5">
            &rarr;
          </span>
        </Link>
      )}

      <h2 className="mt-10 text-sm font-medium uppercase tracking-wide text-neutral-500">
        Company reports
      </h2>
      <ul className="mt-4 space-y-2">
        {companies.map((c) => (
          <li key={c.id}>
            <Link
              href={`/${axis}/${c.id}`}
              className="group flex items-baseline justify-between rounded-lg border border-neutral-200 px-4 py-3 transition-colors hover:border-neutral-400 dark:border-neutral-800 dark:hover:border-neutral-600"
            >
              <span className="font-medium">{c.displayName}</span>
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
