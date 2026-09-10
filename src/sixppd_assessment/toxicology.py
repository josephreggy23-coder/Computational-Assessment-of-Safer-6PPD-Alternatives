"""Tank-aware fish summaries, supported dose fits, and endpoint triangulation."""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

from .assay import (
    aggregate_cell_doses,
    nonnegative_numeric,
    normalize_cell_assay,
    require_columns,
)

TANK = [
    "species",
    "exposure_chemical",
    "exposure_start",
    "nominal_conc",
    "tank_replicate",
]


def summarize_tanks(frame):
    require_columns(frame, TANK + ["fish_id", "mortality", "measured_conc", "flags"])
    fish = frame.loc[frame.fish_id.notna()].copy()
    if fish.empty or fish[TANK].isna().any().any():
        raise ValueError("Missing fish/tank identity")
    if fish.duplicated(TANK + ["fish_id"]).any():
        raise ValueError("Duplicate fish in tank")
    nonnegative_numeric(fish, ["nominal_conc", "mortality"])
    if not fish.mortality.isin([0, 1]).all():
        raise ValueError("Mortality must be binary")
    fish["measured_conc"] = pd.to_numeric(fish.measured_conc, errors="raise")
    present = fish.measured_conc.dropna()
    if (present < 0).any() or not np.isfinite(present).all():
        raise ValueError("Invalid measured concentration")
    fish["qualified"] = fish["flags"].notna()
    # Concentration is tank-level; repeated fish entries must agree.
    if fish.groupby(TANK).measured_conc.nunique().gt(1).any():
        raise ValueError("Conflicting concentrations within tank")
    tanks = fish.groupby(TANK, as_index=False).agg(
        fish_n=("fish_id", "size"),
        deaths=("mortality", "sum"),
        measured_conc=("measured_conc", "first"),
        qualified=("qualified", "any"),
        flags=("flags", lambda x: ";".join(sorted(x.dropna().unique()))),
    )
    tanks["observed_mortality"] = tanks.deaths / tanks.fish_n
    tanks["tank_id"] = tanks[TANK].astype(str).agg("|".join, axis=1)
    tanks["measured_nominal_ratio"] = tanks.measured_conc / tanks.nominal_conc.replace(
        0, np.nan
    )
    return tanks


def summarize_invivo_mortality(frame):
    tanks = summarize_tanks(frame)
    summary = tanks.groupby(
        ["species", "exposure_chemical", "nominal_conc"], as_index=False
    ).agg(
        fish_n=("fish_n", "sum"),
        deaths=("deaths", "sum"),
        tanks_n=("tank_id", "size"),
        exposure_runs_n=("exposure_start", "nunique"),
        min_tank_mortality=("observed_mortality", "min"),
        max_tank_mortality=("observed_mortality", "max"),
        measured_tanks_n=("measured_conc", "count"),
        measured_min_ug_l=("measured_conc", "min"),
        measured_max_ug_l=("measured_conc", "max"),
    )
    summary["observed_mortality"] = summary.deaths / summary.fish_n
    # Wilson intervals are a descriptive fish-binomial sensitivity, not cluster CIs.
    z = 1.959963984540054
    n, p = summary.fish_n, summary.observed_mortality
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    width = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    summary["fish_binomial_ci_low"] = (centre - width).clip(lower=0)
    summary["fish_binomial_ci_high"] = (centre + width).clip(upper=1)
    summary["interval_note"] = (
        "Wilson 95% under independent fish assumption; shared tanks can widen uncertainty"
    )
    return summary


def _fit_logistic(tanks, concentration):
    x = np.log10(tanks[concentration].to_numpy())
    deaths, n = tanks.deaths.to_numpy(), tanks.fish_n.to_numpy()

    def loss(theta):
        eta = theta[0] + np.exp(theta[1]) * x
        return np.sum(n * np.logaddexp(0, eta) - deaths * eta)

    fit = minimize(loss, [0.0, 0.0], method="L-BFGS-B", bounds=[(-40, 40), (-5, 5)])
    if (
        not fit.success
        or np.any(np.isclose(fit.x, [-40, -5]))
        or np.any(np.isclose(fit.x, [40, 5]))
    ):
        return None
    lc50 = 10 ** (-fit.x[0] / np.exp(fit.x[1]))
    if (
        not np.isfinite(lc50)
        or not tanks[concentration].min() <= lc50 <= tanks[concentration].max()
    ):
        return None
    return lc50, fit.x


def fit_fish_dose_response(tanks, bootstrap=300):
    """Binomial logistic likelihood; uncertainty resamples tanks within dose/run."""
    records, curves = [], []
    rng = np.random.default_rng(20260909)
    for chemical, chem in tanks.groupby("exposure_chemical"):
        for basis, column in [
            ("nominal", "nominal_conc"),
            ("measured_unqualified", "measured_conc"),
        ]:
            use = chem.loc[
                chem[column].gt(0) & (True if basis == "nominal" else ~chem.qualified)
            ].reset_index(drop=True)
            row = {
                "chemical": chemical,
                "concentration_basis": basis,
                "n_tanks": len(use),
                "n_fish": int(use.fish_n.sum()),
                "max_tested_ug_l": use[column].max(),
                "lc50_ug_l": np.nan,
                "lc50_ci_low": np.nan,
                "lc50_ci_high": np.nan,
                "bootstrap_valid_n": 0,
                "bootstrap_requested_n": bootstrap,
            }
            means = use.groupby("nominal_conc").agg(
                deaths=("deaths", "sum"), fish_n=("fish_n", "sum")
            )
            rate = means.deaths / means.fish_n
            if len(means) < 4 or not (rate.ge(0.5).any() and rate.lt(0.5).any()):
                row["status"] = "LC50 not bracketed; no extrapolated estimate"
            else:
                fit = _fit_logistic(use, column)
                if fit is None:
                    row["status"] = "Fit unsupported or failed"
                else:
                    lc50, theta = fit
                    row["lc50_ug_l"] = lc50
                    strata = list(
                        use.groupby(["nominal_conc", "exposure_start"]).indices.values()
                    )
                    samples = []
                    for _ in range(bootstrap):
                        indices = np.concatenate(
                            [
                                rng.choice(ix, size=len(ix), replace=True)
                                for ix in strata
                            ]
                        )
                        result = _fit_logistic(use.iloc[indices], column)
                        if result is not None:
                            samples.append(result[0])
                    row["bootstrap_valid_n"] = len(samples)
                    if len(samples) >= max(20, 0.8 * bootstrap):
                        row["lc50_ci_low"], row["lc50_ci_high"] = np.quantile(
                            samples, [0.025, 0.975]
                        )
                    row["status"] = "Fitted within tested range"
                    for conc in np.geomspace(use[column].min(), use[column].max(), 100):
                        curves.append(
                            {
                                "chemical": chemical,
                                "concentration_basis": basis,
                                "concentration_ug_l": conc,
                                "predicted_mortality": expit(
                                    theta[0] + np.exp(theta[1]) * np.log10(conc)
                                ),
                            }
                        )
            row["interpretation"] = (
                "24h coho; zero-dose controls excluded from log fit; tanks resampled within nominal dose/run; no independent study replication"
            )
            records.append(row)
    return pd.DataFrame(records), pd.DataFrame(curves)


def build_orthogonal_endpoint_validation(invivo, invitro, endpoints):
    """Observed-only cross-endpoint comparison; extrapolated ECs stay contextual."""
    mortality = summarize_invivo_mortality(invivo)
    doses = aggregate_cell_doses(normalize_cell_assay(invitro))
    doses = doses.loc[
        doses.cell_type.eq("CSE")
        & doses.in_24h_window
        & doses.ozone_condition.eq("unozonated")
    ]
    means = doses.groupby(
        ["antiozonant", "concentration"], as_index=False
    ).relative_rfu.mean()
    records = []
    for chemical in sorted(set(means.antiozonant) & set(mortality.exposure_chemical)):
        cells = means.loc[means.antiozonant.eq(chemical) & means.concentration.gt(0)]
        fish = mortality.loc[
            mortality.exposure_chemical.eq(chemical) & mortality.nominal_conc.gt(0)
        ]
        ec = endpoints.loc[
            endpoints.chemical.eq(chemical)
            & endpoints.endpoint.eq("EC20")
            & endpoints.cell_type.eq("CSE-119"),
            "effect_concentration_ug_l",
        ]
        published = float(ec.iloc[0]) if len(ec) == 1 else np.nan
        for threshold in [0.1, 0.2, 0.3]:
            cell_call = bool(cells.relative_rfu.le(1 - threshold).any())
            fish_call = bool(fish.observed_mortality.ge(threshold).any())
            records.append(
                {
                    "exposure_chemical": chemical,
                    "effect_threshold": threshold,
                    "cell_highest_tested_ug_l": cells.concentration.max(),
                    "cell_min_mean_relative_rfu": cells.relative_rfu.min(),
                    "cell_effect_observed": cell_call,
                    "fish_highest_tested_ug_l": fish.nominal_conc.max(),
                    "fish_max_observed_mortality": fish.observed_mortality.max(),
                    "fish_effect_observed": fish_call,
                    "published_cell_ec20_ug_l": published,
                    "published_ec20_exceeds_tested_range": bool(
                        published > cells.concentration.max()
                    ),
                    "directionally_concordant": cell_call == fish_call,
                    "validation_interpretation": (
                        "Discordance: cell effect threshold misses organism response"
                        if fish_call and not cell_call
                        else "Effect observed in both systems"
                        if cell_call and fish_call
                        else "Neither threshold reached in tested ranges; safety unproven"
                        if not cell_call and not fish_call
                        else "Cell effect without organism threshold crossing"
                    ),
                    "scope_note": "Exploratory orthogonal endpoint triangulation; unequal concentrations and mechanisms; same release; not external replication",
                }
            )
    return pd.DataFrame(records)
