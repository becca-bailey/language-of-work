"use client";

import { useMemo } from "react";
import { ParentSize } from "@visx/responsive";
import { scaleBand, scaleLinear } from "@visx/scale";
import { TooltipWithBounds, useTooltip } from "@visx/tooltip";
import { localPoint } from "@visx/event";
import { allYears, type StoryCompanySeries } from "@/lib/storyTypes";
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
  inclusionQuote?: string;
  counterQuote?: string;
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
      inclusionQuote: y.stanceMaxQuote?.text,
      counterQuote: y.stanceMinQuote?.text,
    });
  }
  return cells;
}

type Tip = { cell: YearCell | null; year: number };

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
                <p className="mt-1 border-l-2 border-positive pl-2 italic text-neutral-600 dark:text-neutral-300">“{tooltipData.cell.inclusionQuote}”</p>
              )}
              {tooltipData.cell.counterQuote && tooltipData.cell.counterQuote !== tooltipData.cell.inclusionQuote && (
                <p className="mt-1 border-l-2 border-warning pl-2 italic text-neutral-600 dark:text-neutral-300">“{tooltipData.cell.counterQuote}”</p>
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

  if (!withRegisters.length) return null;

  return (
    <div className="space-y-1">
      {withRegisters.map((c) => (
        <div key={c.id}>
          <p className="text-[11px] font-medium text-neutral-600 dark:text-neutral-400">{c.displayName}</p>
          <ParentSize>{({ width }) => (width > 0 ? <CompanyRow company={c} years={years} maxShare={maxShare} width={width} /> : null)}</ParentSize>
        </div>
      ))}
      <div className="mt-3 flex flex-wrap gap-3 text-[10px] text-neutral-500">
        {[...ACTIVE_REGISTERS, ...COUNTER_REGISTERS].map((reg) => (
          <span key={reg} className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-sm" style={{ backgroundColor: COLORS[reg] }} />
            {LABELS[reg]}
          </span>
        ))}
      </div>
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
