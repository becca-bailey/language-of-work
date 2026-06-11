"use client";

import { useMemo, useState } from "react";
import type { StoryYearQuote } from "@/lib/storyTypes";

interface Props {
  quotes: StoryYearQuote[];
}

export default function StoryYearCompare({ quotes }: Props) {
  const years = useMemo(() => {
    const ys = new Set(quotes.map((q) => q.year));
    return [...ys].sort((a, b) => a - b);
  }, [quotes]);

  const [selectedYear, setSelectedYear] = useState(
    () => years[Math.floor(years.length / 2)] ?? years[0] ?? 2014
  );

  const byYear = useMemo(() => {
    const map = new Map<number, StoryYearQuote[]>();
    for (const q of quotes) {
      const list = map.get(q.year) ?? [];
      list.push(q);
      map.set(q.year, list);
    }
    for (const [year, list] of map) {
      map.set(
        year,
        [...list].sort((a, b) => b.score - a.score)
      );
    }
    return map;
  }, [quotes]);

  const active = byYear.get(selectedYear) ?? [];

  if (!years.length || !quotes.length) return null;

  return (
    <div>
      <div className="flex flex-wrap gap-1.5">
        {years.map((year) => (
          <button
            key={year}
            type="button"
            onClick={() => setSelectedYear(year)}
            className={`rounded-md px-2.5 py-1 font-mono text-xs transition-colors ${
              year === selectedYear
                ? "bg-indigo-600 text-white"
                : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200 dark:bg-neutral-800 dark:text-neutral-300 dark:hover:bg-neutral-700"
            }`}
          >
            {year}
          </button>
        ))}
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        {active.map((q) => (
          <div
            key={`${q.company}-${q.year}`}
            className="rounded-lg border border-neutral-200 px-4 py-3 dark:border-neutral-800"
          >
            <div className="flex items-baseline justify-between gap-2">
              <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                {q.displayName}
              </p>
              <p className="font-mono text-xs text-neutral-400">
                {q.zscore >= 0 ? "+" : ""}
                {q.zscore.toFixed(2)}σ
              </p>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-neutral-700 dark:text-neutral-300">
              &ldquo;{q.text}&rdquo;
            </p>
            {q.heading && (
              <p className="mt-1 font-mono text-xs text-neutral-400">{q.heading}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
