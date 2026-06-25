"use client";

import { useMemo, useState } from "react";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { curveMonotoneX } from "@visx/curve";
import { GridRows } from "@visx/grid";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleLinear } from "@visx/scale";
import { LinePath } from "@visx/shape";
import { extent } from "d3-array";
import type { CanonCase } from "@/lib/canonStory";

const MARGIN = { top: 20, right: 24, bottom: 36, left: 52 };
const SERIES_COLOR: Record<string, string> = {
  canon: "#2563eb", // blue — the frozen mission canon
  conduct: "#ea580c", // orange — the erupting conduct line
};

interface Props {
  data: CanonCase;
  poleHigh: string;
  poleLow: string;
}

function Chart({ data, poleHigh, poleLow, width, height }: Props & { width: number; height: number }) {
  const [hovered, setHovered] = useState<string | null>(null);
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const years = useMemo(() => {
    const set = new Set<number>();
    for (const s of data.series) for (const y of s.years) set.add(y.year);
    return [...set].sort((a, b) => a - b);
  }, [data]);

  const allValues = useMemo(
    () => [
      ...data.series.flatMap((s) => s.years.map((y) => y.value)),
      data.canonBand.lo,
      data.canonBand.hi,
    ],
    [data]
  );

  const xScale = useMemo(() => {
    const [min, max] = extent(years) as [number, number];
    return scaleLinear({ domain: [min, max], range: [0, innerW] });
  }, [years, innerW]);

  const yScale = useMemo(() => {
    const [min, max] = extent(allValues) as [number, number];
    const pad = Math.max((max - min) * 0.12, 0.02);
    return scaleLinear({ domain: [min - pad, max + pad], range: [innerH, 0] });
  }, [allValues, innerH]);

  if (innerW <= 0 || innerH <= 0) return null;

  const [domainLo, domainHi] = yScale.domain();
  const showZeroLine = domainLo < 0 && domainHi > 0;

  return (
    <div>
      <svg width={width} height={height} role="img" aria-label={`${data.displayName} mission–rights trajectory`}>
        <Group left={MARGIN.left} top={MARGIN.top}>
          <GridRows
            scale={yScale}
            width={innerW}
            strokeDasharray="2 4"
            className="stroke-neutral-200 dark:stroke-neutral-800"
          />

          {/* Pooled canon reference band — the "frozen" values position. */}
          <rect
            x={0}
            y={yScale(data.canonBand.hi)}
            width={innerW}
            height={Math.max(0, yScale(data.canonBand.lo) - yScale(data.canonBand.hi))}
            className="fill-blue-500/10"
          />
          <text x={4} y={yScale(data.canonBand.hi) - 4} className="fill-blue-500 text-[9px]">
            canon band (±1σ, all years)
          </text>

          {/* Mission / rights divider. */}
          {showZeroLine && (
            <g>
              <line
                x1={0}
                x2={innerW}
                y1={yScale(0)}
                y2={yScale(0)}
                className="stroke-neutral-400 dark:stroke-neutral-600"
                strokeWidth={1.5}
              />
              <text x={innerW - 4} y={yScale(0) - 5} textAnchor="end" className="fill-neutral-400 text-[9px]">
                {poleHigh} ↑ / {poleLow} ↓
              </text>
            </g>
          )}

          {/* External event markers (e.g. the 2024 rupture). */}
          {data.events
            .filter((ev) => ev.year >= years[0] && ev.year <= years[years.length - 1])
            .map((ev) => (
              <g key={ev.id}>
                <line
                  x1={xScale(ev.year)}
                  x2={xScale(ev.year)}
                  y1={0}
                  y2={innerH}
                  strokeDasharray="4 4"
                  className="stroke-amber-400/80"
                />
                <text
                  x={xScale(ev.year) + 3}
                  y={4}
                  transform={`rotate(90, ${xScale(ev.year) + 3}, 4)`}
                  className="fill-amber-600 text-[9px] dark:fill-amber-400"
                >
                  {ev.label}
                </text>
              </g>
            ))}

          {data.series.map((s) => {
            const points = s.years.map((y) => ({ year: y.year, value: y.value, thin: y.thin }));
            const color = SERIES_COLOR[s.id] ?? "#6366f1";
            const dim = hovered && hovered !== s.id;
            return (
              <Group key={s.id}>
                <LinePath
                  data={points}
                  x={(d) => xScale(d.year)}
                  y={(d) => yScale(d.value)}
                  curve={curveMonotoneX}
                  stroke={color}
                  strokeWidth={hovered === s.id ? 3 : 2}
                  strokeOpacity={dim ? 0.25 : 1}
                  fill="none"
                />
                {points.map((d) => (
                  <circle
                    key={d.year}
                    cx={xScale(d.year)}
                    cy={yScale(d.value)}
                    r={d.thin ? 2 : 3.5}
                    fill={d.thin ? "white" : color}
                    stroke={color}
                    strokeWidth={1.5}
                    fillOpacity={dim ? 0.25 : 1}
                    strokeOpacity={dim ? 0.25 : 1}
                  />
                ))}
              </Group>
            );
          })}

          <AxisBottom
            top={innerH}
            scale={xScale}
            tickFormat={(v) => String(v)}
            numTicks={Math.min(years.length, 12)}
            tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "middle" }}
            stroke="currentColor"
            tickStroke="currentColor"
            axisClassName="text-neutral-400"
          />
          <AxisLeft
            scale={yScale}
            numTicks={5}
            tickFormat={(v) => Number(v).toFixed(2)}
            tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "end", dx: -4 }}
            stroke="currentColor"
            tickStroke="currentColor"
            axisClassName="text-neutral-400"
          />
        </Group>
      </svg>

      <div className="mt-3 flex flex-wrap gap-4 text-sm">
        {data.series.map((s) => (
          <button
            key={s.id}
            type="button"
            className="flex items-center gap-2"
            onMouseEnter={() => setHovered(s.id)}
            onMouseLeave={() => setHovered(null)}
          >
            <span
              className="inline-block h-0.5 w-6 rounded"
              style={{
                backgroundColor: SERIES_COLOR[s.id],
                opacity: hovered && hovered !== s.id ? 0.3 : 1,
              }}
            />
            <span className={hovered === s.id ? "font-medium" : ""}>{s.label}</span>
          </button>
        ))}
        <span className="flex items-center gap-2 text-neutral-400">
          <span className="inline-block h-2 w-2 rounded-full border border-current bg-white" />
          hollow = thin year (few chunks)
        </span>
      </div>
    </div>
  );
}

export default function ValuesAsIpChart(props: Props) {
  return (
    <div className="h-96 w-full">
      <ParentSize>
        {({ width, height }) => (width > 0 ? <Chart {...props} width={width} height={height} /> : null)}
      </ParentSize>
    </div>
  );
}
