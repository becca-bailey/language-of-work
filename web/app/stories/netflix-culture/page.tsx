import Link from "next/link";
import { notFound } from "next/navigation";
import NetflixStoryExplorer from "@/components/NetflixStoryExplorer";
import { loadNetflixStory } from "@/lib/netflixStory";

export default async function NetflixCulturePage() {
  const data = await loadNetflixStory();
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
      <div className="mt-8">
        <NetflixStoryExplorer data={data} />
      </div>
    </main>
  );
}
