import Link from "next/link";
import { notFound } from "next/navigation";
import PowerCultureChart from "@/components/PowerCultureChart";
import { loadPowerStory } from "@/lib/powerStory";

export default async function PowerStoryPage() {
  const data = await loadPowerStory();
  if (!data) notFound();

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-12">
      <Link
        href="/"
        className="text-sm text-neutral-500 transition-colors hover:text-neutral-800 dark:hover:text-neutral-200"
      >
        &larr; Stories
      </Link>
      <h1 className="mt-4 text-3xl font-semibold tracking-tight">{data.title}</h1>
      <p className="mt-2 max-w-prose text-lg text-neutral-600 dark:text-neutral-400">
        {data.subtitle}
      </p>
      <p className="mt-4 max-w-prose border-l-2 border-indigo-400 pl-4 text-sm text-neutral-700 dark:text-neutral-300">
        {data.thesis}
      </p>

      <div className="mt-10">
        <PowerCultureChart data={data} />
      </div>

      {/* power-shift cases */}
      <section className="mt-12 space-y-4">
        <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
          Power-shift cases — when control concentrates, culture hardens overnight
        </h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {data.cases.map((c) => (
            <div key={c.company} className="rounded-lg border border-neutral-200 p-4 dark:border-neutral-800">
              <p className="font-semibold">
                {c.company} <span className="font-normal text-neutral-400">· {c.date}</span>
              </p>
              <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">{c.shift}</p>
              <ul className="mt-2 space-y-1">
                {c.quotes.map((q, i) => (
                  <li key={i} className="border-l-2 border-rose-300 pl-2 text-sm italic text-neutral-700 dark:border-rose-700/60 dark:text-neutral-300">
                    &ldquo;{q}&rdquo;
                  </li>
                ))}
              </ul>
              <p className="mt-2 text-[11px] text-neutral-400">{c.source}</p>
            </div>
          ))}
        </div>
        <p className="max-w-prose text-xs italic text-neutral-500">
          Documented illustrations, not in the quantitative aggregate — the moment ownership
          or control concentrates (a buyout, a founder edict), the cultural apparatus
          (committees, political talk, &ldquo;paternalistic&rdquo; benefits) is the first thing cut.
        </p>
      </section>

      <div className="mt-12 max-w-prose space-y-2 text-xs text-neutral-500">
        <p>
          <strong>How to read it.</strong> Across {data.companies.length} companies, two
          signals rise and fall with the worker-power band: <em>idealism</em> (the
          industry-optimism barometer) and <em>DEI</em> (the worker-oriented intervention) —
          both ~+0.75 correlation with the quits rate (smoothed). <em>Performance/intensity</em>{" "}
          stays flat near the top regardless: it serves whoever can hire and fire, so it
          needs no leverage to survive. Idealism co-moves not because it serves workers
          (workers are cynical of &ldquo;change the world&rdquo; talk) but because lofty talk
          and worker leverage both ride the same boom.
        </p>
        <p>
          <strong>Honesty.</strong> {data.companiesNote} {data.power.caveat} This is
          co-movement and selection, not causation; the &ldquo;who benefits&rdquo; labels
          are interpretation. At six companies the aggregate was too noisy to read DEI; the
          co-movement only firmed up at eleven — so treat it as suggestive, not decisive.
        </p>
      </div>
    </main>
  );
}
