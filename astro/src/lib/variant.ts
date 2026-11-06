"use client";

import { useEffect, useState } from "react";

/* Chart presentation variant, read from the URL (?variant=article).

   "site" is the full research view: interaction hints, table views, source
   notes. "article" is the stripped-down version for essay screenshots —
   only what surrounding prose needs. SSR renders "site"; the flag is picked
   up after hydration, before the screenshot script captures (it waits for
   network idle + a settle delay). Static markup uses the .article-hide
   class instead (hidden via [data-variant="article"], set in Layout). */

export type Variant = "site" | "article";

export function useVariant(): Variant {
  const [variant, setVariant] = useState<Variant>("site");
  useEffect(() => {
    const v = new URLSearchParams(window.location.search).get("variant");
    if (v === "article") setVariant("article");
  }, []);
  return variant;
}
