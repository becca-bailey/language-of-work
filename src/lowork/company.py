"""Per-company profile loaded from data/<company>/url_patterns.json."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .config import company_dir
from .io import read_json


@dataclass
class ValidationHypothesis:
    expected_altruism_peak: int
    tolerance: int = 2
    notes: list[str] = field(default_factory=list)


@dataclass
class CompanyProfile:
    company: str
    display_name: str
    patterns: list[dict]
    hosts: list[str]
    spa_json_probes: list[dict] = field(default_factory=list)
    spa_content_paths: list[str] = field(default_factory=list)
    alt_domains: list[dict] = field(default_factory=list)
    validation: ValidationHypothesis | None = None
    comment: str = ""

    @classmethod
    def from_json(cls, data: dict) -> CompanyProfile:
        validation = None
        if "validation" in data and data["validation"]:
            v = data["validation"]
            validation = ValidationHypothesis(
                expected_altruism_peak=v["expected_altruism_peak"],
                tolerance=v.get("tolerance", 2),
                notes=v.get("notes", []),
            )
        return cls(
            company=data["company"],
            display_name=data.get("display_name", data["company"].title()),
            patterns=data["patterns"],
            hosts=data.get("hosts", []),
            spa_json_probes=data.get("spa_json_probes", []),
            spa_content_paths=data.get("spa_content_paths", []),
            alt_domains=data.get("alt_domains", []),
            validation=validation,
            comment=data.get("comment", ""),
        )

    @classmethod
    def load(cls, company: str) -> CompanyProfile:
        path = company_dir(company) / "url_patterns.json"
        return cls.from_json(read_json(path))

    @property
    def profile_path(self) -> Path:
        return company_dir(self.company) / "url_patterns.json"
