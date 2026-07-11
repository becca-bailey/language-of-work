"use client";

import { useMemo, useState } from "react";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { GridRows } from "@visx/grid";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleLinear } from "@visx/scale";
import { TooltipWithBounds, useTooltip } from "@visx/tooltip";
import { useThemeColors } from "@/lib/themeColors";

export interface ScatterPoint {
  id: string;
  displayName: string;
  craft: number; // craft raw mean, 2024-26 (+ = craft pole, − = iteration pole)
  ai: number; // AI mention prevalence, 2024-26
  flagged: boolean;
  note?: string | null;
}

const MARGIN = { top: 20, right: 24, bottom: 44, left: 52 };

function Chart({ points, width, height }: { points: ScatterPoint[]; width: number; height: number }) {
  const theme = useThemeColors();
  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } = useTooltip<ScatterPoint>();
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const xScale = useMemo(() => {
    const vals = points.map((d) => d.craft);
    const pad = 0.012;
    return scaleLinear({ domain: [Math.min(...vals) - pad, Math.max(...vals) + pad], range: [0, innerW] });
  }, [points, innerW]);

  const yScale = useMemo(() => {
    const max = Math.max(...points.map((d) => d.ai));
    return scaleLinear({ domain: [-0.01, max * 1.12 || 0.1], range: [innerH, 0] });
  }, [points, innerH]);

  if (innerW <= 0 || innerH <= 0) return null;
  const dot = theme.resolve("--chart-1");

  // Alternate label offsets along the crowded ai≈0 shelf so names stay legible.
  const zeroShelf = points.filter((p) => p.ai < 0.005).sort((a, b) => a.craft - b.craft);
  const labelDy = (p: ScatterPoint) => {
    const i = zeroShelf.findIndex((z) => z.id === p.id);
    if (i === -1) return -8;
    return i % 2 === 0 ? -8 : 14;
  };

  return (
    <div className="relative">
      <svg width={width} height={height} role="img" aria-label="Craft language level vs AI mention prevalence, 2024–26, one point per company">
        <Group left={MARGIN.left} top={MARGIN.top}>
          <GridRows scale={yScale} width={innerW} strokeDasharray="2 4" className="stroke-neutral-200 dark:stroke-neutral-800" />

          <text x={4} y={12} fontSize={11} className="fill-neutral-400" fontStyle="italic">
            AI adopters ↑
          </text>
          <text x={innerW - 4} y={innerH - 8} fontSize={11} textAnchor="end" className="fill-neutral-400" fontStyle="italic">
            craft holdouts →
          </text>

          {points.map((p) => (
            <g key={p.id}>
              <circle
                cx={xScale(p.craft)}
                cy={yScale(p.ai)}
                r={5}
                fill={p.flagged ? "transparent" : dot}
                stroke={dot}
                strokeWidth={p.flagged ? 1.5 : 0}
                strokeDasharray={p.flagged ? "2 2" : undefined}
                onMouseMove={() =>
                  showTooltip({
                    tooltipData: p,
                    tooltipLeft: MARGIN.left + xScale(p.craft),
                    tooltipTop: MARGIN.top + yScale(p.ai) - 12,
                  })
                }
                onMouseLeave={hideTooltip}
              />
              <text
                x={xScale(p.craft) + 7}
                y={yScale(p.ai) + labelDy(p) + 6}
                fontSize={10}
                className="fill-neutral-500 dark:fill-neutral-400"
              >
                {p.displayName}
              </text>
            </g>
          ))}

          <AxisBottom
            top={innerH}
            scale={xScale}
            numTicks={6}
            tickFormat={(v) => Number(v).toFixed(2)}
            tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "middle" }}
            stroke="currentColor"
            tickStroke="currentColor"
            axisClassName="text-neutral-400 dark:text-neutral-600"
            label="craft ← iteration · axis score, 2024–26 mean"
            labelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "middle", dy: 8 }}
          />
          <AxisLeft
            scale={yScale}
            numTicks={5}
            tickFormat={(v) => `${Math.round(Number(v) * 100)}%`}
            tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "end", dx: -4 }}
            stroke="currentColor"
            tickStroke="currentColor"
            axisClassName="text-neutral-400 dark:text-neutral-600"
            label="share of chunks mentioning AI, 2024–26"
            labelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "middle", dx: -innerH / 2, dy: -38 }}
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
          <p className="font-semibold">{tooltipData.displayName}</p>
          <dl className="mt-1 space-y-0.5 font-mono text-neutral-600 dark:text-neutral-300">
            <div className="flex justify-between gap-4">
              <dt>craft</dt>
              <dd>{tooltipData.craft >= 0 ? "+" : ""}{tooltipData.craft.toFixed(3)}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt>AI mentions</dt>
              <dd>{(tooltipData.ai * 100).toFixed(1)}%</dd>
            </div>
          </dl>
          {tooltipData.note && (
            <p className="mt-2 max-w-64 border-t border-neutral-200 pt-2 text-[11px] leading-snug text-neutral-500 dark:border-neutral-700">
              ⚠ {tooltipData.note}
            </p>
          )}
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function CraftAiScatter({ points }: { points: ScatterPoint[] }) {
  return (
    <div className="h-96 w-full">
      <ParentSize>{({ width, height }) => (width > 0 ? <Chart points={points} width={width} height={height} /> : null)}</ParentSize>
    </div>
  );
}
