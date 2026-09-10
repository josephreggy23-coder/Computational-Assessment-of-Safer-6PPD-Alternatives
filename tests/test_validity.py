"""Scientific regression checks; altered rows are test fixtures, never analysis data."""

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from sixppd_assessment.assay import normalize_cell_assay, aggregate_cell_doses
from sixppd_assessment.modeling import evaluate_models, grouped_splits
from sixppd_assessment.toxicology import (
    build_orthogonal_endpoint_validation,
    fit_fish_dose_response,
    summarize_tanks,
)
from sixppd_assessment.io import load_sources, verify_usgs_files
from sixppd_assessment.reporting import verify_manifest
from sixppd_assessment.assay import summarize_ozone_contrasts

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def raw():
    return pd.read_csv(ROOT / "data/raw/usgs/invitro_data.csv")


@pytest.fixture(scope="module")
def fish():
    return pd.read_csv(ROOT / "data/raw/usgs/invivo_data.csv")


@pytest.fixture(scope="module")
def evaluated(raw):
    return evaluate_models(normalize_cell_assay(raw), permutations=0)


def test_controls_do_not_mix_ozone_conditions_or_dates(raw):
    original = normalize_cell_assay(raw)
    changed = raw.copy()
    changed.loc[changed.ozone_time.eq("t25"), "rfu"] *= 3
    other = normalize_cell_assay(changed)
    pd.testing.assert_series_equal(original.relative_rfu, other.relative_rfu)
    assert original.assay_run.nunique() == 157
    assert original.plate_group.nunique() == 94
    assert original.loc[~original.in_24h_window].shape[0] == 80


def test_controls_match_exact_read(raw):
    a = normalize_cell_assay(raw)
    means = a.loc[a.concentration.eq(0)].groupby("assay_run").relative_rfu.mean()
    np.testing.assert_allclose(means, 1)
    assert aggregate_cell_doses(a).technical_wells_n.sum() == len(raw)


@pytest.mark.parametrize(
    "kind", ["missing_control", "zero_control", "negative", "nan", "duplicate"]
)
def test_bad_assay_inputs_fail_closed(raw, kind):
    bad = raw.copy()
    if kind == "missing_control":
        bad = bad.loc[bad.concentration.ne(0)]
    elif kind == "zero_control":
        bad.loc[bad.concentration.eq(0), "rfu"] = 0
    elif kind == "negative":
        bad.loc[0, "concentration"] = -1
    elif kind == "nan":
        bad.loc[0, "rfu"] = np.nan
    else:
        bad = pd.concat([bad, bad.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError):
        normalize_cell_assay(bad)


def test_outer_folds_are_disjoint_at_physical_plate_level(evaluated):
    metrics, oof, audit, *_ = evaluated
    assert oof.plate_group.nunique() < oof.assay_run.nunique()
    assert oof.groupby("plate_group").outer_fold.nunique().eq(1).all()
    assert oof.nested_selected_prediction.notna().all()
    assert oof.concentration.gt(0).all()
    assert oof.exposure_hours.between(22, 26).all()
    for row in audit.itertuples():
        assert set(json.loads(row.train_plate_groups)).isdisjoint(
            json.loads(row.test_plate_groups)
        )
        scores = json.loads(row.inner_mse_by_candidate)
        assert row.selected_model == min(scores, key=scores.get)
        outer_train = oof.loc[oof.outer_fold.ne(row.outer_fold)]
        for train, test in grouped_splits(outer_train, n_splits=3):
            assert set(outer_train.iloc[train].plate_group).isdisjoint(
                outer_train.iloc[test].plate_group
            )
    assert metrics.rmse.ge(0).all()
    assert metrics.rmse_ci_low.le(metrics.rmse_ci_high).all()


def test_baseline_uses_training_only(evaluated):
    _, oof, *_ = evaluated
    for fold in oof.outer_fold.unique():
        expected = oof.loc[oof.outer_fold.ne(fold), "relative_rfu"].mean()
        np.testing.assert_allclose(
            oof.loc[oof.outer_fold.eq(fold), "train_mean_prediction"], expected
        )


def test_extrapolated_report_ec_does_not_change_observed_call(raw, fish):
    endpoints = pd.read_csv(ROOT / "data/reference/usgs_report_endpoints.csv")
    original = build_orthogonal_endpoint_validation(fish, raw, endpoints)
    altered = endpoints.copy()
    altered["effect_concentration_ug_l"] *= 1000
    other = build_orthogonal_endpoint_validation(fish, raw, altered)
    pd.testing.assert_series_equal(
        original.directionally_concordant, other.directionally_concordant
    )
    ippd = original.loc[original.exposure_chemical.eq("IPPDQ")].set_index(
        "effect_threshold"
    )
    assert ippd.loc[0.1, "directionally_concordant"]
    assert not ippd.loc[0.2, "directionally_concordant"]
    assert not ippd.loc[0.3, "directionally_concordant"]


def test_tanks_preserve_individual_counts_and_concentrations(fish):
    tanks = summarize_tanks(fish)
    assert tanks.fish_n.sum() == len(fish)
    assert tanks.deaths.sum() == fish.mortality.sum()
    assert tanks.tank_id.is_unique
    assert tanks.measured_nominal_ratio.gt(10).any()


@pytest.mark.parametrize("kind", ["duplicate", "mortality", "concentration_conflict"])
def test_bad_fish_inputs_rejected(fish, kind):
    bad = fish.copy()
    if kind == "duplicate":
        bad = pd.concat([bad, bad.iloc[[0]]], ignore_index=True)
    elif kind == "mortality":
        bad.loc[0, "mortality"] = 2
    else:
        bad.loc[0, "measured_conc"] = 100
    with pytest.raises(ValueError):
        summarize_tanks(bad)


def test_lc50_only_when_observed_response_brackets_half(fish):
    fits, curves = fit_fish_dose_response(summarize_tanks(fish), bootstrap=20)
    assert fits.loc[fits.lc50_ug_l.notna(), "chemical"].eq("IPPDQ").all()
    assert fits.loc[fits.chemical.ne("IPPDQ"), "lc50_ug_l"].isna().all()
    assert curves.predicted_mortality.between(0, 1).all()
    nominal = fits.loc[
        fits.chemical.eq("IPPDQ") & fits.concentration_basis.eq("nominal")
    ].iloc[0]
    assert 0.5 < nominal.lc50_ug_l < 1.5


def test_metadata_and_report_tampering_detected(tmp_path):
    import shutil

    sources = load_sources(ROOT / "config/sources.json")
    dest = tmp_path / "data/raw/usgs"
    shutil.copytree(ROOT / "data/raw/usgs", dest)
    (dest / "metadata.xml").write_text("invalid fixture")
    inventory = verify_usgs_files(tmp_path, sources)
    assert not next(r for r in inventory if r["file"] == "metadata.xml")[
        "checksum_valid"
    ]


def test_ozone_contrasts_require_matched_doses_and_report_date_counts(raw):
    contrasts = summarize_ozone_contrasts(normalize_cell_assay(raw))
    assert set(contrasts.antiozonant) == {"6PPD", "7PPD", "IPPD"}
    assert contrasts.concentration.gt(0).all()
    assert contrasts.dates_n_t0.ge(1).all() and contrasts.dates_n_t25.ge(1).all()
    assert not contrasts.duplicated(["antiozonant", "cell_type", "concentration"]).any()
    assert contrasts.interpretation.str.contains("confounded").all()


@pytest.mark.parametrize("unsafe", [False, True])
def test_receipt_rejects_changed_or_outside_files(tmp_path, unsafe):
    import hashlib

    (tmp_path / "results").mkdir()
    fixture = tmp_path / "fixture.txt"
    fixture.write_text("original")
    receipt = {
        "schema_version": 1,
        "input_sha256": {},
        "code_sha256": {},
        "output_sha256": {
            "fixture.txt": hashlib.sha256(fixture.read_bytes()).hexdigest()
        },
    }
    path = tmp_path / "results/run_manifest.json"
    path.write_text(json.dumps(receipt))
    assert verify_manifest(tmp_path) == 1
    if unsafe:
        receipt["output_sha256"] = {"../outside.txt": "0" * 64}
        path.write_text(json.dumps(receipt))
    else:
        fixture.write_text("changed")
    with pytest.raises(ValueError):
        verify_manifest(tmp_path)
