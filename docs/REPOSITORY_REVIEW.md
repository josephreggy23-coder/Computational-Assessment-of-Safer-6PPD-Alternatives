# Research-code review — 2026-09-09

This is a subjective research-code rubric for an evidence-prioritization
project, not an official competition rubric or chemical-safety grade.
Each dimension is worth 10 points; total/80 × 100 gives the percentage.
Scores are judgments supported by evidence, not precise scientific measurements.

| Dimension | Original baseline | Current | Evidence and remaining limitation |
|---|---:|---:|---|
| Question and decision relevance | 9 | 9 | Clear testing-priority question; exposure and tire performance remain incomplete. |
| Provenance and integrity | 10 | 9 | Four verified source assets and input/code/output receipts. Report hash is repository-supplied; registry and identity records remain a dated snapshot. |
| Chemical identity | 9 | 8 | Mixtures excluded from discrete structures; PubChem resolution is not full identity curation. Product chemistry remains incomplete. |
| Statistical validity | 7 | 9 | Exact-read controls, ozone separation, shared plate grouping, technical-well aggregation, tank-resampled LC50 and measured-dose sensitivity. |
| Validation | 3 | 7 | Observed-only orthogonal triangulation, threshold sensitivity, chemical holdout and dose-order diagnostic. No independent external set. |
| ML appropriateness | 7 | 9 | Nested selection, regularized/ensemble/baseline comparisons, OOF predictions, domain flags and conditional cluster intervals. |
| Reproducibility and software | 7 | 10 | Documented installation, pinned versions, complete pipeline, scientific regression tests, CI and artifact receipts. Version snapshot is not a hash lock. |
| Communication and usability | 9 | 9 | Protocol, model card, reproducible figure, warnings and decision table make limitations and next tests explicit. |
| **Total / 80** | **61** | **70** | **76.25% → 87.5% (approximately 88/100)** |

The earlier 78/100 baseline did not match its table arithmetic. The intermediate
85/100 review also overcredited a check that counted an extrapolated EC20 as
an observed effect. Those statements are superseded here. Added complexity
alone earns no credit; correcting unsupported conclusions does.

## Substantive corrections

The earlier control grouping reused plate labels across dates and ozone
treatments. Version 0.2 normalizes each exact read separately and keeps shared
physical plates together during evaluation. Eighty out-of-window observations
are excluded from the 24-hour model. Technical wells are aggregated, and
model choices occur inside training folds.

The earlier three-of-three cell/fish agreement claim was misleading. IPPDQ's
published EC20 of 408.01 µg/L exceeds the tested CSE maximum of 400 µg/L.
Observed CSE means do not reach a 20% reduction, while coho mortality exceeds
20%. Agreement at that threshold is two of three; at 10% it is three of three.
This sensitivity argues against using this cell assay as a sufficient safety
surrogate.

## Current measured results

- Nested selected assay model: RMSE 0.0536 versus training-mean 0.0924 and
  ridge 0.0838; R² 0.662. Conditional plate-bootstrap RMSE interval
  0.0483–0.0587. This is approximately 42% lower error than training-mean.
  The target is 1,377 dose means, so these errors cannot be compared directly
  with the old 6,244-well model.
- All five outer folds select Extra Trees through inner evaluation.
  Held-out 6PPDQ RMSE is approximately 0.214, essentially the training-mean
  comparator's 0.215. Identity features do not support credible prediction
  for an untested chemical.
- IPPDQ nominal LC50: 0.871 µg/L (tank-bootstrap interval 0.810–0.932).
  Unqualified measured-dose subset: 0.785 µg/L (0.714–0.849).
  Both have 300/300 successful bootstrap fits. Other products lack a
  supported LC50 crossing; the pipeline declines to extrapolate.
- All 19 shuffled dose-order diagnostic RMSEs exceed the fixed ensemble's
  unshuffled RMSE. This coarse diagnostic does not establish external validity
  or significance of nested model selection.

## Remaining points require evidence

1. Independently curate more measured fish endpoints with verified structures,
   molar units, duration, censoring and study identifiers. Reserve an untouched
   study/chemical set before additional model choices.
2. Validate decision rules prospectively on those sources and report
   between-study variability and molecular applicability limits.
3. Link parent/product hazards to measured transformation yields,
   environmental exposures and real antiozonant/tire performance.

More algorithms or favorable thresholds cannot replace these evidence gaps.
See [validation protocol](VALIDATION_PROTOCOL.md) and [model card](MODEL_CARD.md).
