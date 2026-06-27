#!/usr/bin/env python
"""Pre-clean raw Wayback/manual HTML captures into minimal semantic HTML.

Manual captures are raw page dumps: Wayback toolbar, bootloader scripts, login
forms, nav, footer — and crucially, on older pages (e.g. 2009 Facebook) the real
careers/culture copy sits in bare <div>s, which the main DOM walker
(lowork.chunking, p/li/td/h* only) silently drops. This step strips the chrome
and promotes the genuine content (divs included) into clean <h2>/<p> so the
normal pipeline (ingest -> extract_chunks) picks it up faithfully.

Reuses lowork.chunking's chrome/nav filters so output matches house style. Never
drops data: originals are preserved under manual_html/_raw/ before overwriting.

Usage: uv run python scripts/clean_manual_html.py --company meta [--file 2009_careers.html]
"""

from __future__ import annotations

import argparse
import re
import shutil

from bs4 import BeautifulSoup, NavigableString, Comment

from lowork.chunking import (
    STRIP_TAGS,
    _is_navigation,
    _is_pure_link_list,
    strip_nav_runs,
    strip_site_chrome,
    _clean,
)
from lowork.config import company_dir
from lowork.io import read_json, write_json

# Wayback rewrite scripts embed the original URL + 14-digit capture timestamp.
# Tolerant of whitespace/newlines: pretty-printed saves split the call across lines.
_WM_RE = re.compile(r'__wm\.wombat\(\s*"(https?://[^"]+)"\s*,\s*"(\d{14})"', re.S)


def _wayback_meta(raw: bytes) -> tuple[str | None, str | None]:
    text = raw.decode("utf-8", errors="replace")
    m = _WM_RE.search(text)
    return (m.group(1), m.group(2)) if m else (None, None)

HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]
# content-bearing blocks, incl. div/span that hold copy directly on old captures
CONTENT_TAGS = ["p", "li", "td", "blockquote", "dd", "dt", "figcaption", "div", "span"]


def _has_direct_text(el) -> bool:
    return any(isinstance(c, NavigableString) and c.strip() for c in el.children)


def _is_leaf_block(el) -> bool:
    """True if no descendant block carries its own direct text (so el owns its copy)."""
    return not any(_has_direct_text(d) for d in el.find_all(CONTENT_TAGS))


# Substring (not \b) chrome match: catches underscore class names the pipeline's
# word-boundary nav filter misses, e.g. footer_container / careers_footer / pagefooter.
_CHROME_RE = re.compile(
    r"wm-ipp|wayback|footer|menubar|masthead|copyright|login|cookie|"
    r"breadcrumb|sitemap|navbar|pagefooter",
    re.I,
)


def _is_chrome(el) -> bool:
    ident = " ".join(el.get("class", []) + [el.get("id") or ""])
    return bool(_CHROME_RE.search(ident))


def clean_html(raw: bytes) -> tuple[str, int]:
    soup = BeautifulSoup(raw, "lxml")
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for tag in soup(STRIP_TAGS):
        tag.decompose()

    body = soup.body or soup
    total_chars = len(body.get_text(" ")) or 1

    def _safe_decompose(el) -> None:
        # Never remove a container that holds most of the page: chrome/footer/nav
        # are small, but obfuscated class/id tokens (e.g. FB atomic CSS) can collide
        # with a keyword on a wrapper that holds the whole content. Guard against it.
        if el.name in ("body", "html"):
            return
        if len(el.get_text(" ")) > 0.5 * total_chars:
            return
        el.decompose()

    for el in soup.find_all(_is_chrome):
        _safe_decompose(el)
    for el in soup.find_all(_is_navigation):
        _safe_decompose(el)

    body = soup.body or soup
    blocks: list[tuple[str, str]] = []  # (kind, text); kind in {"h", "p"}
    for el in body.find_all(HEADING_TAGS + CONTENT_TAGS):
        if el.name in HEADING_TAGS:
            text = _clean(el.get_text(" "))
            if text and len(text.split()) <= 30:
                blocks.append(("h", text))
            continue
        # body copy: only leaf blocks that own their text (avoids parent/child dup)
        if not _has_direct_text(el) or not _is_leaf_block(el):
            continue
        text = strip_site_chrome(strip_nav_runs(_clean(el.get_text(" "))))
        if not text or _is_pure_link_list(text) or len(text.split()) < 6:
            continue
        blocks.append(("p", text))

    # collapse consecutive duplicate paragraphs (repeated chrome)
    out_lines = ["<!doctype html>", "<html><head><meta charset=\"utf-8\">",
                 f"<title>{_clean((soup.title.get_text() if soup.title else '')) }</title>",
                 "</head><body>"]
    seen: set[str] = set()
    kept = 0
    for kind, text in blocks:
        if kind == "p":
            if text in seen:
                continue
            seen.add(text)
            out_lines.append(f"<p>{text}</p>")
            kept += 1
        else:
            out_lines.append(f"<h2>{text}</h2>")
    out_lines.append("</body></html>")
    return "\n".join(out_lines), kept


# --- plain-text path (for SPA pages: paste rendered/selected text) ---

# Optional leading metadata lines, e.g.  "url: https://www.metacareers.com/"  /  "date: 20230701"
_META_LINE = re.compile(r"^\s*#?\s*(url|source|date|captured)\s*[:=]\s*(.+?)\s*$", re.I)


def clean_text(text: str) -> tuple[str, int, str | None, str | None]:
    """Wrap pasted plain text into minimal semantic HTML for the pipeline.

    Honors optional leading `url:` / `date:` header lines so SPA captures carry
    provenance. Blank-line-separated blocks become <p> (or <h2> if short).
    """
    url = date = None
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            i += 1
            continue
        m = _META_LINE.match(lines[i])
        if not m:
            break
        key, val = m.group(1).lower(), m.group(2).strip()
        if key in ("url", "source"):
            url = val
        else:
            d = re.sub(r"\D", "", val)
            if len(d) in (8, 14):
                date = d
        i += 1
    body = "\n".join(lines[i:])

    out = ["<!doctype html>", '<html><head><meta charset="utf-8"></head><body>']
    kept = 0
    seen: set[str] = set()
    for block in re.split(r"\n\s*\n", body):
        t = strip_site_chrome(strip_nav_runs(_clean(block.replace("\n", " "))))
        if not t or _is_pure_link_list(t):
            continue
        if len(t.split()) < 6:  # short standalone line -> treat as a heading
            out.append(f"<h2>{t}</h2>")
        elif t not in seen:
            seen.add(t)
            out.append(f"<p>{t}</p>")
            kept += 1
    out.append("</body></html>")
    return "\n".join(out), kept, url, date


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--company", required=True)
    ap.add_argument("--file", help="single file to clean (default: all *.html)")
    args = ap.parse_args()

    mdir = company_dir(args.company) / "manual_html"
    raw_backup = mdir / "_raw"
    raw_backup.mkdir(exist_ok=True)

    manifest_path = mdir / "manual_manifest.json"
    manifest = (read_json(manifest_path) if manifest_path.exists()
                else {"company": args.company, "captures": []})
    by_file = {c["file"]: c for c in manifest.get("captures", [])}

    text_html = mdir / "_text_html"
    if args.file:
        files = [mdir / args.file]
    else:
        files = sorted(f for f in mdir.iterdir()
                       if f.parent == mdir and f.suffix.lower() in (".html", ".txt", ".md"))
    for f in files:
        backup = raw_backup / f.name
        if backup.exists():
            raw = backup.read_bytes()          # always process from the pristine original
        else:
            raw = f.read_bytes()
            shutil.copy2(f, backup)            # preserve original once

        if f.suffix.lower() in (".txt", ".md"):
            cleaned, kept, url, ts = clean_text(raw.decode("utf-8", errors="replace"))
            text_html.mkdir(exist_ok=True)
            out_file = text_html / (f.stem + ".html")
            out_file.write_text(cleaned, encoding="utf-8")
            manifest_file = f"_text_html/{out_file.name}"
            if not ts:  # fall back to a leading 4-digit year in the filename
                ym = re.match(r"(\d{4})", f.stem)
                ts = ym.group(1) + "0701120000" if ym else None
            if not url:
                url = f"manual-text:{f.stem}"
            source = "manual-text"
        else:
            cleaned, kept = clean_html(raw)
            f.write_text(cleaned, encoding="utf-8")
            manifest_file = f.name
            url, ts = _wayback_meta(raw)
            source = "wayback-manual"

        if url and ts:
            prev = by_file.get(manifest_file, {})
            by_file[manifest_file] = {"file": manifest_file, "url": url,
                                      "capture_date": ts,
                                      "source": prev.get("source", source)}
            note = f"{url} @ {ts}"
        else:
            note = "NO metadata (add url:/date: header or a manifest entry by hand)"
        print(f"{f.name}: {kept} paragraphs ({note})")

    manifest["captures"] = sorted(by_file.values(),
                                  key=lambda c: (c["capture_date"], c["file"]))
    write_json(manifest_path, manifest)
    print(f"\nWrote {manifest_path} ({len(manifest['captures'])} captures)")


if __name__ == "__main__":
    main()
