// Shared presentational block: Netflix deck-quote cards. Used by NetflixStoryExplorer
// (story page) and the essay (via viz/DeckQuotes.astro) — single source of truth.

export interface DeckQuote {
  label: string;
  text: string;
}

export default function DeckQuotes({ quotes }: { quotes: DeckQuote[] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {quotes.map((q) => {
        const caveat = q.label.toLowerCase().includes("caveat");
        return (
          <div
            key={q.label}
            className={`rounded-lg border p-4 ${
              caveat
                ? "border-amber-300 bg-amber-50 dark:border-amber-700/60 dark:bg-amber-950/30"
                : "border-neutral-200 dark:border-neutral-800"
            }`}
          >
            <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
              {q.label}
            </p>
            <p className="mt-1 text-sm text-neutral-700 dark:text-neutral-300">
              &ldquo;{q.text}&rdquo;
            </p>
          </div>
        );
      })}
    </div>
  );
}
