"use client";

import { useMemo, useState } from "react";
import { AxisBottom } from "@visx/axis";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleLinear } from "@visx/scale";
import { LinePath } from "@visx/shape";
import { curveMonotoneX } from "@visx/curve";
import { TooltipWithBounds, useTooltip } from "@visx/tooltip";
import { localPoint } from "@visx/event";
import { useThemeColors } from "@/lib/themeColors";

// --- data shape (matches the worldChanging series in altruism.json) ---
export interface AltruismPoint {
  year: number;
  zscore: number | null;
  control?: number | null;
  quote?: string;
  thin?: boolean;
}
export interface AltruismCompany {
  id: string;
  displayName: string;
  worldChanging: AltruismPoint[];
}

interface Props {
  companies: AltruismCompany[];
  featured?: string;
  metricLabel?: string;
}

const FOCUS_TOKEN = "--info"; // the company in focus
const CTRL_TOKEN = "--muted"; // the dotted control line
const MARGIN = { top: 22, right: 16, bottom: 28, left: 30 };
const HEIGHT = 280;

type Mode = "aggregate" | "company";
type Tip = { year: number; label: string; z: number | null; quote?: string };

function pointsOf(c: AltruismCompany): AltruismPoint[] {
  return c.worldChanging.filter((p) => p.zscore !== null);
}

/** Mean idealism per year across all companies that have a value that year. */
function aggregateSeries(companies: AltruismCompany[]): AltruismPoint[] {
  const byYear = new Map<number, number[]>();
  for (const c of companies)
    for (const p of c.worldChanging)
      if (p.zscore !== null) (byYear.get(p.year) ?? byYear.set(p.year, []).get(p.year)!).push(p.zscore);
  return [...byYear.entries()]
    .map(([year, vs]) => ({ year, zscore: vs.reduce((a, b) => a + b, 0) / vs.length }))
    .sort((a, b) => a.year - b.year);
}

function peakOf(pts: AltruismPoint[]): AltruismPoint | null {
  return pts.reduce<AltruismPoint | null>(
    (best, p) => (best === null || (p.zscore ?? -Infinity) > (best.zscore ?? -Infinity) ? p : best),
    null
  );
}

function Chart({ companies, width, featured, metricLabel }: Props & { width: number }) {
  const theme = useThemeColors(); // resolve tokens to hex for SVG stroke
  const FOCUS = theme.resolve(FOCUS_TOKEN);
  const CTRL = theme.resolve(CTRL_TOKEN);
  const initial = featured && companies.some((c) => c.id === featured) ? featured : companies[0]?.id;
  const [mode, setMode] = useState<Mode>("company");
  const [selected, setSelected] = useState<string>(initial);
  const [hoverYear, setHoverYear] = useState<number | null>(null);
  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } = useTooltip<Tip>();

  const agg = useMemo(() => aggregateSeries(companies), [companies]);
  const focus = companies.find((c) => c.id === selected) ?? companies[0];
  const focusPts = useMemo(() => (focus ? pointsOf(focus) : []), [focus]);
  const peak = useMemo(() => peakOf(focusPts), [focusPts]);

  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = HEIGHT - MARGIN.top - MARGIN.bottom;

  const allYears = companies.flatMap((c) => c.worldChanging.map((p) => p.year));
  const xMin = Math.min(...allYears);
  const xMax = Math.max(...allYears);
  const allZ = [
    ...companies.flatMap((c) => c.worldChanging.map((p) => p.zscore ?? 0)),
    ...agg.map((p) => p.zscore ?? 0),
  ];
  const yLo = Math.min(...allZ, 0) - 0.3;
  const yHi = Math.max(...allZ, 0) + 0.3;

  const xScale = useMemo(() => scaleLinear({ domain: [xMin, xMax], range: [0, innerW] }), [innerW, xMin, xMax]);
  const yScale = useMemo(() => scaleLinear({ domain: [yLo, yHi], range: [innerH, 0] }), [innerH, yLo, yHi]);
  if (innerW <= 0) return null;

  const companyMode = mode === "company";
  const zeroY = yScale(0);

  return (
    <div className="relative">
      <div className="mb-3 flex flex-wrap items-center gap-3 text-xs">
        <div className="inline-flex overflow-hidden rounded border border-neutral-300 dark:border-neutral-700">
          {(["company", "aggregate"] as const).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`px-2.5 py-1 ${mode === m ? "bg-neutral-800 text-white dark:bg-neutral-200 dark:text-neutral-900" : "text-neutral-600 dark:text-neutral-400"}`}
            >
              {m === "company" ? "By company" : "Industry average"}
            </button>
          ))}
        </div>
        {companyMode && (
          <div className="flex flex-wrap gap-1.5 text-neutral-500">
            {companies.map((c) => (
              <button
                key={c.id}
                onClick={() => setSelected(c.id)}
                className={`rounded px-1.5 py-0.5 ${c.id === selected ? "bg-info text-white" : "bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-800 dark:hover:bg-neutral-700"}`}
              >
                {c.displayName}
              </button>
            ))}
          </div>
        )}
      </div>

      <svg width={width} height={HEIGHT} role="img" aria-label={metricLabel ?? "Idealism over time"}>
        <Group left={MARGIN.left} top={MARGIN.top}>
          {/* zero baseline */}
          <line x1={0} x2={innerW} y1={zeroY} y2={zeroY} strokeDasharray="2 3" className="stroke-neutral-300 dark:stroke-neutral-700" />

          {/* faded context: every company */}
          {companies.map((c) => {
            const isFocus = companyMode && c.id === selected;
            if (isFocus) return null;
            return (
              <LinePath
                key={c.id}
                data={pointsOf(c)}
                x={(d) => xScale(d.year)}
                y={(d) => yScale(d.zscore ?? 0)}
                curve={curveMonotoneX}
                stroke={CTRL}
                strokeWidth={1}
                strokeOpacity={companyMode ? 0.18 : 0.3}
                fill="none"
              />
            );
          })}

          {/* aggregate mode: bold mean line */}
          {!companyMode && (
            <LinePath data={agg} x={(d) => xScale(d.year)} y={(d) => yScale(d.zscore ?? 0)} curve={curveMonotoneX} stroke={FOCUS} strokeWidth={2.5} fill="none" />
          )}

          {/* company mode: focus line + dotted control + points + peak */}
          {companyMode && focus && (
            <>
              <LinePath
                data={focus.worldChanging.filter((p) => p.control != null)}
                x={(d) => xScale(d.year)}
                y={(d) => yScale(d.control ?? 0)}
                curve={curveMonotoneX}
                stroke={CTRL}
                strokeWidth={1.25}
                strokeDasharray="3 3"
                fill="none"
              />
              <LinePath data={focusPts} x={(d) => xScale(d.year)} y={(d) => yScale(d.zscore ?? 0)} curve={curveMonotoneX} stroke={FOCUS} strokeWidth={2.5} fill="none" />
              {focusPts.map((p) => (
                <circle
                  key={p.year}
                  cx={xScale(p.year)}
                  cy={yScale(p.zscore ?? 0)}
                  r={hoverYear === p.year ? 4 : 2.5}
                  fill={p.thin ? "white" : FOCUS}
                  stroke={FOCUS}
                  strokeWidth={p.thin ? 1.5 : 0}
                />
              ))}
              {peak && (
                <text x={xScale(peak.year)} y={yScale(peak.zscore ?? 0) - 8} textAnchor="middle" className="fill-info text-[10px] font-medium">
                  peak ’{String(peak.year).slice(2)}
                </text>
              )}
            </>
          )}

          {/* crosshair + hover capture */}
          {hoverYear !== null && (
            <line x1={xScale(hoverYear)} x2={xScale(hoverYear)} y1={0} y2={innerH} className="stroke-neutral-400" strokeWidth={1} strokeOpacity={0.5} />
          )}
          <rect
            x={0}
            y={0}
            width={innerW}
            height={innerH}
            fill="transparent"
            onMouseMove={(ev) => {
              const pt = localPoint(ev);
              if (!pt) return;
              const yr = Math.round(xScale.invert(pt.x - MARGIN.left));
              setHoverYear(yr);
              if (companyMode && focus) {
                const p = focus.worldChanging.find((q) => q.year === yr && q.zscore !== null);
                if (p) showTooltip({ tooltipData: { year: yr, label: focus.displayName, z: p.zscore, quote: p.quote }, tooltipLeft: pt.x, tooltipTop: pt.y });
              } else {
                const a = agg.find((q) => q.year === yr);
                if (a) showTooltip({ tooltipData: { year: yr, label: `Industry average (${companies.length})`, z: a.zscore ?? null }, tooltipLeft: pt.x, tooltipTop: pt.y });
              }
            }}
            onMouseLeave={() => { setHoverYear(null); hideTooltip(); }}
          />

          <AxisBottom top={innerH} scale={xScale} numTicks={7} tickFormat={(v) => String(v)} tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "middle" }} stroke="currentColor" tickStroke="currentColor" axisClassName="text-neutral-400 dark:text-neutral-600" />
        </Group>
      </svg>

      <figcaption className="mt-2 max-w-prose text-xs text-neutral-500">
        {metricLabel ?? "Idealism"} over time.{" "}
        {companyMode ? (
          <>The <span style={{ color: FOCUS }}>solid line</span> is the company in focus; the <span className="text-neutral-400">dotted line</span> tracks how much its page changed (signal vs. churn). Hollow points are thin years (few chunks). Hover for the year and the most idealistic line measured.</>
        ) : (
          <>The bold line is the mean across {companies.length} companies; faded lines are the individual firms.</>
        )}
      </figcaption>

      {tooltipData && (
        <TooltipWithBounds left={tooltipLeft} top={tooltipTop} unstyled applyPositionStyle className="pointer-events-none max-w-xs rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs shadow-md dark:border-neutral-700 dark:bg-neutral-900">
          <p className="font-semibold">{tooltipData.year} · {tooltipData.label}</p>
          <p className="mt-0.5 text-neutral-500">idealism: {tooltipData.z === null ? "–" : tooltipData.z.toFixed(2)}</p>
          {tooltipData.quote && <p className="mt-1 border-l-2 border-info pl-2 italic text-neutral-600 dark:text-neutral-300">“{tooltipData.quote}”</p>}
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function AltruismExplorer({ companies, featured, metricLabel }: Props) {
  return <ParentSize initialSize={{ width: 640, height: 320 }}>{({ width }) => (width > 0 ? <Chart companies={companies} width={width} featured={featured} metricLabel={metricLabel} /> : null)}</ParentSize>;
}
