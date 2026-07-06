"""Structured benefits extraction for the well-being study (Phase 1.2 / 3).

Unlike the register/stance classifiers (one chunk -> one label), a benefits chunk
enumerates MANY items at once ("gym AND 16-week parental leave AND unlimited PTO"), each
carrying its own category, locus, and specificity. That makes the output a list-of-items,
not a per-chunk label — so this uses Anthropic tool-use (forced structured output) rather
than JSON-in-text, which is where nested lists tend to arrive malformed.

Each extracted item:
  category     — leaf taxonomy (PTO variants, mental-health variants, etc.)
  locus        — individual / structural / ambiguous, per the codebook tie-breakers
  specificity  — the falsifiability gradient (enumerated number > named > generic)
  verbatim     — the span the item was read from (for hand-validation + audit)
  value        — the number/weeks if specificity == enumerated_number, else null

locus is the load-bearing, hardest judgment (the individualization index rests on it), so
the codebook's known hard-cases are baked into the system prompt as explicit rules.
"""

from __future__ import annotations

from anthropic import Anthropic

from .config import JUDGE_MODEL

# Leaf categories — subtypes are split out where they change the locus call
# (unlimited vs minimum-enforced PTO; EAP vs therapy stipend vs shutdown).
CATEGORIES = [
    "pto_accrued",
    "pto_unlimited",
    "pto_minimum_enforced",
    "parental_leave",
    "caregiver_support",
    "mental_health_eap",
    "mental_health_therapy_stipend",
    "mental_health_days",
    "mental_health_shutdown",
    "wellness_perk",
    "sabbatical",
    "remote_flexibility",
    "four_day_week",
    "other",
]
LOCI = ["individual", "structural", "ambiguous"]
SPECIFICITIES = ["enumerated_number", "named_no_number", "generic"]

BATCH_SIZE = 10  # chunks per call; each may yield several items

SYSTEM_PROMPT = """You extract enumerated employee well-being BENEFITS from archived company careers/benefits pages.

You are given a batch of text chunks. For EACH distinct well-being item a chunk names, emit one record. A single chunk usually yields several items; a chunk that names no well-being item yields none. Only extract concrete well-being benefits/perks/policies about the company's own employees — not product copy, not recruiting fluff, not customer or community programs.

OUT OF SCOPE — do NOT emit records for these; skip them entirely:
- Compensation and equity: salary, bonus, commission, equity, stock/options/RSUs, "paid in crypto", ownership.
- Retirement and financial: 401(k)/pension/retirement match, financial-planning perks, insurance of any kind (health, dental, vision, life, disability).
- Anything that is not a well-being benefit (office snacks-as-recruiting, generic "great culture").
These are handled as a separate confound category, not here. `other` is reserved for a GENUINE well-being benefit that fits no leaf category — never use it as a dumping ground for compensation.

For each item assign:

category (choose the most specific that fits):
- pto_accrued: paid time off that accrues by tenure / a fixed number of days
- pto_unlimited: "unlimited" / "flexible" / "take what you need" vacation with no fixed allotment
- pto_minimum_enforced: a MANDATORY minimum vacation the company requires people to take
- parental_leave: maternity / paternity / adoption / bonding leave
- caregiver_support: backup childcare, elder care, family-care support, fertility/family-building
- mental_health_eap: an Employee Assistance Program / counseling hotline only
- mental_health_therapy_stipend: a stipend/subscription for therapy or mental-health apps (Headspace, Modern Health, Lyra)
- mental_health_days: dedicated mental-health days off
- mental_health_shutdown: a company-wide closure / synchronized week off for rest
- wellness_perk: gym/fitness stipend, wellness challenge, generic "wellness" perk
- sabbatical: extended leave after tenure
- remote_flexibility: remote / hybrid / flexible-schedule / work-from-anywhere
- four_day_week: a four-day work week
- other: a clear well-being benefit that fits none of the above

locus — WHO absorbs the adaptation cost when disruption hits:
- individual: the burden/decision sits with the employee. Hard rules: unlimited PTO = individual (no coverage guarantee, decision burden on the worker); EAP = individual; therapy stipend = individual; wellness app/stipend = individual.
- structural: the organization changes its own staffing/scheduling/policy so the individual doesn't absorb it. Hard rules: company-wide shutdown = structural; minimum-enforced PTO = structural; backup childcare = structural; sabbatical = structural (extended leave the company absorbs, like paid parental leave).
- ambiguous: genuinely unclear or mixed; do not force it.

remote_flexibility locus is decided by PHRASING, because remote work cuts both ways (it restructures the company but also shifts overhead — internet, workspace — onto the worker):
- structural when framed as the company's operating model: "distributed", "fully remote", "remote-first", "work from anywhere", "asynchronous"/"async by design", "we work from home".
- individual when framed as personal autonomy or onus on the worker: "work whenever you work best", "flexible hours", "flexibility in your schedule", "flexibility to be there for life's moments".
- ambiguous when it is a bare mention ("remote available", "hybrid") with neither framing.

parental_leave locus follows the same guarantee logic as PTO (paid+defined is the mirror of unlimited PTO — a guaranteed entitlement the org absorbs):
- structural when the leave is paid, job-protected, or enumerated in weeks/months ("16 weeks paid parental leave", "up to 4 months paid").
- ambiguous when named but with no pay or duration stated ("generous parental leave", "parental leave programs").
- individual only when the leave is explicitly unpaid or merely "available" with the burden left to the worker.

work/life-balance framing = individual. When a benefit is presented as helping the employee achieve work/life balance ("balance", "work/life", "be there for life's important moments", "fit work around your life"), that individualizes it — balance is framed as the worker's to manage — so code individual. This governs flexibility and perk items. It does NOT override the explicit structural categories above (paid/enumerated parental leave, minimum-enforced PTO, company-wide shutdown, backup childcare, sabbatical), which stay structural even when "balance" is mentioned.

specificity — the falsifiability gradient:
- enumerated_number: names a concrete number ("16 weeks", "5 days", "$2,000 stipend")
- named_no_number: a named benefit with no number ("generous parental leave", "sabbatical program")
- generic: a vague gesture ("great benefits", "we care about wellbeing")

Also return:
- source_chunk_id: the id of the chunk this item came from
- verbatim: the shortest exact span from the chunk that states the benefit
- value: the number/quantity string if specificity is enumerated_number, else null

Call the record_benefits tool exactly once with all items across the whole batch."""

TOOL = {
    "name": "record_benefits",
    "description": "Record every enumerated well-being benefit found across the batch.",
    "input_schema": {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "source_chunk_id": {"type": "string"},
                        "category": {"type": "string", "enum": CATEGORIES},
                        "locus": {"type": "string", "enum": LOCI},
                        "specificity": {"type": "string", "enum": SPECIFICITIES},
                        "verbatim": {"type": "string"},
                        "value": {"type": ["string", "null"]},
                    },
                    "required": [
                        "source_chunk_id", "category", "locus", "specificity", "verbatim",
                    ],
                },
            }
        },
        "required": ["items"],
    },
}


def _valid(item: dict, valid_ids: set[str]) -> bool:
    return (
        item.get("source_chunk_id") in valid_ids
        and item.get("category") in CATEGORIES
        and item.get("locus") in LOCI
        and item.get("specificity") in SPECIFICITIES
        and bool(item.get("verbatim"))
    )


def extract_benefits(chunks: list[dict], model: str = JUDGE_MODEL) -> list[dict]:
    """Extract benefit items from chunks. Returns a flat list of item dicts, each
    carrying company/year/source_chunk_id from the originating chunk."""
    client = Anthropic()
    meta = {c["chunk_id"]: c for c in chunks}
    items: list[dict] = []

    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        payload = [
            {"id": c["chunk_id"], "heading": c.get("heading", ""), "text": c["text"]}
            for c in batch
        ]
        resp = client.messages.create(
            model=model,
            max_tokens=4000,
            temperature=0,
            system=SYSTEM_PROMPT,
            tools=[TOOL],
            tool_choice={"type": "tool", "name": "record_benefits"},
            messages=[{"role": "user", "content": _dump(payload)}],
        )
        block = next((b for b in resp.content if b.type == "tool_use"), None)
        raw = (block.input.get("items", []) if block else [])
        valid_ids = {c["chunk_id"] for c in batch}
        for it in raw:
            if not _valid(it, valid_ids):
                continue
            src = meta[it["source_chunk_id"]]
            items.append({
                "company": src.get("company"),
                "year": src.get("year"),
                "source_chunk_id": it["source_chunk_id"],
                "category": it["category"],
                "locus": it["locus"],
                "specificity": it["specificity"],
                "verbatim": it["verbatim"],
                "value": it.get("value"),
            })
        print(f"  extracted through chunk {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)} "
              f"({len(items)} items so far)")

    return items


def _dump(payload: list[dict]) -> str:
    import json
    return json.dumps(payload, ensure_ascii=False)
