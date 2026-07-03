"use client";

import { useMemo } from "react";
import { ParentSize } from "@visx/responsive";
import { scaleBand, scaleLinear } from "@visx/scale";
import { TooltipWithBounds, useTooltip } from "@visx/tooltip";
import { localPoint } from "@visx/event";
import { allYears, type StoryCompanySeries, type StoryEnvelopeQuote } from "@/lib/storyTypes";
import { DEI_REGISTER_COLORS as COLORS, DEI_REGISTER_TOKEN } from "@/lib/deiRegisters";
import { useThemeColors } from "@/lib/themeColors";

/** Active (pro-inclusion) registers stack upward; counter registers stack downward. */
const ACTIVE_REGISTERS = [
  "explicit_demographic",
  "structural_process",
  "aspirational_vague",
  "belonging_culture",
] as const;

const COUNTER_REGISTERS = ["meritocracy", "civilizational_mission"] as const;

const LABELS: Record<string, string> = {
  explicit_demographic: "explicit demographic",
  structural_process: "structural process",
  aspirational_vague: "aspirational vague",
  belonging_culture: "belonging culture",
  meritocracy: "meritocracy / anti-DEI",
  civilizational_mission: "civilizational mission",
};

const ROW_H = 96;
const MARGIN = { top: 4, right: 8, bottom: 20, left: 12 };

interface Props {
  companies: StoryCompanySeries[];
}

interface YearCell {
  year: number;
  captured: boolean; // page archived that year (nChunks > 0)
  hasDei: boolean; // any active/counter register present
  nChunks: number;
  shares: Record<string, number>;
  counterShares: Record<string, number>;
  inclusionQuote?: StoryEnvelopeQuote | null;
  counterQuote?: StoryEnvelopeQuote | null;
}

function cellsFor(company: StoryCompanySeries): Map<number, YearCell> {
  const cells = new Map<number, YearCell>();
  for (const y of company.years) {
    if (!y.registers) continue;
    const n = Math.max(y.nChunks, 1);
    const shares: Record<string, number> = {};
    for (const reg of ACTIVE_REGISTERS) shares[reg] = (y.registers?.[reg] ?? 0) / n;
    const counterShares: Record<string, number> = {};
    for (const reg of COUNTER_REGISTERS) counterShares[reg] = (y.registers?.[reg] ?? 0) / n;
    const hasDei =
      Object.values(shares).some((v) => v > 0) || Object.values(counterShares).some((v) => v > 0);
    cells.set(y.year, {
      year: y.year,
      captured: y.nChunks > 0,
      hasDei,
      nChunks: y.nChunks,
      shares,
      counterShares,
      // Label-aware quotes: the most salient active-register chunk (falling back
      // to the embedding argmax for pre-relabel data), and the stance-labeled
      // counter chunk — no counter quote at all when none was labeled that year.
      inclusionQuote: y.inclusionQuote ?? y.stanceMaxQuote,
      counterQuote: y.stanceCounterQuote,
    });
  }
  return cells;
}

type Tip = { cell: YearCell | null; year: number };

/** Border color for a tooltip quote — same hue as its register/stance in the legend. */
function quoteColor(q: StoryEnvelopeQuote, fillFor: (reg: string) => string): string | undefined {
  if (q.stance === "civilizational_mission") return fillFor("civilizational_mission");
  if (q.stance === "mission_focus_apolitical") return fillFor("meritocracy");
  if (q.register && (ACTIVE_REGISTERS as readonly string[]).includes(q.register)) return fillFor(q.register);
  return undefined;
}

// ---------------------------------------------------------------------------
// Data-driven narrative grouping. No company is hard-coded: each company's
// trajectory statistics decide its group, so new companies self-sort and the
// grouping tracks the data. Thresholds are the only editorial choice.
// ---------------------------------------------------------------------------
const PEAK_THRESHOLD = 0.25; // active share that counts as "really said it"
const RETREAT_RATIO = 0.5; // recent share below half of peak = retraction
const COUNTER_THRESHOLD = 0.05; // recent counter share that counts as counter-programming

interface Trajectory {
  peak: number;
  peakYear: number | null;
  recent: number; // mean active share, last 2 captured years
  recentCounter: number; // max counter share, last 3 captured years
}

function trajectoryFor(company: StoryCompanySeries): Trajectory {
  const cells = [...cellsFor(company).values()]
    .filter((c) => c.captured)
    .sort((a, b) => a.year - b.year);
  let peak = 0;
  let peakYear: number | null = null;
  for (const c of cells) {
    const active = Object.values(c.shares).reduce((a, b) => a + b, 0);
    if (active > peak) {
      peak = active;
      peakYear = c.year;
    }
  }
  const last2 = cells.slice(-2);
  const recent = last2.length
    ? last2.reduce((s, c) => s + Object.values(c.shares).reduce((a, b) => a + b, 0), 0) / last2.length
    : 0;
  const recentCounter = Math.max(
    0,
    ...cells.slice(-3).map((c) => Object.values(c.counterShares).reduce((a, b) => a + b, 0))
  );
  return { peak, peakYear, recent, recentCounter };
}

interface Group {
  id: string;
  title: string;
  note: string;
  companies: StoryCompanySeries[];
}

function groupCompanies(companies: StoryCompanySeries[]): Group[] {
  const t = new Map(companies.map((c) => [c.id, trajectoryFor(c)]));
  const groups: Group[] = [
    {
      id: "counter",
      title: "Counter-programmers",
      note: "Meaningful counter-programming (apolitical / civilizational framing) in recent years.",
      companies: [],
    },
    {
      id: "retracted",
      title: "Adopted, then retracted",
      note: `Active DEI share peaked above ${Math.round(PEAK_THRESHOLD * 100)}% and has since fallen to less than half its peak.`,
      companies: [],
    },
    {
      id: "steady",
      title: "Steady voices",
      note: "Substantial DEI language without a collapse.",
      companies: [],
    },
    {
      id: "quiet",
      title: "Quiet throughout",
      note: `Active DEI share never crossed ${Math.round(PEAK_THRESHOLD * 100)}%.`,
      companies: [],
    },
  ];
  for (const c of companies) {
    const s = t.get(c.id)!;
    if (s.recentCounter >= COUNTER_THRESHOLD) groups[0].companies.push(c);
    else if (s.peak >= PEAK_THRESHOLD && s.recent <= s.peak * RETREAT_RATIO) groups[1].companies.push(c);
    else if (s.peak >= PEAK_THRESHOLD) groups[2].companies.push(c);
    else groups[3].companies.push(c);
  }
  const by = (fn: (s: Trajectory) => number) => (a: StoryCompanySeries, b: StoryCompanySeries) =>
    fn(t.get(b.id)!) - fn(t.get(a.id)!);
  groups[0].companies.sort(by((s) => s.recentCounter));
  groups[1].companies.sort(by((s) => s.peak - s.recent)); // biggest retreat first
  groups[2].companies.sort(by((s) => s.peak));
  groups[3].companies.sort(by((s) => s.peak));
  return groups.filter((g) => g.companies.length > 0);
}

/** Aggregate anchor: mean active share across companies captured each year. */
function AggregateLine({ companies, years, width }: { companies: StoryCompanySeries[]; years: number[]; width: number }) {
  const H = 84;
  const M = { top: 8, right: 44, bottom: 18, left: MARGIN.left };
  const innerW = width - M.left - M.right;
  const innerH = H - M.top - M.bottom;
  const points = useMemo(() => {
    const cellsByCompany = companies.map((c) => cellsFor(c));
    return years
      .map((year, i) => {
        const shares: number[] = [];
        for (const cells of cellsByCompany) {
          const cell = cells.get(year);
          if (cell?.captured) shares.push(Object.values(cell.shares).reduce((a, b) => a + b, 0));
        }
        if (shares.length < 3) return null; // too few captures to mean anything
        return { i, year, mean: shares.reduce((a, b) => a + b, 0) / shares.length };
      })
      .filter((p): p is { i: number; year: number; mean: number } => p !== null);
  }, [companies, years]);

  if (innerW <= 0 || points.length < 2) return null;
  const maxMean = Math.max(0.15, ...points.map((p) => p.mean));
  const x = (i: number) => (i / Math.max(years.length - 1, 1)) * innerW;
  const y = (m: number) => innerH - (m / maxMean) * (innerH - 8);
  const path = points.map((p, idx) => `${idx === 0 ? "M" : "L"}${x(p.i).toFixed(1)},${y(p.mean).toFixed(1)}`).join(" ");
  const peak = points.reduce((a, b) => (b.mean > a.mean ? b : a));
  const last = points[points.length - 1];
  const pct = (m: number) => `${Math.round(m * 100)}%`;

  return (
    <div>
      <p className="text-[11px] font-medium text-neutral-600 dark:text-neutral-400">
        All companies — mean active-DEI share of careers-page language
      </p>
      <svg width={width} height={H} role="img" aria-label="Mean active DEI share across all companies by year">
        <g transform={`translate(${M.left},${M.top})`}>
          <line x1={0} x2={innerW} y1={innerH} y2={innerH} className="stroke-neutral-200 dark:stroke-neutral-800" />
          <path d={path} fill="none" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="stroke-neutral-500 dark:stroke-neutral-400" />
          {/* peak annotation */}
          <circle cx={x(peak.i)} cy={y(peak.mean)} r={3} className="fill-neutral-500 stroke-white dark:fill-neutral-400 dark:stroke-neutral-950" strokeWidth={2} />
          <text
            x={x(peak.i)}
            y={y(peak.mean) - 7}
            textAnchor={x(peak.i) < 24 ? "start" : x(peak.i) > innerW - 24 ? "end" : "middle"}
            className="fill-neutral-500 text-[10px] font-medium dark:fill-neutral-400"
          >
            {pct(peak.mean)} · {peak.year}
          </text>
          {/* endpoint marker + value */}
          {last.i !== peak.i && (
            <>
              <circle cx={x(last.i)} cy={y(last.mean)} r={3} className="fill-neutral-500 stroke-white dark:fill-neutral-400 dark:stroke-neutral-950" strokeWidth={2} />
              <text x={x(last.i) + 8} y={y(last.mean) + 3} className="fill-neutral-500 text-[10px] font-medium dark:fill-neutral-400">
                {pct(last.mean)}
              </text>
            </>
          )}
          {points
            .filter((p) => p.year % 5 === 0 || p.i === 0)
            .map((p) => (
              <text
                key={p.year}
                x={x(p.i)}
                y={innerH + 13}
                textAnchor={p.i === 0 ? "start" : "middle"}
                className="fill-neutral-400 text-[9px]"
              >
                {p.year}
              </text>
            ))}
        </g>
      </svg>
    </div>
  );
}

function CompanyRow({
  company,
  years,
  maxShare,
  width,
}: {
  company: StoryCompanySeries;
  years: number[];
  maxShare: number;
  width: number;
}) {
  const byYear = useMemo(() => cellsFor(company), [company]);
  const theme = useThemeColors(); // resolve register tokens to hex for SVG fill
  const fillFor = (reg: string) => theme.resolve(DEI_REGISTER_TOKEN[reg]);
  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } = useTooltip<Tip>();

  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = ROW_H - MARGIN.top - MARGIN.bottom;
  const baseline = innerH * 0.72;

  const xScale = useMemo(
    () => scaleBand({ domain: years.map(String), range: [0, innerW], padding: 0.18 }),
    [years, innerW]
  );
  const upScale = useMemo(() => scaleLinear({ domain: [0, maxShare], range: [0, baseline] }), [maxShare, baseline]);
  const downScale = useMemo(
    () => scaleLinear({ domain: [0, maxShare], range: [0, innerH - baseline] }),
    [maxShare, innerH, baseline]
  );

  if (innerW <= 0) return null;

  return (
    // Lift the whole row above the rows below it while its tooltip is open, so a
    // tooltip that flips below the cursor isn't covered by the next row's SVG.
    <div className={`relative ${tooltipData ? "z-30" : ""}`}>
      <svg width={width} height={ROW_H} role="img" aria-label={`${company.displayName} register mix by year`}>
        <g transform={`translate(${MARGIN.left},${MARGIN.top})`}>
          <line x1={0} x2={innerW} y1={baseline} y2={baseline} className="stroke-neutral-300 dark:stroke-neutral-700" />
          {years.map((year) => {
            const cell = byYear.get(year);
            const x = xScale(String(year)) ?? 0;
            const w = xScale.bandwidth();
            const cx = x + w / 2;

            let marks: React.ReactNode;
            if (!cell || !cell.captured) {
              // No capture — we don't know. Hollow open tick.
              marks = (
                <rect
                  x={cx - 1.5}
                  y={baseline - 3}
                  width={3}
                  height={6}
                  className="fill-none stroke-neutral-300 dark:stroke-neutral-700"
                  strokeWidth={1}
                  strokeDasharray="1 1"
                />
              );
            } else if (!cell.hasDei) {
              // Captured, but said nothing about DEI. Solid baseline tick.
              marks = <rect x={x} y={baseline - 1.5} width={w} height={1.5} className="fill-neutral-400 dark:fill-neutral-600" />;
            } else {
              let up = baseline;
              const upBars = ACTIVE_REGISTERS.map((reg) => {
                const share = cell.shares[reg];
                if (share <= 0) return null;
                const h = upScale(share);
                up -= h;
                return <rect key={reg} x={x} y={up} width={w} height={h} fill={fillFor(reg)} />;
              });
              let down = baseline;
              const downBars = COUNTER_REGISTERS.map((reg) => {
                const share = cell.counterShares[reg];
                if (share <= 0) return null;
                const h = downScale(share);
                const bar = <rect key={reg} x={x} y={down} width={w} height={h} fill={fillFor(reg)} />;
                down += h;
                return bar;
              });
              marks = (
                <>
                  {upBars}
                  {downBars}
                </>
              );
            }

            return (
              <g key={year}>
                {marks}
                {/* hover capture for the whole column */}
                <rect
                  x={x}
                  y={0}
                  width={w}
                  height={innerH}
                  fill="transparent"
                  onMouseEnter={(ev) => {
                    const pt = localPoint(ev);
                    if (pt) showTooltip({ tooltipData: { cell: cell ?? null, year }, tooltipLeft: cx + MARGIN.left, tooltipTop: pt.y });
                  }}
                  onMouseLeave={hideTooltip}
                />
              </g>
            );
          })}
          {years.map(
            (year, i) =>
              (i === 0 || year % 5 === 0) && (
                <text
                  key={year}
                  x={(xScale(String(year)) ?? 0) + xScale.bandwidth() / 2}
                  y={innerH + 14}
                  textAnchor="middle"
                  className="fill-neutral-400 text-[9px]"
                >
                  {year}
                </text>
              )
          )}
        </g>
      </svg>

      {tooltipData && (
        <TooltipWithBounds
          left={tooltipLeft}
          top={tooltipTop}
          unstyled
          applyPositionStyle
          className="pointer-events-none z-50 max-w-xs rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs shadow-md dark:border-neutral-700 dark:bg-neutral-900"
        >
          <p className="font-semibold">{company.displayName} · {tooltipData.year}</p>
          {!tooltipData.cell || !tooltipData.cell.captured ? (
            <p className="mt-0.5 text-neutral-500">no careers page archived this year</p>
          ) : !tooltipData.cell.hasDei ? (
            <p className="mt-0.5 text-neutral-500">page archived ({tooltipData.cell.nChunks} chunks); no DEI language</p>
          ) : (
            <>
              <p className="mt-0.5 text-neutral-500">{tooltipData.cell.nChunks} chunks</p>
              {tooltipData.cell.inclusionQuote && (
                <p
                  className="mt-1 border-l-2 border-neutral-300 pl-2 italic text-neutral-600 dark:border-neutral-600 dark:text-neutral-300"
                  style={{ borderColor: quoteColor(tooltipData.cell.inclusionQuote, fillFor) }}
                >
                  “{tooltipData.cell.inclusionQuote.text}”
                </p>
              )}
              {tooltipData.cell.counterQuote &&
                tooltipData.cell.counterQuote.text !== tooltipData.cell.inclusionQuote?.text && (
                  <p
                    className="mt-1 border-l-2 border-neutral-300 pl-2 italic text-neutral-600 dark:border-neutral-600 dark:text-neutral-300"
                    style={{ borderColor: quoteColor(tooltipData.cell.counterQuote, fillFor) }}
                  >
                    “{tooltipData.cell.counterQuote.text}”
                  </p>
                )}
            </>
          )}
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function StoryRegisterChart({ companies }: Props) {
  const withRegisters = useMemo(() => companies.filter((c) => c.years.some((y) => y.registers)), [companies]);
  const years = useMemo(() => allYears(withRegisters), [withRegisters]);

  const maxShare = useMemo(() => {
    let max = 0.2;
    for (const c of withRegisters)
      for (const cell of cellsFor(c).values()) {
        const active = Object.values(cell.shares).reduce((a, b) => a + b, 0);
        const counter = Object.values(cell.counterShares).reduce((a, b) => a + b, 0);
        max = Math.max(max, active, counter);
      }
    return Math.min(max, 1);
  }, [withRegisters]);

  const groups = useMemo(() => groupCompanies(withRegisters), [withRegisters]);

  if (!withRegisters.length) return null;

  return (
    <div className="space-y-1">
      <ParentSize>
        {({ width }) => (width > 0 ? <AggregateLine companies={withRegisters} years={years} width={width} /> : null)}
      </ParentSize>
      {groups.map((g) => (
        <div key={g.id} className="pt-4">
          <h3 className="text-sm font-medium text-info">{g.title}</h3>
          <p className="mb-2 mt-0.5 text-xs text-neutral-500">{g.note}</p>
          <div className="space-y-1">
            {g.companies.map((c) => (
              <div key={c.id}>
                <p className="text-[11px] font-medium text-neutral-600 dark:text-neutral-400">{c.displayName}</p>
                <ParentSize>
                  {({ width }) => (width > 0 ? <CompanyRow company={c} years={years} maxShare={maxShare} width={width} /> : null)}
                </ParentSize>
              </div>
            ))}
          </div>
          <div className="mt-2 flex flex-wrap gap-3 text-[10px] text-neutral-500">
            {[...ACTIVE_REGISTERS, ...COUNTER_REGISTERS].map((reg) => (
              <span key={reg} className="flex items-center gap-1">
                <span className="inline-block h-2 w-2 rounded-sm" style={{ backgroundColor: COLORS[reg] }} />
                {LABELS[reg]}
              </span>
            ))}
          </div>
        </div>
      ))}
      <p className="mt-1 max-w-prose text-xs text-neutral-500">
        Bars above the line = share of chunks in an active DEI register; below the line =
        counter-programming (meritocracy or civilizational-mission framing). A{" "}
        <span className="text-neutral-400">solid baseline tick</span> means the page was archived
        but said nothing about DEI; a <span className="text-neutral-400">dashed open tick</span>{" "}
        means no page was archived that year. Hover any year for the language.
      </p>
    </div>
  );
}
