import type { DeiData } from "@/lib/data";

/** DEI register labels (excludes absent — used for share breakdowns). */
export const DEI_REGISTER_ORDER = [
  "explicit_demographic",
  "structural_process",
  "aspirational_vague",
  "belonging_culture",
  "meritocracy",
  "civilizational_mission",
] as const;

export type DeiRegister = (typeof DEI_REGISTER_ORDER)[number];

export const DEI_REGISTER_COLORS: Record<string, string> = {
  explicit_demographic: "#059669",
  structural_process: "#0d9488",
  aspirational_vague: "#6366f1",
  belonging_culture: "#8b5cf6",
  meritocracy: "#f59e0b",
  civilizational_mission: "#dc2626",
};

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
