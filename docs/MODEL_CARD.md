# Cell-assay model card

Version 0.2; USGS DOI 10.5066/P1DHCMMZ.

**Intended use:** retrospective prediction of relative RFU in replicate plates
under existing chemical/cell/ozone conditions. Evaluation helps inspect assay
reproducibility and dose patterns. No deployment model is shipped.

**Unsupported:** safety certification, unknown-molecule prediction, fish LC50
prediction from RFU, environmental risk estimates, or tire performance.

**Data:** 6,244 original wells, 157 exact assay reads, 94 conservative date/plate
groups. After the 22–26-hour restriction, technical-well averaging and removal
of control doses from scoring, ML uses 1,377 dose means. Cells are coho CSE,
Chinook CHSE and rainbow trout RTG. All data come from one release.

**Target:** RFU averaged at a positive dose in a read, divided by its same-read
zero-dose mean. The publication's six-hour reference is absent; this alternative
normalization is not assumed to yield a calibrated viable-cell fraction.

**Features:** log nominal dose, exposure hours, chemical identity, cell line and
ozone condition. Unknown-category encoding enables stress tests but does not
confer chemical generalization.

**Evaluation:** five outer physical-plate folds and three inner grouped folds;
ridge, Extra Trees and two baselines; fold-fitted preprocessing; complete OOF
and fold audits. Conditional plate-bootstrap intervals, chemical holdout and
within-read dose permutations supplement primary evaluation. All choices are
retrospective and the dataset was already inspected.

**Performance:** selected RMSE 0.0536, R² 0.662, versus training-mean RMSE
0.0924. Intervals condition on fitted OOF predictions. They omit model-refitting
and new-study uncertainty. Held-out chemical performance varies substantially;
6PPDQ is a key failure. See the generated metrics for complete results.

**Applicability:** OOF flags require a known chemical/cell/ozone combination
and a dose in its training range; this is not molecular-domain coverage.
Ozonated mixture concentrations refer to starting parent mass. No model output
enters safety ranks or candidate-readiness tiers.

**Limitations:** inferred plate groups, common study origin, nominal exposure,
limited chemical diversity, possible fluorescence artifacts, endpoint differences,
missing six-hour reference, and few replicate plates. Averaging technical wells
improves precision without adding biological replication.
