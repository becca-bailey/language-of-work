"use client";

import { useMemo } from "react";
import { ParentSize } from "@visx/responsive";
import { scaleBand, scaleLinear } from "@visx/scale";
import { allYears, type StoryCompanySeries } from "@/lib/storyTypes";

/** Active (pro-inclusion) registers stack upward; meritocracy stacks downward. */
const ACTIVE_REGISTERS = [
  "explicit_demographic",
  "structural_process",
  "aspirational_vague",
  "belonging_culture",
] as const;

const COLORS: Record<string, string> = {
  explicit_demographic: "#059669",
  structural_process: "#0d9488",
  aspirational_vague: "#6366f1",
  belonging_culture: "#8b5cf6",
  meritocracy: "#f59e0b",
};

const LABELS: Record<string, string> = {
  explicit_demographic: "explicit demographic",
  structural_process: "structural process",
  aspirational_vague: "aspirational vague",
  belonging_culture: "belonging culture",
  meritocracy: "meritocracy / counter-programming",
};

const ROW_H = 96;
const MARGIN = { top: 4, right: 8, bottom: 20, left: 12 };

interface Props {
  companies: StoryCompanySeries[];
}

interface YearShares {
  year: number;
  nChunks: number;
  shares: Record<string, number>;
  meritocracyShare: number;
}

function sharesFor(company: StoryCompanySeries): YearShares[] {
  return company.years
    .filter((y) => y.registers)
    .map((y) => {
      const n = Math.max(y.nChunks, 1);
      const shares: Record<string, number> = {};
      for (const reg of ACTIVE_REGISTERS) {
        shares[reg] = (y.registers?.[reg] ?? 0) / n;
      }
      return {
        year: y.year,
        nChunks: y.nChunks,
        shares,
        meritocracyShare: (y.registers?.meritocracy ?? 0) / n,
      };
    });
}

function CompanyRow({
  company,
  years,
  maxShare,
  width,
}: {
  company: StoryCompanySeries;
  years: number[];
  maxShare: number;
  width: number;
}) {
  const data = useMemo(() => sharesFor(company), [company]);
  const byYear = useMemo(
    () => new Map(data.map((d) => [d.year, d])),
    [data]
  );

  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = ROW_H - MARGIN.top - MARGIN.bottom;
  // Split the vertical space: active stacks up from the baseline, meritocracy hangs below.
  const baseline = innerH * 0.72;

  const xScale = useMemo(
    () =>
      scaleBand({
        domain: years.map(String),
        range: [0, innerW],
        padding: 0.18,
      }),
    [years, innerW]
  );
  const upScale = useMemo(
    () => scaleLinear({ domain: [0, maxShare], range: [0, baseline] }),
    [maxShare, baseline]
  );
  const downScale = useMemo(
    () =>
      scaleLinear({ domain: [0, maxShare], range: [0, innerH - baseline] }),
    [maxShare, innerH, baseline]
  );

  if (innerW <= 0) return null;

  return (
    <svg width={width} height={ROW_H} role="img" aria-label={`${company.displayName} register mix by year`}>
      <g transform={`translate(${MARGIN.left},${MARGIN.top})`}>
        <line
          x1={0}
          x2={innerW}
          y1={baseline}
          y2={baseline}
          className="stroke-neutral-300 dark:stroke-neutral-700"
        />
        {years.map((year) => {
          const d = byYear.get(year);
          const x = xScale(String(year)) ?? 0;
          const w = xScale.bandwidth();
          if (!d) {
            return (
              <rect
                key={year}
                x={x}
                y={baseline - 2}
                width={w}
                height={2}
                className="fill-neutral-200 dark:fill-neutral-800"
              />
            );
          }
          let yCursor = baseline;
          const bars = ACTIVE_REGISTERS.map((reg) => {
            const share = d.shares[reg];
            if (share <= 0) return null;
            const h = upScale(share);
            yCursor -= h;
            return (
              <rect key={reg} x={x} y={yCursor} width={w} height={h} fill={COLORS[reg]}>
                <title>
                  {company.displayName} {year}: {LABELS[reg]} {(share * 100).toFixed(0)}% ({d.nChunks} chunks)
                </title>
              </rect>
            );
          });
          const merH = downScale(d.meritocracyShare);
          return (
            <g key={year}>
              {bars}
              {d.meritocracyShare > 0 && (
                <rect x={x} y={baseline} width={w} height={merH} fill={COLORS.meritocracy}>
                  <title>
                    {company.displayName} {year}: {LABELS.meritocracy}{" "}
                    {(d.meritocracyShare * 100).toFixed(0)}% ({d.nChunks} chunks)
                  </title>
                </rect>
              )}
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

export default function StoryRegisterChart({ companies }: Props) {
  const withRegisters = useMemo(
    () => companies.filter((c) => c.years.some((y) => y.registers)),
    [companies]
  );
  const years = useMemo(() => allYears(withRegisters), [withRegisters]);

  const maxShare = useMemo(() => {
    let max = 0.2;
    for (const c of withRegisters) {
      for (const d of sharesFor(c)) {
        const active = Object.values(d.shares).reduce((a, b) => a + b, 0);
        max = Math.max(max, active, d.meritocracyShare);
      }
    }
    return Math.min(max, 1);
  }, [withRegisters]);

  if (!withRegisters.length) return null;

  return (
    <div className="space-y-1">
      {withRegisters.map((c) => (
        <div key={c.id}>
          <p className="text-[11px] font-medium text-neutral-600 dark:text-neutral-400">
            {c.displayName}
          </p>
          <ParentSize>
            {({ width }) =>
              width > 0 ? (
                <CompanyRow company={c} years={years} maxShare={maxShare} width={width} />
              ) : null
            }
          </ParentSize>
        </div>
      ))}
      <div className="mt-3 flex flex-wrap gap-3 text-[10px] text-neutral-500">
        {[...ACTIVE_REGISTERS, "meritocracy"].map((reg) => (
          <span key={reg} className="flex items-center gap-1">
            <span
              className="inline-block h-2 w-2 rounded-sm"
              style={{ backgroundColor: COLORS[reg] }}
            />
            {LABELS[reg]}
          </span>
        ))}
      </div>
      <p className="mt-1 text-xs text-neutral-500">
        Bars above the line = share of chunks in an active DEI register that year. Bars below
        the line = meritocracy / anti-DEI counter-programming. Thin grey marks = measured
        years with no DEI-register language at all.
      </p>
    </div>
  );
}
