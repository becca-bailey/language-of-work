// Shared presentational block: the explicit↔implicit phrase table. Used by
// NetflixStoryExplorer (story page) and the essay (via viz/ImplicitExplicit.astro).

export interface ImplicitExplicitRow {
  explicit: string;
  implicit: string;
}

export default function ImplicitExplicitTable({ rows }: { rows: ImplicitExplicitRow[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-neutral-200 text-left text-xs uppercase tracking-wide text-neutral-500 dark:border-neutral-800">
            <th className="py-2 pr-4 font-medium">Netflix, explicit</th>
            <th className="py-2 font-medium">Industry, implicit</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((m) => (
            <tr key={m.explicit} className="border-b border-neutral-100 dark:border-neutral-800/60">
              <td className="py-2 pr-4 text-neutral-700 dark:text-neutral-300">{m.explicit}</td>
              <td className="py-2 text-neutral-600 dark:text-neutral-400">{m.implicit}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
