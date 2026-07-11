"use client";

import { useMemo, useState } from "react";
import { AxisBottom, AxisLeft, AxisRight } from "@visx/axis";
import { curveMonotoneX } from "@visx/curve";
import { GridRows } from "@visx/grid";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleLinear } from "@visx/scale";
import { LinePath } from "@visx/shape";
import { extent } from "d3-array";
import { useThemeColors } from "@/lib/themeColors";

interface CraftYear {
  year: number;
  zscore: number;
  raw: number;
  nChunks: number;
  thin: boolean;
}
interface AiYear {
  year: number;
  prevalence: number | null;
  aiChunks: number;
  thin: boolean;
}
export interface CompanyPair {
  id: string;
  displayName: string;
  craftSeries: CraftYear[];
  aiSeries: AiYear[];
  coverageNote?: string | null;
}

const MARGIN = { top: 16, right: 56, bottom: 36, left: 48 };

// Fixed axis domains so the ruler doesn't change when flipping companies.
// AI_MAX covers every well-sampled year (max non-thin prevalence ≈ 25%);
// thin years above it (e.g. Meta 2026: 11/11 chunks) are clamped to the top
// and annotated with their true value instead of being allowed to set the scale.
const AI_MAX = 0.35;
const CRAFT_Z_MAX = 3;

function Chart({ pair, width, height }: { pair: CompanyPair; width: number; height: number }) {
  const theme = useThemeColors();
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const years = useMemo(() => {
    const all = [...pair.craftSeries.map((d) => d.year), ...pair.aiSeries.map((d) => d.year)];
    return extent(all) as [number, number];
  }, [pair]);

  const xScale = useMemo(
    () => scaleLinear({ domain: years, range: [0, innerW] }),
    [years, innerW]
  );
  const craftScale = useMemo(
    () => scaleLinear({ domain: [-CRAFT_Z_MAX, CRAFT_Z_MAX], range: [innerH, 0] }),
    [innerH]
  );
  const aiScale = useMemo(
    () => scaleLinear({ domain: [0, AI_MAX], range: [innerH, 0] }),
    [innerH]
  );
  const aiY = (p: number) => aiScale(Math.min(p, AI_MAX));
  const craftY = (z: number) => craftScale(Math.max(-CRAFT_Z_MAX, Math.min(z, CRAFT_Z_MAX)));

  if (innerW <= 0 || innerH <= 0) return null;
  const craftColor = theme.resolve("--chart-1");
  const aiColor = theme.resolve("--chart-contrast-1");
  const ai = pair.aiSeries.filter((d) => d.prevalence !== null) as (AiYear & { prevalence: number })[];

  return (
    <svg width={width} height={height} role="img" aria-label={`Craft language and AI mention share over time for ${pair.displayName}`}>
      <Group left={MARGIN.left} top={MARGIN.top}>
        <GridRows scale={craftScale} width={innerW} strokeDasharray="2 4" className="stroke-neutral-200 dark:stroke-neutral-800" />
        {/* zero line for the craft z-scale */}
        <line x1={0} x2={innerW} y1={craftScale(0)} y2={craftScale(0)} className="stroke-neutral-300 dark:stroke-neutral-700" />

        <LinePath
          data={pair.craftSeries}
          x={(d) => xScale(d.year)}
          y={(d) => craftY(d.zscore)}
          curve={curveMonotoneX}
          strokeWidth={2.5}
          fill="none"
          stroke={craftColor}
        />
        {pair.craftSeries.map((d) => (
          <g key={`c-${d.year}`}>
            <circle
              cx={xScale(d.year)}
              cy={craftY(d.zscore)}
              r={d.thin ? 3 : 2.5}
              fill={d.thin ? "transparent" : craftColor}
              stroke={craftColor}
              strokeWidth={d.thin ? 1.2 : 0}
            />
            {Math.abs(d.zscore) > CRAFT_Z_MAX && (
              <text
                x={xScale(d.year)}
                y={craftY(d.zscore) + (d.zscore > 0 ? -7 : 14)}
                fontSize={10}
                textAnchor="middle"
                fill={craftColor}
              >
                {d.zscore > 0 ? "↑" : "↓"} z={d.zscore.toFixed(1)}
              </text>
            )}
          </g>
        ))}

        <LinePath
          data={ai}
          x={(d) => xScale(d.year)}
          y={(d) => aiY(d.prevalence)}
          curve={curveMonotoneX}
          strokeWidth={2.5}
          strokeDasharray="6 3"
          fill="none"
          stroke={aiColor}
        />
        {ai.map((d) => (
          <g key={`a-${d.year}`}>
            <circle
              cx={xScale(d.year)}
              cy={aiY(d.prevalence)}
              r={d.thin ? 3 : 2.5}
              fill={d.thin ? "transparent" : aiColor}
              stroke={aiColor}
              strokeWidth={d.thin ? 1.2 : 0}
            />
            {d.prevalence > AI_MAX && (() => {
              const total = Math.round(d.aiChunks / d.prevalence);
              return (
                <text
                  x={xScale(d.year)}
                  y={aiY(d.prevalence) - 7}
                  fontSize={10}
                  textAnchor="middle"
                  fill={aiColor}
                >
                  ↑ {Math.round(d.prevalence * 100)}% of {total} chunk{total === 1 ? "" : "s"}
                </text>
              );
            })()}
          </g>
        ))}

        <AxisBottom
          top={innerH}
          scale={xScale}
          tickFormat={(v) => String(v)}
          numTicks={Math.min(8, years[1] - years[0])}
          tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "middle" }}
          stroke="currentColor"
          tickStroke="currentColor"
          axisClassName="text-neutral-400 dark:text-neutral-600"
        />
        <AxisLeft
          scale={craftScale}
          numTicks={5}
          tickFormat={(v) => Number(v).toFixed(1)}
          tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "end", dx: -4 }}
          stroke="currentColor"
          tickStroke="currentColor"
          axisClassName="text-neutral-400 dark:text-neutral-600"
        />
        <AxisRight
          left={innerW}
          scale={aiScale}
          numTicks={4}
          tickFormat={(v) => `${Math.round(Number(v) * 100)}%`}
          tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "start", dx: 4 }}
          stroke="currentColor"
          tickStroke="currentColor"
          axisClassName="text-neutral-400 dark:text-neutral-600"
        />
      </Group>
    </svg>
  );
}

export default function CraftAiTrajectories({ pairs }: { pairs: CompanyPair[] }) {
  const ordered = useMemo(
    () => [...pairs].sort((a, b) => a.displayName.localeCompare(b.displayName)),
    [pairs]
  );
  const [selected, setSelected] = useState("apple");
  const active = ordered.find((c) => c.id === selected) ?? ordered[0];
  const theme = useThemeColors();

  return (
    <div className="w-full">
      <div className="flex flex-wrap gap-1.5">
        {ordered.map((c) => (
          <button
            key={c.id}
            onClick={() => setSelected(c.id)}
            className={
              "rounded-full px-2.5 py-0.5 text-xs transition-colors " +
              (c.id === selected
                ? "bg-neutral-800 text-white dark:bg-neutral-200 dark:text-neutral-900"
                : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200 dark:bg-neutral-800 dark:text-neutral-300 dark:hover:bg-neutral-700")
            }
          >
            {c.displayName}
          </button>
        ))}
      </div>

      <div className="mt-2 flex items-center gap-4 text-xs text-neutral-500">
        <span>
          <span className="font-semibold" style={{ color: theme.resolve("--chart-1") }}>— craft</span> (z-score, left)
        </span>
        <span>
          <span className="font-semibold" style={{ color: theme.resolve("--chart-contrast-1") }}>-- AI mentions</span> (share, right)
        </span>
        <span className="text-neutral-400">hollow points = thin years (n &lt; 5) · axes fixed across companies</span>
      </div>

      <div className="h-80 w-full">
        <ParentSize>{({ width, height }) => (width > 0 && active ? <Chart pair={active} width={width} height={height} /> : null)}</ParentSize>
      </div>

      {active?.coverageNote && (
        <p className="mt-1 text-xs italic text-neutral-500">⚠ {active.coverageNote}</p>
      )}
    </div>
  );
}
