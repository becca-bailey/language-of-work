#!/usr/bin/env python
"""Generate an AI narrative for a company from all of its web-export facets.

Reads every per-company facet JSON under astro/src/data/<company>/, hands the
collected data to a pinned model, and writes a short structured narrative to
astro/src/data/synthesis/<company>.json. The prompt, model, and version live in
prompts/synthesis.yaml so the narrative is reconfigurable without code edits.

This is a pipeline stage (see src/lowork/pipeline.py): change-detection is the
fingerprint engine's job — it hashes the company's export dir and the prompt config
and only re-runs this when one of them changes. Nothing here is fetched per page
load.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json

import yaml
from anthropic import Anthropic

from lowork.company import CompanyProfile
from lowork.config import ROOT, WEB_DATA_DIR
from lowork.io import read_json, write_json

CONFIG_PATH = ROOT / "prompts" / "synthesis.yaml"
SYNTHESIS_DIR = WEB_DATA_DIR / "synthesis"

# Facets that are scaffolding/controls rather than substantive signal.
SKIP_FACETS = {"control", "fingerprint"}

# Generic size bounds so the prompt stays bounded as facets grow: cap long
# arrays (e.g. phrase dumps that can run to 1000+ entries) and truncate very
# long strings. Trimming is mostly by shape, but the per-year trajectory is the
# spine of every narrative, so lists under NO_TRUNC_KEYS are never dropped —
# capping `years` was silently hiding most of a company's history from the model.
MAX_LIST = 20
MAX_STR = 1400
NO_TRUNC_KEYS = {"years"}


def _trim(obj, key: str | None = None):
    """Recursively cap list lengths and string sizes to keep the prompt bounded."""
    if isinstance(obj, str):
        return obj if len(obj) <= MAX_STR else obj[:MAX_STR] + "…"
    if isinstance(obj, list):
        cap = len(obj) if key in NO_TRUNC_KEYS else MAX_LIST
        trimmed = [_trim(x) for x in obj[:cap]]
        if len(obj) > cap:
            trimmed.append(f"…(+{len(obj) - cap} more)")
        return trimmed
    if isinstance(obj, dict):
        return {k: _trim(v, k) for k, v in obj.items()}
    return obj


def collect_facets(company: str) -> dict[str, object]:
    """Load every per-company facet JSON, keyed by facet name (filename stem)."""
    cdir = WEB_DATA_DIR / company
    if not cdir.is_dir():
        return {}
    facets: dict[str, object] = {}
    for path in sorted(cdir.glob("*.json")):
        name = path.stem
        if name in SKIP_FACETS:
            continue
        facets[name] = _trim(read_json(path))
    return facets


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()
    return json.loads(text)


def main(company: str) -> None:
    cfg = yaml.safe_load(CONFIG_PATH.read_text())
    model = cfg["model"]
    version = cfg["version"]

    profile = CompanyProfile.load(company)
    display_name = profile.display_name

    facets = collect_facets(company)
    out_path = SYNTHESIS_DIR / f"{company}.json"

    if not facets:
        print(f"[synthesize] {company}: no facets on disk — writing empty narrative")
        write_json(out_path, {
            "company": company,
            "displayName": display_name,
            "headline": None,
            "identity": None,
            "fit": None,
            "sections": [],
            "model": model,
            "promptVersion": version,
            "facetsUsed": [],
            "generatedAt": dt.date.today().isoformat(),
        })
        return

    facets_json = json.dumps(facets, ensure_ascii=False, indent=2)
    user_msg = cfg["template"].format(display_name=display_name, facets=facets_json)

    client = Anthropic()
    # The model very occasionally emits a malformed JSON body (e.g. an
    # unescaped quote inside a verbatim phrase). It is intermittent, so a couple
    # of retries — nudging temperature off zero to break determinism — clears it
    # rather than crashing the whole pipeline run.
    last_err: Exception | None = None
    for attempt in range(3):
        resp = client.messages.create(
            model=model,
            max_tokens=int(cfg.get("max_tokens", 2000)),
            temperature=0.0 if attempt == 0 else 0.4,
            system=cfg["system"],
            messages=[{"role": "user", "content": user_msg}],
        )
        try:
            parsed = _parse_json(resp.content[0].text)
            break
        except json.JSONDecodeError as e:
            last_err = e
            print(f"[synthesize] {company}: malformed JSON (attempt {attempt + 1}/3), retrying")
    else:
        raise RuntimeError(f"synthesize_company: {company} returned invalid JSON 3x") from last_err

    write_json(out_path, {
        "company": company,
        "displayName": display_name,
        "headline": parsed.get("headline"),
        "identity": parsed.get("identity"),
        "fit": parsed.get("fit"),
        "sections": parsed.get("sections", []),
        "model": model,
        "promptVersion": version,
        "facetsUsed": sorted(facets),
        "generatedAt": dt.date.today().isoformat(),
    })
    n = len(parsed.get("sections", []))
    print(f"Wrote {out_path} ({n} sections, facets: {', '.join(sorted(facets))})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", default="google")
    main(parser.parse_args().company)
