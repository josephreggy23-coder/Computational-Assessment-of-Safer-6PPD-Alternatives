from pathlib import Path

import pandas as pd

from sixppd_assessment.analysis import summarize_invivo_mortality
from sixppd_assessment.io import (
    load_candidate_registry,
    load_sources,
    verify_usgs_files,
)


ROOT = Path(__file__).resolve().parents[1]


def test_usgs_files_match_published_checksums() -> None:
    sources = load_sources(ROOT / "config" / "sources.json")
    inventory = verify_usgs_files(ROOT, sources)
    assert len(inventory) == 2
    assert all(record["checksum_valid"] for record in inventory)
    assert sum(int(record["records"]) for record in inventory) == 7250


def test_registry_contains_21_official_candidates() -> None:
    registry = load_candidate_registry(
        ROOT / "data" / "reference" / "candidate_registry.csv"
    )
    assert registry["role"].eq("official_candidate").sum() == 21
    assert registry["role"].eq("benchmark").sum() == 1


def test_report_endpoint_table_contains_only_published_rows() -> None:
    endpoints = pd.read_csv(
        ROOT / "data" / "reference" / "usgs_report_endpoints.csv"
    )
    assert len(endpoints) == 9
    assert set(endpoints["chemical"]) == {"6PPDQ", "7PPDQ", "IPPDQ"}
    assert set(endpoints["endpoint"]) == {"EC5", "EC10", "EC20"}
    published_ec20 = endpoints.loc[
        endpoints["endpoint"].eq("EC20")
    ].set_index("chemical")["effect_concentration_ug_l"]
    assert published_ec20.to_dict() == {
        "6PPDQ": 4.38,
        "7PPDQ": 490.73,
        "IPPDQ": 408.01,
    }


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
