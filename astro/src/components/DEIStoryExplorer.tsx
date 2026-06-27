"use client";

import { useMemo } from "react";
import StoryRegisterChart from "@/components/StoryRegisterChart";
import StoryQuoteTimeline from "@/components/StoryQuoteTimeline";
import StoryStanceEnvelope from "@/components/StoryStanceEnvelope";
import StorySalienceChart from "@/components/StorySalienceChart";
import MaterialDEIChart from "@/components/MaterialDEIChart";
import type { TimelineEvent } from "@/lib/events";
import type { StoryData, StoryHighlight } from "@/lib/storyTypes";
import type { MaterialDEI } from "@/lib/benefitsStory";

interface Props {
  data: StoryData;
  events?: TimelineEvent[];
  framing?: string[];
  materialDEI?: MaterialDEI | null;
}

export default function DEIStoryExplorer({ data, events = [], framing = [], materialDEI = null }: Props) {
  const companies = data.sources.careers?.companies ?? [];
  const hasRegisters = companies.some((c) => c.years.some((y) => y.registers));
  const hasEnvelopes = (data.envelopes?.length ?? 0) > 0;
  const hasSalience = companies.some((c) => c.years.some((y) => y.salienceTopkMean !== undefined));

  const highlightsByStance = useMemo(() => {
    const highlights = (data.highlights ?? []).filter((h) => h.source === "careers");
    const groups = new Map<string, { note: string; items: StoryHighlight[] }>();
    for (const h of highlights) {
      const g = groups.get(h.stance) ?? { note: h.stanceNote, items: [] };
      g.items.push(h);
      groups.set(h.stance, g);
    }
    return [...groups.entries()];
  }, [data.highlights]);

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

      {hasRegisters && (
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

      {materialDEI && materialDEI.total > 0 && (
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
            Is there substance behind the words?
          </h2>
          <p className="mt-1 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
            {materialDEI.blurb} Note the different lens: the bars above are the share of{" "}
            <em>DEI chunks</em> by stance; this line is the share of <em>job postings</em> that name
            a concrete benefit. The rhetoric spikes and retracts — the material substance stays a
            low, flat line.
          </p>
          <div className="mt-4">
            <MaterialDEIChart data={materialDEI} />
          </div>
          <p className="mt-2 max-w-prose text-xs text-neutral-500">
            Self-presentation: what&apos;s <em>advertised</em>, not audited — rarely advertised is
            not the same as rarely offered. Thin and uneven per year; keyword-based. See the{" "}
            <a className="underline" href="/stories/benefits/">
              benefits tracker
            </a>
            .
          </p>
        </section>
      )}

      {hasEnvelopes && (
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
            Stance envelope — did the direction flip?
          </h2>
          <p className="mt-1 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
            A unipolar inclusion score cannot show inversion — anti-DEI copy still scores high
            because it talks about belonging. The envelope plots the most inclusion-leaning and
            most meritocracy-leaning chunk each year (inclusion − meritocracy). Coinbase peaks at
            +0.14 in 2021–22, then negative territory arrives in 2024.
          </p>
          <div className="mt-4">
            <StoryStanceEnvelope envelopes={data.envelopes!} events={events} />
          </div>
        </section>
      )}

      {hasSalience && (
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
            Topical salience — did the topic disappear?
          </h2>
          <p className="mt-1 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
            Separate from stance direction: how much is the page talking about DEI-adjacent topics
            at all? Coinbase keeps high salience while stance inverts; most companies show
            salience peaking around 2021 then evaporating.
          </p>
          <div className="mt-4">
            <StorySalienceChart companies={companies} events={events} />
          </div>
        </section>
      )}

      {data.timelines && data.timelines.length > 0 && (
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
            Chunks that most clearly signal a stance on workplace inclusion — grouped by
            rhetorical move, not just highest scores.
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
    </div>
  );
}
