"use client";

import NetflixConceptTree from "@/components/NetflixConceptTree";
import NetflixEvolutionStrip from "@/components/NetflixEvolutionStrip";
import NetflixObjectivityMatrix from "@/components/NetflixObjectivityMatrix";
import AuditBarChart, { type BarDatum } from "@/components/AuditBarChart";
import DeckQuotes from "@/components/DeckQuotes";
import CoinbaseDiff from "@/components/CoinbaseDiff";
import ImplicitExplicitTable from "@/components/ImplicitExplicitTable";
import type { NetflixStory } from "@/lib/netflixStory";

function SectionHeading({ kicker, title }: { kicker: string; title: string }) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-widest text-[#e50914]">
        {kicker}
      </p>
      <h2 className="mt-1 text-xl font-semibold tracking-tight">{title}</h2>
    </div>
  );
}

export default function NetflixStoryExplorer({ data }: { data: NetflixStory }) {
  const { deckQuotes, propagation, objectivity, objectivityMatrix, implicitExplicit, netflixEvolution } = data;

  const auditData: BarDatum[] = [
    { label: "Claims objective merit", value: objectivity.claim, isTest: false },
    { label: "Defines an actual metric", value: objectivity.metricCredible, isTest: true },
  ];

  return (
    <div className="space-y-14">
      <p className="max-w-prose border-l-2 border-[#e50914] pl-4 text-lg text-neutral-700 dark:text-neutral-300">
        {data.thesis}
      </p>

      {/* Act 1 — the deck */}
      <section className="space-y-4">
        <SectionHeading kicker="Act 1 · The deck" title="What Netflix codified (2009)" />
        <p className="max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
          The most-cited culture document in Silicon Valley defined a performance-filter
          culture in unusually blunt terms — and defined &ldquo;performance&rdquo; with no
          metric at all.
        </p>
        <DeckQuotes quotes={deckQuotes} />
      </section>

      {/* Act 2 — the spread */}
      <section className="space-y-5">
        <SectionHeading kicker="Act 2 · The spread" title="Narrow lift, broad convergence" />
        <p className="max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
          What actually traveled — sorted by how Netflix-distinctive it is. The harsh
          mechanics stayed home; one company copied the bluntest formula; the rest is
          industry convergence that was never Netflix&apos;s to begin with.
        </p>
        <NetflixConceptTree concepts={propagation.concepts} />

        {/* Coinbase one-word diff */}
        <CoinbaseDiff />

        {/* Netflix walked it back */}
        <div className="space-y-3 pt-2">
          <h3 className="text-sm font-semibold">Netflix invented it — and softened it</h3>
          <p className="max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
            {netflixEvolution.headline}
          </p>
          <NetflixEvolutionStrip years={netflixEvolution.years} rows={netflixEvolution.rows} />
        </div>
        <p className="max-w-prose text-xs text-neutral-500">{propagation.note}</p>
      </section>

      {/* Act 3 — the false scoreboard */}
      <section className="space-y-5">
        <SectionHeading kicker="Act 3 · The false scoreboard" title="Borrowed objectivity, no score" />
        <p className="max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
          Across {objectivity.scanned.toLocaleString()} culture chunks, the language claims
          objective performance but never defines how it&apos;s measured.
        </p>
        <div className="max-w-2xl">
          <AuditBarChart data={auditData} />
        </div>

        <NetflixObjectivityMatrix rows={objectivityMatrix} />

        <p className="max-w-prose rounded bg-rose-50 p-3 text-sm text-rose-900 dark:bg-rose-950/40 dark:text-rose-200">
          {objectivity.smokingGun}
        </p>

        {/* implicit <-> explicit */}
        <div className="space-y-2 pt-2">
          <h3 className="text-sm font-semibold">
            The soft language does the same work
          </h3>
          <p className="max-w-prose text-xs text-neutral-500">
            Companies didn&apos;t copy &ldquo;keeper test,&rdquo; but the vaguer phrases
            make the same subjective cut while claiming objectivity (interpretation).
          </p>
          <ImplicitExplicitTable rows={implicitExplicit} />
        </div>

        <p className="max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
          {objectivity.finding} The sports metaphor borrows objectivity&apos;s aura without
          its scoreboard — and the discretion that fills the gap is where bias enters.
          Netflix&apos;s own deck even concedes the analogy is &ldquo;good, but
          imperfect.&rdquo;
        </p>
        <p className="max-w-prose text-xs italic text-neutral-500">
          Measures self-presentation and the missing metric — not bias itself, which is the
          interpretive thesis (see docs). Vocabulary adoption ≠ running the keeper test;
          small N.
        </p>
      </section>
    </div>
  );
}
