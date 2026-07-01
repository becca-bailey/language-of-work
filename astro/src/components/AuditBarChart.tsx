"use client";

import { useMemo } from "react";
import { AxisBottom } from "@visx/axis";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleBand, scaleLinear } from "@visx/scale";
import { Bar } from "@visx/shape";
import { TooltipWithBounds, useTooltip } from "@visx/tooltip";
import { localPoint } from "@visx/event";
import { useThemeColors } from "@/lib/themeColors";

export interface BarDatum {
  label: string;
  value: number;
  /** Highlight in red (e.g. the "0 metrics" / "0 adopters" punchline bar). */
  isTest: boolean;
}

interface Props {
  data: BarDatum[];
}

const MARGIN = { top: 8, right: 40, bottom: 28, left: 180 };
const ROW_H = 30;

function Chart({ data, width }: Props & { width: number }) {
  const theme = useThemeColors(); // alert (warm) for the keeper-test bar, info (cool) otherwise
  const height = MARGIN.top + MARGIN.bottom + data.length * ROW_H;
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = data.length * ROW_H;

  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } =
    useTooltip<BarDatum>();

  const xScale = useMemo(
    () =>
      scaleLinear({
        domain: [0, Math.max(...data.map((d) => d.value), 1)],
        range: [0, innerW],
      }),
    [data, innerW]
  );
  const yScale = useMemo(
    () =>
      scaleBand({
        domain: data.map((d) => d.label),
        range: [0, innerH],
        padding: 0.3,
      }),
    [data, innerH]
  );

  if (innerW <= 0) return null;

  return (
    <div className="relative">
      <svg width={width} height={height} role="img" aria-label="bar comparison">
        <Group left={MARGIN.left} top={MARGIN.top}>
          {data.map((d) => {
            const y = yScale(d.label) ?? 0;
            const w = xScale(d.value);
            return (
              <g key={d.label}>
                <text
                  x={-8}
                  y={y + yScale.bandwidth() / 2}
                  textAnchor="end"
                  dominantBaseline="middle"
                  className="fill-neutral-700 text-[12px] dark:fill-neutral-300"
                >
                  {d.label}
                </text>
                <Bar
                  x={0}
                  y={y}
                  width={Math.max(w, d.value === 0 ? 0 : 2)}
                  height={yScale.bandwidth()}
                  rx={3}
                  fill={d.isTest ? theme.role.alert : theme.role.info}
                  fillOpacity={d.isTest ? 0.9 : 0.8}
                  onMouseMove={(e) => {
                    const p = localPoint(e);
                    if (!p) return;
                    showTooltip({ tooltipData: d, tooltipLeft: p.x, tooltipTop: p.y });
                  }}
                  onMouseLeave={hideTooltip}
                />
                <text
                  x={Math.max(w, 0) + 6}
                  y={y + yScale.bandwidth() / 2}
                  dominantBaseline="middle"
                  className={`text-[12px] tabular-nums ${
                    d.isTest
                      ? "fill-alert font-semibold"
                      : "fill-neutral-500"
                  }`}
                >
                  {d.value}
                </text>
              </g>
            );
          })}

          <AxisBottom
            top={innerH}
            scale={xScale}
            numTicks={5}
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

      {tooltipData && (
        <TooltipWithBounds
          left={tooltipLeft}
          top={tooltipTop}
          unstyled
          applyPositionStyle
          className="pointer-events-none rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs shadow-md dark:border-neutral-700 dark:bg-neutral-900"
        >
          <p className="font-semibold">{tooltipData.label}</p>
          <p className="mt-0.5 font-mono text-neutral-600 dark:text-neutral-300">
            {tooltipData.value}
          </p>
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function AuditBarChart(props: Props) {
  return (
    <ParentSize>
      {({ width }) => (width > 0 ? <Chart {...props} width={width} /> : null)}
    </ParentSize>
  );
}
