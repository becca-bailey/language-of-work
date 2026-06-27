interface MatrixRow {
  concept: string;
  claims: boolean;
  metric: boolean;
  eval: string;
}

export default function NetflixObjectivityMatrix({ rows }: { rows: MatrixRow[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-neutral-200 text-left text-xs uppercase tracking-wide text-neutral-500 dark:border-neutral-800">
            <th className="py-2 pr-4 font-medium">Concept</th>
            <th className="py-2 pr-4 font-medium">Claims objectivity?</th>
            <th className="py-2 pr-4 font-medium">Defines a metric?</th>
            <th className="py-2 font-medium">How the cut is actually made</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr
              key={r.concept}
              className="border-b border-neutral-100 dark:border-neutral-800/60"
            >
              <td className="py-2 pr-4 font-medium text-neutral-800 dark:text-neutral-200">
                {r.concept}
              </td>
              <td className="py-2 pr-4">
                <span className="text-emerald-600 dark:text-emerald-400">
                  {r.claims ? "Yes ✓" : "—"}
                </span>
              </td>
              <td className="py-2 pr-4">
                <span className="font-medium text-rose-600 dark:text-rose-400">
                  {r.metric ? "Yes" : "No ✗"}
                </span>
              </td>
              <td className="py-2 text-neutral-600 dark:text-neutral-400">{r.eval}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-2 text-xs italic text-neutral-500">
        Every row claims objective performance; none defines a metric. The third column
        (how the cut is actually made) is interpretation — the discretionary judgment the
        missing metric leaves behind.
      </p>
    </div>
  );
}
