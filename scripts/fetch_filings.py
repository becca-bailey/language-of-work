#!/usr/bin/env python
"""Fetch 10-K filings from SEC EDGAR and extract Human Capital + Risk Factors sections.

Writes data/<company>/investor/chunks/{year}.jsonl and investor_manifest.json.
Requires a User-Agent per SEC fair-access policy (set SEC_USER_AGENT env var).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import warnings

import httpx
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

from lowork.config import DATA_DIR, company_dir
from lowork.io import write_json, write_jsonl

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

SEC_BASE = "https://data.sec.gov"
ARCHIVES = "https://www.sec.gov/Archives/edgar/data"
USER_AGENT = "LanguageOfWork research@example.com"
MIN_CHUNK_WORDS = 40
MAX_CHUNK_WORDS = 250
MAX_SECTION_CHARS = 12000


def _headers() -> dict[str, str]:
    import os

    ua = os.environ.get("SEC_USER_AGENT", USER_AGENT)
    return {"User-Agent": ua, "Accept-Encoding": "gzip, deflate"}


def _cik_padded(cik: str) -> str:
    return cik.zfill(10)


def _chunk_id(text: str, year: int, section: str, pos: int) -> str:
    h = hashlib.sha256(f"{year}:{section}:{pos}:{text}".encode()).hexdigest()
    return h[:16]


def _split_prose_chunks(text: str, year: int, section: str, source_url: str) -> list[dict]:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text.split()) < MIN_CHUNK_WORDS:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[dict] = []
    buf: list[str] = []
    buf_words = 0
    pos = 0

    def flush() -> None:
        nonlocal pos, buf, buf_words
        if buf_words < MIN_CHUNK_WORDS:
            return
        para = " ".join(buf).strip()
        chunks.append({
            "chunk_id": _chunk_id(para, year, section, pos),
            "text": para,
            "heading": section,
            "source_url": source_url,
            "timestamp": f"{year}0101000000",
            "year": year,
            "word_count": len(para.split()),
            "position": pos,
            "extraction_source": "edgar",
        })
        pos += 1
        buf = []
        buf_words = 0

    for sent in sentences:
        w = len(sent.split())
        if buf_words + w > MAX_CHUNK_WORDS and buf:
            flush()
        buf.append(sent)
        buf_words += w
        if buf_words >= MAX_CHUNK_WORDS:
            flush()
    flush()
    return chunks


def _html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "table"]):
        tag.decompose()
    return soup.get_text("\n", strip=True)


def _extract_sections(text: str) -> dict[str, str]:
    """Pull Human Capital and Risk Factors prose from 10-K plain text."""
    sections: dict[str, str] = {}
    normalized = re.sub(r"\s+", " ", text)

    # Human Capital / Culture and Workforce (Item 1 subsection, post-2020)
    for pattern in (
        r"Culture and Workforce(.*?)(?:Government Regulation|Intellectual Property|Available Information|ITEM\s*1A)",
        r"Human Capital Management(.*?)(?:Government Regulation|Intellectual Property|Available Information|ITEM\s*1A)",
        r"Human Capital Resources(.*?)(?:Government Regulation|Intellectual Property|Available Information|ITEM\s*1A)",
        r"Human Capital(.*?)(?:Available Information|Government Regulation|Intellectual Property|ITEM\s*1A)",
    ):
        m = re.search(pattern, normalized, re.I | re.S)
        if m:
            sections["Human Capital"] = m.group(1).strip()[:MAX_SECTION_CHARS]
            break

    risk_match = re.search(
        r"ITEM\s*1A\.?\s*RISK\s*FACTORS(.*?)(?:ITEM\s*1B\.|ITEM\s*2\.|ITEM\s*3\.)",
        normalized,
        re.I | re.S,
    )
    if risk_match:
        sections["Risk Factors"] = risk_match.group(1).strip()[:MAX_SECTION_CHARS]

    if not sections:
        biz_match = re.search(
            r"ITEM\s*1\.?\s*BUSINESS(.*?)(?:ITEM\s*1A\.|ITEM\s*2\.)",
            normalized,
            re.I | re.S,
        )
        if biz_match:
            sections["Business"] = biz_match.group(1).strip()[:MAX_SECTION_CHARS]

    return sections


def _parse_filings_block(block: dict) -> list[dict]:
    forms = block.get("form", [])
    accessions = block.get("accessionNumber", [])
    dates = block.get("filingDate", [])
    docs = block.get("primaryDocument", [])
    filings = []
    for form, acc, date, doc in zip(forms, accessions, dates, docs):
        if form != "10-K":
            continue
        year = int(date[:4])
        if year < 2010:
            continue
        filings.append({
            "accession": acc.replace("-", ""),
            "accession_dashed": acc,
            "filing_date": date,
            "year": year,
            "primary_document": doc,
        })
    return filings


def list_10k_filings(cik: str, client: httpx.Client) -> list[dict]:
    url = f"{SEC_BASE}/submissions/CIK{_cik_padded(cik)}.json"
    resp = client.get(url)
    resp.raise_for_status()
    data = resp.json()

    filings = _parse_filings_block(data.get("filings", {}).get("recent", {}))
    for fmeta in data.get("filings", {}).get("files", []):
        hist_url = f"{SEC_BASE}/submissions/{fmeta['name']}"
        hist = client.get(hist_url)
        hist.raise_for_status()
        filings.extend(_parse_filings_block(hist.json()))
        time.sleep(0.1)

    # Dedupe by accession; keep latest filing per calendar year
    by_year: dict[int, dict] = {}
    for f in sorted(filings, key=lambda x: x["filing_date"]):
        by_year[f["year"]] = f
    return sorted(by_year.values(), key=lambda f: f["year"])


def fetch_filing_html(cik: str, filing: dict, client: httpx.Client) -> str:
    acc = filing["accession"]
    doc = filing["primary_document"]
    url = f"{ARCHIVES}/{int(cik)}/{acc}/{doc}"
    resp = client.get(url)
    resp.raise_for_status()
    return resp.text


def main(company: str, max_filings: int | None, min_year: int) -> None:
    config = json.loads((DATA_DIR / "filings_config.json").read_text())
    if company not in config:
        raise SystemExit(f"No CIK configured for {company} in filings_config.json")

    cik = config[company]["cik"]
    cdir = company_dir(company)
    investor_dir = cdir / "investor"
    chunks_dir = investor_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    manifest_entries: list[dict] = []
    by_year: dict[int, list[dict]] = {}

    with httpx.Client(headers=_headers(), timeout=60.0, follow_redirects=True) as client:
        filings = [f for f in list_10k_filings(cik, client) if f["year"] >= min_year]
        if max_filings:
            filings = filings[-max_filings:]
        print(f"{company}: {len(filings)} 10-K filings since 2010")

        for filing in filings:
            year = filing["year"]
            print(f"  {year} {filing['filing_date']} ...", end=" ", flush=True)
            try:
                html = fetch_filing_html(cik, filing, client)
            except httpx.HTTPError as e:
                print(f"SKIP ({e})")
                continue
            text = _html_to_text(html)
            sections = _extract_sections(text)
            acc = filing["accession"]
            doc = filing["primary_document"]
            source_url = f"{ARCHIVES}/{int(cik)}/{acc}/{doc}"
            year_chunks: list[dict] = []
            for section, prose in sections.items():
                year_chunks.extend(_split_prose_chunks(prose, year, section, source_url))
            by_year[year] = year_chunks
            manifest_entries.append({
                "year": year,
                "filing_date": filing["filing_date"],
                "accession": filing["accession_dashed"],
                "source_url": source_url,
                "sections": list(sections.keys()),
                "n_chunks": len(year_chunks),
            })
            print(f"{len(year_chunks)} chunks ({', '.join(sections.keys()) or 'none'})")
            time.sleep(0.15)

    total = 0
    for year, chunks in sorted(by_year.items()):
        total += write_jsonl(chunks_dir / f"{year}.jsonl", chunks)

    write_json(investor_dir / "investor_manifest.json", {
        "company": company,
        "cik": cik,
        "filings": manifest_entries,
    })
    print(f"\nWrote {total} investor chunks to {chunks_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", required=True)
    parser.add_argument("--max-filings", type=int, default=None)
    parser.add_argument("--min-year", type=int, default=2020)
    args = parser.parse_args()
    main(args.company, args.max_filings, args.min_year)
