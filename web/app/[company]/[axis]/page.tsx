import Link from "next/link";
import { notFound } from "next/navigation";
import AxisExplorer from "@/components/AxisExplorer";
import { loadAxis } from "@/lib/data";

export default async function AxisPage({
  params,
}: {
  params: Promise<{ company: string; axis: string }>;
}) {
  const { company, axis } = await params;
  const data = await loadAxis(company, axis);
  if (!data) notFound();
  const control = axis === "control" ? null : await loadAxis(company, "control");

  return (
    <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-12">
      <Link
        href="/"
        className="text-sm text-neutral-500 transition-colors hover:text-neutral-800 dark:hover:text-neutral-200"
      >
        &larr; All analyses
      </Link>
      <h1 className="mt-4 text-2xl font-semibold tracking-tight">
        <span className="capitalize">{company}</span>
        <span className="text-neutral-400"> / </span>
        <span className="capitalize">{axis}</span>
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
