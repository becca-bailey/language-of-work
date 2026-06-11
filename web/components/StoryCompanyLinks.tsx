import Link from "next/link";

interface Company {
  id: string;
  displayName: string;
}

interface Props {
  companies: Company[];
  axis: string;
  heading?: string;
}

export default function StoryCompanyLinks({
  companies,
  axis,
  heading = "Per-company detail",
}: Props) {
  if (!companies.length) return null;

  return (
    <section className="mt-10 border-t border-neutral-200 pt-8 dark:border-neutral-800">
      <h2 className="text-sm font-medium uppercase tracking-wide text-neutral-500">
        {heading}
      </h2>
      <ul className="mt-4 space-y-2">
        {companies.map((c) => (
          <li key={c.id}>
            <Link
              href={`/${axis}/${c.id}`}
              className="group flex items-baseline justify-between rounded-lg border border-neutral-200 px-4 py-3 transition-colors hover:border-neutral-400 dark:border-neutral-800 dark:hover:border-neutral-600"
            >
              <span className="font-medium">{c.displayName}</span>
              <span className="text-sm text-neutral-400 transition-transform group-hover:translate-x-0.5">
                &rarr;
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
