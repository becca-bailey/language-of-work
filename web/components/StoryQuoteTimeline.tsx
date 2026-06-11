"use client";

import { useState } from "react";
import type { StoryTimeline } from "@/lib/storyTypes";

const REGISTER_STYLES: Record<string, string> = {
  explicit_demographic:
    "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
  structural_process:
    "bg-teal-100 text-teal-800 dark:bg-teal-950 dark:text-teal-300",
  aspirational_vague:
    "bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300",
  belonging_culture:
    "bg-violet-100 text-violet-800 dark:bg-violet-950 dark:text-violet-300",
  meritocracy:
    "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300",
};

export default function StoryQuoteTimeline({
  timelines,
}: {
  timelines: StoryTimeline[];
}) {
  const companies = timelines.filter((t) => t.quotes.length > 0);
  const [selected, setSelected] = useState(companies[0]?.company ?? "");
  const active = companies.find((t) => t.company === selected);

  if (!companies.length) return null;

  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {companies.map((t) => (
          <button
            key={t.company}
            type="button"
            onClick={() => setSelected(t.company)}
            className={`rounded-full px-3 py-1 text-xs transition-colors ${
              selected === t.company
                ? "bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900"
                : "border border-neutral-300 text-neutral-600 hover:border-neutral-400 dark:border-neutral-700 dark:text-neutral-400"
            }`}
          >
            {t.displayName}
          </button>
        ))}
      </div>

      {active && (
        <ol className="mt-6 space-y-0 border-l border-neutral-200 dark:border-neutral-800">
          {active.quotes.map((q, i) => (
            <li key={`${q.year}-${q.register}-${i}`} className="relative pb-8 pl-6 last:pb-0">
              <span className="absolute left-[-5px] top-1.5 h-2.5 w-2.5 rounded-full bg-neutral-300 dark:bg-neutral-700" />
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-sm font-medium text-neutral-900 dark:text-neutral-100">
                  {q.year}
                </span>
                <span
                  className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                    REGISTER_STYLES[q.register] ??
                    "bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-400"
                  }`}
                >
                  {q.register.replace(/_/g, " ")}
                </span>
              </div>
              <p className="mt-2 max-w-prose text-sm leading-relaxed text-neutral-700 dark:text-neutral-300">
                &ldquo;{q.text}&rdquo;
              </p>
              {q.heading && (
                <p className="mt-1 font-mono text-xs text-neutral-400">{q.heading}</p>
              )}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
