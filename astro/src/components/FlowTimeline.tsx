"use client";

import { useMemo } from "react";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleLinear } from "@visx/scale";
import { useThemeColors } from "@/lib/themeColors";

export interface FlowData {
  byYear: { year: number; commits: number }[];
  events: { date: string; label: string; kind: string }[];
}

const MARGIN = { top: 120, right: 40, bottom: 28, left: 40 };
const KIND_TOKEN: Record<string, string> = {
  add: "--chart-1",
  expand: "--chart-2",
  reframe: "--chart-contrast-2",
  restrict: "--chart-contrast-1",
};

function frac(date: string): number {
  const [y, m] = date.split("-").map(Number);
  return y + (m ? (m - 1) / 12 : 0);
}

function Chart({ data, width, height }: { data: FlowData; width: number; height: number }) {
  const theme = useThemeColors();
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const years = data.byYear.map((d) => d.year);
  const [minY, maxY] = [Math.min(...years), Math.max(...years) + 1];
  const x = useMemo(() => scaleLinear({ domain: [minY, maxY], range: [0, innerW] }), [minY, maxY, innerW]);
  const maxC = Math.max(...data.byYear.map((d) => d.commits));
  const barH = useMemo(() => scaleLinear({ domain: [0, maxC], range: [0, innerH] }), [maxC, innerH]);

  if (innerW <= 0 || innerH <= 0) return null;

  return (
    <svg width={width} height={height} role="img" aria-label="GitLab Family & Friends Day edit history with key events">
      <Group left={MARGIN.left} top={MARGIN.top}>
        {/* commit-density bars per year (muted context) */}
        {data.byYear.map((d) => {
          const bx = x(d.year);
          const bw = Math.max(2, x(d.year + 1) - x(d.year) - 3);
          const h = barH(d.commits);
          return (
            <rect key={d.year} x={bx} y={innerH - h} width={bw} height={h} rx={2} className="fill-neutral-300 dark:fill-neutral-700">
              <title>{`${d.year}: ${d.commits} edits`}</title>
            </rect>
          );
        })}
        <line x1={0} x2={innerW} y1={innerH} y2={innerH} className="stroke-neutral-300 dark:stroke-neutral-700" />
        {years.concat(maxY).map((y) => (
          <text key={y} x={x(y)} y={innerH + 16} textAnchor="middle" fontSize={10} className="fill-neutral-500">
            {y}
          </text>
        ))}

        {/* event markers + labels: each on its own vertical tier with a leader line,
            so the five annotations never collide even when clustered in 2020-2023 */}
        {data.events.map((e, i) => {
          const ex = x(frac(e.date));
          const col = theme.resolve(KIND_TOKEN[e.kind] ?? "--muted");
          const tierY = -MARGIN.top + 6 + i * ((MARGIN.top - 20) / data.events.length);
          const anchor = ex > innerW - 120 ? "end" : "start";
          const dx = anchor === "end" ? -6 : 6;
          return (
            <Group key={e.date} left={ex}>
              <line x1={0} x2={0} y1={tierY + 6} y2={innerH} stroke={col} strokeWidth={1} strokeDasharray="3 3" opacity={0.55} />
              <circle cx={0} cy={innerH} r={4} fill={col} />
              <circle cx={0} cy={tierY + 6} r={2.5} fill={col} />
              <text x={dx} y={tierY + 6} dominantBaseline="middle" textAnchor={anchor} fontSize={10.5} fontWeight={600} fill={col}>
                {e.date.slice(0, 7)} · {e.label}
              </text>
            </Group>
          );
        })}
      </Group>
    </svg>
  );
}

export default function FlowTimeline({ data }: { data: FlowData }) {
  return (
    <div className="h-80 w-full">
      <ParentSize>{({ width, height }) => (width > 0 ? <Chart data={data} width={width} height={height} /> : null)}</ParentSize>
    </div>
  );
}
