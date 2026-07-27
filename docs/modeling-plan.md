# Modeling plan and gates

The project intentionally begins with no fitted machine-learning model.

## Why

The current USGS candidate-specific dataset is scientifically valuable but
contains multiple endpoint types and relatively few distinct chemicals. A
complex model would learn chemical identity more easily than a generalizable
toxicity relationship.

## Model entry gates

Modeling may begin only when all of the following are true:

1. At least 100 distinct, well-defined chemicals have comparable measured
   organism-level acute fish endpoints.
2. At least 20 distinct transformation products are represented.
3. Units are converted to molar concentration with verified molecular weights.
4. Exposure duration and endpoint definitions are harmonized.
5. Replicate publications and repeated measurements are grouped by chemical.
6. The external evaluation set was not used for feature selection.

## Allowed first model

Elastic net regression or logistic regression, depending on the endpoint.

Maximum initial descriptor set:

- molecular weight;
- measured logKow;
- measured water solubility;
- hydrogen-bond acceptor count;
- quinone/transformation-product flag;
- one quantum electrophilicity descriptor.

## Required comparisons

- Median-only baseline.
- Leave-chemical-out or grouped cross-validation.
- Scaffold-grouped validation when structures permit.
- Bootstrap confidence intervals.
- Y-randomization.
- Performance with predicted properties removed.

## Prohibited shortcuts

- Random row splitting when one chemical contributes multiple records.
- Synthetic minority oversampling.
- Generated molecular structures.
- Filling missing toxicity endpoints with model predictions and retraining.
- Selecting descriptors after examining the external test labels.
- Reporting only R-squared without error and calibration.

