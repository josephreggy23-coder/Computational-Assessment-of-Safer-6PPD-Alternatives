"""Nested group validation of measured cell dose responses; no candidate QSAR."""

import json

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .assay import aggregate_cell_doses

SEED = 20260909
FEATURES = [
    "log10_concentration",
    "exposure_hours",
    "antiozonant",
    "cell_type",
    "ozone_condition",
]


def model_candidates():
    pre = ColumnTransformer(
        [
            ("numeric", StandardScaler(), FEATURES[:2]),
            (
                "category",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                FEATURES[2:],
            ),
        ]
    )
    candidates = {}
    for alpha in [0.1, 1.0, 10.0]:
        candidates[f"ridge_alpha_{alpha}"] = make_pipeline(
            clone(pre), Ridge(alpha=alpha)
        )
    for leaf in [3, 10]:
        candidates[f"extra_trees_leaf_{leaf}"] = make_pipeline(
            clone(pre),
            ExtraTreesRegressor(
                n_estimators=150, min_samples_leaf=leaf, random_state=SEED, n_jobs=1
            ),
        )
    return candidates


def grouped_splits(frame, group_column="plate_group", n_splits=5):
    n_groups = frame[group_column].nunique()
    if n_groups < 3:
        raise ValueError("At least three groups are required")
    return list(
        GroupKFold(n_splits=min(n_splits, n_groups)).split(
            frame, groups=frame[group_column]
        )
    )


def _fit_predict(model, train, test, target):
    fitted = clone(model).fit(train[FEATURES], target)
    return fitted.predict(test[FEATURES])


def _cluster_intervals(oof, prediction, repetitions=1000):
    """Paired plate bootstrap of fixed OOF errors (does not refit models)."""
    frame = oof.assign(
        error=(oof.relative_rfu - prediction) ** 2,
        baseline_error=(oof.relative_rfu - oof.train_mean_prediction) ** 2,
    )
    group = frame.groupby("plate_group").agg(
        sse=("error", "sum"), base=("baseline_error", "sum"), n=("error", "size")
    )
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(group), size=(repetitions, len(group)))
    sums = group.to_numpy()[idx].sum(axis=1)
    rmse = np.sqrt(sums[:, 0] / sums[:, 2])
    gain = np.sqrt(sums[:, 1] / sums[:, 2]) - rmse
    return (*np.quantile(rmse, [0.025, 0.975]), *np.quantile(gain, [0.025, 0.975]))


def evaluate_models(assay: pd.DataFrame, permutations: int = 19):
    doses = aggregate_cell_doses(assay)
    # Controls define the target scale; scoring controls would add easy samples.
    frame = doses.loc[doses.in_24h_window & doses.concentration.gt(0)].reset_index(
        drop=True
    )
    candidates = model_candidates()
    oof = frame.copy()
    for col in [
        "ridge_prediction",
        "extra_trees_prediction",
        "nested_selected_prediction",
        "train_mean_prediction",
        "outer_fold",
    ]:
        oof[col] = np.nan
    oof["constant_control_prediction"] = 1.0
    oof["in_training_domain"] = False
    splits = grouped_splits(frame)
    audit = []
    for fold, (train_idx, test_idx) in enumerate(splits):
        train, test = frame.iloc[train_idx], frame.iloc[test_idx]
        inner = grouped_splits(train, n_splits=3)
        scores = {}
        for name, model in candidates.items():
            inner_predictions = np.empty(len(train))
            for itrain, itest in inner:
                inner_predictions[itest] = _fit_predict(
                    model,
                    train.iloc[itrain],
                    train.iloc[itest],
                    train.iloc[itrain].relative_rfu,
                )
            scores[name] = mean_squared_error(train.relative_rfu, inner_predictions)
        chosen = min(scores, key=scores.get)
        best_ridge = min((n for n in scores if n.startswith("ridge")), key=scores.get)
        best_tree = min((n for n in scores if n.startswith("extra")), key=scores.get)
        for col, name in [
            ("ridge_prediction", best_ridge),
            ("extra_trees_prediction", best_tree),
            ("nested_selected_prediction", chosen),
        ]:
            oof.loc[test_idx, col] = _fit_predict(
                candidates[name], train, test, train.relative_rfu
            )
        oof.loc[test_idx, "train_mean_prediction"] = train.relative_rfu.mean()
        oof.loc[test_idx, "outer_fold"] = fold
        for idx in test_idx:
            row = frame.loc[idx]
            match = train.loc[(train[FEATURES[2:]] == row[FEATURES[2:]]).all(axis=1)]
            oof.loc[idx, "in_training_domain"] = (
                not match.empty
                and match.concentration.min()
                <= row.concentration
                <= match.concentration.max()
            )
        audit.append(
            {
                "outer_fold": fold,
                "selected_model": chosen,
                "ridge_model": best_ridge,
                "extra_trees_model": best_tree,
                "inner_mse_by_candidate": json.dumps(scores, sort_keys=True),
                "train_plate_groups": json.dumps(sorted(train.plate_group.unique())),
                "test_plate_groups": json.dumps(sorted(test.plate_group.unique())),
                "train_doses_n": len(train),
                "test_doses_n": len(test),
            }
        )

    metrics = []
    for col in [
        "constant_control_prediction",
        "train_mean_prediction",
        "ridge_prediction",
        "extra_trees_prediction",
        "nested_selected_prediction",
    ]:
        low, high, gain_low, gain_high = _cluster_intervals(oof, oof[col])
        metrics.append(
            {
                "model": col.removesuffix("_prediction"),
                "evaluation": "nested_plate_group_cv",
                "rmse": mean_squared_error(oof.relative_rfu, oof[col]) ** 0.5,
                "mae": mean_absolute_error(oof.relative_rfu, oof[col]),
                "r2": r2_score(oof.relative_rfu, oof[col]),
                "mean_residual": (oof.relative_rfu - oof[col]).mean(),
                "rmse_ci_low": low,
                "rmse_ci_high": high,
                "rmse_gain_vs_train_mean_ci_low": gain_low,
                "rmse_gain_vs_train_mean_ci_high": gain_high,
                "n_doses": len(frame),
                "n_plate_groups": frame.plate_group.nunique(),
                "domain_coverage": oof.in_training_domain.mean(),
                "interval_scope": "1000 plate bootstrap resamples of fixed OOF errors; conditional on fitted folds",
            }
        )

    # Chemical holdout is a stress test of this identity-based assay model.
    stress = frame.copy()
    stress["prediction"] = np.nan
    stress["train_mean_prediction"] = np.nan
    stress["held_out_chemical"] = stress.antiozonant
    for chemical in sorted(frame.antiozonant.unique()):
        test_idx = frame.index[frame.antiozonant.eq(chemical)]
        test = frame.loc[test_idx]
        # Also remove shared physical plates to avoid assay-context leakage.
        train = frame.loc[
            ~frame.antiozonant.eq(chemical) & ~frame.plate_group.isin(test.plate_group)
        ]
        stress.loc[test_idx, "prediction"] = _fit_predict(
            candidates["extra_trees_leaf_3"], train, test, train.relative_rfu
        )
        stress.loc[test_idx, "train_mean_prediction"] = train.relative_rfu.mean()
    stress_metrics = (
        stress.groupby("antiozonant")
        .apply(
            lambda d: pd.Series(
                {
                    "n_doses": len(d),
                    "rmse": mean_squared_error(d.relative_rfu, d.prediction) ** 0.5,
                    "train_mean_rmse": mean_squared_error(
                        d.relative_rfu, d.train_mean_prediction
                    )
                    ** 0.5,
                }
            ),
        )
        .reset_index()
    )

    # Diagnostic: destroy dose ordering within each read, preserving run shifts.
    # Fixed model, same outer splits; no claim of a nested-selection significance test.
    null = []
    rng = np.random.default_rng(SEED)
    model = candidates["extra_trees_leaf_3"]
    fixed_predictions = np.empty(len(frame))
    for tr, te in splits:
        fixed_predictions[te] = _fit_predict(
            model, frame.iloc[tr], frame.iloc[te], frame.iloc[tr].relative_rfu
        )
    observed = mean_squared_error(frame.relative_rfu, fixed_predictions) ** 0.5
    for iteration in range(permutations):
        y = frame.relative_rfu.to_numpy().copy()
        for indices in frame.groupby("assay_run").indices.values():
            y[indices] = rng.permutation(y[indices])
        predicted = np.empty(len(frame))
        for tr, te in splits:
            predicted[te] = _fit_predict(model, frame.iloc[tr], frame.iloc[te], y[tr])
        null.append(
            {
                "permutation": iteration + 1,
                "rmse": mean_squared_error(y, predicted) ** 0.5,
                "unpermuted_fixed_model_rmse": observed,
            }
        )
    null_frame = pd.DataFrame(
        null, columns=["permutation", "rmse", "unpermuted_fixed_model_rmse"]
    )
    return (
        pd.DataFrame(metrics),
        oof,
        pd.DataFrame(audit),
        stress,
        stress_metrics,
        null_frame,
    )


def evaluate_grouped_cell_assay_model(assay):
    """Compatibility entry point returning nested metrics and dose-level OOF."""
    metrics, oof, *_ = evaluate_models(assay, permutations=0)
    return metrics, oof
