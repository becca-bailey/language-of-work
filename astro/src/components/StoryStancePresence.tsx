"use client";

import { useMemo, useState } from "react";
import { ParentSize } from "@visx/responsive";
import { scaleBand, scaleLinear } from "@visx/scale";
import type { StoryStancePresence } from "@/lib/storyTypes";

const STANCE_ORDER = [
  "affirming_dei",
  "neutral",
  "mission_focus_apolitical",
  "performance_elite",
  "civilizational_mission",
] as const;

const COLORS: Record<string, string> = {
  affirming_dei: "#059669",
  neutral: "#d4d4d4",
  mission_focus_apolitical: "#f59e0b",
  performance_elite: "#ef4444",
  civilizational_mission: "#dc2626",
};

const LABELS: Record<string, string> = {
  affirming_dei: "affirming DEI",
  neutral: "neutral",
  mission_focus_apolitical: "mission-focus / apolitical",
  performance_elite: "performance elite",
  civilizational_mission: "civilizational mission",
};

const ROW_H = 96;
const MARGIN = { top: 4, right: 8, bottom: 20, left: 12 };

function CompanyRow({
  data,
  years,
  width,
}: {
  data: StoryStancePresence;
  years: number[];
  width: number;
}) {
  const byYear = useMemo(
    () => new Map(data.years.map((y) => [y.year, y])),
    [data]
  );
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = ROW_H - MARGIN.top - MARGIN.bottom;

  const xScale = useMemo(
    () =>
      scaleBand({
        domain: years.map(String),
        range: [0, innerW],
        padding: 0.18,
      }),
    [years, innerW]
  );
  const yScale = useMemo(
    () => scaleLinear({ domain: [0, 1], range: [innerH, 0] }),
    [innerH]
  );

  if (innerW <= 0) return null;

  return (
    <svg width={width} height={ROW_H} role="img" aria-label={`Stance presence for ${data.displayName}`}>
      <g transform={`translate(${MARGIN.left},${MARGIN.top})`}>
        {years.map((year) => {
          const d = byYear.get(year);
          const x = xScale(String(year)) ?? 0;
          const w = xScale.bandwidth();
          if (!d) return null;
          let yCursor = innerH;
          return (
            <g key={year}>
              {STANCE_ORDER.map((stance) => {
                const share = d.shares[stance] ?? 0;
                if (share <= 0) return null;
                const h = innerH - yScale(share);
                yCursor -= h;
                return (
                  <rect
                    key={stance}
                    x={x}
                    y={yCursor}
                    width={w}
                    height={h}
                    fill={COLORS[stance]}
                  >
                    <title>
                      {data.displayName} {year}: {LABELS[stance]} {(share * 100).toFixed(0)}%
                    </title>
                  </rect>
                );
              })}
            </g>
          );
        })}
        {years.map(
          (year, i) =>
            (i === 0 || year % 5 === 0) && (
              <text
                key={year}
                x={(xScale(String(year)) ?? 0) + xScale.bandwidth() / 2}
                y={innerH + 14}
                textAnchor="middle"
                className="fill-neutral-400 text-[9px]"
              >
                {year}
              </text>
            )
        )}
      </g>
    </svg>
  );
}

export default function StoryStancePresenceChart({
  presence,
}: {
  presence: StoryStancePresence[];
}) {
  const [selected, setSelected] = useState(presence[0]?.company ?? "");
  const active = presence.find((p) => p.company === selected);
  const years = useMemo(() => {
    const set = new Set<number>();
    for (const p of presence) {
      for (const y of p.years) set.add(y.year);
    }
    return [...set].sort((a, b) => a - b);
  }, [presence]);

  if (!presence.length) return null;

  return (
    <div>
      <div className="flex flex-wrap gap-2">
        {presence.map((p) => (
          <button
            key={p.company}
            type="button"
            onClick={() => setSelected(p.company)}
            className={`rounded-full px-3 py-1 text-xs transition-colors ${
              selected === p.company
                ? "bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900"
                : "border border-neutral-300 text-neutral-600"
            }`}
          >
            {p.displayName}
          </button>
        ))}
      </div>
      {active && (
        <div className="mt-2">
          <p className="text-[11px] font-medium text-neutral-600">{active.displayName}</p>
          <ParentSize>
            {({ width }) =>
              width > 0 ? (
                <CompanyRow data={active} years={years} width={width} />
              ) : null
            }
          </ParentSize>
        </div>
      )}
      <div className="mt-3 flex flex-wrap gap-3 text-[10px] text-neutral-500">
        {STANCE_ORDER.map((s) => (
          <span key={s} className="flex items-center gap-1">
            <span
              className="inline-block h-2 w-2 rounded-sm"
              style={{ backgroundColor: COLORS[s] }}
            />
            {LABELS[s]}
          </span>
        ))}
      </div>
      <p className="mt-1 text-xs text-neutral-500">
        Discrete stance classifier (LLM at temp 0). Cross-validates the register chart:
        Coinbase peaks affirming_dei ~2021–22 then mission_focus_apolitical from 2024; Palantir
        should show civilizational_mission from 2025.
      </p>
    </div>
  );
}
