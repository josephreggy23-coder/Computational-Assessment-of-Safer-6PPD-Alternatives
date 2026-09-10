"""End-to-end public-data analysis pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .analysis import (
    build_orthogonal_endpoint_validation,
    build_decision_priorities,
    build_evidence_matrix,
    build_impact_brief,
    compare_published_cell_endpoints,
    normalize_cell_assay,
    summarize_invivo_mortality,
)
from .io import load_candidate_registry, load_sources, verify_usgs_files
from .modeling import evaluate_models
from .toxicology import summarize_tanks, fit_fish_dose_response
from .reporting import write_figure, write_manifest
from .assay import summarize_ozone_contrasts


def run_pipeline(root: Path, permutations: int = 19) -> dict[str, Path]:
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
    endpoints = pd.read_csv(root / "data" / "reference" / "usgs_report_endpoints.csv")

    mortality = summarize_invivo_mortality(invivo)
    matrix = build_evidence_matrix(candidates, invivo, invitro, pubchem)
    endpoint_comparison = compare_published_cell_endpoints(endpoints)
    normalized_assay = normalize_cell_assay(invitro)
    ozone_contrasts = summarize_ozone_contrasts(normalized_assay)
    assay_metrics, assay_oof, folds, stress, stress_metrics, null = evaluate_models(
        normalized_assay, permutations=permutations
    )
    tanks = summarize_tanks(invivo)
    dose_fits, dose_curves = fit_fish_dose_response(tanks)
    endpoint_validation = build_orthogonal_endpoint_validation(
        invivo, invitro, endpoints
    )
    priorities = build_decision_priorities(matrix)
    observed_deaths = tanks.groupby("exposure_chemical").deaths.sum()
    priorities["matched_product_recorded_deaths"] = matrix.usgs_product_label.map(
        observed_deaths
    )
    priorities["organism_warning"] = priorities.matched_product_recorded_deaths.map(
        lambda n: (
            "No matched organism evidence"
            if pd.isna(n)
            else "Observed product mortality: investigate substitution hazard"
            if n > 0
            else "No deaths in tested range; exposure and other hazards remain unresolved"
        )
    )
    brief = build_impact_brief(
        inventory,
        matrix,
        mortality,
        endpoint_comparison,
        assay_metrics,
        endpoint_validation,
    )

    results = root / "results"
    results.mkdir(parents=True, exist_ok=True)
    outputs = {
        "inventory": results / "data_inventory.csv",
        "mortality": results / "invivo_mortality_summary.csv",
        "matrix": results / "evidence_matrix.csv",
        "priorities": results / "decision_priorities.csv",
        "endpoint_comparison": results / "cell_endpoint_comparison.csv",
        "assay_metrics": results / "cell_assay_model_metrics.csv",
        "assay_oof": results / "cell_assay_model_oof_predictions.csv",
        "endpoint_validation": results / "orthogonal_endpoint_validation.csv",
        "assay_normalized": results / "cell_assay_normalized.csv",
        "ozone_contrasts": results / "ozone_matched_dose_contrasts.csv",
        "folds": results / "cell_assay_fold_audit.csv",
        "stress": results / "cell_assay_chemical_holdout_predictions.csv",
        "stress_metrics": results / "cell_assay_chemical_holdout_metrics.csv",
        "null": results / "cell_assay_permutation_diagnostic.csv",
        "tanks": results / "invivo_tank_summary.csv",
        "dose_fits": results / "fish_dose_response.csv",
        "dose_curves": results / "fish_dose_response_curves.csv",
        "figure": results / "validation_overview.png",
        "brief": results / "impact_brief.md",
    }
    inventory.to_csv(outputs["inventory"], index=False)
    mortality.to_csv(outputs["mortality"], index=False)
    matrix.to_csv(outputs["matrix"], index=False)
    priorities.to_csv(outputs["priorities"], index=False)
    endpoint_comparison.to_csv(outputs["endpoint_comparison"], index=False)
    assay_metrics.to_csv(outputs["assay_metrics"], index=False)
    assay_oof.to_csv(outputs["assay_oof"], index=False)
    endpoint_validation.to_csv(outputs["endpoint_validation"], index=False)
    ozone_contrasts.to_csv(outputs["ozone_contrasts"], index=False)
    for key, frame in [
        ("assay_normalized", normalized_assay),
        ("folds", folds),
        ("stress", stress),
        ("stress_metrics", stress_metrics),
        ("null", null),
        ("tanks", tanks),
        ("dose_fits", dose_fits),
        ("dose_curves", dose_curves),
    ]:
        frame.to_csv(outputs[key], index=False)
    write_figure(outputs["figure"], normalized_assay, mortality, assay_metrics)
    outputs["brief"].write_text(brief, encoding="utf-8")
    outputs["manifest"] = write_manifest(root, outputs, permutations)
    return outputs
