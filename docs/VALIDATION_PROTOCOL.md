# Validation protocol, version 0.2

This is a retrospective computational reanalysis frozen on 2026-09-09.
The repository and authors' results were already inspected. No dataset here
is an untouched external test set. Thresholds and candidate models below are
explicit implementation choices, not a preregistered study protocol.

## 1. Data contracts and experimental units

The source is the [USGS 2026 release](https://www.usgs.gov/data/toxicity-6ppd-alternatives-salmonids).
The raw 1,006 fish rows and 6,244 cell wells remain unchanged. Input files,
analysis source code, output files, package versions and seed are recorded in
`results/run_manifest.json`. Published MD5 checks cover the two CSVs and XML;
the report's SHA-256 is a repository reference checksum, not a published USGS checksum.

Fish identity is species + chemical + exposure start + nominal concentration
+ tank replicate + fish ID. Mortality must be binary. Tank concentrations must
be internally consistent. Duplicate fish, duplicate wells, invalid numeric
values and absent or nonpositive solvent controls stop analysis.

Cell controls match chemical + cell line + plate + exact read timestamp +
ozone condition. Missing ozone labels mean unozonated; `t0` and `t25` are
distinct conditions, as specified in the XML. Their controls are never pooled.
Date + plate is the conservative cross-validation group; shared CSE/CHSE
plates and chemicals read on the same date stay together. This group is
inferred from the available metadata; independence across separate dates
cannot be established as equivalent to different laboratories or batches.

The XML describes a six-hour control reference for published cellular
metabolism. These released observations do not contain that reference. We
use same-read zero-dose controls and label the target **relative RFU**. This
is a documented alternative normalization, not reproduction of the published
EC model. The 80 observations outside the 22–26-hour window stay in the
normalized export but are excluded from 24-hour modeling and triangulation.

## 2. Nonlinear assay prediction

Technical wells are averaged within read and dose. The primary evaluation
contains 1,377 nonzero-dose means spanning 94 conservative plate groups.
Zero-dose controls define normalization and are excluded from scoring.
Test-plate controls may define the measured test target; no treated test
response is used to construct training targets or fit preprocessing.

Inputs: log10(concentration + 0.1 µg/L), exposure hours, chemical identity,
cell line, and ozone condition. Concentrations are nominal mass concentrations;
they support this within-assay task and must not be treated as harmonized
molar QSAR endpoints. Mixture concentrations refer to starting parent mass.

Five outer GroupKFold partitions estimate performance. Three inner grouped
folds select among ridge alpha 0.1/1/10 and Extra Trees with minimum leaf
size 3/10, 150 trees and seed 20260909. Scalers and encoders fit inside each
training partition. Inner MSE selects each family configuration and the overall
winner. Report all family results, the selection procedure, a constant-one
control, and a training-fold mean baseline on identical held-out observations.
The nested procedure follows the rationale in the
[scikit-learn example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html).

All outer memberships, inner scores and choices are exported. Domain coverage
means the held-out chemical/cell/ozone combination appears in training and its
dose lies within that combination's training range. It says nothing about
structural applicability to untested molecules.

RMSE, MAE, R² and mean residual are reported. 1,000 paired plate bootstrap
resamples give percentile intervals for RMSE and improvement over the
training-mean baseline. These resample **fixed OOF errors** and therefore
omit model-refitting and between-laboratory uncertainty.

Two additional stress checks are exported:

- Leave one chemical out, also removing any shared test plates from training.
  A fixed 150-tree, leaf-size-3 model is used. This measures how poorly an
  identity-based model may transfer; it is not a structure-toxicity model.
- Nineteen within-read permutations shuffle dose-response means while keeping
  plate effects intact. A fixed leaf-size-3 ensemble is reevaluated on the same
  outer splits. This is a limited dose-order diagnostic with minimum rank
  resolution 1/20, not a significance test for the nested model-selection
  procedure. Increase `--permutations` for a finer exploratory diagnostic.

## 3. Orthogonal biological endpoints

Compare pure, unozonated quinone CSE measurements with separate 24-hour coho
fish mortality. Equal weight goes to each plate mean at a dose. At exploratory
10%, 20% and 30% response thresholds, call an effect only if an **observed**
mean crosses the threshold somewhere in the tested range. This is descriptive
triangulation across endpoints, with three overlapping chemicals.

Published EC20 estimates are context columns. An estimate beyond the measured
dose range cannot make an observed-effect call positive. Consequently IPPDQ
is discordant at 20% and 30%; it agrees at 10%. The two negative-negative
products do not establish sensitivity, specificity or chemical safety.
Different dose ranges, cell metabolism versus organism survival, exposure
measurement limitations and common study provenance limit interpretation.
There is no cross-endpoint prediction model or external validation accuracy.

## 4. Whole-fish dose response and uncertainty

Report each tank, dose-level fish counts/deaths, tank mortality ranges,
exposure-run counts and measured concentration coverage. Dose-level Wilson
95% intervals are a descriptive independent-fish sensitivity only; they do
not correct shared-tank dependence.

Fit an increasing two-parameter logistic model to positive log10 doses using
a binomial likelihood on tank death counts and denominators. Report LC50 only
when at least four nominal treatment levels exist and observed dose-level
mortality brackets 50%. Reject failed/boundary fits and estimates outside the
tested range. This prevents extrapolating an LC50 for zero-mortality products.

The nominal analysis uses all positive nominal exposures. The measured
sensitivity uses positive, unqualified measured concentrations only; missing,
below-LOD and estimated (`E`) concentrations are not imputed. These analyses
have different sample sets, so their difference is not solely a unit effect.
Re-sample whole tanks within nominal dose/exposure-run strata 300 times.
Give a percentile interval only when at least 80% and 20 fits succeed; report
successful and attempted fits. Small numbers of tanks and a single study
remain limitations. Conditional binomial fitting does not estimate a separate
overdispersion parameter; a hierarchical model needs more independent studies.

## 5. Evidence-gated decisions

Candidate readiness remains based on observed coverage. An additional warning
reports mortality in the matched product dataset. Neither the ensemble nor
missing evidence is used to assign a safety rank. Existing gates for broad
chemical prediction remain: comparable measured acute fish endpoints for at
least 100 discrete chemicals and 20 transformation products, verified molar
units, grouped publications, and reserved external evaluation. These counts
are project screening gates, not guarantees of sufficient statistical power.
