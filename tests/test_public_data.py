from pathlib import Path

import pandas as pd

from sixppd_assessment.analysis import (
    build_orthogonal_endpoint_validation,
    build_decision_priorities,
    build_evidence_matrix,
    compare_published_cell_endpoints,
    summarize_invivo_mortality,
)
from sixppd_assessment.io import (
    load_candidate_registry,
    load_sources,
    verify_usgs_files,
)


ROOT = Path(__file__).resolve().parents[1]


def test_usgs_files_match_published_checksums() -> None:
    sources = load_sources(ROOT / "config" / "sources.json")
    inventory = verify_usgs_files(ROOT, sources)
    assert len(inventory) == 4
    assert all(record["checksum_valid"] for record in inventory)
    assert sum(int(record["records"] or 0) for record in inventory) == 7250


def test_registry_contains_21_official_candidates() -> None:
    registry = load_candidate_registry(
        ROOT / "data" / "reference" / "candidate_registry.csv"
    )
    assert registry["role"].eq("official_candidate").sum() == 21
    assert registry["role"].eq("benchmark").sum() == 1


def test_report_endpoint_table_contains_only_published_rows() -> None:
    endpoints = pd.read_csv(ROOT / "data" / "reference" / "usgs_report_endpoints.csv")
    assert len(endpoints) == 9
    assert set(endpoints["chemical"]) == {"6PPDQ", "7PPDQ", "IPPDQ"}
    assert set(endpoints["endpoint"]) == {"EC5", "EC10", "EC20"}
    published_ec20 = endpoints.loc[endpoints["endpoint"].eq("EC20")].set_index(
        "chemical"
    )["effect_concentration_ug_l"]
    assert published_ec20.to_dict() == {
        "6PPDQ": 4.38,
        "7PPDQ": 490.73,
        "IPPDQ": 408.01,
    }
    comparison = compare_published_cell_endpoints(endpoints)
    ratios = comparison.loc[comparison["endpoint"].eq("EC20")].set_index("chemical")[
        "concentration_ratio_vs_6ppdq"
    ]
    assert ratios["6PPDQ"] == 1.0
    assert round(ratios["7PPDQ"], 1) == 112.0
    assert round(ratios["IPPDQ"], 1) == 93.2


def test_mortality_summary_preserves_observed_fish_total() -> None:
    invivo = pd.read_csv(ROOT / "data" / "raw" / "usgs" / "invivo_data.csv")
    summary = summarize_invivo_mortality(invivo)
    assert summary["fish_n"].sum() == invivo["fish_id"].notna().sum()
    assert set(summary["species"]) == {"coho"}
    assert set(summary["exposure_chemical"]) == {
        "CCPDQ",
        "CPPDQ",
        "DPPDQ",
        "HPPDQ",
        "IPPDQ",
        "OPPDQ",
    }


def test_each_candidate_receives_a_next_decisive_test() -> None:
    registry = load_candidate_registry(
        ROOT / "data" / "reference" / "candidate_registry.csv"
    )
    invivo = pd.read_csv(ROOT / "data" / "raw" / "usgs" / "invivo_data.csv")
    invitro = pd.read_csv(ROOT / "data" / "raw" / "usgs" / "invitro_data.csv")
    pubchem = pd.read_csv(ROOT / "data" / "processed" / "pubchem_identities.csv")
    matrix = build_evidence_matrix(registry, invivo, invitro, pubchem)
    priorities = build_decision_priorities(matrix)
    assert len(priorities) == len(registry)
    assert priorities["next_decisive_test"].notna().all()
    dtpd = priorities.loc[priorities["short_name"].eq("DTPD/DPPD")].iloc[0]
    assert not dtpd["has_discrete_identity"]
    assert "Resolve composition" in dtpd["next_decisive_test"]


def test_orthogonal_endpoint_validation_keeps_scope_explicit() -> None:
    invivo = pd.read_csv(ROOT / "data" / "raw" / "usgs" / "invivo_data.csv")
    invitro = pd.read_csv(ROOT / "data" / "raw" / "usgs" / "invitro_data.csv")
    endpoints = pd.read_csv(ROOT / "data" / "reference" / "usgs_report_endpoints.csv")
    validation = build_orthogonal_endpoint_validation(invivo, invitro, endpoints)
    assert set(validation["exposure_chemical"]) == {"CCPDQ", "DPPDQ", "IPPDQ"}
    primary = validation.loc[validation.effect_threshold.eq(0.2)]
    assert primary["directionally_concordant"].sum() == 2
    ippd = primary.loc[primary.exposure_chemical.eq("IPPDQ")].iloc[0]
    assert not ippd.cell_effect_observed
    assert ippd.fish_effect_observed
    assert ippd.published_ec20_exceeds_tested_range
    assert validation["scope_note"].str.contains("not external replication").all()
