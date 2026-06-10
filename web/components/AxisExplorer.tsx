"use client";

import { useMemo, useState } from "react";
import AxisChart, { type ChartRow } from "@/components/AxisChart";
import type { AxisData, YearScore } from "@/lib/data";

interface Props {
  axis: AxisData;
  control: AxisData | null;
}

export default function AxisExplorer({ axis, control }: Props) {
  const axisYears = axis.years;
  const controlYears = control?.years ?? [];

  const byYear = useMemo(
    () => new Map(axisYears.map((y) => [y.year, y])),
    [axisYears]
  );
  const [selectedYear, setSelectedYear] = useState<number>(
    axisYears[axisYears.length - 1]?.year
  );

  const rows: ChartRow[] = useMemo(() => {
    const controlByYear = new Map(controlYears.map((y) => [y.year, y.zscore]));
    const years = [
      ...new Set([...axisYears.map((y) => y.year), ...controlByYear.keys()]),
    ].sort((a, b) => a - b);
    return years.map((year) => {
      const y = byYear.get(year);
      return {
        year,
        value: y?.zscore ?? null,
        control: controlByYear.get(year) ?? null,
        thin: y?.thin ?? false,
        nItems: y?.nChunks ?? 0,
        kUsed: y?.kUsed ?? 0,
      };
    });
  }, [axisYears, controlYears, byYear]);

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
          Sentence-level scoring — top idealistic lines per year, not diluted
          by page chrome. Click a point to inspect. Amber rings = thin coverage.
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
        {axisYears.map((y) => (
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
              z = {selected.zscore.toFixed(2)} · {selected.nChunks} sentences ·
              top-{selected.kUsed}
            </span>
            {selected.thin && (
              <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
                thin coverage
              </span>
            )}
          </div>

          <h3 className="mt-5 text-sm font-medium uppercase tracking-wide text-neutral-500">
            Top-matching sentences (the evidence)
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
