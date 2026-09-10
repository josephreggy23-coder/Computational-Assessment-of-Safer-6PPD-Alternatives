"""Assay contracts and local-control normalization of measured observations."""

import numpy as np
import pandas as pd


def require_columns(frame, columns):
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")


def nonnegative_numeric(frame, columns):
    for col in columns:
        frame[col] = pd.to_numeric(frame[col], errors="raise")
        if not np.isfinite(frame[col]).all() or frame[col].lt(0).any():
            raise ValueError(f"{col} must be finite and nonnegative")


def normalize_cell_assay(frame: pd.DataFrame) -> pd.DataFrame:
    """Same-read solvent normalization; not a reproduction of report EC fits.

    Metadata describes a 6-hour control reference, absent from this release.
    We therefore explicitly use same-read zero-dose controls. Plate labels are
    reused across dates, chemicals and ozone conditions: these are never pooled.
    """
    required = [
        "antiozonant",
        "cell_type",
        "plate",
        "time",
        "timepoint",
        "ozone_time",
        "well_positions",
        "concentration",
        "rfu",
    ]
    require_columns(frame, required)
    assay = frame.copy()
    if assay.empty:
        raise ValueError("Empty cell assay")
    keys = ["antiozonant", "cell_type", "plate", "time", "well_positions"]
    if assay[keys].isna().any().any():
        raise ValueError("Missing assay identity")
    nonnegative_numeric(assay, ["concentration", "rfu", "timepoint"])
    assay["ozone_condition"] = assay["ozone_time"].fillna("unozonated")
    if not assay["ozone_condition"].isin(["unozonated", "t0", "t25"]).all():
        raise ValueError("Unknown ozone condition")
    if assay.duplicated(keys + ["ozone_condition"]).any():
        raise ValueError("Duplicate measured well within read")
    assay["source_row"] = np.arange(len(assay)) + 2
    assay["experiment_date"] = pd.to_datetime(
        assay["time"], errors="raise"
    ).dt.strftime("%Y-%m-%d")
    # Conservatively hold shared plates across cell types and chemicals together.
    assay["plate_group"] = assay["experiment_date"] + "|" + assay["plate"]
    grouping = ["antiozonant", "cell_type", "plate", "time", "ozone_condition"]
    controls = (
        assay.loc[assay.concentration.eq(0)]
        .groupby(grouping)
        .rfu.agg(control_mean_rfu="mean", control_wells_n="size")
    )
    assay = assay.join(controls, on=grouping, validate="many_to_one")
    if assay.control_mean_rfu.isna().any() or assay.control_mean_rfu.le(0).any():
        raise ValueError("Every assay read requires positive zero-dose controls")
    assay["relative_rfu"] = assay.rfu / assay.control_mean_rfu
    assay["log10_concentration"] = np.log10(assay.concentration + 0.1)
    assay["exposure_hours"] = assay.timepoint / 60
    assay["in_24h_window"] = assay.exposure_hours.between(22, 26)
    assay["assay_run"] = assay[grouping].astype(str).agg("|".join, axis=1)
    return assay


def aggregate_cell_doses(assay: pd.DataFrame) -> pd.DataFrame:
    """One row per read/dose; technical wells are not independent ML samples."""
    keys = [
        "antiozonant",
        "cell_type",
        "plate",
        "experiment_date",
        "plate_group",
        "assay_run",
        "ozone_condition",
        "concentration",
        "log10_concentration",
        "exposure_hours",
        "in_24h_window",
    ]
    return assay.groupby(keys, as_index=False).agg(
        relative_rfu=("relative_rfu", "mean"),
        technical_wells_n=("rfu", "size"),
        control_mean_rfu=("control_mean_rfu", "first"),
        control_wells_n=("control_wells_n", "first"),
    )


def summarize_ozone_contrasts(assay):
    """Matched dose contrasts; dates are separate batches, so no causal p-value."""
    doses = aggregate_cell_doses(assay)
    doses = doses.loc[
        doses.in_24h_window
        & doses.concentration.gt(0)
        & doses.ozone_condition.isin(["t0", "t25"])
    ]
    keys = ["antiozonant", "cell_type", "concentration"]
    date_means = doses.groupby(
        keys + ["ozone_condition", "experiment_date"], as_index=False
    ).relative_rfu.mean()
    means = date_means.groupby(keys + ["ozone_condition"], as_index=False).agg(
        relative_rfu=("relative_rfu", "mean"), dates_n=("experiment_date", "nunique")
    )
    t0 = means.loc[means.ozone_condition.eq("t0")].drop(columns="ozone_condition")
    t25 = means.loc[means.ozone_condition.eq("t25")].drop(columns="ozone_condition")
    contrast = t0.merge(t25, on=keys, suffixes=("_t0", "_t25"), validate="one_to_one")
    contrast["ozonated_minus_t0_relative_rfu"] = (
        contrast.relative_rfu_t25 - contrast.relative_rfu_t0
    )
    contrast["interpretation"] = (
        "Date-balanced descriptive contrast; ozone and batch are confounded; nominal parent mass, not product concentration"
    )
    return contrast
