import type { StoryPeakPresent } from "@/lib/storyTypes";

interface Props {
  items: StoryPeakPresent[];
}

function QuoteBlock({
  label,
  year,
  zscore,
  quote,
}: {
  label: string;
  year: number;
  zscore: number;
  quote: { text: string; heading?: string } | null;
}) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
        {label}{" "}
        <span className="font-mono normal-case">
          ({year}, {zscore >= 0 ? "+" : ""}
          {zscore.toFixed(2)}σ)
        </span>
      </p>
      {quote ? (
        <>
          <p className="mt-2 text-sm leading-relaxed text-neutral-800 dark:text-neutral-200">
            &ldquo;{quote.text}&rdquo;
          </p>
          {quote.heading && (
            <p className="mt-1 font-mono text-xs text-neutral-400">{quote.heading}</p>
          )}
        </>
      ) : (
        <p className="mt-2 text-sm text-neutral-500">No evidence quote for this year.</p>
      )}
    </div>
  );
}

export default function StoryPeakPresent({ items }: Props) {
  const visible = items.filter(
    (item) => item.peakQuote || item.latestQuote
  );
  if (!visible.length) return null;

  return (
    <div className="space-y-8">
      {visible.map((item) => (
        <div
          key={item.company}
          className="rounded-lg border border-neutral-200 p-5 dark:border-neutral-800"
        >
          <h3 className="font-medium text-neutral-900 dark:text-neutral-100">
            {item.displayName}
          </h3>
          <div className="mt-4 grid gap-6 md:grid-cols-2">
            <QuoteBlock
              label="Peak idealism"
              year={item.peakYear}
              zscore={item.peakZscore}
              quote={item.peakQuote}
            />
            <QuoteBlock
              label="Most recent"
              year={item.latestYear}
              zscore={item.latestZscore}
              quote={item.latestQuote}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
