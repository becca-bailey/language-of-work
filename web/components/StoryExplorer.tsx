"use client";

import { useMemo, useState } from "react";
import StoryTrendChart from "@/components/StoryTrendChart";
import StoryHeatmap from "@/components/StoryHeatmap";
import StoryRegisterChart from "@/components/StoryRegisterChart";
import StoryQuoteTimeline from "@/components/StoryQuoteTimeline";
import type { TimelineEvent } from "@/lib/events";
import type { StoryData, StoryHighlight, StoryMetricKey } from "@/lib/storyTypes";

interface Props {
  data: StoryData;
  events?: TimelineEvent[];
  framing?: string[];
}

const SOURCE_LABELS: Record<string, string> = {
  careers: "Careers pages",
  investor: "Investor filings (10-K)",
};

export default function StoryExplorer({ data, events = [], framing = [] }: Props) {
  const sources = Object.keys(data.sources);
  const [source, setSource] = useState(sources[0] ?? "careers");

  const sourceData = data.sources[source];
  const companies = sourceData?.companies ?? [];

  // DEI story uses register-derived shares and a signed net score;
  // performance story keeps the embedding presence share.
  const isDei = data.story === "dei";
  const hasRegisters = companies.some((c) => c.years.some((y) => y.registers));
  const trendMetricKey: StoryMetricKey = isDei ? "netScore" : "fractionPresent";
  const heatmapMetricKey: StoryMetricKey = isDei ? "activeShare" : "fractionPresent";
  const trendLabel = isDei
    ? "Net score (inclusion − meritocracy)"
    : data.metricLabel;

  const lexiconEntries = useMemo(() => {
    const entries: { era: string; terms: typeof data.lexicons[string] }[] = [];
    for (const [era, terms] of Object.entries(data.lexicons)) {
      if (terms.length) entries.push({ era, terms });
    }
    return entries;
  }, [data.lexicons]);

  const filteredHighlights = useMemo(() => {
    if (!data.highlights?.length) return [];
    return data.highlights.filter((h) => h.source === source);
  }, [data.highlights, source]);

  const highlightsByStance = useMemo(() => {
    const groups = new Map<string, { note: string; items: StoryHighlight[] }>();
    for (const h of filteredHighlights) {
      const g = groups.get(h.stance) ?? { note: h.stanceNote, items: [] };
      g.items.push(h);
      groups.set(h.stance, g);
    }
    return [...groups.entries()];
  }, [filteredHighlights]);

  return (
    <div className="space-y-10">
      {framing.map((p, i) => (
        <p
          key={i}
          className={
            i === 0
              ? "max-w-prose text-lg text-neutral-700 dark:text-neutral-300"
              : "max-w-prose text-sm text-neutral-600 dark:text-neutral-400"
          }
        >
          {p}
        </p>
      ))}

      {sources.length > 1 && (
        <div className="flex flex-wrap gap-2">
          {sources.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setSource(s)}
              className={`rounded-full px-4 py-1.5 text-sm transition-colors ${
                source === s
                  ? "bg-indigo-600 text-white"
                  : "border border-neutral-300 text-neutral-600 hover:border-neutral-400 dark:border-neutral-700 dark:text-neutral-400"
              }`}
            >
              {SOURCE_LABELS[s] ?? s}
            </button>
          ))}
        </div>
      )}

      {source === "investor" && sourceData?.coverageStart && (
        <p className="text-xs text-amber-700 dark:text-amber-500">
          Investor coverage is reliable from FY{sourceData.coverageStart} onward (SEC Human Capital
          disclosure requirement). Earlier years may be sparse.
        </p>
      )}

      {isDei && hasRegisters && (
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
            What kind of DEI language, year by year
          </h2>
          <p className="mt-1 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
            Every careers-page chunk is classified into a DEI register by an LLM. This shows
            stance, not just topic: aspirational boilerplate, structural commitments, and
            anti-DEI counter-programming each get their own color.
          </p>
          <div className="mt-4">
            <StoryRegisterChart companies={companies} />
          </div>
        </section>
      )}

      {isDei && !hasRegisters && source === "investor" && (
        <p className="text-xs text-neutral-500">
          Register classification covers careers pages only — switch to Careers pages to see
          the register breakdown. Investor filings are scored on the net inclusion metric
          below.
        </p>
      )}

      {isDei && data.timelines && data.timelines.length > 0 && (
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
            How each company&apos;s voice changed
          </h2>
          <p className="mt-1 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
            First and most recent appearance of each register on a company&apos;s careers
            pages — read top to bottom as a then-vs-now narrative.
          </p>
          <div className="mt-4">
            <StoryQuoteTimeline timelines={data.timelines} />
          </div>
        </section>
      )}

      {highlightsByStance.length > 0 && (
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
            Standout language
          </h2>
          <p className="mt-1 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
            {isDei
              ? "Chunks that most clearly signal a stance on workplace inclusion — grouped by rhetorical move, not just highest scores."
              : "Chunks that most clearly signal a stance on hard work and performance — grouped by register, not just highest scores."}
          </p>
          <div className="mt-6 space-y-8">
            {highlightsByStance.map(([stance, { note, items }]) => (
              <div key={stance}>
                <h3 className="text-sm font-medium text-indigo-700 dark:text-indigo-400">
                  {items[0]?.stanceLabel}
                </h3>
                <p className="mt-1 text-xs text-neutral-500">{note}</p>
                <ul className="mt-3 space-y-3">
                  {items.map((h) => (
                    <li
                      key={h.id}
                      className="rounded-lg border border-neutral-200 px-4 py-3 dark:border-neutral-800"
                    >
                      <p className="text-sm leading-relaxed text-neutral-800 dark:text-neutral-200">
                        &ldquo;{h.text}&rdquo;
                      </p>
                      <p className="mt-2 font-mono text-xs text-neutral-400">
                        {h.displayName} · {h.year}
                        {h.heading ? ` · ${h.heading}` : ""}
                      </p>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
          Industry trend
        </h2>
        <p className="mt-1 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
          {isDei
            ? "Directional embedding score: how much closer the year's strongest language sits to inclusion than to meritocracy framing. Above zero = inclusion-leaning; below = meritocracy-leaning. Bold line = cross-company mean."
            : `Bold line = cross-company mean of ${data.metricLabel.toLowerCase()}. Faint lines = individual companies (hover to highlight).`}
        </p>
        <div className="mt-4">
          <StoryTrendChart
            companies={companies}
            metricLabel={trendLabel}
            metricKey={trendMetricKey}
            format={isDei ? "signed" : "percent"}
            events={events}
            coverageStart={source === "investor" ? sourceData?.coverageStart : undefined}
          />
        </div>
      </section>

      {(!isDei || hasRegisters) && (
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
            Company fingerprint
          </h2>
          <p className="mt-1 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
            {isDei
              ? "Each cell = share of that company's chunks in that year classified into an active DEI register. Blank cells = absence or no data."
              : "Each cell = share of that company's chunks in that year scoring above threshold. Blank cells = absence or no data."}
          </p>
          <div className="mt-4">
            <StoryHeatmap companies={companies} metricKey={heatmapMetricKey} />
          </div>
        </section>
      )}

      {lexiconEntries.length > 0 && (
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
            Phrase lexicons
          </h2>
          <div className="mt-4 grid gap-6 sm:grid-cols-2">
            {lexiconEntries.map(({ era, terms }) => (
              <div key={era}>
                <h3 className="text-xs font-medium text-violet-600 capitalize">
                  {era.replace(/_/g, " ")}
                </h3>
                <ul className="mt-2 space-y-2 text-xs text-neutral-600 dark:text-neutral-400">
                  {terms.slice(0, 8).map((t) => (
                    <li key={`${t.company ?? ""}-${t.term}`}>
                      <span className="font-medium">{t.term}</span>
                      {t.company && (
                        <span className="text-neutral-400"> · {t.company}</span>
                      )}
                      <span className="text-neutral-400">
                        {" "}
                        ({t.first_year}–{t.last_year})
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
