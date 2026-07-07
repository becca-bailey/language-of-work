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
import { bisector, extent } from "d3-array";
import { localPoint } from "@visx/event";
import { useThemeColors } from "@/lib/themeColors";

export interface LocusRow {
  year: number;
  mentalHealth: number; // individual-locus care
  caregiving: number; // structural-locus care
  nChunks: number;
}

const MARGIN = { top: 16, right: 120, bottom: 36, left: 48 };
const bisectYear = bisector<LocusRow, number>((d) => d.year).center;

// individual-locus = "self" (halt orange); structural-locus = "system" (arcade purple)
const SERIES = [
  { key: "mentalHealth" as const, label: "Mental health", sub: "individual", token: "--chart-contrast-1" },
  { key: "caregiving" as const, label: "Family / caregiving", sub: "structural", token: "--chart-1" },
];

function Chart({ rows, width, height }: { rows: LocusRow[]; width: number; height: number }) {
  const theme = useThemeColors();
  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } = useTooltip<LocusRow>();
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const xScale = useMemo(() => {
    const [min, max] = extent(rows, (d) => d.year) as [number, number];
    return scaleLinear({ domain: [min, max], range: [0, innerW] });
  }, [rows, innerW]);

  const yScale = useMemo(() => {
    const vals = rows.flatMap((d) => [d.mentalHealth, d.caregiving]);
    const max = Math.max(...vals);
    return scaleLinear({ domain: [0, max * 1.15 || 1], range: [innerH, 0] });
  }, [rows, innerH]);

  const tickValues = useMemo(() => {
    const [min, max] = extent(rows, (d) => d.year) as [number, number];
    const step = 2;
    const t: number[] = [];
    for (let y = Math.ceil(min / step) * step; y <= max; y += step) t.push(y);
    if (t[t.length - 1] !== max) t.push(max);
    return t;
  }, [rows]);

  const nearestRow = useCallback(
    (event: React.MouseEvent<SVGRectElement>) => {
      const point = localPoint(event);
      if (!point) return null;
      const year = xScale.invert(point.x - MARGIN.left);
      return rows[bisectYear(rows, year)] ?? null;
    },
    [rows, xScale]
  );

  if (innerW <= 0 || innerH <= 0) return null;
  const color = (token: string) => theme.resolve(token);
  const last = rows[rows.length - 1];

  return (
    <div className="relative">
      <svg width={width} height={height} role="img" aria-label="Mental health vs family/caregiving benefit prevalence over time">
        <Group left={MARGIN.left} top={MARGIN.top}>
          <GridRows scale={yScale} width={innerW} strokeDasharray="2 4" className="stroke-neutral-200 dark:stroke-neutral-800" />

          {SERIES.map((s) => (
            <LinePath
              key={s.key}
              data={rows}
              x={(d) => xScale(d.year)}
              y={(d) => yScale(d[s.key])}
              curve={curveMonotoneX}
              strokeWidth={2.5}
              fill="none"
              stroke={color(s.token)}
            />
          ))}

          {SERIES.map((s) =>
            rows.map((d) => (
              <circle key={`${s.key}-${d.year}`} cx={xScale(d.year)} cy={yScale(d[s.key])} r={2.5} fill={color(s.token)} />
            ))
          )}

          {/* direct labels at the right end (satisfies the contrast-relief requirement) */}
          {SERIES.map((s) => (
            <text
              key={`lbl-${s.key}`}
              x={innerW + 8}
              y={yScale(last[s.key])}
              dominantBaseline="middle"
              fontSize={12}
              fill={color(s.token)}
              fontWeight={600}
            >
              {s.label}
              <tspan x={innerW + 8} dy={14} fontSize={10} fontWeight={400} className="fill-neutral-500">
                {s.sub}-locus
              </tspan>
            </text>
          ))}

          <AxisBottom
            top={innerH}
            scale={xScale}
            tickFormat={(v) => String(v)}
            tickValues={tickValues}
            tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "middle" }}
            stroke="currentColor"
            tickStroke="currentColor"
            axisClassName="text-neutral-400 dark:text-neutral-600"
          />
          <AxisLeft
            scale={yScale}
            numTicks={5}
            tickFormat={(v) => `${Math.round(Number(v) * 100)}%`}
            tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "end", dx: -4 }}
            stroke="currentColor"
            tickStroke="currentColor"
            axisClassName="text-neutral-400 dark:text-neutral-600"
          />

          <rect
            width={innerW}
            height={innerH}
            fill="transparent"
            onMouseMove={(e) => {
              const row = nearestRow(e);
              if (!row) return;
              showTooltip({ tooltipData: row, tooltipLeft: MARGIN.left + xScale(row.year), tooltipTop: MARGIN.top + 8 });
            }}
            onMouseLeave={hideTooltip}
          />
        </Group>
      </svg>

      {tooltipData && (
        <TooltipWithBounds
          left={tooltipLeft}
          top={tooltipTop}
          unstyled
          applyPositionStyle
          className="pointer-events-none rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs shadow-md dark:border-neutral-700 dark:bg-neutral-900"
        >
          <p className="font-semibold">{tooltipData.year}</p>
          <dl className="mt-1 space-y-0.5 font-mono text-neutral-600 dark:text-neutral-300">
            <div className="flex justify-between gap-4">
              <dt style={{ color: color("--chart-contrast-1") }}>mental health</dt>
              <dd>{(tooltipData.mentalHealth * 100).toFixed(0)}%</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt style={{ color: color("--chart-1") }}>caregiving</dt>
              <dd>{(tooltipData.caregiving * 100).toFixed(0)}%</dd>
            </div>
          </dl>
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function LocusDivergenceChart({ rows }: { rows: LocusRow[] }) {
  return (
    <div className="h-90 w-full">
      <ParentSize>{({ width, height }) => (width > 0 ? <Chart rows={rows} width={width} height={height} /> : null)}</ParentSize>
    </div>
  );
}
