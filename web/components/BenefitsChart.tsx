import type { BenefitsCategory } from "@/lib/benefitsStory";

const W = 240;
const H = 56;
const PAD = 4;

function Spark({ cat, years, yMax }: { cat: BenefitsCategory; years: number[]; yMax: number }) {
  const y0 = years[0];
  const y1 = years[years.length - 1];
  const span = y1 - y0 || 1;
  const pts = cat.series.map((s) => {
    const x = PAD + ((s.year - y0) / span) * (W - 2 * PAD);
    const y = PAD + (H - 2 * PAD) * (1 - s.smoothed / yMax);
    return { ...s, x, y };
  });
  const path = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
  const color = "#0ea5e9";
  const last = pts[pts.length - 1];
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" preserveAspectRatio="none" aria-hidden>
      <path d={path} fill="none" stroke={color} strokeWidth={2} />
      {pts.map((p) => (
        <circle key={p.year} cx={p.x} cy={p.y} r={2} fill={color} fillOpacity={p.count ? 0.9 : 0.2}>
          <title>{`${p.year}: ${(p.share * 100).toFixed(0)}% of postings (${p.count} chunks)`}</title>
        </circle>
      ))}
      {last && <circle cx={last.x} cy={last.y} r={3} fill={color} />}
    </svg>
  );
}

export default function BenefitsChart({
  categories,
  years,
}: {
  categories: BenefitsCategory[];
  years: number[];
}) {
  const yMax = Math.max(
    ...categories.flatMap((c) => c.series.map((s) => s.smoothed)),
    0.01
  );
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {categories.map((c) => (
        <div key={c.id} className="rounded-lg border border-neutral-200 p-3 dark:border-neutral-800">
          <div className="flex items-baseline justify-between gap-2">
            <span className="text-sm font-medium">{c.label}</span>
          </div>
          <div className="mt-1">
            <Spark cat={c} years={years} yMax={yMax} />
          </div>
          <p className="mt-1 text-[11px] text-neutral-500">
            peak {c.peakYear} · {c.total} mentions
          </p>
        </div>
      ))}
    </div>
  );
}
