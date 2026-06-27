import Link from "next/link";
import { notFound } from "next/navigation";
import { loadCultureFitStory } from "@/lib/cultureFitStory";

export default async function CultureFitPage() {
  const data = await loadCultureFitStory();
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
      <p className="mt-4 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
        {data.intro}
      </p>

      <div className="mt-10 space-y-6">
        {data.cards.map((c) => (
          <section
            key={c.id}
            className="rounded-lg border border-neutral-200 p-5 dark:border-neutral-800"
          >
            <h2 className="text-lg font-semibold tracking-tight">{c.displayName}</h2>
            <p className="mt-1 max-w-prose text-sm text-neutral-700 dark:text-neutral-300">
              {c.summary}
            </p>
            <ul className="mt-3 space-y-2">
              {c.quotes.map((q, i) => (
                <li
                  key={i}
                  className="border-l-2 border-neutral-200 pl-3 text-sm italic text-neutral-600 dark:border-neutral-700 dark:text-neutral-400"
                >
                  <span className="mr-1 not-italic tabular-nums text-xs text-neutral-400">
                    {q.year}
                  </span>
                  &ldquo;{q.text}&rdquo;
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>

      <p className="mt-8 max-w-prose text-xs italic text-neutral-500">{data.caveat}</p>
    </main>
  );
}
