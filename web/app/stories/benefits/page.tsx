import Link from "next/link";
import { notFound } from "next/navigation";
import BenefitsChart from "@/components/BenefitsChart";
import { loadBenefitsStory } from "@/lib/benefitsStory";

export default async function BenefitsPage() {
  const data = await loadBenefitsStory();
  if (!data) notFound();

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-12">
      <Link
        href="/"
        className="text-sm text-neutral-500 transition-colors hover:text-neutral-800 dark:hover:text-neutral-200"
      >
        &larr; Stories
      </Link>
      <h1 className="mt-4 text-3xl font-semibold tracking-tight">{data.title}</h1>
      <p className="mt-2 max-w-prose text-lg text-neutral-600 dark:text-neutral-400">
        {data.subtitle}
      </p>
      <p className="mt-4 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
        {data.intro}
      </p>

      <div className="mt-8">
        <BenefitsChart categories={data.categories} years={data.years} />
      </div>

      <div className="mt-8 max-w-prose space-y-2 text-xs text-neutral-500">
        <p>
          Each panel shares a y-scale, so taller lines are more commonly advertised. The{" "}
          <span className="rounded bg-purple-100 px-1 text-purple-700 dark:bg-purple-950/50 dark:text-purple-300">
            also DEI
          </span>{" "}
          tag marks categories (fertility) that double as a diversity signal —
          see the{" "}
          <Link className="underline" href="/stories/dei">
            DEI story
          </Link>
          . Hover a point for the year and share.
        </p>
        <p>
          <strong>Honesty.</strong> {data.caveat}
        </p>
      </div>
    </main>
  );
}
