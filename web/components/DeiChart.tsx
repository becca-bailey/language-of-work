"use client";

import { useCallback, useMemo } from "react";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { curveMonotoneX } from "@visx/curve";
import { GridRows } from "@visx/grid";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleLinear } from "@visx/scale";
import { LinePath } from "@visx/shape";
import { TooltipWithBounds, useTooltip } from "@visx/tooltip";
import { extent } from "d3-array";
import { localPoint } from "@visx/event";
import type { DeiYearScore } from "@/lib/data";
import { DEI_EVENTS, type TimelineEvent } from "@/lib/events";

export interface DeiChartRow {
  year: number;
  inclusion: number | null;
  thin: boolean;
  nChunks: number;
}

interface Props {
  rows: DeiChartRow[];
  events?: TimelineEvent[];
  selectedYear: number;
  onSelectYear: (year: number) => void;
}

const MARGIN = { top: 24, right: 24, bottom: 36, left: 52 };

function Chart({
  rows,
  events = DEI_EVENTS,
  selectedYear,
  onSelectYear,
  width,
  height,
}: Props & { width: number; height: number }) {
  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } =
    useTooltip<DeiChartRow>();

  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const allYears = rows.map((d) => d.year);
  const values = rows
    .map((d) => d.inclusion)
    .filter((v): v is number => v !== null);

  const xScale = useMemo(() => {
    const [min, max] = extent(allYears) as [number, number];
    return scaleLinear({ domain: [min, max], range: [0, innerW] });
  }, [allYears, innerW]);

  const yScale = useMemo(() => {
    const [min, max] = extent(values) as [number, number];
    const pad = (max - min) * 0.12 || 0.05;
    return scaleLinear({
      domain: [Math.max(0, min - pad), max + pad],
      range: [innerH, 0],
    });
  }, [values, innerH]);

  const inclusionPts = rows.filter((d) => d.inclusion !== null);

  const nearestRow = useCallback(
    (event: React.MouseEvent<SVGRectElement>) => {
      const point = localPoint(event);
      if (!point) return null;
      const year = Math.round(xScale.invert(point.x - MARGIN.left));
      return rows.reduce((best, r) =>
        Math.abs(r.year - year) < Math.abs(best.year - year) ? r : best
      );
    },
    [rows, xScale]
  );

  if (innerW <= 0 || innerH <= 0) return null;

  return (
    <div className="relative">
      <svg width={width} height={height} role="img" aria-label="DEI intensity over time">
        <Group left={MARGIN.left} top={MARGIN.top}>
          <GridRows scale={yScale} width={innerW} strokeDasharray="2 4" className="stroke-neutral-200 dark:stroke-neutral-800" />
          {events.map((ev) => (
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
          <LinePath data={inclusionPts} x={(d) => xScale(d.year)} y={(d) => yScale(d.inclusion as number)} curve={curveMonotoneX} strokeWidth={2} fill="none" className="stroke-emerald-600" />
          {inclusionPts.map((d) => (
            <g key={d.year}>
              {d.thin && (
                <circle
                  cx={xScale(d.year)}
                  cy={yScale(d.inclusion as number)}
                  r={7}
                  fill="none"
                  strokeWidth={2}
                  className="stroke-amber-500"
                />
              )}
              <circle
                cx={xScale(d.year)}
                cy={yScale(d.inclusion as number)}
                r={d.year === selectedYear ? 5 : 3}
                className={
                  d.year === selectedYear
                    ? "fill-emerald-700"
                    : "fill-emerald-500"
                }
              />
            </g>
          ))}
          <AxisBottom top={innerH} scale={xScale} tickFormat={(v) => String(v)} numTicks={Math.min(rows.length, 12)} tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "middle" }} />
          <AxisLeft scale={yScale} numTicks={6} label="inclusion cosine" labelProps={{ className: "fill-neutral-500 text-[11px]" }} tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "end", dx: -4 }} />
          <rect width={innerW} height={innerH} fill="transparent" onMouseMove={(e) => { const row = nearestRow(e); if (row) showTooltip({ tooltipData: row, tooltipLeft: MARGIN.left + xScale(row.year), tooltipTop: MARGIN.top + yScale(row.inclusion ?? 0) - 12 }); }} onMouseLeave={hideTooltip} onClick={(e) => { const row = nearestRow(e); if (row) onSelectYear(row.year); }} />
        </Group>
      </svg>
      {tooltipData && (
        <TooltipWithBounds left={tooltipLeft} top={tooltipTop} unstyled applyPositionStyle className="pointer-events-none rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs shadow-md dark:border-neutral-700 dark:bg-neutral-900">
          <p className="font-semibold">{tooltipData.year}</p>
          <p>inclusion: {tooltipData.inclusion?.toFixed(3)}</p>
          <p>{tooltipData.nChunks} chunks</p>
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function DeiChart(props: Props) {
  return (
    <div className="h-96 w-full">
      <ParentSize>{({ width, height }) => width > 0 ? <Chart {...props} width={width} height={height} /> : null}</ParentSize>
    </div>
  );
}

export function deiRowsFromYears(years: DeiYearScore[]): DeiChartRow[] {
  return years.map((y) => ({
    year: y.year,
    inclusion: y.inclusionTopkMean,
    thin: y.thin,
    nChunks: y.nChunks,
  }));
}
