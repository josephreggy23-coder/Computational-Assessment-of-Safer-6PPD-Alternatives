# Data dictionary

## `data/raw/usgs/invivo_data.csv`

Official USGS whole-fish exposure records. The pipeline does not alter this
file.

| Field | Meaning |
|---|---|
| `species` | Tested fish species |
| `fish_hatch_date` | Hatch date reported by USGS |
| `exposure_chemical` | USGS chemical label |
| `exposure_start` | Exposure start timestamp |
| `tank_replicate` | Tank replicate identifier |
| `fish_id` | Fish identifier within the exposure group |
| `nominal_conc` | Nominal exposure concentration in micrograms per liter |
| `time_of_death` | Recorded death time where applicable |
| `mass_g` | Fish mass in grams |
| `length_cm` | Fish length in centimeters |
| `mortality` | Observed binary mortality field |
| `initial_or_final` | Sampling-time qualifier |
| `fish_nofish` | Analytical sample qualifier |
| `measured_conc` | Measured concentration in micrograms per liter |
| `flags` | Laboratory or detection qualifier |

The analysis groups mortality by the reported nominal concentration and does
not substitute measured concentrations where values are below detection or
otherwise qualified.

## `data/raw/usgs/invitro_data.csv`

Official USGS well-level cell-line measurements.

| Field | Meaning |
|---|---|
| `well_positions` | Plate-well identifier |
| `concentration` | Reported exposure concentration |
| `cell_type` | Salmonid cell line |
| `rfu` | Relative fluorescence units |
| `antiozonant` | Parent or product label |
| `plate` | Plate identifier |
| `time` | Measurement timestamp |
| `timepoint` | Reported elapsed time |
| `ozone_time` | Ozonation qualifier where applicable |

The reanalysis uses same-read solvent normalization, an explicitly documented
alternative to the source metadata's six-hour reference, which is unavailable.
Relative RFU is an assay response, not a calibrated mortality probability.

## `data/reference/candidate_registry.csv`

Traceable registry of 21 official DTSC candidates plus the 6PPD benchmark.
Mixtures, polymers, materials, and undisclosed products are explicitly marked.

## `data/processed/pubchem_identities.csv`

Unmodified identity fields returned by PubChem for CASRN queries. `resolved`
means PubChem returned a record; it does not by itself mean the structure is a
valid representation of a mixture or material. The analysis applies a separate
discrete-identity gate.

## `results/evidence_matrix.csv`

Boolean evidence-coverage fields and an evidence-readiness conclusion. It is
not a toxicity or safety ranking.

## `results/cell_endpoint_comparison.csv`

Published CSE-119 EC5, EC10, and EC20 values with concentration ratios against
6PPDQ for the same cell line and endpoint. A larger ratio means a higher
concentration is estimated for the same modeled cell effect; it does not prove
whole-organism or environmental safety.

## `results/decision_priorities.csv`

One next decision-changing test for every candidate, selected from actual
evidence coverage and identity status. No numeric safety score is used.

## Version 0.2 derived outputs

| File | Unit and interpretation |
|---|---|
| cell_assay_normalized.csv | One raw well; source_row points to CSV line including header; exact-read control mean, ozone, date, plate group, 24h eligibility and relative RFU. |
| cell_assay_model_oof_predictions.csv | One nonzero dose mean per eligible read; technical_wells_n, outer_fold, domain flag and all model/baseline predictions. |
| cell_assay_fold_audit.csv | One outer fold; JSON arrays of complete train/test plate groups, inner scores and selected models. |
| cell_assay_model_metrics.csv | RMSE/MAE/R², signed residual, conditional plate-bootstrap 95% RMSE and paired gain intervals. Gain is baseline RMSE minus model RMSE. |
| cell_assay_chemical_holdout_predictions.csv | Dose means predicted without their chemical or shared plates in training. |
| cell_assay_chemical_holdout_metrics.csv | Errors per held-out chemical; tests transfer of an identity-based model. |
| cell_assay_permutation_diagnostic.csv | Fixed-model dose-order null RMSE per shuffle and its unshuffled comparator. |
| ozone_matched_dose_contrasts.csv | Matched chemical/cell/dose, means balanced across dates, t25 minus t0 relative RFU and date counts; no causal inference. |
| invivo_tank_summary.csv | One tank, fish/deaths, nominal/measured µg/L, qualifier and measured/nominal ratio. |
| fish_dose_response.csv | LC50 µg/L and tank-bootstrap interval for supported fits, basis, successful/attempted resamples and no-fit status. Blank means unestimated. |
| fish_dose_response_curves.csv | Model predictions within the tested range; these are fitted curves, not new measurements. |
| orthogonal_endpoint_validation.csv | One matched chemical per 10/20/30% threshold; separate observed calls, tested maxima, published EC20 and extrapolation flag. |
| run_manifest.json | SHA-256 fingerprints of inputs, code and output artifacts; versions, seed and normalization/protocol identity. |

The fish summary includes tank ranges and Wilson intervals under the explicitly
stated independent-fish assumption. Candidate priorities also report recorded
deaths in matched products and distinguish no recorded deaths from missing data.
