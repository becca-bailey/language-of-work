"use client";

import StoryTrendChart from "@/components/StoryTrendChart";
import type { TimelineEvent } from "@/lib/events";
import type { StoryCompanySeries } from "@/lib/storyTypes";

interface Props {
  companies: StoryCompanySeries[];
  events?: TimelineEvent[];
}

export default function StorySalienceChart({ companies, events = [] }: Props) {
  const withSalience = companies.filter((c) =>
    c.years.some((y) => y.salienceTopkMean !== undefined)
  );

  if (!withSalience.length) return null;

  return (
    <StoryTrendChart
      companies={withSalience}
      metricLabel="Topical salience (max inclusion, meritocracy)"
      metricKey="salienceTopkMean"
      format="percent"
      events={events}
    />
  );
}
