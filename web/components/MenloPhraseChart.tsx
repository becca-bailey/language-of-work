"use client";

import { useMemo } from "react";
import { AxisBottom } from "@visx/axis";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleBand, scaleLinear, scaleOrdinal } from "@visx/scale";
import { Bar } from "@visx/shape";
import { TooltipWithBounds, useTooltip } from "@visx/tooltip";
import { localPoint } from "@visx/event";
import type { MenloPhrase } from "@/lib/menloStory";

interface Props {
  groups: Record<string, MenloPhrase[]>;
  groupLabels: Record<string, string>;
}

const MARGIN = { top: 8, right: 16, bottom: 28, left: 168 };
const ROW_H = 22;
const COLORS: Record<string, string> = {
  trademarks: "#f59e0b",
  joy_mission: "#10b981",
  method: "#6366f1",
};

type Row = MenloPhrase & { group: string };
type Tip = Row;

function Chart({ groups, groupLabels, width }: Props & { width: number }) {
  const rows: Row[] = useMemo(
    () =>
      Object.entries(groups).flatMap(([group, terms]) =>
        terms.map((t) => ({ ...t, group }))
      ),
    [groups]
  );

  const height = MARGIN.top + MARGIN.bottom + rows.length * ROW_H;
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = rows.length * ROW_H;

  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } =
    useTooltip<Tip>();

  const xScale = useMemo(() => {
    const minY = Math.min(...rows.map((r) => r.first_year));
    const maxY = Math.max(...rows.map((r) => r.last_year));
    return scaleLinear({ domain: [minY, maxY], range: [0, innerW] });
  }, [rows, innerW]);

  const yScale = useMemo(
    () =>
      scaleBand({
        domain: rows.map((r) => r.term),
        range: [0, innerH],
        padding: 0.25,
      }),
    [rows, innerH]
  );

  const color = useMemo(
    () =>
      scaleOrdinal({
        domain: Object.keys(COLORS),
        range: Object.values(COLORS),
      }),
    []
  );

  if (innerW <= 0) return null;

  return (
    <div className="relative">
      <svg width={width} height={height} role="img" aria-label="Branded vocabulary over time">
        <Group left={MARGIN.left} top={MARGIN.top}>
          {/* light gridlines every ~5 years */}
          {xScale.ticks(6).map((yr) => (
            <line
              key={yr}
              x1={xScale(yr)}
              x2={xScale(yr)}
              y1={0}
              y2={innerH}
              className="stroke-neutral-100 dark:stroke-neutral-800"
            />
          ))}

          {rows.map((r) => {
            const y = yScale(r.term) ?? 0;
            const x0 = xScale(r.first_year);
            const w = Math.max(xScale(r.last_year) - x0, 3);
            return (
              <g key={`${r.group}-${r.term}`}>
                <text
                  x={-8}
                  y={y + yScale.bandwidth() / 2}
                  textAnchor="end"
                  dominantBaseline="middle"
                  className="fill-neutral-700 text-[11px] dark:fill-neutral-300"
                >
                  {r.term}
                </text>
                <Bar
                  x={x0}
                  y={y}
                  width={w}
                  height={yScale.bandwidth()}
                  rx={3}
                  fill={color(r.group)}
                  fillOpacity={0.85}
                  onMouseMove={(e) => {
                    const p = localPoint(e);
                    if (!p) return;
                    showTooltip({
                      tooltipData: r,
                      tooltipLeft: p.x,
                      tooltipTop: p.y,
                    });
                  }}
                  onMouseLeave={hideTooltip}
                />
              </g>
            );
          })}

          <AxisBottom
            top={innerH}
            scale={xScale}
            numTicks={6}
            tickFormat={(v) => String(v)}
            tickLabelProps={{
              className: "fill-neutral-500 text-[11px]",
              textAnchor: "middle",
            }}
            stroke="currentColor"
            tickStroke="currentColor"
            axisClassName="text-neutral-400 dark:text-neutral-600"
          />
        </Group>
      </svg>

      <div className="mt-2 flex flex-wrap gap-4 text-xs">
        {Object.keys(COLORS).map((g) => (
          <div key={g} className="flex items-center gap-1.5">
            <span
              className="inline-block h-2 w-3 rounded-sm"
              style={{ backgroundColor: COLORS[g] }}
            />
            <span className="text-neutral-500">{groupLabels[g] ?? g}</span>
          </div>
        ))}
      </div>

      {tooltipData && (
        <TooltipWithBounds
          left={tooltipLeft}
          top={tooltipTop}
          unstyled
          applyPositionStyle
          className="pointer-events-none max-w-xs rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs shadow-md dark:border-neutral-700 dark:bg-neutral-900"
        >
          <p className="font-semibold">
            {tooltipData.term}
            <span className="ml-2 font-normal text-neutral-500">
              {tooltipData.first_year}&ndash;{tooltipData.last_year} · ×
              {tooltipData.count}
            </span>
          </p>
          {tooltipData.example && (
            <p className="mt-1 italic text-neutral-600 dark:text-neutral-300">
              &ldquo;{tooltipData.example.slice(0, 140)}&rdquo;
            </p>
          )}
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function MenloPhraseChart(props: Props) {
  return (
    <ParentSize>
      {({ width }) => (width > 0 ? <Chart {...props} width={width} /> : null)}
    </ParentSize>
  );
}
