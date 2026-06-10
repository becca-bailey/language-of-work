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

export interface ChartRow {
  year: number;
  value: number | null;
  control: number | null;
  thin: boolean;
  nChunks: number;
  kUsed: number;
}

interface Props {
  rows: ChartRow[];
  axisName: string;
  selectedYear: number;
  onSelectYear: (year: number) => void;
}

const MARGIN = { top: 16, right: 24, bottom: 36, left: 52 };
const bisectYear = bisector<ChartRow, number>((d) => d.year).center;

function Chart({
  rows,
  axisName,
  selectedYear,
  onSelectYear,
  width,
  height,
}: Props & { width: number; height: number }) {
  const { showTooltip, hideTooltip, tooltipData, tooltipLeft, tooltipTop } =
    useTooltip<ChartRow>();

  const innerW = width - MARGIN.left - MARGIN.right;
  const innerH = height - MARGIN.top - MARGIN.bottom;

  const xScale = useMemo(() => {
    const [min, max] = extent(rows, (d) => d.year) as [number, number];
    return scaleLinear({ domain: [min, max], range: [0, innerW] });
  }, [rows, innerW]);

  const yScale = useMemo(() => {
    const values = rows.flatMap((d) =>
      [d.value, d.control].filter((v): v is number => v !== null)
    );
    const [min, max] = extent(values) as [number, number];
    const pad = (max - min) * 0.12 || 1;
    return scaleLinear({ domain: [min - pad, max + pad], range: [innerH, 0] });
  }, [rows, innerH]);

  const valuePoints = rows.filter((d) => d.value !== null);
  const controlPoints = rows.filter((d) => d.control !== null);

  const nearestRow = useCallback(
    (event: React.MouseEvent<SVGRectElement>) => {
      const point = localPoint(event);
      if (!point) return null;
      const year = xScale.invert(point.x - MARGIN.left);
      return rows[bisectYear(rows, year)] ?? null;
    },
    [rows, xScale]
  );

  if (innerW <= 0 || innerH <= 0) return null;

  return (
    <div className="relative">
      <svg width={width} height={height} role="img" aria-label={`${axisName} axis over time`}>
        <Group left={MARGIN.left} top={MARGIN.top}>
          <GridRows
            scale={yScale}
            width={innerW}
            strokeDasharray="2 4"
            className="stroke-neutral-200 dark:stroke-neutral-800"
          />
          <line
            x1={0}
            x2={innerW}
            y1={yScale(0)}
            y2={yScale(0)}
            className="stroke-neutral-300 dark:stroke-neutral-700"
          />

          <LinePath
            data={controlPoints}
            x={(d) => xScale(d.year)}
            y={(d) => yScale(d.control as number)}
            curve={curveMonotoneX}
            strokeWidth={1.5}
            strokeDasharray="6 4"
            fill="none"
            className="stroke-neutral-400 dark:stroke-neutral-500"
          />
          <LinePath
            data={valuePoints}
            x={(d) => xScale(d.year)}
            y={(d) => yScale(d.value as number)}
            curve={curveMonotoneX}
            strokeWidth={2}
            fill="none"
            className="stroke-indigo-500"
          />

          {valuePoints.map((d) => (
            <g key={d.year}>
              {d.thin && (
                <circle
                  cx={xScale(d.year)}
                  cy={yScale(d.value as number)}
                  r={7}
                  fill="none"
                  strokeWidth={2}
                  className="stroke-amber-500"
                />
              )}
              <circle
                cx={xScale(d.year)}
                cy={yScale(d.value as number)}
                r={d.year === selectedYear ? 5 : 3}
                className={
                  d.year === selectedYear
                    ? "fill-indigo-600"
                    : "fill-indigo-400 dark:fill-indigo-500"
                }
              />
            </g>
          ))}

          <AxisBottom
            top={innerH}
            scale={xScale}
            tickFormat={(v) => String(v)}
            numTicks={Math.min(rows.length, 12)}
            tickLabelProps={{
              className: "fill-neutral-500 text-[11px]",
              textAnchor: "middle",
            }}
            stroke="currentColor"
            tickStroke="currentColor"
            axisClassName="text-neutral-400 dark:text-neutral-600"
          />
          <AxisLeft
            scale={yScale}
            numTicks={6}
            label="z-score (within company)"
            labelProps={{ className: "fill-neutral-500 text-[11px]" }}
            tickLabelProps={{
              className: "fill-neutral-500 text-[11px]",
              textAnchor: "end",
              dx: -4,
            }}
            stroke="currentColor"
            tickStroke="currentColor"
            axisClassName="text-neutral-400 dark:text-neutral-600"
          />

          <rect
            width={innerW}
            height={innerH}
            fill="transparent"
            onMouseMove={(e) => {
              const row = nearestRow(e);
              if (!row) return;
              showTooltip({
                tooltipData: row,
                tooltipLeft: MARGIN.left + xScale(row.year),
                tooltipTop:
                  MARGIN.top + yScale(row.value ?? row.control ?? 0) - 12,
              });
            }}
            onMouseLeave={hideTooltip}
            onClick={(e) => {
              const row = nearestRow(e);
              if (row?.value !== null && row) onSelectYear(row.year);
            }}
          />
        </Group>
      </svg>

      {tooltipData && (
        <TooltipWithBounds
          left={tooltipLeft}
          top={tooltipTop}
          unstyled
          applyPositionStyle
          className="pointer-events-none rounded-lg border border-neutral-200 bg-white px-3 py-2 text-xs shadow-md dark:border-neutral-700 dark:bg-neutral-900"
        >
          <p className="font-semibold">
            {tooltipData.year}
            {tooltipData.thin && (
              <span className="ml-2 font-normal text-amber-600 dark:text-amber-400">
                thin coverage
              </span>
            )}
          </p>
          <dl className="mt-1 space-y-0.5 font-mono text-neutral-600 dark:text-neutral-300">
            {tooltipData.value !== null && (
              <div className="flex justify-between gap-4">
                <dt>{axisName}</dt>
                <dd>{tooltipData.value.toFixed(2)}</dd>
              </div>
            )}
            {tooltipData.control !== null && (
              <div className="flex justify-between gap-4">
                <dt>control</dt>
                <dd>{tooltipData.control.toFixed(2)}</dd>
              </div>
            )}
            {tooltipData.value !== null && (
              <div className="flex justify-between gap-4">
                <dt>chunks</dt>
                <dd>
                  {tooltipData.nChunks} (top-{tooltipData.kUsed})
                </dd>
              </div>
            )}
          </dl>
        </TooltipWithBounds>
      )}
    </div>
  );
}

export default function AxisChart(props: Props) {
  return (
    <div className="h-90 w-full">
      <ParentSize>
        {({ width, height }) =>
          width > 0 ? <Chart {...props} width={width} height={height} /> : null
        }
      </ParentSize>
    </div>
  );
}
