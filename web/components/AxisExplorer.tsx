"use client";

import { useMemo, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceDot,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AxisData, YearScore } from "@/lib/data";

interface Props {
  axis: AxisData;
  control: AxisData | null;
}

interface Row {
  year: number;
  value: number | null;
  control: number | null;
  thin: boolean;
}

export default function AxisExplorer({ axis, control }: Props) {
  const byYear = useMemo(
    () => new Map(axis.years.map((y) => [y.year, y])),
    [axis]
  );
  const [selectedYear, setSelectedYear] = useState<number>(
    axis.years[axis.years.length - 1]?.year
  );

  const rows: Row[] = useMemo(() => {
    const controlByYear = new Map(
      (control?.years ?? []).map((y) => [y.year, y.zscore])
    );
    const years = [
      ...new Set([...axis.years.map((y) => y.year), ...controlByYear.keys()]),
    ].sort();
    return years.map((year) => ({
      year,
      value: byYear.get(year)?.zscore ?? null,
      control: controlByYear.get(year) ?? null,
      thin: byYear.get(year)?.thin ?? false,
    }));
  }, [axis, control, byYear]);

  const selected: YearScore | undefined = byYear.get(selectedYear);

  return (
    <div>
      <div className="h-90 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={rows}
            margin={{ top: 10, right: 20, bottom: 5, left: 0 }}
            onClick={(state) => {
              const year = Number(state?.activeLabel);
              if (year && byYear.has(year)) setSelectedYear(year);
            }}
          >
            <CartesianGrid strokeDasharray="2 4" strokeOpacity={0.3} />
            <XAxis dataKey="year" fontSize={12} tickMargin={6} />
            <YAxis
              fontSize={12}
              label={{
                value: "z-score (within company)",
                angle: -90,
                position: "insideLeft",
                fontSize: 11,
              }}
            />
            <Tooltip
              formatter={(v, name) => [
                typeof v === "number" ? v.toFixed(2) : String(v ?? ""),
                String(name),
              ]}
              labelFormatter={(year) => {
                const y = byYear.get(Number(year));
                return y
                  ? `${year} — n=${y.nChunks} chunks (top-${y.kUsed})${y.thin ? " · THIN COVERAGE" : ""}`
                  : String(year);
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="value"
              name={axis.axis}
              stroke="#6366f1"
              strokeWidth={2}
              connectNulls
              dot={{ r: 3 }}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="control"
              name="control"
              stroke="#9ca3af"
              strokeWidth={1.5}
              strokeDasharray="6 4"
              connectNulls
              dot={false}
            />
            {rows
              .filter((r) => r.thin && r.value !== null)
              .map((r) => (
                <ReferenceDot
                  key={r.year}
                  x={r.year}
                  y={r.value as number}
                  r={7}
                  fill="none"
                  stroke="#f59e0b"
                  strokeWidth={2}
                />
              ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-1 text-xs text-neutral-500">
        Click a point to inspect a year. Amber rings mark thin-coverage years
        (fewer chunks than the top-k window).
      </p>

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
