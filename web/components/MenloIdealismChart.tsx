"use client";

import { useMemo } from "react";
import type { MenloIdealismYear, MenloCohortSeries } from "@/lib/menloStory";

interface Props {
  series: MenloIdealismYear[];
  cohort: MenloCohortSeries[];
}

const W = 720;
const H = 360;
const M = { top: 20, right: 96, bottom: 36, left: 36 };
const innerW = W - M.left - M.right;
const innerH = H - M.top - M.bottom;

export default function MenloIdealismChart({ series, cohort }: Props) {
  const { x, y, menloRobustPath, menloPts, cohortPaths, zeroY, yearTicks } =
    useMemo(() => {
      const allYears = [
        ...series.map((s) => s.year),
        ...cohort.flatMap((c) => c.years.map((y) => y.year)),
      ];
      const allZ = [
        ...series.map((s) => s.zscore),
        ...cohort.flatMap((c) => c.years.map((y) => y.zscore)),
      ];
      const yearMin = Math.min(...allYears);
      const yearMax = Math.max(...allYears);
      const zMin = Math.min(...allZ);
      const zMax = Math.max(...allZ);
      const zPad = (zMax - zMin) * 0.08;

      const x = (year: number) =>
        M.left + ((year - yearMin) / (yearMax - yearMin || 1)) * innerW;
      const y = (z: number) =>
        M.top + innerH - ((z - (zMin - zPad)) / (zMax + zPad - (zMin - zPad) || 1)) * innerH;

      const toPath = (pts: { year: number; zscore: number }[]) =>
        pts
          .map((p, i) => `${i === 0 ? "M" : "L"}${x(p.year).toFixed(1)},${y(p.zscore).toFixed(1)}`)
          .join(" ");

      // Menlo line: connect robust years only (thin years shown as faint dots).
      const robust = series.filter((s) => !s.thin);
      const menloRobustPath = toPath(robust);
      const menloPts = series.map((s) => ({ ...s, cx: x(s.year), cy: y(s.zscore) }));

      const cohortPaths = cohort.map((c) => ({
        id: c.id,
        displayName: c.displayName,
        d: toPath(c.years),
        end: c.years[c.years.length - 1],
      }));

      const zeroY = zMin < 0 && zMax > 0 ? y(0) : null;
      const yearTicks = [];
      for (let yr = Math.ceil(yearMin / 4) * 4; yr <= yearMax; yr += 4) {
        yearTicks.push(yr);
      }
      return { x, y, menloRobustPath, menloPts, cohortPaths, zeroY, yearTicks };
    }, [series, cohort]);

  return (
    <figure className="w-full">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full"
        role="img"
        aria-label="Menlo idealism over time versus cohort"
      >
        {/* zero baseline */}
        {zeroY !== null && (
          <line
            x1={M.left}
            x2={W - M.right}
            y1={zeroY}
            y2={zeroY}
            stroke="currentColor"
            strokeOpacity={0.18}
            strokeDasharray="3 3"
          />
        )}

        {/* x axis ticks */}
        {yearTicks.map((yr) => (
          <g key={yr}>
            <text
              x={x(yr)}
              y={H - 12}
              textAnchor="middle"
              className="fill-neutral-400 text-[11px]"
            >
              {yr}
            </text>
          </g>
        ))}

        {/* cohort (faded, the industry) */}
        {cohortPaths.map((c) => (
          <g key={c.id}>
            <path
              d={c.d}
              fill="none"
              stroke="currentColor"
              strokeOpacity={0.28}
              strokeWidth={1.5}
              className="text-neutral-500"
            />
            <text
              x={x(c.end.year) + 6}
              y={y(c.end.zscore) + 3}
              className="fill-neutral-400 text-[11px]"
            >
              {c.displayName}
            </text>
          </g>
        ))}

        {/* Menlo robust-year line (highlight) */}
        <path
          d={menloRobustPath}
          fill="none"
          stroke="#f59e0b"
          strokeWidth={2.75}
          strokeLinejoin="round"
          strokeLinecap="round"
        />
        {/* Menlo points: solid for robust, faint+small for thin years */}
        {menloPts.map((p) => (
          <circle
            key={p.year}
            cx={p.cx}
            cy={p.cy}
            r={p.thin ? 2 : 3.5}
            fill={p.thin ? "#fcd34d" : "#f59e0b"}
            fillOpacity={p.thin ? 0.5 : 1}
          />
        ))}
        {/* Menlo end label */}
        {menloPts.length > 0 && (
          <text
            x={menloPts[menloPts.length - 1].cx + 6}
            y={menloPts[menloPts.length - 1].cy + 3}
            className="text-[11px] font-semibold"
            fill="#f59e0b"
          >
            Menlo
          </text>
        )}
      </svg>
      <figcaption className="mt-2 text-xs text-neutral-500">
        Idealism z-scored within each company (shape &amp; timing, not absolute level).
        <span className="text-amber-600 dark:text-amber-500"> Amber</span> = Menlo
        (solid line through robust years; faint dots = thin years, n&lt;5). Gray = the
        careers-page cohort.
      </figcaption>
    </figure>
  );
}
