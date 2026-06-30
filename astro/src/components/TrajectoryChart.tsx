"use client";

import { useState } from "react";
import AxisChart, { type ChartRow } from "./AxisChart";

interface Props {
  rows: ChartRow[];
  label: string;
}

// Self-contained wrapper for the explore-page small-multiples: AxisChart needs
// selectedYear + onSelectYear, but Astro islands can't receive function props.
// Holding the state here keeps the island's props fully serializable.
export default function TrajectoryChart({ rows, label }: Props) {
  const [selectedYear, setSelectedYear] = useState(
    rows.length ? rows[rows.length - 1].year : 0
  );
  return (
    <AxisChart
      rows={rows}
      axisName={label}
      selectedYear={selectedYear}
      onSelectYear={setSelectedYear}
    />
  );
}
