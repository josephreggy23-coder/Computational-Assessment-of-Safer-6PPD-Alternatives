"""End-to-end public-data analysis pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .analysis import (
    build_decision_priorities,
    build_evidence_matrix,
    build_impact_brief,
    compare_published_cell_endpoints,
    summarize_invivo_mortality,
)
from .io import load_candidate_registry, load_sources, verify_usgs_files


def run_pipeline(root: Path) -> dict[str, Path]:
    sources = load_sources(root / "config" / "sources.json")
    inventory = pd.DataFrame(verify_usgs_files(root, sources))
    if not inventory["checksum_valid"].all():
        invalid = inventory.loc[~inventory["checksum_valid"], "file"].tolist()
        raise RuntimeError(f"USGS integrity check failed: {invalid}")

    candidates = load_candidate_registry(
        root / "data" / "reference" / "candidate_registry.csv"
    )
    invivo = pd.read_csv(root / "data" / "raw" / "usgs" / "invivo_data.csv")
    invitro = pd.read_csv(root / "data" / "raw" / "usgs" / "invitro_data.csv")
    pubchem_path = root / "data" / "processed" / "pubchem_identities.csv"
    pubchem = pd.read_csv(pubchem_path) if pubchem_path.exists() else None
    endpoints = pd.read_csv(
        root / "data" / "reference" / "usgs_report_endpoints.csv"
    )

    mortality = summarize_invivo_mortality(invivo)
    matrix = build_evidence_matrix(candidates, invivo, invitro, pubchem)
    endpoint_comparison = compare_published_cell_endpoints(endpoints)
    priorities = build_decision_priorities(matrix)
    brief = build_impact_brief(
        inventory, matrix, mortality, endpoint_comparison
    )

    results = root / "results"
    results.mkdir(parents=True, exist_ok=True)
    outputs = {
        "inventory": results / "data_inventory.csv",
        "mortality": results / "invivo_mortality_summary.csv",
        "matrix": results / "evidence_matrix.csv",
        "priorities": results / "decision_priorities.csv",
        "endpoint_comparison": results / "cell_endpoint_comparison.csv",
        "brief": results / "impact_brief.md",
    }
    inventory.to_csv(outputs["inventory"], index=False)
    mortality.to_csv(outputs["mortality"], index=False)
    matrix.to_csv(outputs["matrix"], index=False)
    priorities.to_csv(outputs["priorities"], index=False)
    endpoint_comparison.to_csv(outputs["endpoint_comparison"], index=False)
    outputs["brief"].write_text(brief, encoding="utf-8")
    return outputs
