import type { MaterialDEI } from "@/lib/benefitsStory";

const W = 640;
const H = 200;
const PAD_L = 36;
const PAD_R = 12;
const PAD_T = 12;
const PAD_B = 26;

export default function MaterialDEIChart({ data }: { data: MaterialDEI }) {
  const series = data.series;
  const years = series.map((s) => s.year);
  const y0 = years[0];
  const y1 = years[years.length - 1];
  const span = y1 - y0 || 1;
  const yMax = Math.max(...series.map((s) => s.share), 0.1); // floor 10% so a low flat line reads as low
  const x = (yr: number) => PAD_L + ((yr - y0) / span) * (W - PAD_L - PAD_R);
  const y = (share: number) => PAD_T + (H - PAD_T - PAD_B) * (1 - share / yMax);

  const pts = series.map((s) => ({ ...s, cx: x(s.year), cy: y(s.smoothed) }));
  const linePath = pts.map((p, i) => `${i === 0 ? "M" : "L"}${p.cx.toFixed(1)},${p.cy.toFixed(1)}`).join(" ");
  const areaPath = `${linePath} L${pts[pts.length - 1].cx.toFixed(1)},${y(0).toFixed(1)} L${pts[0].cx.toFixed(1)},${y(0).toFixed(1)} Z`;

  const gridShares = [0, yMax / 2, yMax];
  const tickYears = years.filter((yr) => yr % 3 === 0 || yr === y1);

  return (
    <div>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label={data.label}>
        {gridShares.map((g) => (
          <g key={g}>
            <line x1={PAD_L} x2={W - PAD_R} y1={y(g)} y2={y(g)} stroke="currentColor" className="text-neutral-200 dark:text-neutral-800" strokeWidth={1} />
            <text x={PAD_L - 6} y={y(g) + 3} textAnchor="end" className="fill-neutral-400 text-[9px]">
              {(g * 100).toFixed(0)}%
            </text>
          </g>
        ))}
        <path d={areaPath} fill="#a855f7" fillOpacity={0.1} />
        <path d={linePath} fill="none" stroke="#a855f7" strokeWidth={2} />
        {pts.map((p) => (
          <circle key={p.year} cx={p.cx} cy={p.cy} r={3} fill="#a855f7" fillOpacity={p.count ? 1 : 0.25}>
            <title>{`${p.year}: ${(p.share * 100).toFixed(1)}% of postings (${p.count})`}</title>
          </circle>
        ))}
        {tickYears.map((yr) => (
          <text key={yr} x={x(yr)} y={H - 8} textAnchor="middle" className="fill-neutral-400 text-[9px]">
            {`'${String(yr).slice(2)}`}
          </text>
        ))}
      </svg>
      <p className="mt-2 text-xs text-neutral-500">
        <span className="font-medium text-neutral-600 dark:text-neutral-400">What&apos;s in it:</span>{" "}
        {data.components
          .filter((c) => c.total > 0)
          .map((c) => `${c.label} (${c.total})`)
          .join(" · ")}
        {" — "}
        {data.total} postings total.
      </p>
    </div>
  );
}
