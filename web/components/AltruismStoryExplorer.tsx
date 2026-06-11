"use client";

import StorySparklines from "@/components/StorySparklines";
import StoryYearCompare from "@/components/StoryYearCompare";
import StoryPeakPresent from "@/components/StoryPeakPresent";
import type { StoryData } from "@/lib/storyTypes";

interface Props {
  data: StoryData;
  framing?: string[];
}

export default function AltruismStoryExplorer({ data, framing = [] }: Props) {
  const companies = data.sources.careers?.companies ?? [];
  const peakPresent = data.peakPresent ?? [];
  const yearQuotes = data.yearQuotes ?? [];

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

      {companies.length > 0 && (
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
            When did idealism peak?
          </h2>
          <p className="mt-1 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
            Each company&apos;s careers copy projected onto an idealism ↔ commercial
            pragmatism axis, then z-scored within company. Google&apos;s famous
            &ldquo;change the world&rdquo; era peaks around 2014 at sentence level;
            the sparklines show who else had a moment — and when it passed.
          </p>
          <div className="mt-4">
            <StorySparklines
              companies={companies}
              metricLabel={data.metricLabel}
            />
          </div>
        </section>
      )}

      {peakPresent.length > 0 && (
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
            Peak vs. present
          </h2>
          <p className="mt-1 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
            The highest-scoring idealistic sentence from each company&apos;s peak
            year beside the most recent year measured — a then-vs-now read on
            employer branding.
          </p>
          <div className="mt-4">
            <StoryPeakPresent items={peakPresent} />
          </div>
        </section>
      )}

      {yearQuotes.length > 0 && (
        <section>
          <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
            Same year, different voices
          </h2>
          <p className="mt-1 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
            Pick a year to see what each company&apos;s careers page was literally
            saying at peak idealism — side by side, not overlaid on one chart.
          </p>
          <div className="mt-4">
            <StoryYearCompare quotes={yearQuotes} />
          </div>
        </section>
      )}
    </div>
  );
}
