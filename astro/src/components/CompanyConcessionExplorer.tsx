"use client";

import { useCallback, useMemo, useState } from "react";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { curveMonotoneX } from "@visx/curve";
import { GridRows } from "@visx/grid";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleLinear } from "@visx/scale";
import { LinePath } from "@visx/shape";
import { TooltipWithBounds, useTooltip } from "@visx/tooltip";
import { bisector, extent } from "d3-array";
import { localPoint } from "@visx/event";
import { useThemeColors } from "@/lib/themeColors";

interface YearRow {
  year: number;
  careZ: number;
  deiZ: number;
}
export interface CompanyTraj {
  id: string;
  displayName: string;
  r: number;
  years: YearRow[];
}

const MARGIN = { top: 16, right: 84, bottom: 34, left: 40 };
const bisectYear = bisector<YearRow, number>((d) => d.year).center;

function Chart({ rows, width, height }: { rows: YearRow[]; width: number; height: number }) {
  const theme = useThemeColors();
  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } = useTooltip<YearRow>();
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const xScale = useMemo(() => {
    const [min, max] = extent(rows, (d) => d.year) as [number, number];
    return scaleLinear({ domain: [min, max], range: [0, innerW] });
  }, [rows, innerW]);
  const yScale = useMemo(() => {
    const vals = rows.flatMap((d) => [d.careZ, d.deiZ]);
    const [min, max] = extent(vals) as [number, number];
    const pad = (max - min) * 0.12 || 1;
    return scaleLinear({ domain: [min - pad, max + pad], range: [innerH, 0] });
  }, [rows, innerH]);
  const tickValues = useMemo(() => {
    const [min, max] = extent(rows, (d) => d.year) as [number, number];
    const t: number[] = [];
    for (let y = Math.ceil(min / 2) * 2; y <= max; y += 2) t.push(y);
    if (t[t.length - 1] !== max) t.push(max);
    return t;
  }, [rows]);

  const nearest = useCallback(
    (e: React.MouseEvent<SVGRectElement>) => {
      const pt = localPoint(e);
      if (!pt) return null;
      return rows[bisectYear(rows, xScale.invert(pt.x - MARGIN.left))] ?? null;
    },
    [rows, xScale]
  );

  if (innerW <= 0 || innerH <= 0) return null;
  const c = (t: string) => theme.resolve(t);
  const last = rows[rows.length - 1];
  const series = [
    { key: "careZ" as const, label: "Care talk", token: "--chart-1" },
    { key: "deiZ" as const, label: "DEI talk", token: "--chart-2" },
  ];

  return (
    <div className="relative">
      <svg width={width} height={height} role="img" aria-label="Care and DEI rhetoric for the selected company">
        <Group left={MARGIN.left} top={MARGIN.top}>
          <GridRows scale={yScale} width={innerW} strokeDasharray="2 4" className="stroke-neutral-200 dark:stroke-neutral-800" />
          <line x1={0} x2={innerW} y1={yScale(0)} y2={yScale(0)} className="stroke-neutral-300 dark:stroke-neutral-700" />
          {series.map((s) => (
            <LinePath key={s.key} data={rows} x={(d) => xScale(d.year)} y={(d) => yScale(d[s.key])}
              curve={curveMonotoneX} strokeWidth={2.5} fill="none" stroke={c(s.token)} />
          ))}
          {series.map((s) => (
            <text key={`l-${s.key}`} x={innerW + 6} y={yScale(last[s.key])} dominantBaseline="middle" fontSize={11} fontWeight={600} fill={c(s.token)}>
              {s.label}
            </text>
          ))}
          <AxisBottom top={innerH} scale={xScale} tickFormat={(v) => String(v)} tickValues={tickValues}
            tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "middle" }}
            stroke="currentColor" tickStroke="currentColor" axisClassName="text-neutral-400 dark:text-neutral-600" />
          <AxisLeft scale={yScale} numTicks={5} label="within-company z"
            labelProps={{ className: "fill-neutral-500 text-[11px]" }}
            tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "end", dx: -4 }}
            stroke="currentColor" tickStroke="currentColor" axisClassName="text-neutral-400 dark:text-neutral-600" />
          <rect width={innerW} height={innerH} fill="transparent"
            onMouseMove={(e) => { const r = nearest(e); if (r) showTooltip({ tooltipData: r, tooltipLeft: MARGIN.left + xScale(r.year), tooltipTop: MARGIN.top + 8 }); }}
            onMouseLeave={hideTooltip} />
        </Group>
      </svg>
      {tooltipData && (
        <TooltipWithBounds left={tooltipLeft} top={tooltipTop} unstyled applyPositionStyle
          className="pointer-events-none rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs shadow-md dark:border-neutral-700 dark:bg-neutral-900">
          <p className="font-semibold">{tooltipData.year}</p>
          <dl className="mt-1 space-y-0.5 font-mono text-neutral-600 dark:text-neutral-300">
            <div className="flex justify-between gap-4"><dt style={{ color: c("--chart-1") }}>care</dt><dd>{tooltipData.careZ.toFixed(2)}</dd></div>
            <div className="flex justify-between gap-4"><dt style={{ color: c("--chart-2") }}>DEI</dt><dd>{tooltipData.deiZ.toFixed(2)}</dd></div>
          </dl>
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function CompanyConcessionExplorer({ companies }: { companies: CompanyTraj[] }) {
  const [selected, setSelected] = useState(companies[0]?.id);
  const active = companies.find((c) => c.id === selected) ?? companies[0];
  if (!active) return null;

  return (
    <div className="my-6">
      <div className="mb-3 flex flex-wrap gap-1.5">
        {companies.map((c) => (
          <button
            key={c.id}
            onClick={() => setSelected(c.id)}
            className={
              "rounded-full border px-2.5 py-1 text-xs transition-colors " +
              (c.id === selected
                ? "border-transparent bg-info text-white"
                : "border-neutral-300 text-neutral-600 hover:border-info hover:text-info dark:border-neutral-700 dark:text-neutral-300")
            }
          >
            {c.displayName}
          </button>
        ))}
      </div>
      <p className="mb-1 text-sm text-neutral-500">
        <span className="font-medium text-neutral-700 dark:text-neutral-200">{active.displayName}</span>
        {" — care & DEI talk move together at "}
        <span className="tabular-nums">r = {active.r >= 0 ? "+" : ""}{active.r.toFixed(2)}</span>
      </p>
      <div className="h-80 w-full">
        <ParentSize initialSize={{ width: 640, height: 320 }}>{({ width, height }) => (width > 0 ? <Chart rows={active.years} width={width} height={height} /> : null)}</ParentSize>
      </div>
    </div>
  );
}
