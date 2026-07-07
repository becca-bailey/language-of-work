"use client";

import { useCallback, useMemo } from "react";
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

export interface ConcessionRow {
  year: number;
  careZ: number;
  deiZ: number;
  quits: number | null;
  quitsZ?: number;
}

const MARGIN = { top: 16, right: 96, bottom: 36, left: 44 };
const bisectYear = bisector<ConcessionRow, number>((d) => d.year).center;

function Chart({ rows, width, height }: { rows: ConcessionRow[]; width: number; height: number }) {
  const theme = useThemeColors();
  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } = useTooltip<ConcessionRow>();
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  // z-score quits within the shown window so all three sit on one (standardized) axis.
  const data = useMemo(() => {
    const q = rows.map((r) => r.quits).filter((v): v is number => v != null);
    const m = q.reduce((a, b) => a + b, 0) / q.length;
    const sd = Math.sqrt(q.reduce((a, b) => a + (b - m) ** 2, 0) / q.length) || 1;
    return rows.map((r) => ({ ...r, quitsZ: r.quits != null ? (r.quits - m) / sd : undefined }));
  }, [rows]);

  const series = [
    { key: "careZ" as const, label: "Care talk", token: "--chart-1", dash: undefined },
    { key: "deiZ" as const, label: "DEI talk", token: "--chart-2", dash: undefined },
    { key: "quitsZ" as const, label: "Quits rate", token: "--muted", dash: "6 4" },
  ];

  const xScale = useMemo(() => {
    const [min, max] = extent(data, (d) => d.year) as [number, number];
    return scaleLinear({ domain: [min, max], range: [0, innerW] });
  }, [data, innerW]);

  const yScale = useMemo(() => {
    const vals = data.flatMap((d) => [d.careZ, d.deiZ, d.quitsZ].filter((v): v is number => v != null));
    const [min, max] = extent(vals) as [number, number];
    const pad = (max - min) * 0.12 || 1;
    return scaleLinear({ domain: [min - pad, max + pad], range: [innerH, 0] });
  }, [data, innerH]);

  const tickValues = useMemo(() => {
    const [min, max] = extent(data, (d) => d.year) as [number, number];
    const t: number[] = [];
    for (let y = Math.ceil(min / 2) * 2; y <= max; y += 2) t.push(y);
    if (t[t.length - 1] !== max) t.push(max);
    return t;
  }, [data]);

  const nearestRow = useCallback(
    (event: React.MouseEvent<SVGRectElement>) => {
      const point = localPoint(event);
      if (!point) return null;
      const year = xScale.invert(point.x - MARGIN.left);
      return data[bisectYear(data, year)] ?? null;
    },
    [data, xScale]
  );

  if (innerW <= 0 || innerH <= 0) return null;
  const color = (t: string) => theme.resolve(t);
  const last = data[data.length - 1];

  return (
    <div className="relative">
      <svg width={width} height={height} role="img" aria-label="Care and DEI rhetoric vs the quits rate, standardized">
        <Group left={MARGIN.left} top={MARGIN.top}>
          <GridRows scale={yScale} width={innerW} strokeDasharray="2 4" className="stroke-neutral-200 dark:stroke-neutral-800" />
          <line x1={0} x2={innerW} y1={yScale(0)} y2={yScale(0)} className="stroke-neutral-300 dark:stroke-neutral-700" />

          {series.map((s) => (
            <LinePath
              key={s.key}
              data={data.filter((d) => d[s.key] != null)}
              x={(d) => xScale(d.year)}
              y={(d) => yScale(d[s.key] as number)}
              curve={curveMonotoneX}
              strokeWidth={s.key === "quitsZ" ? 1.5 : 2.5}
              strokeDasharray={s.dash}
              fill="none"
              stroke={color(s.token)}
            />
          ))}

          {series.map((s) => (
            <text key={`l-${s.key}`} x={innerW + 6} y={yScale(last[s.key] as number)} dominantBaseline="middle" fontSize={11} fontWeight={600} fill={color(s.token)}>
              {s.label}
            </text>
          ))}

          <AxisBottom top={innerH} scale={xScale} tickFormat={(v) => String(v)} tickValues={tickValues}
            tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "middle" }}
            stroke="currentColor" tickStroke="currentColor" axisClassName="text-neutral-400 dark:text-neutral-600" />
          <AxisLeft scale={yScale} numTicks={5} label="standardized (z)"
            labelProps={{ className: "fill-neutral-500 text-[11px]" }}
            tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "end", dx: -4 }}
            stroke="currentColor" tickStroke="currentColor" axisClassName="text-neutral-400 dark:text-neutral-600" />

          <rect width={innerW} height={innerH} fill="transparent"
            onMouseMove={(e) => {
              const row = nearestRow(e);
              if (!row) return;
              showTooltip({ tooltipData: row, tooltipLeft: MARGIN.left + xScale(row.year), tooltipTop: MARGIN.top + 8 });
            }}
            onMouseLeave={hideTooltip} />
        </Group>
      </svg>

      {tooltipData && (
        <TooltipWithBounds left={tooltipLeft} top={tooltipTop} unstyled applyPositionStyle
          className="pointer-events-none rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs shadow-md dark:border-neutral-700 dark:bg-neutral-900">
          <p className="font-semibold">{tooltipData.year}</p>
          <dl className="mt-1 space-y-0.5 font-mono text-neutral-600 dark:text-neutral-300">
            <div className="flex justify-between gap-4"><dt style={{ color: color("--chart-1") }}>care</dt><dd>{tooltipData.careZ.toFixed(2)}</dd></div>
            <div className="flex justify-between gap-4"><dt style={{ color: color("--chart-2") }}>DEI</dt><dd>{tooltipData.deiZ.toFixed(2)}</dd></div>
            {tooltipData.quits != null && (
              <div className="flex justify-between gap-4"><dt>quits</dt><dd>{tooltipData.quits.toFixed(1)}%</dd></div>
            )}
          </dl>
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function ConcessionChart({ rows }: { rows: ConcessionRow[] }) {
  return (
    <div className="h-90 w-full">
      <ParentSize>{({ width, height }) => (width > 0 ? <Chart rows={rows} width={width} height={height} /> : null)}</ParentSize>
    </div>
  );
}
