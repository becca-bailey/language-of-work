"""Pipeline orchestrator: a stage DAG over the existing scripts.

Defines every corpus-update step as a `Stage` with declared inputs/outputs,
dependency edges, and which stories it serves. A content-hash fingerprint engine
detects which stages are stale (the "diffing tool"); the runner walks the DAG in
topological order and calls each script's `main()` in-process, serially, so
order is always correct and parquet writes never collide.

Stories are the user-facing on/off switch (pipeline.yaml). Company membership is
a property of presentation: per-company analysis stages run for the *union* of
their enabled stories' company sets; export stages filter to their own story's
set. See pipeline.yaml and docs.
"""

from __future__ import annotations

import hashlib
import importlib.util
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable

import yaml

from .config import ROOT, WEB_DATA_DIR, company_dir
from .io import load_all_chunks, read_json, write_json

ANALYSIS_LABELS = {"mission_brand", "benefits_perks"}

CONFIG_PATH = ROOT / "pipeline.yaml"
STATE_PATH = ROOT / "data" / ".pipeline_state.json"
SCRIPTS_DIR = ROOT / "scripts"

GLOBAL_KEY = "*"  # state/company key for global stages

# Axes scored for every company — the per-company "values fingerprint" on the
# explore page reads the full set. `control` is the autonomy axis (used as a
# semantic control for altruism); all have built vectors in axes/built/.
FINGERPRINT_AXES = [
    "altruism", "control", "performance", "meritocracy", "wellbeing",
    "inclusion", "techno_optimism", "wellbeing_locus", "craft",
]


def _axis_inputs(*names: str) -> tuple[str, ...]:
    """Built axis vectors as stage inputs, so editing/rebuilding an axis marks
    its scorers stale (previously a rebuilt vector could silently coexist with
    scores computed from the old one)."""
    return tuple(f"repo:axes/built/{n}.json" for n in names)


class Scope(Enum):
    PER_COMPANY = "per_company"
    GLOBAL = "global"


ALL = "__ALL__"  # sentinel: stage serves every story


# --- calling the existing scripts -------------------------------------------

_loaded: dict[str, object] = {}


def _script(name: str):
    """Import scripts/<name>.py once; its main() is the stage body."""
    if name not in _loaded:
        spec = importlib.util.spec_from_file_location(
            f"_pipeline_scripts.{name}", SCRIPTS_DIR / f"{name}.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        _loaded[name] = mod
    return _loaded[name]


def _call(name: str, *args, **kwargs):
    return _script(name).main(*args, **kwargs)  # type: ignore[attr-defined]


# --- the DAG ----------------------------------------------------------------


@dataclass(frozen=True)
class Stage:
    name: str
    run: Callable                      # (company) for per-company; (companies) for global
    scope: Scope
    stories: tuple[str, ...]           # story slugs, or (ALL,)
    inputs: tuple[str, ...] = ()       # path specs (see _resolve)
    outputs: tuple[str, ...] = ()
    depends: tuple[str, ...] = ()      # upstream stage names (ordering only)


# Path-spec convention: a spec starting with "repo:" resolves under ROOT
# (optionally with a {co} placeholder for per-company exports); any other spec
# is a per-company filename resolved under company_dir(company).
def _resolve(spec: str, company: str | None) -> Path:
    if spec.startswith("repo:"):
        rel = spec[len("repo:"):]
        if company is not None:
            rel = rel.format(co=company)
        return ROOT / rel
    return company_dir(company) / spec  # type: ignore[arg-type]


STAGES: list[Stage] = [
    # --- shared ingestion (every story) ---
    Stage("extract_chunks", lambda c: _call("extract_chunks", c), Scope.PER_COMPANY,
          (ALL,), inputs=("snapshots.json", "raw_html"), outputs=("chunks",)),
    Stage("classify_chunks", lambda c: _call("classify_chunks", c, False), Scope.PER_COMPANY,
          (ALL,), inputs=("chunks",), outputs=("classifications.json",),
          depends=("extract_chunks",)),
    Stage("embed_chunks", lambda c: _call("embed_chunks", c, "dei"), Scope.PER_COMPANY,
          (ALL,), inputs=("chunks", "classifications.json"), outputs=("embeddings.parquet",),
          depends=("classify_chunks",)),

    # --- altruism ---
    Stage("score_axes", lambda c: _call("score_axes", c, FINGERPRINT_AXES),
          Scope.PER_COMPANY, ("altruism", "wellbeing"),
          inputs=("embeddings.parquet", "classifications.json", *_axis_inputs(*FINGERPRINT_AXES)),
          outputs=("axis_scores.parquet",),
          depends=("embed_chunks",)),
    Stage("score_altruism_split", lambda c: _call("score_altruism_split", c),
          Scope.PER_COMPANY, ("altruism", "power"),
          inputs=("embeddings.parquet", "classifications.json",
                  *_axis_inputs("altruism", "techno_optimism")),
          outputs=("altruism_split.parquet",), depends=("embed_chunks",)),

    # --- dei (registers feed both dei and power; stance/phrases are dei-only) ---
    Stage("classify_dei_register",
          lambda c: _call("classify_dei_register", c, False, False, False),
          Scope.PER_COMPANY, ("dei", "power"),
          inputs=("chunks", "classifications.json"), outputs=("dei_registers.json",),
          depends=("classify_chunks",)),
    Stage("classify_dei_stance",
          lambda c: _call("classify_dei_stance", c, heuristic=False, validate_only=False,
                          reclassify_all=False),
          Scope.PER_COMPANY, ("dei",),
          inputs=("chunks", "classifications.json", "dei_registers.json"),
          outputs=("dei_stances.json",), depends=("classify_dei_register",)),
    Stage("score_dei", lambda c: _call("score_dei", c), Scope.PER_COMPANY, ("dei", "power"),
          inputs=("embeddings.parquet", "classifications.json", "dei_registers.json",
                  *_axis_inputs("inclusion", "meritocracy")),
          outputs=("dei_scores.parquet", "dei_evidence.json"),
          depends=("embed_chunks", "classify_dei_register")),
    Stage("score_dei_stance", lambda c: _call("score_dei_stance", c), Scope.PER_COMPANY, ("dei",),
          inputs=("embeddings.parquet", "dei_registers.json", "dei_stances.json",
                  *_axis_inputs("dei_stance")),
          outputs=("dei_stance_scores.parquet", "dei_stance_evidence.json"),
          depends=("embed_chunks", "classify_dei_stance")),
    Stage("track_dei_phrases", lambda c: _call("track_dei_phrases", c),
          Scope.PER_COMPANY, ("dei",),
          inputs=("embeddings.parquet", "classifications.json"), outputs=("dei_phrases.json",),
          depends=("embed_chunks",)),

    # --- performance ---
    Stage("score_performance", lambda c: _call("score_performance", c),
          Scope.PER_COMPANY, ("performance", "power"),
          inputs=("embeddings.parquet", "classifications.json", *_axis_inputs("performance")),
          outputs=("performance_scores.parquet", "performance_evidence.json"),
          depends=("embed_chunks",)),
    Stage("track_performance_phrases", lambda c: _call("track_performance_phrases", c),
          Scope.PER_COMPANY, ("performance",),
          inputs=("embeddings.parquet", "classifications.json"),
          outputs=("performance_phrases.json",), depends=("embed_chunks",)),

    # --- ai (mention tracker is pure regex; the framing axis scores only
    # gated chunks and embeds them itself cache-first, so neither needs
    # embeddings.parquet) ---
    Stage("track_ai_mentions", lambda c: _call("track_ai_mentions", c),
          Scope.PER_COMPANY, ("ai",),
          inputs=("chunks", "classifications.json"), outputs=("ai_mentions.json",),
          depends=("classify_chunks",)),
    Stage("score_ai_language", lambda c: _call("score_ai_language", c),
          Scope.PER_COMPANY, ("ai",),
          inputs=("chunks", "classifications.json", *_axis_inputs("ai_tool_mandate")),
          outputs=("ai_language_scores.parquet", "ai_evidence.json"),
          depends=("classify_chunks",)),

    # --- per-company web exports ---
    Stage("export_web", lambda c: _call("export_web", c), Scope.PER_COMPANY, ("altruism",),
          inputs=("axis_scores.parquet", "altruism_split.parquet"),
          outputs=("repo:astro/src/data/{co}/altruism.json",
                   "repo:astro/src/data/companies.json"),
          depends=("score_axes", "score_altruism_split")),
    Stage("export_dei_web", lambda c: _call("export_dei_web", c), Scope.PER_COMPANY, ("dei",),
          inputs=("dei_scores.parquet",),
          outputs=("repo:astro/src/data/{co}/dei.json", "repo:astro/src/data/companies.json"),
          depends=("score_dei",)),
    Stage("export_ai_web", lambda c: _call("export_ai_web", c), Scope.PER_COMPANY, ("ai",),
          inputs=("ai_mentions.json", "ai_language_scores.parquet"),
          outputs=("repo:astro/src/data/{co}/ai.json",),
          depends=("track_ai_mentions", "score_ai_language")),

    # --- per-company AI narrative (reads the whole export dir generically) ---
    # Hashing the entire {co} export dir means any facet added later flows into
    # both the prompt and change-detection with no edit here; the prompt config is
    # hashed too so editing the prompt/model regenerates. Output lives OUTSIDE
    # the hashed dir so it never sits in its own input set.
    Stage("synthesize_company", lambda c: _call("synthesize_company", c),
          Scope.PER_COMPANY, ("profiles",),
          inputs=("repo:astro/src/data/{co}", "repo:prompts/synthesis.yaml"),
          outputs=("repo:astro/src/data/synthesis/{co}.json",),
          depends=("export_web", "export_dei_web")),

    # --- cross-company values fingerprint (one bar per axis, vs. peers) ---
    # Global: each axis is standardized across the whole cohort, so it must see
    # every company's axis levels at once. Outputs live outside the hashed
    # per-company dir so they don't perturb synthesize_company's inputs.
    Stage("export_fingerprints", lambda comps: _call("export_fingerprints", comps),
          Scope.GLOBAL, ("profiles",), inputs=("axis_scores.parquet",),
          outputs=("repo:astro/src/data/fingerprints/{co}.json",),
          depends=("export_web",)),

    # --- global trackers ---
    Stage("track_benefits", lambda comps: _call("track_benefits", comps), Scope.GLOBAL,
          ("benefits",), inputs=("chunks", "classifications.json"),
          outputs=("repo:data/benefits_trends.md", "repo:astro/src/data/stories/benefits.json"),
          depends=("classify_chunks",)),
    Stage("track_culture_propagation",
          lambda comps: _call("track_culture_propagation", 0.64, 0.50, 0.85, 3, comps), Scope.GLOBAL,
          ("netflix-culture",), inputs=("embeddings.parquet", "classifications.json"),
          outputs=("repo:data/culture_propagation.json",), depends=("embed_chunks",)),

    # --- global story exports (one per story; filter to the story's set) ---
    Stage("export_story_altruism", lambda comps: _call("export_story_web", "altruism", comps),
          Scope.GLOBAL, ("altruism",),
          inputs=("axis_scores.parquet", "altruism_split.parquet"),
          outputs=("repo:astro/src/data/stories/altruism.json",),
          depends=("score_axes", "score_altruism_split")),
    Stage("export_story_dei", lambda comps: _call("export_story_web", "dei", comps),
          Scope.GLOBAL, ("dei",),
          inputs=("dei_scores.parquet", "dei_stance_scores.parquet", "dei_phrases.json"),
          outputs=("repo:astro/src/data/stories/dei.json",),
          depends=("score_dei", "score_dei_stance", "track_dei_phrases")),
    # Wellbeing is a story axis (dataset exported cross-company) but has no MDX
    # story page yet; scoring rides on score_axes via FINGERPRINT_AXES.
    Stage("export_story_wellbeing", lambda comps: _call("export_story_web", "wellbeing", comps),
          Scope.GLOBAL, ("wellbeing",),
          inputs=("axis_scores.parquet",),
          outputs=("repo:astro/src/data/stories/wellbeing.json",),
          depends=("score_axes",)),
    # AI is a story axis like wellbeing (dataset exported cross-company, no MDX
    # story page yet).
    Stage("export_story_ai", lambda comps: _call("export_ai_web", None, True),
          Scope.GLOBAL, ("ai",),
          inputs=("ai_mentions.json", "ai_language_scores.parquet"),
          outputs=("repo:astro/src/data/stories/ai.json",),
          depends=("track_ai_mentions", "score_ai_language")),
    Stage("export_story_performance",
          lambda comps: _call("export_story_web", "performance", comps), Scope.GLOBAL,
          ("performance",), inputs=("performance_scores.parquet", "performance_phrases.json"),
          outputs=("repo:astro/src/data/stories/performance.json",),
          depends=("score_performance", "track_performance_phrases")),
    Stage("export_power_story", lambda comps: _call("export_power_story", comps), Scope.GLOBAL,
          ("power",),
          inputs=("altruism_split.parquet", "dei_scores.parquet", "performance_scores.parquet",
                  "repo:data/power_proxies.json"),
          outputs=("repo:astro/src/data/stories/power.json",),
          depends=("score_altruism_split", "score_dei", "score_performance")),
    Stage("power_robustness", lambda comps: _call("power_robustness"), Scope.GLOBAL, ("power",),
          inputs=("repo:astro/src/data/stories/power.json",),
          outputs=("repo:data/power_robustness.md",), depends=("export_power_story",)),
    Stage("export_netflix_story", lambda comps: _call("export_netflix_story", comps),
          Scope.GLOBAL, ("netflix-culture",),
          inputs=("repo:data/culture_propagation.json", "embeddings.parquet"),
          outputs=("repo:astro/src/data/stories/netflix-culture.json",),
          depends=("track_culture_propagation",)),
]

STAGE_BY_NAME = {s.name: s for s in STAGES}


# --- config -----------------------------------------------------------------


@dataclass
class Config:
    companies: list[str]                   # universe
    enabled: set[str]                      # enabled story slugs
    story_companies: dict[str, list[str]]  # story -> effective company set


def load_config(path: Path = CONFIG_PATH) -> Config:
    raw = yaml.safe_load(path.read_text())
    universe = list(raw["companies"])
    enabled: set[str] = set()
    story_companies: dict[str, list[str]] = {}
    for slug, val in raw["stories"].items():
        if val is False or (isinstance(val, dict) and val.get("enabled") is False):
            continue
        enabled.add(slug)
        subset = val.get("companies") if isinstance(val, dict) else None
        story_companies[slug] = list(subset) if subset else universe
    return Config(universe, enabled, story_companies)


def effective_companies(stage: Stage, cfg: Config) -> list[str]:
    """Union of the company sets of the enabled stories this stage serves."""
    if ALL in stage.stories:
        served = cfg.enabled
    else:
        served = {s for s in stage.stories if s in cfg.enabled}
    out: list[str] = []
    for slug in served:
        for c in cfg.story_companies[slug]:
            if c not in out:
                out.append(c)
    return [c for c in cfg.companies if c in out]  # stable universe order


def active_stages(cfg: Config) -> list[Stage]:
    """Stages serving at least one enabled story, topologically sorted."""
    active = [s for s in STAGES if ALL in s.stories or any(x in cfg.enabled for x in s.stories)]
    names = {s.name for s in active}
    ordered: list[Stage] = []
    seen: set[str] = set()

    def visit(stage: Stage):
        if stage.name in seen:
            return
        seen.add(stage.name)
        for dep in stage.depends:
            if dep in names:
                visit(STAGE_BY_NAME[dep])
        ordered.append(stage)

    for s in active:
        visit(s)
    return ordered


# --- fingerprinting ---------------------------------------------------------


def _hash_path(h, path: Path) -> None:
    if path.is_dir():
        for f in sorted(path.rglob("*")):
            if f.is_file():
                h.update(f"\0{f.relative_to(path)}\0".encode())
                h.update(f.read_bytes())
    elif path.exists():
        h.update(path.read_bytes())
    else:
        h.update(b"\0MISSING\0")


def fingerprint(stage: Stage, companies: list[str]) -> str:
    """Content hash of a stage's inputs (over all in-scope companies)."""
    h = hashlib.sha256()
    targets = companies if stage.scope is Scope.GLOBAL else companies[:1]
    for co in targets or [None]:  # type: ignore[list-item]
        for spec in stage.inputs:
            h.update(f"\0{spec}@{co}\0".encode())
            _hash_path(h, _resolve(spec, co))
    return h.hexdigest()[:16]


# Stages whose output must cover every (analysis) chunk, not merely exist —
# an incremental classifier whose file exists but skips new chunks is "dirty".
# Maps stage -> (output filename, chunk set: "all" chunks or "analysis" only).
_COVERAGE: dict[str, tuple[str, str]] = {
    "classify_chunks": ("classifications.json", "all"),
    "embed_chunks": ("embeddings.parquet", "analysis"),
    "classify_dei_register": ("dei_registers.json", "analysis"),
    "classify_dei_stance": ("dei_stances.json", "analysis"),
}


def _coverage_incomplete(stage_name: str, company: str) -> bool:
    """True if a coverage-tracked stage's output misses some required chunk."""
    spec = _COVERAGE.get(stage_name)
    if spec is None:
        return False
    fname, which = spec
    cdir = company_dir(company)
    chunks_dir = cdir / "chunks"
    if not chunks_dir.exists():
        return False
    chunks = load_all_chunks(chunks_dir)
    if which == "all":
        required = {c["chunk_id"] for c in chunks}
    else:
        cls_p = cdir / "classifications.json"
        labels = read_json(cls_p) if cls_p.exists() else {}
        required = {c["chunk_id"] for c in chunks
                    if labels.get(c["chunk_id"]) in ANALYSIS_LABELS}
    out = cdir / fname
    if not out.exists():
        return bool(required)
    if fname.endswith(".parquet"):
        import pandas as pd
        covered = set(pd.read_parquet(out, columns=["chunk_id"])["chunk_id"])
    else:
        covered = set(read_json(out))
    return not required.issubset(covered)


def _outputs_present(stage: Stage, companies: list[str]) -> bool:
    targets = companies if stage.scope is Scope.GLOBAL else companies[:1]
    for co in targets or [None]:  # type: ignore[list-item]
        for spec in stage.outputs:
            if not _resolve(spec, co).exists():
                return False
    return True


def _state_key(stage: Stage, company: str) -> str:
    return f"{stage.name}:{company}"


def load_state() -> dict:
    return read_json(STATE_PATH) if STATE_PATH.exists() else {}


def save_state(state: dict) -> None:
    write_json(STATE_PATH, state)


# --- evaluation (shared by diff and run) ------------------------------------


@dataclass
class Step:
    stage: Stage
    companies: list[str]   # which companies to run (the effective/in-scope set)
    reason: str


def changed_companies(cfg: Config, state: dict) -> list[str]:
    """Companies whose ingestion input (snapshots.json/raw_html) has changed."""
    st = STAGE_BY_NAME["extract_chunks"]
    out = []
    for co in cfg.companies:
        if state.get(_state_key(st, co)) != fingerprint(st, [co]) \
                or not _outputs_present(st, [co]):
            out.append(co)
    return out


def evaluate(cfg: Config, state: dict, only_companies: set[str] | None = None,
             force: bool = False) -> list[Step]:
    """Predictive plan: stages (and the companies) that need to run, in DAG order.

    A stage is dirty if its input fingerprint changed, an output is missing, or
    any upstream stage is dirty (propagated). Used by both `diff` (report) and
    `run` (execute) so they never disagree.
    """
    plan: list[Step] = []
    dirty_pc: dict[str, set[str]] = {}   # per-company stage -> dirty companies
    dirty_g: set[str] = set()            # dirty global stage names

    for stage in active_stages(cfg):
        comps = effective_companies(stage, cfg)
        if stage.scope is Scope.PER_COMPANY:
            run_for: set[str] = set()
            reasons: set[str] = set()
            for co in comps:
                if only_companies is not None and co not in only_companies:
                    continue
                up = [d for d in stage.depends if co in dirty_pc.get(d, set())]
                if force:
                    run_for.add(co); reasons.add("forced")
                elif up:
                    run_for.add(co); reasons.add(f"upstream {up[0]}")
                elif not _outputs_present(stage, [co]):
                    run_for.add(co); reasons.add("output missing")
                elif _coverage_incomplete(stage.name, co):
                    run_for.add(co); reasons.add("incomplete coverage")
                elif state.get(_state_key(stage, co)) != fingerprint(stage, [co]):
                    run_for.add(co); reasons.add("inputs changed")
            if run_for:
                dirty_pc[stage.name] = run_for
                plan.append(Step(stage, [c for c in comps if c in run_for],
                                 ", ".join(sorted(reasons))))
        else:  # GLOBAL
            up = [d for d in stage.depends
                  if dirty_pc.get(d) or d in dirty_g]
            reason = None
            if force:
                reason = "forced"
            elif up:
                reason = f"upstream {up[0]}"
            elif not _outputs_present(stage, comps):
                reason = "output missing"
            elif state.get(_state_key(stage, GLOBAL_KEY)) != fingerprint(stage, comps):
                reason = "inputs changed"
            if reason:
                dirty_g.add(stage.name)
                plan.append(Step(stage, comps, reason))
    return plan


def run(cfg: Config, only_companies: set[str] | None = None, force: bool = False) -> list[Step]:
    """Execute the plan in DAG order, in-process and serially, updating state."""
    state = load_state()
    plan = evaluate(cfg, state, only_companies, force)
    for step in plan:
        stage = step.stage
        if stage.scope is Scope.PER_COMPANY:
            for co in step.companies:
                print(f"[run] {stage.name} :: {co} ({step.reason})")
                stage.run(co)
                state[_state_key(stage, co)] = fingerprint(stage, [co])
        else:
            print(f"[run] {stage.name} :: {len(step.companies)} companies ({step.reason})")
            stage.run(step.companies)
            state[_state_key(stage, GLOBAL_KEY)] = fingerprint(stage, step.companies)
        save_state(state)  # checkpoint after each stage
    return plan


def record_baseline(cfg: Config) -> int:
    """Mark all stages clean against the current files (no execution).

    Run once after adopting the orchestrator on an already-built corpus so the
    first real `run` is incremental instead of rebuilding everything.
    """
    state: dict = {}
    n = 0
    for stage in active_stages(cfg):
        comps = effective_companies(stage, cfg)
        if stage.scope is Scope.PER_COMPANY:
            for co in comps:
                state[_state_key(stage, co)] = fingerprint(stage, [co])
                n += 1
        else:
            state[_state_key(stage, GLOBAL_KEY)] = fingerprint(stage, comps)
            n += 1
    save_state(state)
    return n


# --- coverage / validate ----------------------------------------------------


def coverage(company: str) -> dict:
    """Per-company chunk → classified → register → stance → embedded counts."""
    import pandas as pd
    cdir = company_dir(company)
    chunks_dir = cdir / "chunks"
    n_chunks = len(load_all_chunks(chunks_dir)) if chunks_dir.exists() else 0
    cls = read_json(cdir / "classifications.json") if (cdir / "classifications.json").exists() else {}
    analysis = {cid for cid, lab in cls.items() if lab in ANALYSIS_LABELS}

    def _keys(name: str) -> set[str]:
        p = cdir / name
        return set(read_json(p)) if p.exists() else set()

    reg, stance = _keys("dei_registers.json"), _keys("dei_stances.json")
    emb: set[str] = set()
    epath = cdir / "embeddings.parquet"
    if epath.exists():
        emb = set(pd.read_parquet(epath, columns=["chunk_id"])["chunk_id"])
    return {
        "company": company, "chunks": n_chunks, "classified": len(cls),
        "analysis": len(analysis),
        "register_missing": len(analysis - reg),
        "stance_missing": len(analysis - stance),
        "embed_missing": len(analysis - emb),
    }


def validate(cfg: Config) -> list[str]:
    """Coverage assertions. Returns a list of warning strings (empty == OK)."""
    warnings: list[str] = []
    # config sanity: every story allow-list is a subset of the universe
    universe = set(cfg.companies)
    for slug, comps in cfg.story_companies.items():
        extra = set(comps) - universe
        if extra:
            warnings.append(f"story '{slug}' lists companies not in `companies`: {sorted(extra)}")

    dei_set = set(cfg.story_companies.get("dei", [])) | set(cfg.story_companies.get("power", []))
    for co in cfg.companies:
        cov = coverage(co)
        if cov["analysis"] and cov["embed_missing"]:
            warnings.append(f"{co}: {cov['embed_missing']} analysis chunks not embedded "
                            f"(run embed_chunks)")
        if co in dei_set and cov["analysis"]:
            if cov["register_missing"]:
                warnings.append(f"{co}: {cov['register_missing']} analysis chunks lack a DEI "
                                f"register (run classify_dei_register) — score_dei would emit zeros")
            if cov["stance_missing"]:
                warnings.append(f"{co}: {cov['stance_missing']} analysis chunks lack a DEI stance "
                                f"(run classify_dei_stance)")
    return warnings


def prose_figures() -> dict:
    """Cross-company numbers that hand-written MDX cites — surface for eyeballing."""
    out: dict = {}
    pr = ROOT / "data" / "power_robustness.md"
    if pr.exists():
        for line in pr.read_text().splitlines():
            if line.startswith("| Idealism") or line.startswith("| DEI language"):
                cells = [c.strip().replace("*", "") for c in line.strip("|").split("|")]
                out[cells[0]] = f"r_raw={cells[1]} r_diff={cells[3]} LOO={cells[5]}"
    nf = WEB_DATA_DIR / "stories" / "netflix-culture.json"
    if nf.exists():
        obj = read_json(nf).get("objectivity", {})
        out["netflix objectivity.scanned"] = obj.get("scanned")
    return out
