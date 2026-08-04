"use client";

import { useMemo } from "react";
import { ParentSize } from "@visx/responsive";
import { scaleBand, scaleLinear } from "@visx/scale";
import { TooltipWithBounds, useTooltip } from "@visx/tooltip";
import { localPoint } from "@visx/event";
import { BarSegment, SEGMENT_GAP } from "@/components/chartMarks";

/** Group-reference counts by year, stacked by frame — visx version sharing
 * BarSegment styling with the DEI register row (rounded ends + segment
 * gaps). Frame colors arrive as CSS color strings so the chart follows the
 * site theme in light and dark. */

export interface RefsYearRow {
  year: number;
  posts: number;         // total posts that year
  postsWithRefs: number; // posts referencing a marginalized group
  frames: Record<string, number>; // POSTS bucketed by their worst frame (sums to postsWithRefs)
}
export interface FrameDef {
  key: string;
  label: string;
  color: string;
  /** Text color for the in-segment count (default white); set for light
   * segment colors where white doesn't read. */
  countFill?: string;
  /** Tailwind fill classes for the in-segment count when it must adapt to
   * the theme (e.g. "fill-neutral-700 dark:fill-neutral-100"). */
  countClass?: string;
}

const H = 240;
const MARGIN = { top: 18, right: 8, bottom: 34, left: 8 };

type Tip = { year: RefsYearRow; frame: FrameDef; count: number };

/** Minimum segment height (px) for an in-segment count label. */
const COUNT_MIN_H = 12;

function Chart({
  rows,
  frames,
  width,
  showTotals,
  showSegmentCounts,
}: {
  rows: RefsYearRow[];
  frames: FrameDef[];
  width: number;
  showTotals: boolean;
  showSegmentCounts: boolean;
}) {
  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } = useTooltip<Tip>();
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = H - MARGIN.top - MARGIN.bottom;

  const total = (r: RefsYearRow) => frames.reduce((s, f) => s + (r.frames[f.key] ?? 0), 0);
  const maxTotal = useMemo(() => Math.max(1, ...rows.map(total)), [rows, frames]);

  const xScale = useMemo(
    () => scaleBand({ domain: rows.map((r) => String(r.year)), range: [0, innerW], padding: 0.24 }),
    [rows, innerW]
  );
  const yScale = useMemo(() => scaleLinear({ domain: [0, maxTotal], range: [0, innerH] }), [maxTotal, innerH]);

  if (innerW <= 0) return null;

  return (
    <div className="relative">
      <svg width={width} height={H} role="img" aria-label="Group references by year, stacked by frame">
        <g transform={`translate(${MARGIN.left},${MARGIN.top})`}>
          <line x1={0} x2={innerW} y1={innerH} y2={innerH} className="stroke-neutral-300 dark:stroke-neutral-700" />
          {rows.map((r) => {
            const x = xScale(String(r.year)) ?? 0;
            const w = xScale.bandwidth();
            const cx = x + w / 2;
            let cursor = innerH;
            let first = true;
            const segs = frames.map((f) => {
              const count = r.frames[f.key] ?? 0;
              if (count <= 0) return null;
              if (!first) cursor -= SEGMENT_GAP;
              first = false;
              const h = Math.max(2, yScale(count));
              cursor -= h;
              const segY = cursor;
              return (
                <g key={f.key}>
                  <BarSegment
                    x={x}
                    y={segY}
                    width={w}
                    height={h}
                    fill={f.color}
                    onMouseMove={(e) => {
                      const p = localPoint(e);
                      showTooltip({ tooltipData: { year: r, frame: f, count }, tooltipLeft: p?.x ?? 0, tooltipTop: p?.y ?? 0 });
                    }}
                    onMouseLeave={hideTooltip}
                  />
                  {showSegmentCounts && h >= COUNT_MIN_H && (
                    <text
                      x={cx}
                      y={segY + h / 2 + 3.5}
                      textAnchor="middle"
                      className={`pointer-events-none text-[10px] font-medium tabular-nums ${f.countClass ?? ""}`}
                      style={f.countClass ? undefined : { fill: f.countFill ?? "white" }}
                    >
                      {count}
                    </text>
                  )}
                </g>
              );
            });
            const t = total(r);
            return (
              <g key={r.year}>
                {segs}
                {showTotals && t > 0 && (
                  <text x={cx} y={cursor - 5} textAnchor="middle" className="fill-neutral-500 text-[11px] tabular-nums">
                    {t}
                  </text>
                )}
                <text x={cx} y={innerH + 14} textAnchor="middle" className="fill-neutral-500 text-[11px]">
                  {r.year}
                </text>
                <text x={cx} y={innerH + 27} textAnchor="middle" className="fill-neutral-400 text-[10px] tabular-nums">
                  {r.postsWithRefs}/{r.posts}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
      {tooltipData && (
        <TooltipWithBounds left={tooltipLeft} top={tooltipTop} className="z-40">
          <div className="max-w-[240px] text-xs">
            <p className="font-medium">
              {tooltipData.year.year} · {tooltipData.frame.label}
            </p>
            <p className="mt-0.5 text-neutral-600 dark:text-neutral-300">
              {tooltipData.count} post{tooltipData.count === 1 ? "" : "s"} — worst framing {tooltipData.frame.label}
            </p>
            <p className="mt-0.5 text-neutral-500">
              {tooltipData.year.postsWithRefs} of {tooltipData.year.posts} posts that year reference a marginalized group
            </p>
          </div>
        </TooltipWithBounds>
      )}
    </div>
  );
}

/** The composition flip, unmissable: share of references threat-framed per
 * year, as labeled dots. Years with no references get a muted tick. */
function FlipStrip({ rows, threatKey, color, width }: { rows: RefsYearRow[]; threatKey: string; color: string; width: number }) {
  const SH = 46;
  const innerW = width - MARGIN.left - MARGIN.right;
  const xScale = scaleBand({ domain: rows.map((r) => String(r.year)), range: [0, innerW], padding: 0.24 });
  const y = 26;
  return (
    <svg width={width} height={SH} role="img" aria-label="Share of references threat-framed, by year">
      <g transform={`translate(${MARGIN.left},0)`}>
        <line x1={0} x2={innerW} y1={y} y2={y} className="stroke-neutral-200 dark:stroke-neutral-800" />
        {rows.map((r) => {
          const pos = xScale(String(r.year));
          if (pos === undefined) return null;
          const cx = pos + xScale.bandwidth() / 2;
          const total = Object.values(r.frames).reduce((a, b) => a + b, 0);
          if (total === 0) {
            return (
              <g key={r.year}>
                <rect x={cx - 1.5} y={y - 3} width={3} height={6} className="fill-neutral-300 dark:fill-neutral-700" />
                <text x={cx} y={y - 8} textAnchor="middle" className="fill-neutral-400 text-[9px]">
                  no refs
                </text>
              </g>
            );
          }
          const share = (r.frames[threatKey] ?? 0) / total;
          return (
            <g key={r.year}>
              <circle cx={cx} cy={y} r={4.5} style={{ fill: color }} />
              <text x={cx} y={y - 9} textAnchor="middle" className="fill-neutral-500 text-[10px] font-medium tabular-nums">
                {Math.round(100 * share)}%
              </text>
            </g>
          );
        })}
      </g>
    </svg>
  );
}

export default function FounderRefsChart({
  rows,
  frames,
  showTotals = true,
  showSegmentCounts = false,
  showFlipStrip = false,
}: {
  rows: RefsYearRow[];
  frames: FrameDef[];
  /** Column total above each bar. */
  showTotals?: boolean;
  /** Count inside each segment tall enough to hold it. */
  showSegmentCounts?: boolean;
  /** Companion strip: share of references threat-framed per year. */
  showFlipStrip?: boolean;
}) {
  if (!rows?.length) return null;
  const threat = frames.find((f) => f.key === "threat_crime_framing");
  return (
    <ParentSize initialSize={{ width: 480, height: H }}>
      {({ width }) =>
        width > 0 ? (
          <div>
            <Chart rows={rows} frames={frames} width={width} showTotals={showTotals} showSegmentCounts={showSegmentCounts} />
            {showFlipStrip && threat && (
              <>
                <FlipStrip rows={rows} threatKey={threat.key} color={threat.color} width={width} />
                <p className="mt-1 text-[10.5px] text-neutral-500">Share of that year's references framed as threat, crime, or removal.</p>
              </>
            )}
          </div>
        ) : null
      }
    </ParentSize>
  );
}
