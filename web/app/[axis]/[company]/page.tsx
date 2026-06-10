import Link from "next/link";
import { notFound } from "next/navigation";
import AxisExplorer from "@/components/AxisExplorer";
import { loadAxis } from "@/lib/data";
import { getAxisContent } from "@/lib/content";

export default async function CompanyReportPage({
  params,
}: {
  params: Promise<{ axis: string; company: string }>;
}) {
  const { axis, company } = await params;
  // control is only an overlay on other axes, never a standalone page
  if (axis === "control") notFound();
  const data = await loadAxis(company, axis);
  if (!data) notFound();
  const control = await loadAxis(company, "control");
  const content = getAxisContent(axis);

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-12">
      <Link
        href={`/${axis}`}
        className="text-sm text-neutral-500 transition-colors hover:text-neutral-800 dark:hover:text-neutral-200"
      >
        &larr; {content.title}
      </Link>
      <h1 className="mt-4 text-2xl font-semibold tracking-tight">
        {data.displayName ?? data.company}
        <span className="text-neutral-400"> / </span>
        {content.title}
      </h1>
      <p className="mt-2 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
        Yearly top-k mean of mission/brand sentences projected onto the {axis}{" "}
        contrast axis, z-scored within company. The dashed control axis tracks
        page composition — if both move together, the signal is composition,
        not values.
      </p>
      <div className="mt-8">
        <AxisExplorer axis={data} control={control} />
      </div>
    </main>
  );
}
