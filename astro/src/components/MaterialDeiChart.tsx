"use client";

import { useCallback, useMemo } from "react";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { curveMonotoneX } from "@visx/curve";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleLinear } from "@visx/scale";
import { Area } from "@visx/shape";
import { TooltipWithBounds, useTooltip } from "@visx/tooltip";
import { bisector } from "d3-array";
import { localPoint } from "@visx/event";
import { useThemeColors } from "@/lib/themeColors";

interface Component {
  id: string;
  label: string;
  values: number[];
}
export interface MaterialDeiData {
  years: number[];
  components: Component[];
}
interface Row {
  year: number;
  bands: { id: string; label: string; y0: number; y1: number; v: number; color: string }[];
  total: number;
}

const MARGIN = { top: 12, right: 16, bottom: 30, left: 36 };
// validated categorical set (7 bands) — CVD all-pairs worst dE 12.9
const COLORS = ["#5e1af4", "#2a78d6", "#1baf7a", "#eda100", "#ff6230", "#e34948", "#e87ba4"];
const bisectYear = bisector<Row, number>((d) => d.year).center;

function Chart({ data, width, height }: { data: MaterialDeiData; width: number; height: number }) {
  const theme = useThemeColors();
  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } = useTooltip<Row>();
  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;
  const surface = theme.resolve("--background") || "#fff";

  const rows: Row[] = useMemo(() => {
    return data.years.map((year, i) => {
      let cum = 0;
      const bands = data.components.map((c, ci) => {
        const v = c.values[i] ?? 0;
        const band = { id: c.id, label: c.label, y0: cum, y1: cum + v, v, color: COLORS[ci % COLORS.length] };
        cum += v;
        return band;
      });
      return { year, bands, total: cum };
    });
  }, [data]);

  const xScale = useMemo(
    () => scaleLinear({ domain: [data.years[0], data.years[data.years.length - 1]], range: [0, innerW] }),
    [data.years, innerW]
  );
  const yScale = useMemo(
    () => scaleLinear({ domain: [0, Math.max(...rows.map((r) => r.total)) * 1.08 || 1], range: [innerH, 0] }),
    [rows, innerH]
  );
  const tickValues = useMemo(() => {
    const t: number[] = [];
    for (let y = Math.ceil(data.years[0] / 2) * 2; y <= data.years[data.years.length - 1]; y += 2) t.push(y);
    return t;
  }, [data.years]);

  const nearest = useCallback(
    (e: React.MouseEvent<SVGRectElement>) => {
      const pt = localPoint(e);
      if (!pt) return null;
      return rows[bisectYear(rows, xScale.invert(pt.x - MARGIN.left))] ?? null;
    },
    [rows, xScale]
  );

  if (innerW <= 0 || innerH <= 0) return null;

  return (
    <div className="relative">
      <svg width={width} height={height} role="img" aria-label="DEI-adjacent benefit mentions by type over time">
        <Group left={MARGIN.left} top={MARGIN.top}>
          {data.components.map((c, ci) => (
            <Area
              key={c.id}
              data={rows}
              x={(d) => xScale(d.year)}
              y0={(d) => yScale(d.bands[ci].y0)}
              y1={(d) => yScale(d.bands[ci].y1)}
              curve={curveMonotoneX}
            >
              {({ path }) => (
                <path d={path(rows) || ""} fill={COLORS[ci % COLORS.length]} stroke={surface} strokeWidth={1} />
              )}
            </Area>
          ))}
          <AxisBottom top={innerH} scale={xScale} tickFormat={(v) => String(v)} tickValues={tickValues}
            tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "middle" }}
            stroke="currentColor" tickStroke="currentColor" axisClassName="text-neutral-400 dark:text-neutral-600" />
          <AxisLeft scale={yScale} numTicks={4}
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
          <dl className="mt-1 space-y-0.5 text-neutral-600 dark:text-neutral-300">
            {[...tooltipData.bands].reverse().filter((b) => b.v > 0).map((b) => (
              <div key={b.id} className="flex items-center justify-between gap-3">
                <dt className="flex items-center gap-1.5">
                  <span className="inline-block h-2 w-2 rounded-sm" style={{ background: b.color }} />
                  {b.label}
                </dt>
                <dd className="font-mono">{b.v.toFixed(1)}</dd>
              </div>
            ))}
          </dl>
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function MaterialDeiChart({ data }: { data: MaterialDeiData }) {
  const legend = data.components;
  return (
    <div>
      <div className="mb-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-neutral-600 dark:text-neutral-300">
        {legend.map((c, i) => (
          <span key={c.id} className="flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ background: COLORS[i % COLORS.length] }} />
            {c.label}
          </span>
        ))}
      </div>
      <div className="h-80 w-full">
        <ParentSize>{({ width, height }) => (width > 0 ? <Chart data={data} width={width} height={height} /> : null)}</ParentSize>
      </div>
    </div>
  );
}
