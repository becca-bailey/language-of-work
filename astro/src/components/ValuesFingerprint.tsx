"use client";

import { useMemo } from "react";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleBand, scaleLinear } from "@visx/scale";
import { Bar } from "@visx/shape";
import { TooltipWithBounds, useTooltip } from "@visx/tooltip";
import { localPoint } from "@visx/event";
import { useThemeColors } from "@/lib/themeColors";
import type { FingerprintAxis } from "@/lib/data";

interface Props {
  axes: FingerprintAxis[];
}

const MARGIN = { top: 8, right: 24, bottom: 24, left: 150 };
const ROW_H = 34;

// Diverging bars centered at zero: positive = the careers copy leans on this
// value MORE than peers, negative = less. Mean z-score across all years.
function Chart({ axes, width }: Props & { width: number }) {
  const theme = useThemeColors(); // positive (cool) vs negative (warm) valence
  const data = useMemo(
    () => [...axes].sort((a, b) => b.zscore - a.zscore),
    [axes]
  );
  const height = MARGIN.top + MARGIN.bottom + data.length * ROW_H;
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = data.length * ROW_H;

  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } =
    useTooltip<FingerprintAxis>();

  const xScale = useMemo(() => {
    const maxAbs = Math.max(1, ...data.map((d) => Math.abs(d.zscore)));
    return scaleLinear({ domain: [-maxAbs, maxAbs], range: [0, innerW] });
  }, [data, innerW]);

  const yScale = useMemo(
    () =>
      scaleBand({
        domain: data.map((d) => d.axis),
        range: [0, innerH],
        padding: 0.32,
      }),
    [data, innerH]
  );

  if (innerW <= 0) return null;
  const zero = xScale(0);

  return (
    <div className="relative">
      <svg width={width} height={height} role="img" aria-label="values fingerprint">
        <Group left={MARGIN.left} top={MARGIN.top}>
          {/* zero baseline */}
          <line
            x1={zero}
            x2={zero}
            y1={0}
            y2={innerH}
            className="stroke-neutral-300 dark:stroke-neutral-700"
            strokeWidth={1}
          />
          {data.map((d) => {
            const y = yScale(d.axis) ?? 0;
            const x = xScale(Math.min(0, d.zscore));
            const w = Math.abs(xScale(d.zscore) - zero);
            const positive = d.zscore >= 0;
            return (
              <g key={d.axis}>
                <text
                  x={-MARGIN.left + 4}
                  y={y + yScale.bandwidth() / 2}
                  dominantBaseline="middle"
                  className="fill-neutral-600 text-[12px] dark:fill-neutral-300"
                >
                  {d.label}
                </text>
                <Bar
                  x={x}
                  y={y}
                  width={Math.max(w, 2)}
                  height={yScale.bandwidth()}
                  rx={3}
                  fill={positive ? theme.role.info : theme.role.negative}
                  fillOpacity={0.85}
                  onMouseMove={(e) => {
                    const p = localPoint(e);
                    if (!p) return;
                    showTooltip({ tooltipData: d, tooltipLeft: p.x, tooltipTop: p.y });
                  }}
                  onMouseLeave={hideTooltip}
                />
              </g>
            );
          })}
        </Group>
      </svg>

      <div className="mt-1 flex justify-between px-1 text-[10px] uppercase tracking-wide text-neutral-400">
        <span>← less than peers</span>
        <span>more than peers →</span>
      </div>

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
            z = {tooltipData.zscore > 0 ? "+" : ""}
            {tooltipData.zscore.toFixed(2)} vs peers · {tooltipData.nYears} yrs
          </p>
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function ValuesFingerprint(props: Props) {
  return (
    <ParentSize>
      {({ width }) => (width > 0 ? <Chart {...props} width={width} /> : null)}
    </ParentSize>
  );
}
