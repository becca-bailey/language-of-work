"use client";

import CompareChart, { type CompanySeries } from "@/components/CompareChart";
import MenloPhraseChart from "@/components/MenloPhraseChart";
import MenloAuditChart, { type AuditDatum } from "@/components/MenloAuditChart";
import type { TimelineEvent } from "@/lib/events";
import type { MenloStory } from "@/lib/menloStory";

function eventYear(date: string): number {
  const [y, m] = date.split("-");
  return Number(y) + (m ? (Number(m) - 1) / 12 : 0);
}

const GROUP_LABELS: Record<string, string> = {
  trademarks: "Trademarks & brand marks",
  joy_mission: "Joy / mission slogans",
  method: "Method & practice",
};

function SectionHeading({ kicker, title }: { kicker: string; title: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-widest text-amber-600 dark:text-amber-500">
        {kicker}
      </p>
      <h2 className="mt-1 text-xl font-semibold tracking-tight">{title}</h2>
    </div>
  );
}

export default function MenloStoryExplorer({ data }: { data: MenloStory }) {
  const { idealism, brandedLanguage, events, annotations, impactAudit, outsiderView } =
    data;
  const auditData: AuditDatum[] = Object.entries(impactAudit.counts).map(
    ([label, n]) => {
      const isTest = label.startsWith("named adopter");
      return { label, value: isTest ? impactAudit.namedAdopterCredible : n, isTest };
    }
  );

  // Idealism line: Menlo (highlighted first) + the cleaned cohort, for CompareChart.
  const idealismSeries: CompanySeries[] = [
    {
      company: "menlo",
      displayName: "Menlo",
      points: idealism.series.map((s) => ({
        year: s.year,
        zscore: s.zscore,
        thin: s.thin,
      })),
    },
    ...idealism.cohort.map((c) => ({
      company: c.id,
      displayName: c.displayName,
      points: c.years.map((y) => ({ year: y.year, zscore: y.zscore, thin: false })),
    })),
  ];
  const chartEvents: TimelineEvent[] = events.map((ev, i) => ({
    id: `menlo-ev-${i}`,
    label: ev.label.split(/[:(]/)[0].trim().slice(0, 30),
    year: eventYear(ev.date),
    description: ev.label,
  }));

  return (
    <div className="space-y-14">
      {/* Thesis */}
      <p className="max-w-prose border-l-2 border-amber-400 pl-4 text-lg text-neutral-700 dark:text-neutral-300">
        {data.thesis}
      </p>

      {/* Act 1 — branded language */}
      <section className="space-y-4">
        <SectionHeading kicker="Act 1 · The belief" title="A vocabulary they codified" />
        <p className="max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
          When each branded term enters Menlo&apos;s own copy and how long it persists
          (2006–2026). High-Tech Anthropology® and &ldquo;joy&rdquo; run the whole
          length; some marks were coined and dropped; &ldquo;return joy&rdquo; is a
          late addition.
        </p>
        <MenloPhraseChart groups={brandedLanguage} groupLabels={GROUP_LABELS} />
      </section>

      {/* Act 2 — idealism by era */}
      <section className="space-y-4">
        <SectionHeading
          kicker="Act 2 · The megaphone"
          title="Idealism that never collapsed"
        />
        <p className="max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
          {idealism.note} Against the careers-page cohort, the contrast is the point:
          Menlo holds and rises while the industry&apos;s idealism peaks and falls away.
        </p>
        <CompareChart
          series={idealismSeries}
          axisName="idealism"
          events={chartEvents}
        />
      </section>

      {/* Act 3 — the echo */}
      <section className="space-y-4">
        <SectionHeading
          kicker="Act 3 · The echo that never came"
          title="How Menlo counts its “impact”"
        />
        <p className="max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
          Every impact claim in the 374-chunk firm corpus, by what it actually counts.
          The denominator is people who came to <em>look</em> — never workplaces that
          rebuilt on the model.
        </p>
        <div className="max-w-2xl">
          <MenloAuditChart data={auditData} />
        </div>
        <p className="max-w-prose rounded bg-rose-50 p-3 text-sm text-rose-900 dark:bg-rose-950/40 dark:text-rose-200">
          <strong>0 credible named adopters.</strong> {impactAudit.finding}
        </p>
        <p className="max-w-prose text-xs italic text-neutral-500">
          {impactAudit.guardrail}
        </p>

        {outsiderView.length > 0 && (
          <div className="space-y-2 pt-2">
            <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
              The outside view (Hacker News) — admired rarity, not template
            </p>
            <ul className="space-y-2">
              {outsiderView.map((q, i) => (
                <li
                  key={i}
                  className="max-w-prose border-l-2 border-neutral-200 pl-3 text-sm text-neutral-600 dark:border-neutral-700 dark:text-neutral-400"
                >
                  <span className="mr-1 text-xs tabular-nums text-neutral-400">
                    {q.year}
                  </span>
                  {q.text}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      {/* Events */}
      <section className="space-y-3">
        <SectionHeading kicker="Timeline" title="Datable events" />
        <ul className="space-y-2">
          {events.map((ev, i) => (
            <li key={i} className="flex gap-3 text-sm">
              <span className="w-20 shrink-0 tabular-nums text-neutral-500">
                {ev.date}
              </span>
              <span className="text-neutral-700 dark:text-neutral-300">
                {ev.label}
                <span className="ml-2 rounded bg-neutral-100 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-neutral-500 dark:bg-neutral-800">
                  {ev.kind}
                </span>
              </span>
            </li>
          ))}
        </ul>
        {annotations.map((a, i) => (
          <p key={i} className="max-w-prose text-xs italic text-neutral-500">
            {a.label}
          </p>
        ))}
      </section>
    </div>
  );
}
