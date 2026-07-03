"""Pinned models, paths, and pipeline constants.

Models are pinned by exact version string and recorded on every output row.
Changing a pin invalidates comparability with previously generated artifacts;
the embedding cache is keyed by model so old vectors are never silently mixed.
"""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
AXES_DIR = ROOT / "axes"
DOCS_DIR = ROOT / "docs"
# Web-facing JSON the export scripts emit and the Astro site reads at build
# time. Lives inside the Astro project so the whole site deploys from `astro/`.
WEB_DATA_DIR = ROOT / "astro" / "src" / "data"

# Pinned models (temperature 0 everywhere)
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSIONS = 3072
CLASSIFIER_MODEL = "claude-haiku-4-5-20251001"
# DEI register classification is a nuanced call (workforce-vs-customer demographics,
# ERG-vs-commitment, CSR-vs-workplace). Haiku needed Sonnet before the prompt carried
# calibration examples; with them it validates at 0.96 vs Sonnet's 0.92 on the
# hand-labeled sample (2026-07), so it's the default for cost and speed.
REGISTER_MODEL = "claude-haiku-4-5-20251001"
JUDGE_MODEL = "claude-sonnet-4-5-20250929"

# Chunking targets
CHUNK_MIN_WORDS = 50
CHUNK_MAX_WORDS = 300

# Scoring
TOP_K = 5  # adaptive: k = min(TOP_K, n_chunks_in_year)

# Near-duplicate threshold (cosine) for carried-forward detection
NEAR_DUP_COSINE = 0.95

CHUNK_LABELS = [
    "mission_brand",
    "employee_story",
    "job_listing",
    "benefits_perks",
    "process_logistics",
    "legal_boilerplate",
    "navigation_junk",
]

# Project 3 (values-as-IP) content filter. Register is already tagged at fetch
# (firm/worker/press/legal) and the axes do the measurement, so this set is
# small: isolate the canon subset (H3/H5 operate on canon, not all firm text)
# and drop junk. CANON_ANALYSIS_LABELS = what gets embedded/scored.
CANON_LABELS = [
    "canon",      # codified mission/values/Creed/"Way"/manifesto, firm voice
    "on_topic",   # substantive relevant content that isn't canon
    "junk",       # nav, code, off-topic tangents, fragments
]
CANON_ANALYSIS_LABELS = {"canon", "on_topic"}


def company_dir(company: str) -> Path:
    d = DATA_DIR / company
    d.mkdir(parents=True, exist_ok=True)
    return d


PIPELINE_CONFIG = ROOT / "pipeline.yaml"


def load_companies(path: Path = PIPELINE_CONFIG) -> list[str]:
    """The company universe, read from pipeline.yaml.

    Single source of truth for "which companies exist." The pipeline passes an
    explicit company set to each stage; scripts use this only as the default for
    standalone CLI runs, so adding a company means editing pipeline.yaml alone.
    """
    import yaml

    return list(yaml.safe_load(path.read_text())["companies"])
