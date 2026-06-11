import Link from "next/link";
import { notFound } from "next/navigation";
import DEIStoryExplorer from "@/components/DEIStoryExplorer";
import StoryCompanyLinks from "@/components/StoryCompanyLinks";
import { DEI_EVENTS } from "@/lib/events";
import { loadStory } from "@/lib/stories";

export default async function DeiStoryPage() {
  const data = await loadStory("dei");
  if (!data) notFound();

  const companies =
    data.sources.careers?.companies.map((c) => ({
      id: c.id,
      displayName: c.displayName,
    })) ?? [];

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-12">
      <Link
        href="/"
        className="text-sm text-neutral-500 transition-colors hover:text-neutral-800 dark:hover:text-neutral-200"
      >
        &larr; Stories
      </Link>
      <h1 className="mt-4 text-3xl font-semibold tracking-tight">DEI Language</h1>
      <div className="mt-8">
        <DEIStoryExplorer
          data={data}
          events={DEI_EVENTS}
          framing={[
            "When did substantive diversity and inclusion language appear on careers pages — and who retracted it after 2023? Coinbase's apolitical stance, Netflix's \"not a family\" culture memo, and Palantir's civilizational mission copy are counter-examples worth reading alongside Google, Amazon, and Meta.",
            "The inclusion embedding axis measures topic, not stance. Anti-DEI copy like \"refuge from division\" scores high on inclusion because it borrows belonging vocabulary — so a unipolar score cannot show the flip. The stance envelope (inclusion − meritocracy per chunk) and register classifier are the fixes.",
            "Two different stories need two metrics: topical salience (is the page talking about this at all?) and signed stance (which direction?). Coinbase is the rare case where salience stays high while stance inverts. Armstrong's September 2020 blog memo precedes the careers-page shift by roughly three years.",
          ]}
        />
      </div>
      <StoryCompanyLinks companies={companies} axis="dei" />
    </main>
  );
}
