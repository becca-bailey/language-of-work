import type { DeiData } from "@/lib/data";

/** DEI register labels (excludes absent — used for share breakdowns). The two
 * counter keys are STANCE-classifier counts (mission_focus_apolitical /
 * civilizational_mission), shipped alongside the pro-inclusion registers. */
export const DEI_REGISTER_ORDER = [
  "explicit_demographic",
  "structural_process",
  "aspirational_vague",
  "belonging_culture",
  "mission_focus_apolitical",
  "civilizational_mission",
] as const;

export type DeiRegister = (typeof DEI_REGISTER_ORDER)[number];

// Register → color token (see styles/globals.css). Inclusion-oriented registers use the
// cool default chart series; the apolitical / civilizational counter-stances use the warm
// "contrast" series so they read as the opposing pole. Resolve to hex in charts via
// useThemeColors().resolve(); DEI_REGISTER_COLORS gives var() strings for CSS/style use.
export const DEI_REGISTER_TOKEN: Record<string, string> = {
  explicit_demographic: "--chart-1",
  structural_process: "--chart-2",
  aspirational_vague: "--chart-3", // lavender — ordered before the pink below
  belonging_culture: "--chart-4", // pink
  mission_focus_apolitical: "--chart-contrast-1",
  civilizational_mission: "--chart-contrast-2",
};

export const DEI_REGISTER_COLORS: Record<string, string> = Object.fromEntries(
  Object.entries(DEI_REGISTER_TOKEN).map(([k, v]) => [k, `var(${v})`]),
);

export interface CompanyRegisterShare {
  company: string;
  displayName: string;
  shares: Record<string, number>;
  totalDeiChunks: number;
}

export function registerSharesFromDei(data: DeiData): CompanyRegisterShare {
  const totals: Record<string, number> = {};
  for (const y of data.years) {
    for (const reg of DEI_REGISTER_ORDER) {
      totals[reg] = (totals[reg] ?? 0) + (y.registers[reg] ?? 0);
    }
  }
  const totalDeiChunks = Object.values(totals).reduce((a, b) => a + b, 0);
  const shares: Record<string, number> = {};
  for (const reg of DEI_REGISTER_ORDER) {
    shares[reg] = totalDeiChunks > 0 ? (totals[reg] ?? 0) / totalDeiChunks : 0;
  }
  return {
    company: data.company,
    displayName: data.displayName ?? data.company,
    shares,
    totalDeiChunks,
  };
}

/** Dominant non-absent register for findings copy. */
export function dominantRegister(data: DeiData): string | null {
  const share = registerSharesFromDei(data);
  if (share.totalDeiChunks === 0) return null;
  let best: string | null = null;
  let bestVal = 0;
  for (const reg of DEI_REGISTER_ORDER) {
    if (share.shares[reg] > bestVal) {
      bestVal = share.shares[reg];
      best = reg;
    }
  }
  return bestVal >= 0.35 ? best : null;
}
