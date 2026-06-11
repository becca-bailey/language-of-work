import Link from "next/link";
import { notFound } from "next/navigation";
import StoryExplorer from "@/components/StoryExplorer";
import { DEI_EVENTS } from "@/lib/events";
import { loadStory } from "@/lib/stories";

export default async function DeiStoryPage() {
  const data = await loadStory("dei");
  if (!data) notFound();

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-12">
      <Link
        href="/dei"
        className="text-sm text-neutral-500 transition-colors hover:text-neutral-800 dark:hover:text-neutral-200"
      >
        &larr; DEI topic
      </Link>
      <h1 className="mt-4 text-3xl font-semibold tracking-tight">DEI Language</h1>
      <div className="mt-8">
        <StoryExplorer
          data={data}
          events={DEI_EVENTS}
          framing={[
            "When did substantive diversity and inclusion language appear on careers pages — and who retracted it after 2023? Coinbase's apolitical stance and Netflix's \"not a family\" culture memo are counter-examples worth reading alongside Google, Amazon, and Meta.",
            "The primary chart classifies what kind of DEI language each company used — from explicit demographic commitments to vague aspiration to outright meritocracy counter-programming — because stance matters more than topic. A page rejecting DEI mentions diversity just as often as a page embracing it.",
            "Early patterns suggest at least three distinct responses — adopt-and-retract, adopt-and-quiet, and never-adopt or counter-program — but as coverage fills in, these stories may change. The per-company quote timelines often tell the story more clearly than any aggregate.",
            "Toggle to compare employee-facing careers copy with investor 10-K Human Capital sections.",
          ]}
        />
      </div>
      <p className="mt-10 text-sm text-neutral-500">
        <Link href="/dei/compare" className="text-indigo-600 hover:underline dark:text-indigo-400">
          Per-company DEI detail &rarr;
        </Link>
      </p>
    </main>
  );
}
