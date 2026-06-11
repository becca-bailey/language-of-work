import Link from "next/link";
import { notFound } from "next/navigation";
import StoryExplorer from "@/components/StoryExplorer";
import { PERFORMANCE_EVENTS } from "@/lib/events";
import { loadStory } from "@/lib/stories";

export default async function PerformanceStoryPage() {
  const data = await loadStory("performance");
  if (!data) notFound();

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-12">
      <Link
        href="/"
        className="text-sm text-neutral-500 transition-colors hover:text-neutral-800 dark:hover:text-neutral-200"
      >
        &larr; Home
      </Link>
      <h1 className="mt-4 text-3xl font-semibold tracking-tight">
        Performance Language
      </h1>
      <div className="mt-8">
        <StoryExplorer
          data={data}
          events={PERFORMANCE_EVENTS}
          framing={[
            "When did Silicon Valley careers pages start talking about intensity, hustle, and being \"hardcore\"? Netflix's culture memo and Coinbase's 2020 mission-focused turn give sharper before/after anchors than the big-four panel alone.",
            "Performance language is measured as the share of mission/brand chunks scoring above threshold on a performance-intensity pole. Standout quotes are grouped by stance (work hard play hard, raise the bar, mission intensity, and others). Toggle to compare careers pages with investor 10-K filings.",
          ]}
        />
      </div>
    </main>
  );
}
