"use client";

import { useMemo } from "react";
import { ParentSize } from "@visx/responsive";
import { scaleBand } from "@visx/scale";
import {
  metricValue,
  type StoryCompanySeries,
  type StoryMetricKey,
} from "@/lib/storyTypes";

const MARGIN = { top: 8, right: 8, bottom: 28, left: 100 };

interface Props {
  companies: StoryCompanySeries[];
  metricKey?: StoryMetricKey;
}

function colorFor(value: number): string {
  if (value <= 0.01) return "#f5f5f5";
  if (value < 0.15) return "#c7d2fe";
  if (value < 0.3) return "#818cf8";
  if (value < 0.5) return "#4f46e5";
  return "#312e81";
}

function Chart({
  companies,
  metricKey = "fractionPresent",
  width,
  height,
}: Props & { width: number; height: number }) {
  const years = useMemo(() => {
    const set = new Set<number>();
    for (const c of companies) {
      for (const y of c.years) set.add(y.year);
    }
    return [...set].sort((a, b) => a - b);
  }, [companies]);

  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;
  const cellH = Math.min(28, innerH / Math.max(companies.length, 1));

  const xScale = useMemo(
    () => scaleBand({ domain: years.map(String), range: [0, innerW], padding: 0.05 }),
    [years, innerW]
  );
  const yScale = useMemo(
    () => scaleBand({ domain: companies.map((c) => c.id), range: [0, cellH * companies.length], padding: 0.08 }),
    [companies, cellH]
  );

  const lookup = useMemo(() => {
    const map = new Map<string, number>();
    for (const c of companies) {
      for (const y of c.years) {
        const v = metricValue(y, metricKey);
        if (v !== null) map.set(`${c.id}:${y.year}`, v);
      }
    }
    return map;
  }, [companies, metricKey]);

  if (innerW <= 0 || innerH <= 0) return null;

  return (
    <svg width={width} height={MARGIN.top + cellH * companies.length + MARGIN.bottom} role="img" aria-label="Company by year heatmap">
      <g transform={`translate(${MARGIN.left},${MARGIN.top})`}>
        {companies.map((c) =>
          years.map((year) => {
            const val = lookup.get(`${c.id}:${year}`) ?? 0;
            const x = xScale(String(year)) ?? 0;
            const y = yScale(c.id) ?? 0;
            const w = xScale.bandwidth();
            const h = yScale.bandwidth();
            return (
              <g key={`${c.id}-${year}`}>
                <rect
                  x={x}
                  y={y}
                  width={w}
                  height={h}
                  fill={colorFor(val)}
                  rx={2}
                  className="stroke-white dark:stroke-neutral-900"
                  strokeWidth={1}
                >
                  <title>
                    {c.displayName} {year}: {(val * 100).toFixed(1)}%
                  </title>
                </rect>
              </g>
            );
          })
        )}

        {years.map((year) => (
          <text
            key={year}
            x={(xScale(String(year)) ?? 0) + xScale.bandwidth() / 2}
            y={cellH * companies.length + 16}
            textAnchor="middle"
            className="fill-neutral-500 text-[10px]"
          >
            {String(year).slice(2)}
          </text>
        ))}

        {companies.map((c) => (
          <text
            key={c.id}
            x={-8}
            y={(yScale(c.id) ?? 0) + yScale.bandwidth() / 2}
            textAnchor="end"
            dominantBaseline="middle"
            className="fill-neutral-600 text-[11px] dark:fill-neutral-400"
          >
            {c.displayName}
          </text>
        ))}
      </g>
    </svg>
  );
}

export default function StoryHeatmap(props: Props) {
  const h = 40 + props.companies.length * 32;
  return (
    <div className="w-full" style={{ height: h }}>
      <ParentSize>
        {({ width }) => (width > 0 ? <Chart {...props} width={width} height={h} /> : null)}
      </ParentSize>
    </div>
  );
}
