"use client";

import { useMemo, useState } from "react";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { curveMonotoneX } from "@visx/curve";
import { GridRows } from "@visx/grid";
import { Group } from "@visx/group";
import { ParentSize } from "@visx/responsive";
import { scaleLinear } from "@visx/scale";
import { AreaClosed, LinePath } from "@visx/shape";
import { extent } from "d3-array";
import type { TimelineEvent } from "@/lib/events";
import type { StoryCompanyEnvelope, StoryEnvelopeQuote } from "@/lib/storyTypes";

const MARGIN = { top: 24, right: 24, bottom: 40, left: 52 };
const DEFAULT_COMPANY = "coinbase";

const REGISTER_STYLES: Record<string, string> = {
  explicit_demographic: "bg-emerald-100 text-emerald-800",
  structural_process: "bg-teal-100 text-teal-800",
  aspirational_vague: "bg-indigo-100 text-indigo-800",
  belonging_culture: "bg-violet-100 text-violet-800",
  meritocracy: "bg-amber-100 text-amber-800",
  civilizational_mission: "bg-red-100 text-red-800",
};

interface Props {
  envelopes: StoryCompanyEnvelope[];
  events?: TimelineEvent[];
}

type EnvelopeMode = "diff" | "bipolar";

interface EnvelopePoint {
  year: number;
  max?: number;
  min?: number;
  churn?: number;
}

function numOrUndefined(v: number | null | undefined): number | undefined {
  return typeof v === "number" && Number.isFinite(v) ? v : undefined;
}

function QuoteCard({ label, quote }: { label: string; quote: StoryEnvelopeQuote }) {
  const reg = quote.register ?? "";
  return (
    <div className="rounded-lg border border-neutral-200 px-3 py-2 dark:border-neutral-800">
      <p className="text-[10px] font-medium uppercase tracking-wide text-neutral-500">{label}</p>
      <p className="mt-1 text-xs leading-relaxed text-neutral-700 dark:text-neutral-300">
        &ldquo;{quote.text}&rdquo;
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2">
        {reg && (
          <span
            className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
              REGISTER_STYLES[reg] ?? "bg-neutral-100 text-neutral-600"
            }`}
          >
            {reg.replace(/_/g, " ")}
          </span>
        )}
        {typeof quote.stanceDiff === "number" && (
          <span className="font-mono text-[10px] text-neutral-400">
            diff {quote.stanceDiff >= 0 ? "+" : ""}
            {quote.stanceDiff.toFixed(3)}
          </span>
        )}
        {typeof quote.stanceProjection === "number" && (
          <span className="font-mono text-[10px] text-neutral-400">
            bipolar {quote.stanceProjection >= 0 ? "+" : ""}
            {quote.stanceProjection.toFixed(3)}
          </span>
        )}
      </div>
    </div>
  );
}

function Chart({
  data,
  events = [],
  mode,
  width,
  height,
  onHoverYear,
}: {
  data: StoryCompanyEnvelope;
  events?: TimelineEvent[];
  mode: EnvelopeMode;
  width: number;
  height: number;
  onHoverYear: (year: number | null) => void;
}) {
  const maxPoints = useMemo(
    () =>
      data.years
        .map((y) => ({
          year: y.year,
          max: numOrUndefined(mode === "bipolar" ? y.bipolarMax : y.stanceMax),
        }))
        .filter((p): p is { year: number; max: number } => p.max !== undefined),
    [data, mode]
  );
  const minPoints = useMemo(
    () =>
      data.years
        .map((y) => ({
          year: y.year,
          min: numOrUndefined(mode === "bipolar" ? y.bipolarMin : y.stanceMin),
        }))
        .filter((p): p is { year: number; min: number } => p.min !== undefined),
    [data, mode]
  );

  const points = useMemo((): EnvelopePoint[] => {
    return data.years
      .map((y) => ({
        year: y.year,
        max: numOrUndefined(mode === "bipolar" ? y.bipolarMax : y.stanceMax),
        min: numOrUndefined(mode === "bipolar" ? y.bipolarMin : y.stanceMin),
        churn: y.textChurn,
      }))
      .filter((p) => p.max !== undefined || p.min !== undefined);
  }, [data, mode]);

  const bandPoints = useMemo(
    () =>
      data.years
        .map((y) => ({
          year: y.year,
          max: numOrUndefined(mode === "bipolar" ? y.bipolarMax : y.stanceMax),
          min: numOrUndefined(mode === "bipolar" ? y.bipolarMin : y.stanceMin),
        }))
        .filter(
          (p): p is { year: number; max: number; min: number } =>
            p.max !== undefined && p.min !== undefined
        ),
    [data, mode]
  );

  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const chartYears = useMemo(
    () => data.years.map((y) => y.year).sort((a, b) => a - b),
    [data]
  );

  const allVals = points.flatMap((p) =>
    [p.max, p.min].filter((v): v is number => v !== undefined)
  );

  const xScale = useMemo(() => {
    const [min, max] = extent(chartYears) as [number, number];
    return scaleLinear({ domain: [min, max], range: [0, innerW] });
  }, [chartYears, innerW]);

  const yScale = useMemo(() => {
    if (!allVals.length) {
      return scaleLinear({ domain: [-0.1, 0.1], range: [innerH, 0] });
    }
    const [min, max] = extent(allVals) as [number, number];
    const pad = Math.max((max - min) * 0.15, 0.03);
    const lo = mode === "diff" ? Math.min(min - pad, 0) : min - pad;
    const hi = mode === "diff" ? Math.max(max + pad, 0) : max + pad;
    return scaleLinear({
      domain: [lo, hi],
      range: [innerH, 0],
    });
  }, [allVals, innerH, mode]);

  const [lo, hi] = yScale.domain();
  const showZero = mode === "diff" && lo <= 0 && hi >= 0;

  if (innerW <= 0 || innerH <= 0 || !points.length) return null;

  const yearMin = chartYears[0];
  const yearMax = chartYears[chartYears.length - 1];

  return (
    <svg
      width={width}
      height={height}
      role="img"
      aria-label={`Stance envelope for ${data.displayName}`}
    >
      <Group left={MARGIN.left} top={MARGIN.top}>
        <GridRows
          scale={yScale}
          width={innerW}
          strokeDasharray="2 4"
          className="stroke-neutral-200 dark:stroke-neutral-800"
        />

        {showZero && (
          <g>
            <line
              x1={0}
              x2={innerW}
              y1={yScale(0)}
              y2={yScale(0)}
              className="stroke-neutral-400"
              strokeWidth={1.5}
            />
            <text
              x={innerW - 4}
              y={yScale(0) - 5}
              textAnchor="end"
              className="fill-neutral-400 text-[9px]"
            >
              inclusion-leaning ↑ / meritocracy-leaning ↓
            </text>
          </g>
        )}

        {events
          .filter((ev) => yearMin !== undefined && yearMax !== undefined && ev.year >= yearMin && ev.year <= yearMax)
          .map((ev) => (
            <g key={ev.id}>
              <line
                x1={xScale(ev.year)}
                x2={xScale(ev.year)}
                y1={0}
                y2={innerH}
                strokeDasharray="4 4"
                className="stroke-amber-400/70"
              />
              <text
                x={xScale(ev.year) + 3}
                y={4}
                transform={`rotate(90, ${xScale(ev.year) + 3}, 4)`}
                className="fill-amber-600 text-[9px]"
              >
                {ev.label}
              </text>
            </g>
          ))}

        {bandPoints.length > 1 && (
          <AreaClosed
            data={bandPoints}
            x={(d) => xScale(d.year)}
            y0={(d) => yScale(d.min)}
            y1={(d) => yScale(d.max)}
            yScale={yScale}
            curve={curveMonotoneX}
            className="fill-emerald-200/40 dark:fill-emerald-900/30"
          />
        )}

        {maxPoints.length > 1 && (
          <LinePath
            data={maxPoints}
            x={(d) => xScale(d.year)}
            y={(d) => yScale(d.max)}
            curve={curveMonotoneX}
            stroke="#059669"
            strokeWidth={2.5}
            fill="none"
          />
        )}
        {minPoints.length > 1 && (
          <LinePath
            data={minPoints}
            x={(d) => xScale(d.year)}
            y={(d) => yScale(d.min)}
            curve={curveMonotoneX}
            stroke="#f59e0b"
            strokeWidth={2.5}
            fill="none"
          />
        )}

        {points.map((d) => (
          <g
            key={d.year}
            onMouseEnter={() => onHoverYear(d.year)}
            onMouseLeave={() => onHoverYear(null)}
          >
            {d.max !== undefined && (
              <circle
                cx={xScale(d.year)}
                cy={yScale(d.max)}
                r={5}
                fill="#059669"
                className="cursor-pointer"
              />
            )}
            {d.min !== undefined && (
              <circle
                cx={xScale(d.year)}
                cy={yScale(d.min)}
                r={5}
                fill="#f59e0b"
                className="cursor-pointer"
              />
            )}
            {d.churn !== undefined && d.churn < 0.2 && (
              <title>{d.year}: mostly stale copy (churn {(d.churn * 100).toFixed(0)}%)</title>
            )}
          </g>
        ))}

        <AxisBottom
          top={innerH}
          scale={xScale}
          tickFormat={(v) => String(v)}
          numTicks={Math.min(chartYears.length, 10)}
          tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "middle" }}
        />
        <AxisLeft
          scale={yScale}
          numTicks={5}
          tickFormat={(v) => Number(v).toFixed(2)}
          tickLabelProps={{ className: "fill-neutral-500 text-[11px]", textAnchor: "end", dx: -4 }}
        />
      </Group>
    </svg>
  );
}

export default function StoryStanceEnvelope({ envelopes, events = [] }: Props) {
  const companies = envelopes.filter((e) =>
    e.years.some(
      (y) =>
        numOrUndefined(y.stanceMax) !== undefined ||
        numOrUndefined(y.stanceMin) !== undefined ||
        numOrUndefined(y.bipolarMax) !== undefined ||
        numOrUndefined(y.bipolarMin) !== undefined
    )
  );
  const [selected, setSelected] = useState(
    companies.find((c) => c.company === DEFAULT_COMPANY)?.company ?? companies[0]?.company ?? ""
  );
  const [hoverYear, setHoverYear] = useState<number | null>(null);
  const [mode, setMode] = useState<EnvelopeMode>("diff");

  const active = companies.find((c) => c.company === selected);
  const hasBipolar = active?.years.some((y) => numOrUndefined(y.bipolarMax) !== undefined);

  const hoverPoint = active?.years.find((y) => y.year === hoverYear);

  if (!companies.length) return null;

  return (
    <div>
      <div className="flex flex-wrap items-center gap-2">
        {companies.map((c) => (
          <button
            key={c.company}
            type="button"
            onClick={() => setSelected(c.company)}
            className={`rounded-full px-3 py-1 text-xs transition-colors ${
              selected === c.company
                ? "bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900"
                : "border border-neutral-300 text-neutral-600 hover:border-neutral-400 dark:border-neutral-700 dark:text-neutral-400"
            }`}
          >
            {c.displayName}
          </button>
        ))}
        {hasBipolar && (
          <div className="ml-auto flex gap-1">
            {(["diff", "bipolar"] as EnvelopeMode[]).map((m) => (
              <button
                key={m}
                type="button"
                onClick={() => setMode(m)}
                className={`rounded-full px-3 py-1 text-[10px] ${
                  mode === m
                    ? "bg-indigo-600 text-white"
                    : "border border-neutral-300 text-neutral-500"
                }`}
              >
                {m === "diff" ? "inclusion − meritocracy" : "bipolar DEI axis"}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="mt-2 flex gap-4 text-xs text-neutral-500">
        <span className="flex items-center gap-1">
          <span className="inline-block h-0.5 w-4 bg-emerald-600" />
          Most inclusion-leaning chunk
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-0.5 w-4 bg-amber-500" />
          Most meritocracy-leaning chunk
        </span>
      </div>

      <div className="mt-4 h-80 w-full">
        {active && (
          <ParentSize>
            {({ width, height }) =>
              width > 0 ? (
                <Chart
                  data={active}
                  events={events}
                  mode={mode}
                  width={width}
                  height={height}
                  onHoverYear={setHoverYear}
                />
              ) : null
            }
          </ParentSize>
        )}
      </div>

      {hoverPoint &&
        (hoverPoint.stanceMaxQuote ||
          hoverPoint.stanceMinQuote ||
          hoverPoint.stanceCounterQuote) && (
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {hoverPoint.stanceMaxQuote && (
            <QuoteCard label={`${hoverYear} — most inclusion-leaning`} quote={hoverPoint.stanceMaxQuote} />
          )}
          {hoverPoint.stanceMinQuote && (
            <QuoteCard label={`${hoverYear} — most meritocracy-leaning`} quote={hoverPoint.stanceMinQuote} />
          )}
          {hoverPoint.stanceCounterQuote &&
            hoverPoint.stanceCounterQuote.text !== hoverPoint.stanceMinQuote?.text &&
            hoverPoint.stanceCounterQuote.text !== hoverPoint.stanceMaxQuote?.text && (
              <QuoteCard
                label={`${hoverYear} — counter-programming`}
                quote={hoverPoint.stanceCounterQuote}
              />
            )}
        </div>
      )}

      <p className="mt-3 text-xs text-neutral-500">
        Green = highest inclusion−meritocracy score among careers-page chunks that year. Orange =
        lowest. The shaded band is the gap between the two extrema.
      </p>
    </div>
  );
}
