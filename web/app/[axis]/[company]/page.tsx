import Link from "next/link";
import { notFound } from "next/navigation";
import AxisExplorer from "@/components/AxisExplorer";
import DeiExplorer from "@/components/DeiExplorer";
import { loadAxis, loadCompaniesManifest, loadDei } from "@/lib/data";
import { getAxisContent } from "@/lib/content";
import { storyPathForAxis } from "@/lib/stories";

export async function generateStaticParams() {
  const manifest = await loadCompaniesManifest();
  const params: { axis: string; company: string }[] = [];
  for (const c of manifest) {
    for (const axis of c.axes) {
      if (axis !== "control") params.push({ axis, company: c.id });
    }
  }
  return params;
}

export default async function CompanyReportPage({
  params,
}: {
  params: Promise<{ axis: string; company: string }>;
}) {
  const { axis, company } = await params;
  // control is only an overlay on other axes, never a standalone page
  if (axis === "control") notFound();
  const content = getAxisContent(axis);
  const backHref = storyPathForAxis(axis) ?? `/${axis}`;
  const backLabel = storyPathForAxis(axis) ? "Story" : content.title;

  if (axis === "dei") {
    const dei = await loadDei(company);
    if (!dei) notFound();
    return (
      <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-12">
        <Link
          href={backHref}
          className="text-sm text-neutral-500 transition-colors hover:text-neutral-800 dark:hover:text-neutral-200"
        >
          &larr; DEI {backLabel.toLowerCase()}
        </Link>
        <h1 className="mt-4 text-2xl font-semibold tracking-tight">
          {dei.displayName ?? dei.company}
          <span className="text-neutral-400"> / </span>
          {content.title}
        </h1>
        <p className="mt-2 max-w-prose text-sm text-neutral-600 dark:text-neutral-400">
          Inclusion intensity (raw cosine to the inclusion pole) on mission/brand
          chunks — near-zero means the language is absent, not opposed. Meritocracy
          rhetoric shows up in the register breakdown below. Vertical lines mark
          external events.
        </p>
        <div className="mt-8">
          <DeiExplorer data={dei} />
        </div>
      </main>
    );
  }

  const data = await loadAxis(company, axis);
  if (!data) notFound();
  const control = await loadAxis(company, "control");

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-12">
      <Link
        href={backHref}
        className="text-sm text-neutral-500 transition-colors hover:text-neutral-800 dark:hover:text-neutral-200"
      >
        &larr; {storyPathForAxis(axis) ? `${content.title} story` : content.title}
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
