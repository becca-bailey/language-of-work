import type { NetflixConcept } from "@/lib/netflixStory";

const TIERS: { id: NetflixConcept["tier"]; title: string; blurb: string; accent: string }[] = [
  {
    id: "lift",
    title: "The one that propagated",
    blurb: "A distinctively-Netflix formula another company printed nearly verbatim.",
    accent: "border-amber-400",
  },
  {
    id: "netflix_only",
    title: "Stayed Netflix-only",
    blurb: "The harshest mechanics — adopted in spirit across the industry, but rarely put in writing on anyone else's page.",
    accent: "border-[#e50914]",
  },
  {
    id: "generic",
    title: "Convergent industry language (not Netflix-derived)",
    blurb: '"Raise the bar" is Amazon\'s Leadership Principle; "best and brightest" predates everyone. Multiple companies used these independently — convergence, not propagation.',
    accent: "border-neutral-300 dark:border-neutral-700",
  },
];

export default function NetflixConceptTree({ concepts }: { concepts: NetflixConcept[] }) {
  return (
    <div className="space-y-6">
      {TIERS.map((tier) => {
        const items = concepts.filter((c) => c.tier === tier.id);
        if (!items.length) return null;
        return (
          <div key={tier.id} className={`border-l-2 ${tier.accent} pl-4`}>
            <h3 className="text-sm font-semibold">{tier.title}</h3>
            <p className="mt-0.5 max-w-prose text-xs text-neutral-500">{tier.blurb}</p>
            <ul className="mt-3 space-y-2">
              {items.map((c) => (
                <li key={c.id} className="text-sm">
                  <span className="font-medium text-neutral-800 dark:text-neutral-200">
                    {c.label}
                  </span>
                  {tier.id === "lift" && c.adopters[0] && (
                    <span className="text-neutral-600 dark:text-neutral-400">
                      {" "}— Netflix {c.originYear} →{" "}
                      <span className="font-medium text-amber-700 dark:text-amber-400">
                        {c.adopters[0].displayName} {c.adopters[0].year} (verbatim)
                      </span>
                    </span>
                  )}
                  {tier.id === "netflix_only" && (
                    <span className="text-neutral-500">
                      {" "}— Netflix {c.originYear ?? ""}
                      {c.adopters.length === 0
                        ? " · no other company in the corpus"
                        : " · " + c.adopters.map((a) => `${a.displayName} ${a.year}`).join(", ")}
                    </span>
                  )}
                  {tier.id === "generic" && (
                    <span className="text-neutral-500">
                      {" "}—{" "}
                      {c.adopters.length
                        ? c.adopters.map((a) => `${a.displayName} ${a.year}`).join(", ")
                        : "industry-wide"}
                      <span className="ml-1 rounded bg-neutral-100 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-neutral-500 dark:bg-neutral-800">
                        convergent
                      </span>
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        );
      })}
    </div>
  );
}
