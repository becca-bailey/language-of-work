"use client";

import { useMemo } from "react";
import { ParentSize } from "@visx/responsive";
import { allYears, type StoryCompanySeries } from "@/lib/storyTypes";
import { DEI_REGISTER_COLORS } from "@/lib/deiRegisters";
import { cellsFor, CompanyRegisterRow } from "@/components/StoryRegisterChart";

/** Register chart for the founder-speech draft: the DEI story's inner row
 * component reused directly — same marks, colors, and tooltips — without
 * the outer wrapper's narrative grouping or aggregate line (DEI-story
 * editorial). Renders every series it's given (the blog next to Basecamp's
 * careers pages, 2021–present) on a SHARED scale and year domain, so the
 * rows are directly comparable. Scale fits the data (no 20% floor) and
 * nonzero bars get a minimum height so rare classes stay visible. */

const LEGEND: { key: string; label: string }[] = [
  { key: "explicit_demographic", label: "explicit demographic" },
  { key: "structural_process", label: "structural process" },
  { key: "aspirational_vague", label: "aspirational vague" },
  { key: "belonging_culture", label: "belonging culture" },
  { key: "mission_focus_apolitical", label: "apolitical / anti-DEI" },
  { key: "civilizational_mission", label: "civilizational mission" },
];

export default function FounderRegisterRow({ companies }: { companies: StoryCompanySeries[] }) {
  const years = useMemo(() => allYears(companies), [companies]);
  // Count scale (not share): bar heights match the totals labels, and a
  // count of 1 is the same height in every year and row.
  const maxValue = useMemo(() => {
    let max = 1;
    for (const company of companies) {
      for (const cell of cellsFor(company).values()) {
        const active = Object.values(cell.counts).length
          ? Object.entries(cell.counts)
              .filter(([k]) => k in cell.shares)
              .reduce((s, [, v]) => s + v, 0)
          : 0;
        const counter = Object.entries(cell.counts)
          .filter(([k]) => k in cell.counterShares)
          .reduce((s, [, v]) => s + v, 0);
        max = Math.max(max, active, counter);
      }
    }
    return max;
  }, [companies]);

  if (!companies.length) return null;

  return (
    <div>
      {companies.map((company) => {
        // Denominator caption: the rows compare composition, not volume —
        // say each corpus's size where the reader can't miss it.
        const ns = company.years.map((y) => y.nChunks).filter((n) => n > 0);
        const nNote = ns.length
          ? `${Math.min(...ns).toLocaleString()}–${Math.max(...ns).toLocaleString()} paragraphs/year`
          : "";
        return (
        <div key={company.id} className="mt-2 first:mt-0">
          <p className="text-[11px] font-medium text-neutral-600 dark:text-neutral-400">
            {company.displayName}
            {nNote && <span className="ml-2 font-normal text-neutral-400">{nNote}</span>}
          </p>
          <ParentSize initialSize={{ width: 480, height: 220 }}>
            {({ width }) =>
              width > 0 ? (
                <CompanyRegisterRow
                  company={company}
                  years={years}
                  maxShare={maxValue}
                  width={width}
                  rowHeight={220}
                  minBarPx={3}
                  showTotals
                  scale="count"
                />
              ) : null
            }
          </ParentSize>
        </div>
        );
      })}
      <div className="mt-2 flex flex-wrap gap-3 text-[10px] text-neutral-500">
        {LEGEND.map((d) => (
          <span key={d.key} className="flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-sm" style={{ backgroundColor: DEI_REGISTER_COLORS[d.key] }} />
            {d.label}
          </span>
        ))}
      </div>
      {/* Table fallback: the hover tooltips are mouse-only; this is the tap/
          screen-reader path and the exact numbers. */}
      <details className="mt-3">
        <summary className="cursor-pointer text-xs text-neutral-500">Full table (chunk counts by class and year)</summary>
        <div className="overflow-x-auto">
          <table className="mt-2 text-xs tabular-nums">
            <thead>
              <tr className="text-left text-neutral-500">
                <th className="pr-4 font-medium">corpus</th>
                <th className="pr-4 font-medium">year</th>
                <th className="pr-4 font-medium">paragraphs</th>
                {LEGEND.map((d) => (
                  <th key={d.key} className="pr-4 font-medium">{d.label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {companies.flatMap((company) =>
                company.years.map((y) => (
                  <tr key={`${company.id}-${y.year}`}>
                    <td className="pr-4 py-0.5">{company.displayName}</td>
                    <td className="pr-4">{y.year}</td>
                    <td className="pr-4">{y.nChunks.toLocaleString()}</td>
                    {LEGEND.map((d) => (
                      <td key={d.key} className="pr-4">{y.registers?.[d.key] ?? 0}</td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
