"use client";

import { useMemo, useState } from "react";
import AxisChart, { type ChartRow } from "@/components/AxisChart";
import type { AxisData, YearScore } from "@/lib/data";

interface Props {
  axis: AxisData;
  control: AxisData | null;
}

export default function AxisExplorer({ axis, control }: Props) {
  const byYear = useMemo(
    () => new Map(axis.years.map((y) => [y.year, y])),
    [axis]
  );
  const [selectedYear, setSelectedYear] = useState<number>(
    axis.years[axis.years.length - 1]?.year
  );

  const rows: ChartRow[] = useMemo(() => {
    const controlByYear = new Map(
      (control?.years ?? []).map((y) => [y.year, y.zscore])
    );
    const years = [
      ...new Set([...axis.years.map((y) => y.year), ...controlByYear.keys()]),
    ].sort((a, b) => a - b);
    return years.map((year) => {
      const y = byYear.get(year);
      return {
        year,
        value: y?.zscore ?? null,
        control: controlByYear.get(year) ?? null,
        thin: y?.thin ?? false,
        nChunks: y?.nChunks ?? 0,
        kUsed: y?.kUsed ?? 0,
      };
    });
  }, [axis, control, byYear]);

  const selected: YearScore | undefined = byYear.get(selectedYear);

  return (
    <div>
      <AxisChart
        rows={rows}
        axisName={axis.axis}
        selectedYear={selectedYear}
        onSelectYear={setSelectedYear}
      />
      <div className="mt-1 flex items-center justify-between">
        <p className="text-xs text-neutral-500">
          Click a point to inspect a year. Amber rings mark thin-coverage years
          (fewer chunks than the top-k window).
        </p>
        <div className="flex items-center gap-4 text-xs text-neutral-500">
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-0.5 w-5 bg-indigo-500" />
            {axis.axis}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block h-0 w-5 border-t-[1.5px] border-dashed border-neutral-400" />
            control
          </span>
        </div>
      </div>

      <div className="mt-8 flex flex-wrap gap-1.5">
        {axis.years.map((y) => (
          <button
            key={y.year}
            onClick={() => setSelectedYear(y.year)}
            className={`rounded-md px-2.5 py-1 font-mono text-xs transition-colors ${
              y.year === selectedYear
                ? "bg-indigo-600 text-white"
                : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200 dark:bg-neutral-800 dark:text-neutral-300 dark:hover:bg-neutral-700"
            }`}
          >
            {y.year}
          </button>
        ))}
      </div>

      {selected && (
        <section className="mt-6 rounded-xl border border-neutral-200 p-5 dark:border-neutral-800">
          <div className="flex flex-wrap items-baseline gap-x-4 gap-y-1">
            <h2 className="text-xl font-semibold">{selected.year}</h2>
            <span className="font-mono text-sm text-neutral-500">
              z = {selected.zscore.toFixed(2)} · {selected.nChunks} chunks ·
              top-{selected.kUsed}
            </span>
            {selected.thin && (
              <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
                thin coverage
              </span>
            )}
            {selected.carriedForwardFrac !== null && (
              <span
                className="rounded-full bg-neutral-100 px-2 py-0.5 text-xs text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300"
                title="Fraction of this year's mission chunks near-duplicated from the prior year"
              >
                {Math.round(selected.carriedForwardFrac * 100)}% carried
                forward · {Math.round((1 - selected.carriedForwardFrac) * 100)}%
                new text
              </span>
            )}
          </div>

          <h3 className="mt-5 text-sm font-medium uppercase tracking-wide text-neutral-500">
            Top-matching chunks (the evidence)
          </h3>
          <ul className="mt-3 space-y-3">
            {selected.quotes.map((q, i) => (
              <li
                key={i}
                className="border-l-2 border-indigo-300 pl-4 dark:border-indigo-700"
              >
                {q.heading && (
                  <p className="text-xs font-medium text-neutral-500">
                    {q.heading}
                  </p>
                )}
                <blockquote className="mt-0.5 text-sm leading-relaxed text-neutral-800 dark:text-neutral-200">
                  &ldquo;{q.text}&rdquo;
                </blockquote>
                <p className="mt-1 font-mono text-xs text-neutral-400">
                  projection {q.score.toFixed(3)}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
