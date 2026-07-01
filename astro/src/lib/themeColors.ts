"use client";

import { useEffect, useState } from "react";

/* Runtime reader for the color tokens defined in styles/globals.css.

   CSS variables don't resolve in SVG presentation attributes (fill="var(--x)"
   does nothing), so visx charts need the *resolved* hex/rgb. getComputedStyle
   resolves nested var() chains for custom properties, so reading --chart-1
   returns the palette hex. All chart components are client-hydrated, so this
   runs in the browser. Keeping globals.css the single source of truth. */

export type Role =
  | "info"
  | "positive"
  | "negative"
  | "alert"
  | "accent"
  | "warning"
  | "origin"
  | "muted";

const ROLES: Role[] = [
  "info",
  "positive",
  "negative",
  "alert",
  "accent",
  "warning",
  "origin",
  "muted",
];

const CHART = ["--chart-1", "--chart-2", "--chart-3", "--chart-4", "--chart-5"];
const CHART_CONTRAST = ["--chart-contrast-1", "--chart-contrast-2", "--chart-contrast-3"];

// SSR-safe fallbacks (match globals.css Layer A/C) used before hydration reads.
const FALLBACK: Record<string, string> = {
  "--info": "#7669e9",
  "--positive": "#5e1af4",
  "--negative": "#ff6230",
  "--alert": "#ff6230",
  "--accent": "#f8bcca",
  "--warning": "#ffbe98",
  "--origin": "#5e1af4",
  "--muted": "#9ca3af",
  "--chart-1": "#5e1af4",
  "--chart-2": "#7669e9",
  "--chart-3": "#d599fb",
  "--chart-4": "#f8bcca",
  "--chart-5": "#3a1097",
  "--chart-contrast-1": "#ff6230",
  "--chart-contrast-2": "#ffbe98",
  "--chart-contrast-3": "#bdb7f4",
};

function readToken(name: string): string {
  if (typeof window === "undefined") return FALLBACK[name] ?? "#000";
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || FALLBACK[name] || "#000";
}

export interface ThemeColors {
  role: Record<Role, string>;
  /** Cool default series, in order. Use `chart[i % chart.length]` for N series. */
  chart: string[];
  /** Warm contrast series (opposition/highlight); excludes the reserved alert. */
  chartContrast: string[];
  /** Resolve any token by CSS variable name, e.g. resolve("--chart-1"). */
  resolve: (varName: string) => string;
  /** Mix a token with white/black/transparent to derive a shade (0..1 amount). */
  shade: (base: string, amount: number, mixWith?: "white" | "black" | "transparent") => string;
}

function snapshot(): ThemeColors {
  const role = Object.fromEntries(ROLES.map((r) => [r, readToken(`--${r}`)])) as Record<Role, string>;
  return {
    role,
    chart: CHART.map(readToken),
    chartContrast: CHART_CONTRAST.map(readToken),
    resolve: readToken,
    shade: (base, amount, mixWith = "white") =>
      `color-mix(in srgb, ${base} ${Math.round(amount * 100)}%, ${mixWith})`,
  };
}

/** React hook: reads tokens after mount and re-reads when the OS theme flips. */
export function useThemeColors(): ThemeColors {
  const [colors, setColors] = useState<ThemeColors>(() => snapshot());
  useEffect(() => {
    setColors(snapshot());
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => setColors(snapshot());
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);
  return colors;
}
