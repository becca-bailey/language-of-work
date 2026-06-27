"use client";

import { useMemo, useState } from "react";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { curveMonotoneX } from "@visx/curve";
import { GridRows } from "@visx/grid";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleLinear, scaleOrdinal } from "@visx/scale";
import { LinePath } from "@visx/shape";
import { extent } from "d3-array";
import type { TimelineEvent } from "@/lib/events";
import {
  allYears,
  industryMeanByYear,
  metricValue,
  type StoryCompanySeries,
  type StoryMetricKey,
} from "@/lib/storyTypes";

const MARGIN = { top: 20, right: 24, bottom: 36, left: 52 };
const COLORS = ["#6366f1", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#06b6d4"];

interface Props {
  companies: StoryCompanySeries[];
  metricLabel: string;
  metricKey?: StoryMetricKey;
  format?: "percent" | "signed";
  events?: TimelineEvent[];
  coverageStart?: number;
}

function Chart({
  companies,
  metricLabel,
  metricKey = "fractionPresent",
  format = "percent",
  events = [],
  coverageStart,
  width,
  height,
}: Props & { width: number; height: number }) {
  const [hovered, setHovered] = useState<string | null>(null);
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const years = useMemo(() => allYears(companies), [companies]);
  const meanPoints = useMemo(
    () =>
      years
        .map((year) => {
          const mean = industryMeanByYear(companies, year, metricKey);
          return mean !== null ? { year, value: mean } : null;
        })
        .filter((p): p is { year: number; value: number } => p !== null),
    [companies, years, metricKey]
  );

  const companyPoints = useMemo(
    () =>
      companies.map((c) => ({
        id: c.id,
        points: c.years
          .map((y) => {
            const v = metricValue(y, metricKey);
            return v !== null ? { year: y.year, value: v } : null;
          })
          .filter((p): p is { year: number; value: number } => p !== null),
      })),
    [companies, metricKey]
  );

  const allValues = useMemo(
    () => [
      ...companyPoints.flatMap((c) => c.points.map((p) => p.value)),
      ...meanPoints.map((p) => p.value),
    ],
    [companyPoints, meanPoints]
  );

  const xScale = useMemo(() => {
    const [min, max] = extent(years) as [number, number];
    return scaleLinear({ domain: [min, max], range: [0, innerW] });
  }, [years, innerW]);

  const yScale = useMemo(() => {
    const [min, max] = extent(allValues) as [number, number];
    const pad = Math.max((max - min) * 0.12, 0.02);
    const lo = format === "signed" ? min - pad : Math.max(0, min - pad);
    return scaleLinear({
      domain: [lo, max + pad],
      range: [innerH, 0],
    });
  }, [allValues, innerH, format]);

  const colorScale = useMemo(
    () =>
      scaleOrdinal({
        domain: companies.map((c) => c.id),
        range: COLORS,
      }),
    [companies]
  );

  const formatTick = (v: number) =>
    format === "percent" ? `${(v * 100).toFixed(0)}%` : v.toFixed(2);

  const [domainLo, domainHi] = yScale.domain();
  const showZeroLine = format === "signed" && domainLo < 0 && domainHi > 0;

  if (innerW <= 0 || innerH <= 0) return null;

  return (
    <div>
      <svg width={width} height={height} role="img" aria-label={metricLabel}>
        <Group left={MARGIN.left} top={MARGIN.top}>
          <GridRows
            scale={yScale}
            width={innerW}
            strokeDasharray="2 4"
            className="stroke-neutral-200 dark:stroke-neutral-800"
          />

          {coverageStart !== undefined && (
            <rect
              x={xScale(coverageStart)}
              y={0}
              width={innerW - xScale(coverageStart)}
              height={innerH}
              className="fill-amber-50/40 dark:fill-amber-950/20"
            />
          )}

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
              <text
                x={innerW - 4}
                y={yScale(0) - 5}
                textAnchor="end"
                className="fill-neutral-400 text-[9px]"
              >
                inclusion-leaning ↑ / meritocracy-leaning ↓
              </text>
            </g>
          )}

          {events
            .filter((ev) => ev.year >= years[0] && ev.year <= years[years.length - 1])
            .map((ev) => (
              <g key={ev.id}>
                <line
                  x1={xScale(ev.year)}
                  x2={xScale(ev.year)}
                  y1={0}
                  y2={innerH}
                  strokeDasharray="4 4"
                  className="stroke-amber-400/70"
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

          {companyPoints.map((c) => (
            <LinePath
              key={c.id}
              data={c.points}
              x={(d) => xScale(d.year)}
              y={(d) => yScale(d.value)}
              curve={curveMonotoneX}
              stroke={colorScale(c.id)}
              strokeWidth={hovered === c.id ? 2.5 : 1}
              strokeOpacity={hovered && hovered !== c.id ? 0.2 : 0.45}
              fill="none"
            />
          ))}

          <LinePath
            data={meanPoints}
            x={(d) => xScale(d.year)}
            y={(d) => yScale(d.value)}
            curve={curveMonotoneX}
            className="stroke-neutral-900 dark:stroke-neutral-100"
            strokeWidth={3}
            fill="none"
          />

          {meanPoints.map((d) => (
            <circle
              key={d.year}
              cx={xScale(d.year)}
              cy={yScale(d.value)}
              r={4}
              className="fill-neutral-900 dark:fill-neutral-100"
            />
          ))}

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
            tickFormat={(v) => formatTick(Number(v))}
            label={metricLabel}
            labelProps={{ className: "fill-neutral-500 text-[11px]" }}
            tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "end", dx: -4 }}
            stroke="currentColor"
            tickStroke="currentColor"
            axisClassName="text-neutral-400"
          />
        </Group>
      </svg>

      <div className="mt-3 flex flex-wrap gap-4 text-sm">
        <div className="flex items-center gap-2 font-medium">
          <span className="inline-block h-0.5 w-6 rounded bg-neutral-900 dark:bg-neutral-100" />
          Industry mean
        </div>
        {companies.map((c) => (
          <button
            key={c.id}
            type="button"
            className="flex items-center gap-2"
            onMouseEnter={() => setHovered(c.id)}
            onMouseLeave={() => setHovered(null)}
          >
            <span
              className="inline-block h-0.5 w-6 rounded"
              style={{ backgroundColor: colorScale(c.id), opacity: hovered && hovered !== c.id ? 0.3 : 1 }}
            />
            <span className={hovered === c.id ? "font-medium" : ""}>{c.displayName}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default function StoryTrendChart(props: Props) {
  return (
    <div className="h-96 w-full">
      <ParentSize>
        {({ width, height }) =>
          width > 0 ? <Chart {...props} width={width} height={height} /> : null
        }
      </ParentSize>
    </div>
  );
}
