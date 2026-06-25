import Link from "next/link";
import { notFound } from "next/navigation";
import ValuesAsIpChart from "@/components/ValuesAsIpChart";
import { loadCanonStory, type CanonQuote } from "@/lib/canonStory";

const FRAMING = [
  "Codifying a culture into intellectual property — a trademarked \"Way,\" a founder-authored creed, a controlled commons — is the move available to leaders once the conditions that made the values real have receded. The canon is durable in a way those conditions were not, so it persists, frozen, while practice drifts beneath it.",
  "This view tracks Automattic's firm-register language on the mission ←→ rights axis. Each chunk is scored by where it sits between mission language (\"democratize publishing,\" giving everyone a voice) and rights language (protecting marks, infringement, licensing, consistent enforcement). The codified canon is plotted apart from everything else the firm published.",
  "The Pathway-B prediction: the canon barely moves — it stays near the mission pole — while the surrounding conduct language erupts toward rights and enforcement under stress. The same frozen values, turned into an asset to wield.",
];

function QuoteList({ title, quotes, accent }: { title: string; quotes: CanonQuote[]; accent: string }) {
  return (
    <div>
      <h3 className="text-sm font-medium uppercase tracking-wide text-neutral-500">{title}</h3>
      <ul className="mt-3 space-y-3">
        {quotes.map((q, i) => (
          <li key={i} className={`border-l-2 ${accent} pl-3`}>
            <p className="text-sm text-neutral-700 dark:text-neutral-300">“{q.text}”</p>
            <p className="mt-1 text-xs text-neutral-400">
              {q.year}
              {q.heading ? ` · ${q.heading}` : ""} · {q.score.toFixed(3)}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default async function ValuesAsIpStoryPage() {
  const data = await loadCanonStory();
  if (!data || !data.cases.length) notFound();

  const story = data.cases[0]; // Automattic anchor (Pathway B)

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-12">
      <Link
        href="/"
        className="text-sm text-neutral-500 transition-colors hover:text-neutral-800 dark:hover:text-neutral-200"
      >
        &larr; Stories
      </Link>
      <h1 className="mt-4 text-3xl font-semibold tracking-tight">{data.title}</h1>
      <p className="mt-2 text-sm text-neutral-500">{story.displayName} · Pathway B (weaponization)</p>

      <div className="mt-8 space-y-4">
        {FRAMING.map((p, i) => (
          <p key={i} className="max-w-prose text-neutral-600 dark:text-neutral-400">
            {p}
          </p>
        ))}
      </div>

      <div className="mt-10">
        <ValuesAsIpChart data={story} poleHigh={data.poleHigh} poleLow={data.poleLow} />
      </div>

      {story.events[0]?.description && (
        <p className="mt-4 max-w-prose text-sm text-neutral-500">
          <span className="font-medium text-amber-600 dark:text-amber-400">{story.events[0].label}.</span>{" "}
          {story.events[0].description}
        </p>
      )}

      <div className="mt-12 grid gap-8 sm:grid-cols-2">
        <QuoteList
          title="Canon at the mission pole"
          quotes={story.missionQuotes}
          accent="border-blue-400"
        />
        <QuoteList
          title="Conduct at the rights pole"
          quotes={story.rightsQuotes}
          accent="border-orange-400"
        />
      </div>

      <p className="mt-10 max-w-prose text-xs text-neutral-400">
        Firm-register chunks only (worker testimony excluded to avoid the cross-register confound).
        Hollow points mark thin years with few chunks; the canon corpus is small by design, so read
        its line as a flat reference, not a precise trajectory.
      </p>
    </main>
  );
}
