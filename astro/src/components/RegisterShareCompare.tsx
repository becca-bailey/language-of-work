"use client";

import { useMemo } from "react";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleBand, scaleLinear, scaleOrdinal } from "@visx/scale";
import { Bar } from "@visx/shape";
import type { DeiData } from "@/lib/data";
import {
  DEI_REGISTER_ORDER,
  DEI_REGISTER_COLORS,
  registerSharesFromDei,
  type CompanyRegisterShare,
} from "@/lib/deiRegisters";

const REGISTER_ORDER = DEI_REGISTER_ORDER;
const COLORS = DEI_REGISTER_COLORS;

const MARGIN = { top: 8, right: 8, bottom: 8, left: 88 };

function Chart({
  rows,
  width,
  height,
}: {
  rows: CompanyRegisterShare[];
  width: number;
  height: number;
}) {
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const yScale = useMemo(
    () =>
      scaleBand({
        domain: rows.map((r) => r.displayName),
        range: [0, innerH],
        padding: 0.25,
      }),
    [rows, innerH]
  );
  const xScale = useMemo(
    () => scaleLinear({ domain: [0, 1], range: [0, innerW] }),
    [innerW]
  );
  const colorScale = scaleOrdinal({
    domain: REGISTER_ORDER as unknown as string[],
    range: REGISTER_ORDER.map((r) => COLORS[r]),
  });

  return (
    <svg width={width} height={height} role="img" aria-label="DEI register share by company">
      <Group left={MARGIN.left} top={MARGIN.top}>
        {rows.map((row) => {
          const y = yScale(row.displayName) ?? 0;
          const barH = yScale.bandwidth();
          let x0 = 0;
          return REGISTER_ORDER.map((reg) => {
            const share = row.shares[reg] ?? 0;
            if (share <= 0) return null;
            const w = xScale(share);
            const bar = (
              <Bar
                key={`${row.company}-${reg}`}
                x={x0}
                y={y}
                width={w}
                height={barH}
                fill={colorScale(reg)}
              />
            );
            x0 += w;
            return bar;
          });
        })}
        {rows.map((row) => {
          const y = (yScale(row.displayName) ?? 0) + yScale.bandwidth() / 2;
          return (
            <text
              key={row.company}
              x={-8}
              y={y}
              textAnchor="end"
              dominantBaseline="middle"
              className="fill-neutral-600 text-[11px] dark:fill-neutral-400"
            >
              {row.displayName}
            </text>
          );
        })}
      </Group>
    </svg>
  );
}

export default function RegisterShareCompare({
  datasets,
}: {
  datasets: DeiData[];
}) {
  const rows = useMemo(
    () => datasets.map(registerSharesFromDei),
    [datasets]
  );
  const height = Math.max(120, rows.length * 48 + MARGIN.top + MARGIN.bottom);

  return (
    <div>
      <div className="w-full" style={{ height }}>
        <ParentSize>
          {({ width, height: h }) =>
            width > 0 ? <Chart rows={rows} width={width} height={h} /> : null
          }
        </ParentSize>
      </div>
      <div className="mt-2 flex flex-wrap gap-3 text-[10px] text-neutral-500">
        {REGISTER_ORDER.map((reg) => (
          <span key={reg} className="flex items-center gap-1">
            <span
              className="inline-block h-2 w-2 rounded-sm"
              style={{ backgroundColor: COLORS[reg] }}
            />
            {reg.replace(/_/g, " ")}
          </span>
        ))}
      </div>
      <p className="mt-2 text-xs text-neutral-500">
        Share of DEI-register chunks (excluding absent) across all measured years.
        Compares <em>what kind</em> of language, not how much.
      </p>
    </div>
  );
}
