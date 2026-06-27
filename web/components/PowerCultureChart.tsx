"use client";

import { useMemo, useState } from "react";
import { AxisBottom } from "@visx/axis";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleLinear } from "@visx/scale";
import { AreaClosed, LinePath } from "@visx/shape";
import { curveMonotoneX } from "@visx/curve";
import { TooltipWithBounds, useTooltip } from "@visx/tooltip";
import { localPoint } from "@visx/event";
import type { PowerStory, PowerMetric } from "@/lib/powerStory";

const X_MIN = 2013;
const X_MAX = 2026;
const MARGIN = { top: 18, right: 18, bottom: 26, left: 12 };
const PANEL_H = 92;
const PANEL_GAP = 14;
const COLOR: Record<string, string> = {
  optimism: "#6366f1",
  workers: "#10b981",
  management: "#ef4444",
  wellbeing: "#14b8a6",
};

type Tip =
  | { kind: "cross"; year: number }
  | { kind: "event"; label: string; date: string; ekind: string };

function valueAt(metric: PowerMetric, company: string | null, year: number): number | null {
  const src = company
    ? metric.perCompany.find((c) => c.id === company)?.series
    : metric.series;
  const p = src?.find((s) => s.year === year);
  return p ? p.norm : null;
}

function Chart({ data, width }: { data: PowerStory; width: number }) {
  const [mode, setMode] = useState<"aggregate" | "company">("aggregate");
  const [hoverCo, setHoverCo] = useState<string | null>(null);
  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } =
    useTooltip<Tip>();

  const metrics = data.metrics;
  const innerW = width - MARGIN.left - MARGIN.right;
  const totalH = MARGIN.top + MARGIN.bottom + metrics.length * (PANEL_H + PANEL_GAP);
  const xScale = useMemo(() => scaleLinear({ domain: [X_MIN, X_MAX], range: [0, innerW] }), [innerW]);
  const yScale = useMemo(() => scaleLinear({ domain: [0, 1], range: [PANEL_H, 0] }), []);
  const power = data.power.series.filter((p) => p.year >= X_MIN);
  const events = data.events.filter((e) => e.year >= X_MIN);
  const companies = metrics[0]?.perCompany.map((c) => ({ id: c.id, name: c.displayName })) ?? [];

  const crossYear = tooltipData?.kind === "cross" ? tooltipData.year : null;
  if (innerW <= 0) return null;

  return (
    <div className="relative">
      {/* controls */}
      <div className="mb-3 flex flex-wrap items-center gap-3 text-xs">
        <div className="inline-flex overflow-hidden rounded border border-neutral-300 dark:border-neutral-700">
          {(["aggregate", "company"] as const).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`px-2.5 py-1 ${mode === m ? "bg-neutral-800 text-white dark:bg-neutral-200 dark:text-neutral-900" : "text-neutral-600 dark:text-neutral-400"}`}
            >
              {m === "aggregate" ? "Industry average" : "By company"}
            </button>
          ))}
        </div>
        {mode === "company" && (
          <div className="flex flex-wrap gap-1.5 text-neutral-500">
            {companies.map((c) => (
              <span
                key={c.id}
                onMouseEnter={() => setHoverCo(c.id)}
                onMouseLeave={() => setHoverCo(null)}
                className={`cursor-default rounded px-1.5 py-0.5 ${hoverCo === c.id ? "bg-neutral-800 text-white dark:bg-neutral-200 dark:text-neutral-900" : "bg-neutral-100 dark:bg-neutral-800"}`}
              >
                {c.name}
              </span>
            ))}
          </div>
        )}
      </div>

      <svg width={width} height={totalH} role="img" aria-label="Culture language vs worker power">
        {metrics.map((m, i) => {
          const top = MARGIN.top + i * (PANEL_H + PANEL_GAP);
          const color = COLOR[m.benefits];
          return (
            <Group key={m.id} left={MARGIN.left} top={top}>
              <AreaClosed data={power} x={(d) => xScale(d.year)} y={(d) => yScale(d.norm)}
                yScale={yScale} curve={curveMonotoneX}
                className="fill-neutral-200/60 dark:fill-neutral-700/40" />

              {/* events */}
              {events.map((e, j) => (
                <line key={j} x1={xScale(e.year)} x2={xScale(e.year)} y1={0} y2={PANEL_H}
                  strokeDasharray="3 3" className="stroke-amber-400/50" />
              ))}

              {/* lines */}
              {mode === "company"
                ? m.perCompany.map((c) => {
                    const hot = hoverCo === c.id;
                    return (
                      <LinePath key={c.id} data={c.series} x={(d) => xScale(d.year)}
                        y={(d) => yScale(d.norm)} curve={curveMonotoneX}
                        stroke={hot ? color : "#9ca3af"} strokeWidth={hot ? 2.5 : 1}
                        strokeOpacity={hot ? 1 : hoverCo ? 0.15 : 0.35} fill="none" />
                    );
                  })
                : (
                  <>
                    <LinePath data={m.series} x={(d) => xScale(d.year)} y={(d) => yScale(d.norm)}
                      curve={curveMonotoneX} stroke={color} strokeWidth={2.5} fill="none" />
                    {m.series.map((s) => (
                      <circle key={s.year} cx={xScale(s.year)} cy={yScale(s.norm)} r={2.5} fill={color} />
                    ))}
                  </>
                )}

              {/* crosshair */}
              {crossYear !== null && (
                <line x1={xScale(crossYear)} x2={xScale(crossYear)} y1={0} y2={PANEL_H}
                  className="stroke-neutral-400" strokeWidth={1} />
              )}

              {/* crosshair capture (under the event hit areas, which sit on top) */}
              <rect x={0} y={0} width={innerW} height={PANEL_H} fill="transparent"
                onMouseMove={(ev) => {
                  const pt = localPoint(ev); if (!pt) return;
                  const yr = Math.round(xScale.invert(pt.x - MARGIN.left));
                  if (yr < X_MIN || yr > X_MAX) return;
                  showTooltip({ tooltipData: { kind: "cross", year: yr }, tooltipLeft: pt.x, tooltipTop: pt.y });
                }}
                onMouseLeave={hideTooltip} />

              <text x={4} y={-5} className="fill-neutral-700 text-[11px] font-medium dark:fill-neutral-300">
                {m.label}
              </text>

              {/* event hit areas (hover) — on top */}
              {events.map((e, j) => (
                <rect key={`h${j}`} x={xScale(e.year) - 4} y={0} width={8} height={PANEL_H}
                  fill="transparent" style={{ cursor: "pointer" }}
                  onMouseEnter={(ev) => {
                    const pt = localPoint(ev); if (!pt) return;
                    showTooltip({ tooltipData: { kind: "event", label: e.label, date: e.date, ekind: e.kind }, tooltipLeft: pt.x, tooltipTop: pt.y });
                  }}
                  onMouseLeave={hideTooltip} />
              ))}

              {i === metrics.length - 1 && (
                <AxisBottom top={PANEL_H} scale={xScale} numTicks={7} tickFormat={(v) => String(v)}
                  tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "middle" }}
                  stroke="currentColor" tickStroke="currentColor"
                  axisClassName="text-neutral-400 dark:text-neutral-600" />
              )}
            </Group>
          );
        })}
      </svg>

      <figcaption className="mt-2 max-w-prose text-xs text-neutral-500">
        Each panel: the language metric (line) over the{" "}
        <span className="rounded bg-neutral-200/80 px-1 dark:bg-neutral-700/60">shaded worker-power band</span>{" "}
        (quits rate, normalized). Toggle to <em>By company</em> and hover a name to trace one
        firm. Hover a dashed line for the power event. n = {data.companies.length} companies.
      </figcaption>

      {tooltipData && (
        <TooltipWithBounds left={tooltipLeft} top={tooltipTop} unstyled applyPositionStyle
          className="pointer-events-none max-w-xs rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs shadow-md dark:border-neutral-700 dark:bg-neutral-900">
          {tooltipData.kind === "event" ? (
            <>
              <p className="font-semibold">{tooltipData.date}</p>
              <p className="mt-0.5 text-neutral-600 dark:text-neutral-300">{tooltipData.label}</p>
              <p className="mt-0.5 text-[10px] uppercase tracking-wide text-amber-600">{tooltipData.ekind}</p>
            </>
          ) : (
            <>
              <p className="font-semibold">
                {tooltipData.year}
                {mode === "company" && hoverCo ? ` · ${companies.find((c) => c.id === hoverCo)?.name}` : ""}
              </p>
              <p className="mt-0.5 text-neutral-500">
                worker power: {(power.find((p) => p.year === tooltipData.year)?.norm ?? 0).toFixed(2)}
              </p>
              {metrics.map((m) => {
                const v = valueAt(m, mode === "company" ? hoverCo : null, tooltipData.year);
                return (
                  <p key={m.id} style={{ color: COLOR[m.benefits] }}>
                    {m.id}: {v === null ? "–" : v.toFixed(2)}
                  </p>
                );
              })}
            </>
          )}
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function PowerCultureChart({ data }: { data: PowerStory }) {
  return (
    <ParentSize>
      {({ width }) => (width > 0 ? <Chart data={data} width={width} /> : null)}
    </ParentSize>
  );
}
