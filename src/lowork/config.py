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

# Pinned models (temperature 0 everywhere)
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSIONS = 3072
CLASSIFIER_MODEL = "claude-haiku-4-5-20251001"
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
    "job_listing",
    "benefits_perks",
    "process_logistics",
    "legal_boilerplate",
    "navigation_junk",
]


def company_dir(company: str) -> Path:
    d = DATA_DIR / company
    d.mkdir(parents=True, exist_ok=True)
    return d
