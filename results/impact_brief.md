# Impact brief

## Decision headline

Only **2 of 21** official alternatives currently map to an explicitly matched transformation-product organism dataset in this first framework release.

**4 of 21** have matched transformation-product cell-line evidence, while **17 of 21** have no matched toxicity evidence in the included USGS cell or organism files.

**7 of 21** are mixtures, polymers, materials, or proprietary products that cannot be responsibly represented as one molecular structure.

## Measured evidence analyzed

The in-vivo file contains observations covering **6 chemical labels**, **1006 fish records**, and **138 recorded deaths** across the tested concentrations.

The cell-line and whole-fish evidence are kept separate because they are not interchangeable endpoints.

## Measured benchmark comparison

In published coho CSE-119 cell results at EC20, IPPDQ required 93.2x the 6PPDQ concentration (published model estimate); 7PPDQ required 112.0x the 6PPDQ concentration (published model estimate). This indicates lower potency in that assay, not proof of ecological safety.

## Highest-impact next experiment

For each candidate with a defined identity, identify its actual ozonation products and test the complete product mixture in a sensitive salmonid system. Parent-only testing is insufficient: the USGS report found that ozonated mixtures could be more biologically active than purified quinones.

## Validation and model boundary

Across **3** overlapping products, the observed cellular 20% response call and 24-hour coho mortality call were concordant for **2**. This is an orthogonal endpoint check within one release. IPPDQ is discordant at 20% and 30%; its published EC20 lies beyond the cell test range and is excluded from observed calls. The 10% threshold gives a different conclusion. No independent external replication exists.

The nonlinear cell-assay model achieved grouped out-of-fold RMSE **0.054** versus **0.092** for a training-fold mean baseline. Nested selection and shared-plate holdout support only internal assay prediction. The use of chemical identity means it is not a candidate-safety model and does not produce candidate rankings.

## Interpretation boundary

These results rank evidence needs, not chemical safety. A candidate with little data remains unranked; it is not treated as low risk.

## Integrity

All 4 included USGS files passed the recorded integrity checks (published MD5 for data/metadata; repository SHA-256 for the report). No synthetic observations or generated molecules were used.
