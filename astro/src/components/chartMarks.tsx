"use client";

/** Shared mark styling for every stacked bar chart (Becca 2026-08-01:
 * rounded segment ends + a small gap between colors, consistent across
 * charts). Both the DEI register row and the founder references chart draw
 * their segments through BarSegment, so the look is defined once. */

import type { SVGProps } from "react";

/** Px gap between stacked color segments (matches the HTML charts' 2px). */
export const SEGMENT_GAP = 2;
/** Corner radius on each segment (matches the HTML charts' 3px). */
export const SEGMENT_RADIUS = 3;

/** One stacked-bar segment: rounded corners capped so slivers don't distort;
 * fill goes through style so CSS color functions (var(), color-mix()) work. */
export function BarSegment({
  x,
  y,
  width,
  height,
  fill,
  ...rest
}: {
  x: number;
  y: number;
  width: number;
  height: number;
  fill: string;
} & Omit<SVGProps<SVGRectElement>, "x" | "y" | "width" | "height" | "fill">) {
  const rx = Math.min(SEGMENT_RADIUS, height / 2, width / 2);
  return <rect x={x} y={y} width={width} height={height} rx={rx} style={{ fill }} {...rest} />;
}
