import type { NetflixEvolutionRow } from "@/lib/netflixStory";

interface Props {
  years: number[];
  rows: NetflixEvolutionRow[];
}

export default function NetflixEvolutionStrip({ years, rows }: Props) {
  const shown = years.filter((y) => y >= 2009);
  return (
    <figure className="w-full overflow-x-auto">
      <div
        className="grid items-center gap-y-1 text-[11px]"
        style={{
          gridTemplateColumns: `minmax(11rem, max-content) repeat(${shown.length}, 1fr)`,
        }}
      >
        {/* header row */}
        <div />
        {shown.map((y) => (
          <div key={y} className="text-center text-neutral-400">
            {y % 5 === 0 || y === shown[shown.length - 1] ? `'${String(y).slice(2)}` : ""}
          </div>
        ))}

        {rows.map((r) => {
          const set = new Set(r.present);
          return (
            <FragmentRow key={r.concept}>
              <div className="pr-2 text-neutral-700 dark:text-neutral-300">
                {r.concept}
                {r.retired && r.lastYear <= 2022 && (
                  <span className="ml-1 text-[10px] text-amber-600 dark:text-amber-500">
                    retired ’{String(r.lastYear).slice(2)}
                  </span>
                )}
              </div>
              {shown.map((y) => {
                const on = set.has(y);
                const isSeverance = r.retired && r.lastYear <= 2022;
                return (
                  <div key={y} className="flex justify-center">
                    <span
                      title={`${r.concept} · ${y}: ${on ? "present" : "absent"}`}
                      className={`block h-3 w-3 rounded-sm ${
                        on
                          ? isSeverance
                            ? "bg-amber-500"
                            : "bg-[#e50914]/80"
                          : "bg-neutral-200 dark:bg-neutral-800"
                      }`}
                    />
                  </div>
                );
              })}
            </FragmentRow>
          );
        })}
      </div>
      <figcaption className="mt-3 max-w-prose text-xs text-neutral-500">
        Netflix&apos;s own culture copy, concept by year (red = present; amber = the
        formula it later retired). &ldquo;Adequate → severance&rdquo; ran 2009–2022, then
        vanished from Netflix&apos;s ~2023 rewrite — the same line{" "}
        <span className="text-amber-700 dark:text-amber-400">Coinbase printed in 2024.</span>{" "}
        (2023 is a thin-capture gap, not a real disappearance — keeper-test and dream-team
        resume in 2024.)
      </figcaption>
    </figure>
  );
}

// react fragment that still participates in the parent grid
function FragmentRow({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
