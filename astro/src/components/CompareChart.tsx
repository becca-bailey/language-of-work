"use client";

import { useCallback, useMemo } from "react";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { curveMonotoneX } from "@visx/curve";
import { GridRows } from "@visx/grid";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleLinear, scaleOrdinal } from "@visx/scale";
import { LinePath } from "@visx/shape";
import { TooltipWithBounds, useTooltip } from "@visx/tooltip";
import { extent } from "d3-array";
import { localPoint } from "@visx/event";
import type { TimelineEvent } from "@/lib/events";

export interface CompanySeries {
  company: string;
  displayName: string;
  points: { year: number; zscore: number; thin: boolean }[];
}

interface Props {
  series: CompanySeries[];
  axisName: string;
  events?: TimelineEvent[];
}

const MARGIN = { top: 16, right: 24, bottom: 36, left: 52 };
const COLORS = [
  "#6366f1",
  "#f59e0b",
  "#10b981",
  "#ef4444",
  "#8b5cf6",
  "#06b6d4",
];

type TooltipRow = { year: number; company: string; displayName: string; zscore: number; thin: boolean };

function Chart({
  series,
  axisName,
  events = [],
  width,
  height,
}: Props & { width: number; height: number }) {
  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } =
    useTooltip<TooltipRow>();

  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const allYears = useMemo(
    () => series.flatMap((s) => s.points.map((p) => p.year)),
    [series]
  );
  const allZ = useMemo(
    () => series.flatMap((s) => s.points.map((p) => p.zscore)),
    [series]
  );

  const xScale = useMemo(() => {
    const [min, max] = extent(allYears) as [number, number];
    return scaleLinear({ domain: [min, max], range: [0, innerW] });
  }, [allYears, innerW]);

  const yScale = useMemo(() => {
    const [min, max] = extent(allZ) as [number, number];
    const pad = (max - min) * 0.12 || 1;
    return scaleLinear({ domain: [min - pad, max + pad], range: [innerH, 0] });
  }, [allZ, innerH]);

  const colorScale = useMemo(
    () =>
      scaleOrdinal({
        domain: series.map((s) => s.company),
        range: COLORS,
      }),
    [series]
  );

  const yearIndex = useMemo(() => {
    const years = [...new Set(allYears)].sort((a, b) => a - b);
    return years;
  }, [allYears]);

  const nearestAtYear = useCallback(
    (year: number): TooltipRow | null => {
      let best: TooltipRow | null = null;
      let bestDist = Infinity;
      for (const s of series) {
        const pt = s.points.find((p) => p.year === year);
        if (!pt) continue;
        const dist = Math.abs(pt.year - year);
        if (dist < bestDist) {
          bestDist = dist;
          best = {
            year: pt.year,
            company: s.company,
            displayName: s.displayName,
            zscore: pt.zscore,
            thin: pt.thin,
          };
        }
      }
      return best;
    },
    [series]
  );

  if (innerW <= 0 || innerH <= 0) return null;

  return (
    <div className="relative">
      <svg width={width} height={height} role="img" aria-label={`${axisName} comparison over time`}>
        <Group left={MARGIN.left} top={MARGIN.top}>
          <GridRows
            scale={yScale}
            width={innerW}
            strokeDasharray="2 4"
            className="stroke-neutral-200 dark:stroke-neutral-800"
          />
          <line
            x1={0}
            x2={innerW}
            y1={yScale(0)}
            y2={yScale(0)}
            className="stroke-neutral-300 dark:stroke-neutral-700"
          />

          {events
            .filter(
              (ev) =>
                ev.year >= xScale.domain()[0] && ev.year <= xScale.domain()[1]
            )
            .map((ev) => (
              <g key={ev.id}>
                <line
                  x1={xScale(ev.year)}
                  x2={xScale(ev.year)}
                  y1={0}
                  y2={innerH}
                  strokeDasharray="4 4"
                  className="stroke-amber-400/70"
                />
                <text
                  x={xScale(ev.year) + 3}
                  y={4}
                  textAnchor="start"
                  transform={`rotate(90, ${xScale(ev.year) + 3}, 4)`}
                  className="fill-amber-600 text-[9px] dark:fill-amber-400"
                >
                  {ev.label}
                </text>
              </g>
            ))}

          {series.map((s) => (
            <LinePath
              key={s.company}
              data={s.points}
              x={(d) => xScale(d.year)}
              y={(d) => yScale(d.zscore)}
              curve={curveMonotoneX}
              stroke={colorScale(s.company)}
              strokeWidth={2}
              fill="none"
            />
          ))}

          {series.map((s) =>
            s.points.map((d) => (
              <g key={`${s.company}-${d.year}`}>
                {d.thin && (
                  <circle
                    cx={xScale(d.year)}
                    cy={yScale(d.zscore)}
                    r={7}
                    fill="none"
                    strokeWidth={2}
                    className="stroke-amber-500"
                  />
                )}
                <circle
                  cx={xScale(d.year)}
                  cy={yScale(d.zscore)}
                  r={3}
                  fill={colorScale(s.company)}
                />
              </g>
            ))
          )}

          <AxisBottom
            top={innerH}
            scale={xScale}
            tickFormat={(v) => String(v)}
            numTicks={Math.min(yearIndex.length, 12)}
            tickLabelProps={{
              className: "fill-neutral-500 text-[11px]",
              textAnchor: "middle",
            }}
            stroke="currentColor"
            tickStroke="currentColor"
            axisClassName="text-neutral-400 dark:text-neutral-600"
          />
          <AxisLeft
            scale={yScale}
            numTicks={6}
            label="z-score (within company)"
            labelProps={{ className: "fill-neutral-500 text-[11px]" }}
            tickLabelProps={{
              className: "fill-neutral-500 text-[11px]",
              textAnchor: "end",
              dx: -4,
            }}
            stroke="currentColor"
            tickStroke="currentColor"
            axisClassName="text-neutral-400 dark:text-neutral-600"
          />

          <rect
            width={innerW}
            height={innerH}
            fill="transparent"
            onMouseMove={(e) => {
              const point = localPoint(e);
              if (!point) return;
              const year = Math.round(xScale.invert(point.x - MARGIN.left));
              const row = nearestAtYear(year);
              if (!row) return;
              showTooltip({
                tooltipData: row,
                tooltipLeft: MARGIN.left + xScale(row.year),
                tooltipTop: MARGIN.top + yScale(row.zscore) - 12,
              });
            }}
            onMouseLeave={hideTooltip}
          />
        </Group>
      </svg>

      <div className="mt-3 flex flex-wrap gap-4 text-sm">
        {series.map((s) => (
          <div key={s.company} className="flex items-center gap-2">
            <span
              className="inline-block h-0.5 w-6 rounded"
              style={{ backgroundColor: colorScale(s.company) }}
            />
            <span>{s.displayName}</span>
          </div>
        ))}
      </div>

      {tooltipData && (
        <TooltipWithBounds
          left={tooltipLeft}
          top={tooltipTop}
          unstyled
          applyPositionStyle
          className="pointer-events-none rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs shadow-md dark:border-neutral-700 dark:bg-neutral-900"
        >
          <p className="font-semibold">
            {tooltipData.displayName} · {tooltipData.year}
            {tooltipData.thin && (
              <span className="ml-2 font-normal text-amber-600 dark:text-amber-400">
                thin coverage
              </span>
            )}
          </p>
          <p className="mt-1 font-mono text-neutral-600 dark:text-neutral-300">
            {axisName}: {tooltipData.zscore.toFixed(2)}
          </p>
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function CompareChart(props: Props) {
  return (
    <div className="h-96 w-full">
      <ParentSize>
        {({ width, height }) =>
          width > 0 ? <Chart {...props} width={width} height={height} /> : null
        }
      </ParentSize>
    </div>
  );
}
