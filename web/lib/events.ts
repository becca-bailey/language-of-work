export interface TimelineEvent {
  id: string;
  label: string;
  /** Fractional year for chart placement, e.g. 2020.4 = May 2020 */
  year: number;
  description?: string;
}

/** Shared external events annotated on DEI charts. */
export const DEI_EVENTS: TimelineEvent[] = [
  {
    id: "george-floyd",
    label: "George Floyd protests",
    year: 2020 + 5 / 12,
    description: "May 2020 — corporate DEI commitments surge across tech.",
  },
  {
    id: "scotus-aa",
    label: "SCOTUS affirmative action",
    year: 2023 + 6 / 12,
    description: "June 2023 — Supreme Court limits race-conscious college admissions.",
  },
  {
    id: "election-2024",
    label: "2024 US election",
    year: 2024 + 11 / 12,
    description: "November 2024 — renewed political pressure on corporate DEI programs.",
  },
  {
    id: "amazon-dei-winddown",
    label: "Amazon DEI wind-down",
    year: 2024 + 12 / 12,
    description: "December 2024 — Amazon scales back internal DEI programs.",
  },
  {
    id: "meta-dei-end",
    label: "Meta DEI program end",
    year: 2025 + 1 / 12,
    description: "January 2025 — Meta ends several DEI initiatives.",
  },
];

/** External events annotated on performance-language charts. */
export const PERFORMANCE_EVENTS: TimelineEvent[] = [
  {
    id: "musk-hardcore",
    label: "Musk \"extremely hardcore\" email",
    year: 2022 + 10 / 12,
    description:
      "November 2022 — Elon Musk's ultimatum to Twitter/X employees to commit to an \"extremely hardcore\" culture.",
  },
  {
    id: "layoffs-2023",
    label: "Tech layoff wave",
    year: 2023 + 1 / 12,
    description:
      "Early 2023 — Major tech companies cut headcount; intensity language rises on careers pages.",
  },
  {
    id: "coinbase-mission",
    label: "Coinbase mission-focused memo",
    year: 2020 + 8 / 12,
    description:
      "September 2020 — Brian Armstrong declares Coinbase a mission-focused company; offers exit packages to employees who disagree.",
  },
];
