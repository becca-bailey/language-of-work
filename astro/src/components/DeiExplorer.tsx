"use client";

import { useMemo, useState } from "react";
import DeiChart, { deiRowsFromYears } from "@/components/DeiChart";
import RegisterChart from "@/components/RegisterChart";
import type { DeiData } from "@/lib/data";

export default function DeiExplorer({ data }: { data: DeiData }) {
  const years = data.years;
  const [selectedYear, setSelectedYear] = useState(years[years.length - 1]?.year ?? 2020);
  const selected = useMemo(() => years.find((y) => y.year === selectedYear), [years, selectedYear]);
  const rows = useMemo(() => deiRowsFromYears(years), [years]);

  return (
    <div className="space-y-10">
      <div>
        <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">Inclusion intensity</h2>
        <p className="mt-1 text-xs text-neutral-500">Raw cosine to inclusion pole — near-zero means absent. Amber rings = thin coverage.</p>
        <div className="mt-4">
          <DeiChart rows={rows} selectedYear={selectedYear} onSelectYear={setSelectedYear} />
        </div>
      </div>

      <div>
        <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">Register breakdown</h2>
        <p className="mt-1 text-xs text-neutral-500">
          What kind of DEI language, not just how much. Chunks with no DEI
          language are omitted — an empty year means the pages said nothing.
        </p>
        <div className="mt-4">
          <RegisterChart years={years} />
        </div>
      </div>

      {selected && (
        <div>
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">{selectedYear} evidence</h2>
          <div className="mt-4 flex flex-wrap gap-1.5">
            {years.map((y) => (
              <button key={y.year} onClick={() => setSelectedYear(y.year)} className={`rounded-md px-2.5 py-1 font-mono text-xs ${y.year === selectedYear ? "bg-emerald-700 text-white" : "bg-neutral-100 text-neutral-600 dark:bg-neutral-800"}`}>{y.year}</button>
            ))}
          </div>
          <div className="mt-4 grid gap-6 md:grid-cols-2">
            <div>
              <h3 className="text-xs font-medium text-emerald-700">Top inclusion</h3>
              <ul className="mt-2 space-y-3 text-sm">
                {selected.inclusionQuotes.map((q, i) => (
                  <li key={i} className="rounded-lg border border-neutral-200 p-3 dark:border-neutral-800">
                    {q.heading && <p className="text-xs font-medium text-neutral-500">{q.heading}</p>}
                    <p className="mt-1 text-neutral-800 dark:text-neutral-200">{q.text}</p>
                    <p className="mt-1 font-mono text-xs text-neutral-400">score {q.score}</p>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="text-xs font-medium text-violet-600">Inclusion phrases</h3>
              <ul className="mt-2 space-y-1 text-xs text-neutral-600 dark:text-neutral-400">
                {(data.phrases.lexicons?.inclusion ?? data.phrases.terms)
                  .filter((t) => t.first_year <= selectedYear && t.last_year >= selectedYear)
                  .slice(0, 12)
                  .map((t) => (
                    <li key={t.term}>
                      <span className="font-medium">{t.term}</span> ({t.first_year}–{t.last_year})
                    </li>
                  ))}
              </ul>
              {(data.phrases.lexicons?.civilizational?.length ?? 0) > 0 && (
                <>
                  <h3 className="mt-4 text-xs font-medium text-amber-700 dark:text-amber-500">
                    Civilizational framing
                  </h3>
                  <ul className="mt-2 space-y-1 text-xs text-neutral-600 dark:text-neutral-400">
                    {data.phrases.lexicons!.civilizational!
                      .filter((t) => t.first_year <= selectedYear && t.last_year >= selectedYear)
                      .map((t) => (
                        <li key={t.term}>
                          <span className="font-medium">{t.term}</span> ({t.first_year}–{t.last_year})
                        </li>
                      ))}
                  </ul>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
