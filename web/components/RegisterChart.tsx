"use client";

import { useMemo } from "react";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleBand, scaleLinear, scaleOrdinal } from "@visx/scale";
import { Bar } from "@visx/shape";
import type { DeiYearScore } from "@/lib/data";

// "absent" is excluded: it just counts analyzed chunks, not DEI language
const REGISTER_ORDER = [
  "explicit_demographic",
  "structural_process",
  "aspirational_vague",
  "belonging_culture",
  "meritocracy",
  "civilizational_mission",
] as const;

const COLORS: Record<string, string> = {
  explicit_demographic: "#059669",
  structural_process: "#0d9488",
  aspirational_vague: "#6366f1",
  belonging_culture: "#8b5cf6",
  meritocracy: "#f59e0b",
  civilizational_mission: "#dc2626",
};

const MARGIN = { top: 8, right: 8, bottom: 36, left: 40 };

function Chart({ years, width, height }: { years: DeiYearScore[]; width: number; height: number }) {
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const yearLabels = years.map((y) => String(y.year));
  const xScale = useMemo(
    () => scaleBand({ domain: yearLabels, range: [0, innerW], padding: 0.2 }),
    [yearLabels, innerW]
  );
  const maxTotal = Math.max(
    ...years.map((y) =>
      REGISTER_ORDER.reduce((sum, reg) => sum + (y.registers[reg] ?? 0), 0)
    ),
    1
  );
  const yScale = useMemo(() => scaleLinear({ domain: [0, maxTotal], range: [innerH, 0] }), [maxTotal, innerH]);
  const colorScale = scaleOrdinal({ domain: REGISTER_ORDER as unknown as string[], range: REGISTER_ORDER.map((r) => COLORS[r]) });

  return (
    <svg width={width} height={height} role="img" aria-label="DEI register breakdown by year">
      <Group left={MARGIN.left} top={MARGIN.top}>
        {years.map((y) => {
          const x = xScale(String(y.year)) ?? 0;
          const barW = xScale.bandwidth();
          let cumulative = 0;
          return REGISTER_ORDER.map((reg) => {
            const count = y.registers[reg] ?? 0;
            if (!count) return null;
            const yTop = yScale(cumulative + count);
            const yBottom = yScale(cumulative);
            cumulative += count;
            return (
              <Bar
                key={`${y.year}-${reg}`}
                x={x}
                y={yTop}
                width={barW}
                height={yBottom - yTop}
                fill={colorScale(reg)}
              />
            );
          });
        })}
        <AxisBottom top={innerH} scale={xScale} tickLabelProps={{ className: "fill-neutral-500 text-[10px]", textAnchor: "middle" }} />
        <AxisLeft scale={yScale} numTicks={4} tickLabelProps={{ className: "fill-neutral-500 text-[10px]", textAnchor: "end", dx: -4 }} />
      </Group>
    </svg>
  );
}

export default function RegisterChart({ years }: { years: DeiYearScore[] }) {
  return (
    <div>
      <div className="h-48 w-full">
        <ParentSize>{({ width, height }) => width > 0 ? <Chart years={years} width={width} height={height} /> : null}</ParentSize>
      </div>
      <div className="mt-2 flex flex-wrap gap-3 text-[10px] text-neutral-500">
        {REGISTER_ORDER.map((reg) => (
          <span key={reg} className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-sm" style={{ backgroundColor: COLORS[reg] }} />
            {reg.replace(/_/g, " ")}
          </span>
        ))}
      </div>
    </div>
  );
}
