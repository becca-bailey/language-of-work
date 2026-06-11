import Link from "next/link";
import { notFound } from "next/navigation";
import AltruismStoryExplorer from "@/components/AltruismStoryExplorer";
import StoryCompanyLinks from "@/components/StoryCompanyLinks";
import { loadStory } from "@/lib/stories";

export default async function AltruismStoryPage() {
  const data = await loadStory("altruism");
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
      <h1 className="mt-4 text-3xl font-semibold tracking-tight">
        Changing the World
      </h1>
      <div className="mt-8">
        <AltruismStoryExplorer
          data={data}
          framing={[
            "Which tech companies said they were changing the world — and did that early optimism fade? This story tracks idealistic employer language on careers pages from the mid-2000s through today.",
            "Scores are z-scored within each company, so the question is when a company's own copy got more or less idealistic — not whether Google sounds loftier than Amazon. Compare shapes and timing, not absolute levels.",
            "Sentence-level scoring surfaces the most idealistic lines per year (\"Can one conversation change the world?\") rather than diluting them with navigation chrome. When idealism drops alongside the control axis, the signal may be page composition — not rhetoric.",
          ]}
        />
      </div>
      <StoryCompanyLinks companies={companies} axis="altruism" />
    </main>
  );
}
