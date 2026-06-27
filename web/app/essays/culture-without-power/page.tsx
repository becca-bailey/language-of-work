import Link from "next/link";
import { notFound } from "next/navigation";
import NetflixConceptTree from "@/components/NetflixConceptTree";
import NetflixEvolutionStrip from "@/components/NetflixEvolutionStrip";
import NetflixObjectivityMatrix from "@/components/NetflixObjectivityMatrix";
import AuditBarChart, { type BarDatum } from "@/components/AuditBarChart";
import PowerCultureChart from "@/components/PowerCultureChart";
import { loadNetflixStory } from "@/lib/netflixStory";
import { loadPowerStory } from "@/lib/powerStory";

// Working scaffold for the synthesis essay. Outline notes (status: draft|todo) are
// placeholders to be replaced with prose; data-viz and quotes are wired live and
// interspersed at their anchor points (viz ids resolved in renderViz below).

type Sec = { h: string; status: "draft" | "todo"; notes: string[]; viz?: string };
type Part = { n: string; title: string; secs: Sec[] };

const PARTS: Part[] = [
  {
    n: "I",
    title: "Setup — the problem & the mythology",
    secs: [
      { h: "The sports metaphor that never measured", status: "draft", notes: [
        "Personal frame: DBC empathy work vs. Netflix performance culture (2013).",
        "The promise: metrics, objectivity, fairness through transparency.",
        "The gap: the sports metaphor assumes consistent measurement; knowledge work has none.",
        "Hook: Netflix was honest in ways that made it seem trustworthy — and that honesty hid a deeper problem.",
      ] },
      { h: "Why the sports metaphor fails (silently)", status: "draft", notes: [
        "How sports measurement works: same court, same hoop, same rules, same scoreboard.",
        "Why knowledge work is incomparable: different problems, contexts, no shared metric.",
        "Implication: if you can't measure performance, power decides what counts.",
      ] },
      { h: "The gap: claims without metrics", status: "draft", notes: [
        "Netflix deck's explicit numbers (2x, 10x, 'adequate performance gets severance').",
        "Netflix deck's explicit refusal: 'no bell curves, no rankings, no quotas.'",
        "The keeper test as the actual mechanism: subjective judgment disguised as evaluation.",
        "Sleight of hand: borrows objectivity's aura without its mechanism.",
      ] },
      { h: "When culture becomes the tool", status: "draft", notes: [
        "Two models: protective culture (DBC, empathy) vs. filtering culture (Netflix, keeper test).",
        "Both assume culture can solve the problem of unmeasurable standards.",
        "Both miss the real problem: power uses culture language to hide subjective decisions.",
      ] },
      { h: "The real question: why power wins", status: "draft", notes: [
        "Personal story: husband's paternity leave → 'performance' becomes 'availability.'",
        "When standards are unmeasurable, whoever has power decides.",
        "Culture work makes exclusionary decisions sound neutral.",
        "The question the essay answers: why does power choose control over profit?",
      ] },
      { h: "What Netflix actually codified", status: "draft", notes: [
        "Internal consistency: transparent about the keeper test.",
        "Hidden mechanism: who decides 'adequate'? who is 'we'?",
        "The model that spread: honest-but-incomplete — let others keep power while hiding it.",
      ] },
      { h: "The pattern: from intention to mechanism", status: "draft", notes: [
        "Good intentions (DBC empathy, Netflix transparency) → structural limits → power logic.",
        "What the data shows: harsh mechanics stayed Netflix-only; soft versions spread.",
      ] },
      { h: "What this essay does / a note on standing", status: "draft", notes: [
        "Map what Netflix said; track what spread; show the objectivity gap; connect to power.",
        "Standing: you benefited from meritocracy mythology, and it still failed you. Good intentions ≠ good structures.",
      ] },
    ],
  },
  {
    n: "II",
    title: "The Netflix deck — what it actually said",
    secs: [
      { h: "2.1 The 2009 moment: transparency as a selling point", status: "todo", notes: [
        "Context: post-dot-com, streaming vs. Blockbuster, Netflix scaling.",
        "2001 origin: the layoff paradox (cut 1/3, team worked better).",
        "Why influential: Sandberg's endorsement + SlideShare virality (~15M views).",
        "What made it different: blunt about firing, explicit about metrics.",
      ], viz: "deckQuotes" },
      { h: "2.2 The seven principles (decoded)", status: "todo", notes: [
        "For each: what it claims vs. what it hides.",
        "Values; high performance (2x/10x); freedom & responsibility; context not control;",
        "highly aligned / loosely coupled; top-of-market pay; promotions ('self-improving').",
      ] },
      { h: "2.3 The keeper test: where subjectivity hides", status: "todo", notes: [
        "'Would I fight to keep this person?' — sounds objective, is gut preference.",
        "Filters for similarity to the judge (Schneider's ASA model); homogeneity reproduces itself.",
        "Netflix refuses to rank, then relies entirely on subjective judgment.",
      ] },
      { h: "2.4 The severance promise: generosity as exit strategy", status: "todo", notes: [
        "'Adequate performance gets a generous severance package' — a one-way valve.",
        "Assumption: non-keepers are interchangeable, replaceable.",
        "Stayed Netflix-only in public — too brutal to advertise; Coinbase adopted it verbatim in 2024.",
      ] },
      { h: "2.5 The imperfect admission: the slide Netflix buried", status: "todo", notes: [
        "Netflix's own slide: 'Pro sports team metaphor is good, but imperfect.'",
        "Acknowledges the analogy breaks down — then doubles down anyway.",
      ], viz: "evolution" },
    ],
  },
  {
    n: "III",
    title: "The spread — what propagated & what didn't",
    secs: [
      { h: "3.1 The propagation question", status: "todo", notes: [
        "Hypothesis: harsh mechanics stayed Netflix-only; soft language became ubiquitous.",
        "Method: semantic matching (≥0.62) + verbatim regex over 9 key concepts. Self-presentation, not practice.",
      ], viz: "conceptTree" },
      { h: "3.2 What stayed Netflix-only (the harsh mechanics)", status: "todo", notes: [
        "Keeper test; 'adequate → severance'; 'team, not a family'; 'high performer ≫ average.'",
        "Too explicit about manager discretion — companies kept the logic, changed the language.",
      ] },
      { h: "3.3 What spread broadly (but may not be Netflix-derived)", status: "todo", notes: [
        "'Raise the bar' (Amazon origin), 'hire only the best,' 'high expectations,' 'judged by outcomes.'",
        "Convergent, not traceable to Netflix; same logic, softer phrasing.",
      ] },
      { h: "3.4 The Coinbase exception: Netflix's one true disciple", status: "todo", notes: [
        "Coinbase 2024: 'Unremarkable performance gets a generous severance package' (0.86, one-word edit).",
        "Only company to print the formula — and it did so the year Netflix dropped it.",
      ], viz: "coinbaseDiff" },
      { h: "3.5 What this pattern means", status: "todo", notes: [
        "Netflix authored the canonical language; harsh mechanics stayed isolated; the ethos spread by convergence.",
        "Soft language hides the subjectivity Netflix made visible.",
      ] },
    ],
  },
  {
    n: "IV",
    title: "The objectivity audit — claims vs. metrics",
    secs: [
      { h: "4.1–4.2 Claims of objectivity vs. defined metrics", status: "todo", notes: [
        "~7% of culture language makes objective performance claims; 0% define an actual metric.",
        "Netflix: 'no bell curves or rankings or quotas.' Evaluation is entirely discretionary.",
      ], viz: "auditBar" },
      { h: "4.3 The keeper test as the real mechanism", status: "todo", notes: [
        "Actual mechanism: manager's gut preference, disguised as merit.",
        "Biased toward the similar; against the different, the obligated, the challenging. No appeal.",
      ], viz: "objectivityMatrix" },
      { h: "4.4 How soft language does the same work", status: "todo", notes: [
        "'Raise the bar' / 'high expectations' / 'judged by outcomes' — claim objectivity, define nothing.",
      ], viz: "implicitExplicit" },
      { h: "4.5 The entry point for bias", status: "todo", notes: [
        "Unmeasurable standards → judgment fills the gap (Rivera on culture fit; Castilla & Benard, the meritocracy paradox).",
        "Gendered, racial, age, and parenting bias enter as 'high standards.'",
      ] },
    ],
  },
  {
    n: "V",
    title: "Dev Bootcamp & the limits of protective culture",
    secs: [
      { h: "5.1–5.2 The empathy experiment, and what it got right", status: "todo", notes: [
        "DBC 2012–2017: Engineering Empathy (~20% of program) — microaggressions, stereotype threat, allyship.",
        "Real community, real skills, a genuine alternative to the meritocracy narrative.",
      ] },
      { h: "5.3–5.4 Why protective culture still failed (the DBC paradox)", status: "todo", notes: [
        "Couldn't make graduates competitive in a system that doesn't measure fairness.",
        "You can teach empathy to students; you can't teach it to a power structure.",
        "Closure was financial; the model's failure was structural.",
      ] },
      { h: "5.5 Why protective culture lost to performance culture", status: "todo", notes: [
        "Netflix won: honest, clear (even if subjective), gave permission to cut in the name of performance.",
        "Culture work promised what the structure couldn't deliver; made power invisible without changing it.",
      ] },
    ],
  },
  {
    n: "VI",
    title: "Why power wins — the structural argument",
    secs: [
      { h: "6.1–6.2 The question, and what your husband's case shows", status: "todo", notes: [
        "Why choose control over profit? Why unmeasurable standards when measurable ones are more defensible?",
        "High performer + parental leave → 'performance' redefined as availability; power redefined his value.",
      ] },
      { h: "6.3–6.4 The unmeasurable standard as a tool of power", status: "todo", notes: [
        "Measurable standards can be appealed; unmeasurable ones can't. Invisible power = unaccountable power.",
        "Culture language sounds descriptive but is prescriptive — it decides who belongs.",
      ], viz: "powerChart" },
      { h: "6.5 The convergence: why everyone adopted this logic", status: "todo", notes: [
        "Unmeasurable performance → cut without legal risk, exercise power without oversight, look progressive while excluding.",
        "Spread because it worked for companies with power — not because Netflix forced it.",
      ] },
      { h: "6.6–6.7 The post-2020 shift, and the logical endpoint", status: "todo", notes: [
        "The mask drops: Musk ('I'm just better'), Thiel, 'talent density,' Coinbase's verbatim copy.",
        "Not a conspiracy — a structural endpoint: more power → less need for pretense → explicit exclusion.",
        "Tie back to the data: DEI tracks worker power and recedes; performance never needed leverage.",
      ] },
    ],
  },
  {
    n: "VII",
    title: "Synthesis — what this means",
    secs: [
      { h: "7.1–7.2 The sports metaphor as a structural lie; culture as the tool of power", status: "todo", notes: [
        "Borrowed sports language creates a false impression of objectivity; subjective judgment hides as merit.",
        "Excluded people blame themselves; included people believe in meritocracy; the system seems inevitable.",
      ] },
      { h: "7.3 Why 'culture add' changed nothing", status: "todo", notes: [
        "Renamed 'fit' → 'add' (~2016); vocabulary shifted, mechanism didn't. More insidious because it sounds inclusive.",
      ] },
      { h: "7.4–7.6 The unasked question; what power optimizes for; the question for you", status: "todo", notes: [
        "A measurable system would be better for workers (maybe for companies) — but distributes power more widely.",
        "Power optimizes for control, homogeneity, predictability, judgment without accountability.",
        "Reader prompt: find the unmeasurable standards — they tell you who has power.",
      ] },
    ],
  },
  {
    n: "VIII",
    title: "Epilogue — personal reflection",
    secs: [
      { h: "8.1–8.3 What I understand now / wish I'd known / what comes after", status: "todo", notes: [
        "I was never the problem; the system was never meritocratic.",
        "Good intentions don't fix bad structures; 'we have no metrics' is the moment power enters.",
        "This is a diagnosis, not a solution — but naming the mechanism lets you choose whether to participate.",
      ] },
    ],
  },
];

export default async function CultureWithoutPowerEssay() {
  const netflix = await loadNetflixStory();
  const power = await loadPowerStory();
  if (!netflix && !power) notFound();

  const auditData: BarDatum[] = netflix
    ? [
        { label: "Claims objective merit", value: netflix.objectivity.claim, isTest: false },
        { label: "Defines an actual metric", value: netflix.objectivity.metricCredible, isTest: true },
      ]
    : [];

  function renderViz(id: string) {
    switch (id) {
      case "deckQuotes":
        return netflix ? (
          <div className="my-6 grid gap-3 sm:grid-cols-2">
            {netflix.deckQuotes.map((q) => (
              <div key={q.label} className="rounded-lg border border-neutral-200 p-4 dark:border-neutral-800">
                <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">{q.label}</p>
                <p className="mt-1 text-sm text-neutral-700 dark:text-neutral-300">&ldquo;{q.text}&rdquo;</p>
              </div>
            ))}
          </div>
        ) : null;
      case "conceptTree":
        return netflix ? <div className="my-6"><NetflixConceptTree concepts={netflix.propagation.concepts} /></div> : null;
      case "evolution":
        return netflix ? (
          <div className="my-6">
            <p className="mb-2 text-sm text-neutral-600 dark:text-neutral-400">{netflix.netflixEvolution.headline}</p>
            <NetflixEvolutionStrip years={netflix.netflixEvolution.years} rows={netflix.netflixEvolution.rows} />
          </div>
        ) : null;
      case "coinbaseDiff":
        return (
          <div className="my-6 rounded-lg border border-amber-300 bg-amber-50 p-4 dark:border-amber-700/60 dark:bg-amber-950/30">
            <p className="text-xs font-medium uppercase tracking-wide text-amber-700 dark:text-amber-500">
              The one verbatim lift
            </p>
            <div className="mt-2 space-y-1 font-mono text-sm">
              <p>
                <span className="text-neutral-500">Netflix 2009: </span>
                <span className="rounded bg-rose-200/60 px-1 dark:bg-rose-900/50">adequate</span> performance gets a
                generous severance package
              </p>
              <p>
                <span className="text-neutral-500">Coinbase 2024: </span>
                <span className="rounded bg-amber-200/70 px-1 dark:bg-amber-800/50">unremarkable</span> performance gets
                a generous severance package
              </p>
            </div>
            <p className="mt-2 text-xs text-amber-900 dark:text-amber-200">
              A one-word edit (0.86 similarity) — the only company to print the formula, in the year Netflix dropped it.
            </p>
          </div>
        );
      case "auditBar":
        return netflix ? <div className="my-6 max-w-2xl"><AuditBarChart data={auditData} /></div> : null;
      case "objectivityMatrix":
        return netflix ? <div className="my-6"><NetflixObjectivityMatrix rows={netflix.objectivityMatrix} /></div> : null;
      case "implicitExplicit":
        return netflix ? (
          <div className="my-6 overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b border-neutral-200 text-left text-xs uppercase tracking-wide text-neutral-500 dark:border-neutral-800">
                  <th className="py-2 pr-4 font-medium">Netflix, explicit</th>
                  <th className="py-2 font-medium">Industry, implicit</th>
                </tr>
              </thead>
              <tbody>
                {netflix.implicitExplicit.map((m) => (
                  <tr key={m.explicit} className="border-b border-neutral-100 dark:border-neutral-800/60">
                    <td className="py-2 pr-4 text-neutral-700 dark:text-neutral-300">{m.explicit}</td>
                    <td className="py-2 text-neutral-600 dark:text-neutral-400">{m.implicit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null;
      case "powerChart":
        return power ? <div className="my-6"><PowerCultureChart data={power} /></div> : null;
      default:
        return null;
    }
  }

  return (
    <main className="mx-auto w-full max-w-3xl flex-1 px-6 py-12">
      <Link
        href="/"
        className="text-sm text-neutral-500 transition-colors hover:text-neutral-800 dark:hover:text-neutral-200"
      >
        &larr; Home
      </Link>
      <h1 className="mt-4 text-4xl font-semibold tracking-tight">Culture Without Power</h1>
      <p className="mt-3 max-w-prose text-lg text-neutral-600 dark:text-neutral-400">
        The sports metaphor that never measured, the Netflix model that spread, and why — when
        performance can&rsquo;t be measured — power decides what counts.
      </p>
      <p className="mt-4 max-w-prose rounded border border-dashed border-neutral-300 bg-neutral-50 p-3 text-xs text-neutral-500 dark:border-neutral-700 dark:bg-neutral-900/40">
        Working draft. The italic notes under each heading are the outline, to be replaced with
        prose; the charts and quotes are live and will update with the data.
      </p>

      <article className="mt-10 space-y-12">
        {PARTS.map((part) => (
          <section key={part.n}>
            <p className="text-xs font-semibold uppercase tracking-widest text-rose-600 dark:text-rose-400">
              Part {part.n}
            </p>
            <h2 className="mt-1 text-2xl font-semibold tracking-tight">{part.title}</h2>
            <div className="mt-6 space-y-8">
              {part.secs.map((sec) => (
                <div key={sec.h}>
                  <h3 className="flex items-baseline gap-2 text-base font-medium">
                    {sec.h}
                    <span
                      className={`rounded px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide ${
                        sec.status === "draft"
                          ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300"
                          : "bg-neutral-100 text-neutral-500 dark:bg-neutral-800 dark:text-neutral-400"
                      }`}
                    >
                      {sec.status}
                    </span>
                  </h3>
                  <ul className="mt-2 space-y-1 border-l-2 border-neutral-200 pl-4 text-sm italic text-neutral-500 dark:border-neutral-700">
                    {sec.notes.map((note, i) => (
                      <li key={i}>{note}</li>
                    ))}
                  </ul>
                  {sec.viz ? renderViz(sec.viz) : null}
                </div>
              ))}
            </div>
          </section>
        ))}
      </article>
    </main>
  );
}
