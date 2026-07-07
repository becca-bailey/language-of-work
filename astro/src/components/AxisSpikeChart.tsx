"use client";

import { useMemo } from "react";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleBand, scaleLinear } from "@visx/scale";
import { useThemeColors } from "@/lib/themeColors";

export interface AxisSpikeRow {
  axis: string;
  label: string;
  z2020: number;
  concession: boolean;
}

const MARGIN = { top: 8, right: 44, bottom: 28, left: 124 };

function Chart({ rows, width, height }: { rows: AxisSpikeRow[]; width: number; height: number }) {
  const theme = useThemeColors();
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const xScale = useMemo(() => {
    const max = Math.max(...rows.map((r) => Math.abs(r.z2020)));
    return scaleLinear({ domain: [Math.min(0, ...rows.map((r) => r.z2020)), max * 1.05], range: [0, innerW] });
  }, [rows, innerW]);
  const yScale = useMemo(
    () => scaleBand({ domain: rows.map((r) => r.label), range: [0, innerH], padding: 0.28 }),
    [rows, innerH]
  );

  if (innerW <= 0 || innerH <= 0) return null;
  const zero = xScale(0);
  const accent = theme.resolve("--chart-1");
  const muted = theme.resolve("--muted");

  return (
    <svg width={width} height={height} role="img" aria-label="Each axis's 2020 spike as a within-axis z-score">
      <Group left={MARGIN.left} top={MARGIN.top}>
        <line x1={zero} x2={zero} y1={0} y2={innerH} className="stroke-neutral-300 dark:stroke-neutral-700" />
        {rows.map((r) => {
          const y = yScale(r.label) ?? 0;
          const bw = yScale.bandwidth();
          const x = Math.min(zero, xScale(r.z2020));
          const w = Math.abs(xScale(r.z2020) - zero);
          const fill = r.concession ? accent : muted;
          return (
            <Group key={r.axis} top={y}>
              <rect x={x} y={0} width={w} height={bw} rx={3} fill={fill} opacity={r.concession ? 1 : 0.55}>
                <title>{`${r.label}: ${r.z2020 > 0 ? "+" : ""}${r.z2020} SD in 2020`}</title>
              </rect>
              <text x={-8} y={bw / 2} dominantBaseline="middle" textAnchor="end" fontSize={12}
                className={r.concession ? "fill-neutral-800 dark:fill-neutral-100" : "fill-neutral-500"}
                fontWeight={r.concession ? 600 : 400}>
                {r.label}
              </text>
              <text x={xScale(r.z2020) + (r.z2020 >= 0 ? 6 : -6)} y={bw / 2} dominantBaseline="middle"
                textAnchor={r.z2020 >= 0 ? "start" : "end"} fontSize={11} className="fill-neutral-500 tabular-nums">
                {r.z2020 > 0 ? "+" : ""}{r.z2020.toFixed(1)}
              </text>
            </Group>
          );
        })}
        <text x={zero} y={innerH + 18} textAnchor="middle" fontSize={10} className="fill-neutral-500">
          2020 deviation from each axis's own average (SD)
        </text>
      </Group>
    </svg>
  );
}

export default function AxisSpikeChart({ rows }: { rows: AxisSpikeRow[] }) {
  return (
    <div className="h-72 w-full">
      <ParentSize>{({ width, height }) => (width > 0 ? <Chart rows={rows} width={width} height={height} /> : null)}</ParentSize>
    </div>
  );
}
