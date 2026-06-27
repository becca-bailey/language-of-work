// Shared presentational block: the Netflix→Coinbase one-word verbatim lift. Static
// content. Used by NetflixStoryExplorer (story page) and the essay (via viz/CoinbaseDiff.astro).

export default function CoinbaseDiff() {
  return (
    <div className="rounded-lg border border-amber-300 bg-amber-50 p-4 dark:border-amber-700/60 dark:bg-amber-950/30">
      <p className="text-xs font-medium uppercase tracking-wide text-amber-700 dark:text-amber-500">
        The one verbatim lift
      </p>
      <div className="mt-2 space-y-1 font-mono text-sm">
        <p>
          <span className="text-neutral-500">Netflix 2009: </span>
          <span className="rounded bg-rose-200/60 px-1 dark:bg-rose-900/50">adequate</span>{" "}
          performance gets a generous severance package
        </p>
        <p>
          <span className="text-neutral-500">Coinbase 2024: </span>
          <span className="rounded bg-amber-200/70 px-1 dark:bg-amber-800/50">unremarkable</span>{" "}
          performance gets a generous severance package
        </p>
      </div>
      <p className="mt-2 text-xs text-amber-900 dark:text-amber-200">
        A one-word edit (0.86 similarity) — the only company to print the formula. And it
        printed it in 2024, the year Netflix itself had dropped it.
      </p>
    </div>
  );
}
