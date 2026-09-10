# Modeling plan and gates

Version 0.2 adds nested, grouped prediction of cell-assay dose means.
The target is same-read control-normalized RFU. Chemical identity,
concentration, cell line, ozone condition and exposure time are inputs.
Ridge and Extra Trees are compared with two simple baselines.
See the [validation protocol](VALIDATION_PROTOCOL.md) and
[model card](MODEL_CARD.md) for the complete retrospective procedure.

## Gates for chemical generalization

The present release has six whole-organism chemical labels, 12 cell-assay
labels and no independently reserved external set. A broad structure-toxicity
model requires all of these project gates:

1. At least 100 discrete chemicals with comparable measured acute fish endpoints.
2. At least 20 distinct transformation products.
3. Verified molecular weights and molar concentrations.
4. Harmonized duration, species and endpoints, preserving censoring.
5. Repeated measurements/publications grouped by chemical and study.
6. External evaluation reserved before descriptor and model selection.

The numerical gates are screening requirements, not a power calculation.
Adequacy depends on chemical diversity and measurement noise. Candidate
identities must be curated independently of model outputs.

A primary elastic-net or logistic model, depending on the endpoint, should be
compared with a prespecified gradient-boosted-tree secondary model after these
gates are met. Both need identical chemical/scaffold splits, external studies,
error/calibration metrics, grouped uncertainty and Y-randomization.

## Prohibited shortcuts

- Random row splits of repeated chemicals, plates or tanks.
- Synthetic training observations, generated structures or oversampling.
- Filling unknown toxicities with predictions and retraining.
- Treating parents as sufficient proxies for transformation products.
- Selecting models or features using external evaluation labels.
- Treating missing EC estimates as negatives, or extrapolated estimates as observations.
- Calling resampling or within-study triangulation independent replication.
