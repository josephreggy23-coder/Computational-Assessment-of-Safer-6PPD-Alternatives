"""Input validation and integrity checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


def md5sum(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_sources(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def verify_usgs_files(root: Path, sources: dict) -> list[dict[str, object]]:
    inventory: list[dict[str, object]] = []
    entries = dict(sources["usgs_2026"]["files"])
    for name in ["metadata", "report"]:
        meta = sources["usgs_2026"][name]
        entries[meta["filename"]] = meta
    for filename, metadata in entries.items():
        path = root / "data" / "raw" / "usgs" / filename
        exists = path.exists()
        algorithm = "md5" if "md5" in metadata else "sha256"
        observed = (
            hashlib.new(algorithm, path.read_bytes(), usedforsecurity=False).hexdigest()
            if exists
            else None
        )
        expected = metadata[algorithm].lower()
        valid = observed == expected if observed else False
        rows = len(pd.read_csv(path)) if valid and path.suffix == ".csv" else None
        inventory.append(
            {
                "source": "USGS 2026",
                "file": filename,
                "exists": exists,
                "checksum_valid": valid,
                "records": rows,
                "checksum_algorithm": algorithm,
                "expected_checksum": expected,
                "observed_checksum": observed,
                "checksum_origin": "repository reference"
                if algorithm == "sha256"
                else "published USGS MD5",
                "license": sources["usgs_2026"]["license"]
                if algorithm == "md5"
                else "Washington report: preserve attribution",
                "source_url": sources["usgs_2026"]["doi"],
            }
        )
    return inventory


def load_candidate_registry(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"casrn": "string"})
    required = {
        "candidate_id",
        "preferred_name",
        "short_name",
        "casrn",
        "candidate_class",
        "role",
        "usgs_parent_label",
        "usgs_product_label",
        "source_url",
        "retrieval_date",
        "identity_note",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Candidate registry missing columns: {sorted(missing)}")
    if frame["candidate_id"].duplicated().any():
        raise ValueError("candidate_id must be unique")
    official_count = int(frame["role"].eq("official_candidate").sum())
    if official_count != 21:
        raise ValueError(
            f"Expected 21 official DTSC candidates, found {official_count}"
        )
    return frame
