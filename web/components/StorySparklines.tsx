"use client";

import { useMemo } from "react";
import { peakYearForSeries, type StoryCompanySeries } from "@/lib/storyTypes";

const COLORS = ["#6366f1", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#06b6d4"];

interface Props {
  companies: StoryCompanySeries[];
  metricLabel?: string;
}

function Sparkline({
  years,
  color,
  width,
  height,
}: {
  years: { year: number; zscore: number }[];
  color: string;
  width: number;
  height: number;
}) {
  if (years.length < 2) return null;

  const pad = 4;
  const innerW = width - pad * 2;
  const innerH = height - pad * 2;
  const values = years.map((y) => y.zscore);
  const yearMin = years[0].year;
  const yearMax = years[years.length - 1].year;
  const valMin = Math.min(...values, 0);
  const valMax = Math.max(...values, 0);
  const valPad = Math.max((valMax - valMin) * 0.15, 0.2);
  const lo = valMin - valPad;
  const hi = valMax + valPad;

  const points = years
    .map((y) => {
      const x = pad + ((y.year - yearMin) / (yearMax - yearMin || 1)) * innerW;
      const yPos = pad + innerH - ((y.zscore - lo) / (hi - lo || 1)) * innerH;
      return `${x},${yPos}`;
    })
    .join(" ");

  const zeroY =
    lo < 0 && hi > 0 ? pad + innerH - ((0 - lo) / (hi - lo)) * innerH : null;

  return (
    <svg width={width} height={height} aria-hidden>
      {zeroY !== null && (
        <line
          x1={pad}
          x2={width - pad}
          y1={zeroY}
          y2={zeroY}
          stroke="currentColor"
          strokeOpacity={0.15}
          strokeWidth={1}
        />
      )}
      <polyline
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        strokeLinejoin="round"
        strokeLinecap="round"
        points={points}
      />
    </svg>
  );
}

export default function StorySparklines({ companies, metricLabel }: Props) {
  const series = useMemo(
    () =>
      companies
        .map((c) => ({
          ...c,
          points: c.years
            .filter((y): y is typeof y & { zscore: number } => typeof y.zscore === "number")
            .map((y) => ({ year: y.year, zscore: y.zscore })),
        }))
        .filter((c) => c.points.length >= 2),
    [companies]
  );

  if (!series.length) return null;

  return (
    <div>
      {metricLabel && (
        <p className="mb-4 text-xs text-neutral-500">
          {metricLabel} — each line is z-scored within its own company, so compare
          timing and shape, not absolute height.
        </p>
      )}
      <div className="grid gap-4 sm:grid-cols-2">
        {series.map((c, i) => {
          const peak = peakYearForSeries(c.years);
          const latest = c.points[c.points.length - 1];
          return (
            <div
              key={c.id}
              className="rounded-lg border border-neutral-200 px-4 py-3 dark:border-neutral-800"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium text-neutral-900 dark:text-neutral-100">
                    {c.displayName}
                  </p>
                  {peak && (
                    <p className="mt-0.5 font-mono text-xs text-neutral-500">
                      peak {peak.year}
                      {latest && latest.year !== peak.year
                        ? ` · latest ${latest.year} (${latest.zscore >= 0 ? "+" : ""}${latest.zscore.toFixed(2)}σ)`
                        : ""}
                    </p>
                  )}
                </div>
                <Sparkline
                  years={c.points}
                  color={COLORS[i % COLORS.length]}
                  width={120}
                  height={40}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
