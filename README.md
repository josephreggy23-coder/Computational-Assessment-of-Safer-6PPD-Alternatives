# TREADSENTINEL

## Cross-Endpoint Toxicity Assessment and Evidence-Gated Screening of 6PPD Alternatives

**Paper title:** *TREADSENTINEL: Cross-Endpoint Toxicity Assessment and
Evidence-Gated Screening of 6PPD Alternatives.*

**Author:** Joseph Reggy · **Software version:** 0.2.0 ·
**Analysis snapshot:** 2026-09-09 · **Study type:** retrospective computational
reanalysis of public experimental data · **Manuscript status:** unpublished draft.

This README is both the project overview and a self-contained briefing for
Claude or another report writer. It explains the scientific question, data,
implemented methods, verified results, interpretation boundaries, and the
files supporting each claim.

[Paper draft](docs/PAPER_DRAFT.md) ·
[Validation protocol](docs/VALIDATION_PROTOCOL.md) ·
[Model card](docs/MODEL_CARD.md) ·
[Data provenance](docs/data-provenance.md) ·
[Data dictionary](docs/data-dictionary.md)

![Cross-endpoint comparison and nested model evaluation](results/validation_overview.png)

## 1. Executive summary

TREADSENTINEL asks which proposed replacements for the tire antiozonant 6PPD
have enough evidence for comparative testing, which show measured warning
signals, and which cannot yet be evaluated responsibly.

The contribution is a reproducible framework connecting candidate identity,
parent/product evidence, cell-assay responses, whole-fish mortality, and
testing priorities. It includes an internally evaluated nonlinear model of
cellular assay response. The framework does not identify a proven safe tire
replacement or establish that a candidate works in a commercial tire.

The main findings of the committed analysis are:

1. **Evidence is sparse:** only 2 of 21 registry alternatives have explicitly
   matched transformation-product whole-fish evidence; 4 have matched product
   cell data, and 17 have no matched toxicity evidence in the included files.
2. **Endpoints can disagree:** IPPDQ crosses the 20% coho mortality threshold
   but does not show an observed 20% reduction in mean CSE signal within the
   tested cell-dose range. Agreement across the three overlapping products is
   2/3 at 20% and 30%, changing to 3/3 at 10%.
3. **A supported fish dose response exists for IPPDQ:** nominal 24-hour LC50 is
   0.871 µg/L, with a tank-bootstrap 95% interval of 0.810–0.932. The measured,
   unqualified concentration subset yields 0.785 µg/L (0.714–0.849).
4. **The ensemble predicts replicate assay responses better than simple
   comparators:** nested selected RMSE is 0.0536 versus 0.0924 for a
   training-mean baseline, an approximately 42% reduction on the same target.
5. **Chemical transfer remains weak:** when 6PPDQ is held out entirely, the
   fixed ensemble's RMSE is 0.2144 versus 0.2152 for the training-mean
   comparator. Internal replicate-plate prediction does not establish
   generalization to new molecules.

All findings are retrospective and arise from one USGS release. There is no
independently reserved external validation dataset.

## 2. Scientific motivation, question, and contribution

6PPD protects tire rubber against ozone damage. Its transformation product
6PPD-quinone motivates concern about salmonid toxicity and interest in
replacement antiozonants. The USGS studies included here examine parent
chemicals, purified quinones, and selected ozonated product mixtures
([data release](https://www.usgs.gov/data/toxicity-6ppd-alternatives-salmonids);
[report record](https://pubs.usgs.gov/publication/70273838)).

The decision question is:

> Which publicly identified 6PPD alternatives warrant comparative testing,
> which have measured hazard warnings, and which require additional identity
> or toxicity evidence before a defensible assessment?

A separate mechanistic hypothesis in the [research plan](docs/research-plan.md)
concerns quinone-like transformation products and electrophilicity.
**That hypothesis is not established here:** the repository does not measure
electrophilicity, reaction energies, transformation yields, or environmental
exposure. Present results support evidence prioritization and assay analysis.

The project's original contribution is the computational integration and
reanalysis, not the collection of the underlying experimental measurements.
The intended readers are environmental researchers, materials scientists,
and others allocating resources for substitution testing.

## 3. What is implemented and what remains planned

| Component | Current status | Permitted use |
|---|---|---|
| Candidate registry and identity gate | Implemented for 21 alternatives plus 6PPD | Identify matched evidence and unresolved composition |
| Parent/product evidence matrix | Implemented | Describe coverage in the included sources |
| Cellular control normalization | Implemented using same-read solvent controls | Analyze relative fluorescence within defined assay conditions |
| Fish mortality and dose-response analysis | Implemented with tank summaries and nominal/measured sensitivity | Estimate supported within-study LC50s and expose uncertainty |
| Cross-endpoint comparison | Implemented for three overlapping products | Explore observed cellular/organism agreement and disagreement |
| Nested ridge/Extra Trees comparison | Implemented | Evaluate replicate-plate assay prediction |
| Chemical holdout and permutation diagnostics | Implemented | Test transfer limits and contribution of dose ordering |
| Ozonation contrasts | Implemented descriptively | Compare matched doses while disclosing batch confounding |
| Broad structure-toxicity QSAR | Not implemented | Requires additional curated chemicals and harmonized endpoints |
| Independent external validation | Not available | Requires an untouched independent study/chemical set |
| Quantum descriptors, fate/exposure integration | Planned | No computed results should be attributed to these components |
| Tire performance or replacement certification | Not established | Requires physical performance and realistic exposure evidence |

## 4. Data inventory and provenance

### Sources and units of observation

| Source/file | Contents | Role in this analysis |
|---|---|---|
| [USGS in-vivo CSV](data/raw/usgs/invivo_data.csv) | 1,006 coho records; six product labels; 126 tanks; 138 recorded deaths | Measured whole-organism response |
| [USGS in-vitro CSV](data/raw/usgs/invitro_data.csv) | 6,244 measured cell wells; 12 chemical labels; three cell types | Measured cellular assay response |
| [USGS metadata](data/raw/usgs/metadata.xml) | Experimental and field definitions | Interpretation of units, timing, controls, and qualifiers |
| [Archived report](data/raw/usgs/usgs_2026_alternatives_final_report.pdf) | Published study report | Context and published fitted cell endpoints |
| [Published endpoint transcription](data/reference/usgs_report_endpoints.csv) | Nine CSE-119 EC5/EC10/EC20 estimates for 6PPDQ, 7PPDQ, and IPPDQ | Comparison of published model estimates |
| [Candidate registry](data/reference/candidate_registry.csv) | 21 DTSC alternatives plus the 6PPD benchmark | Evidence matching and identity restrictions |
| [PubChem identity snapshot](data/processed/pubchem_identities.csv) | CASRN query responses and structure/identity fields | Candidate identity support, subject to the discrete-identity gate |

The six fish product labels are **CCPDQ, CPPDQ, DPPDQ, HPPDQ, IPPDQ, and OPPDQ**.
There are no 6PPDQ fish observations in this included fish CSV. Do not infer
an in-vivo 6PPDQ reference LC50 from this file.

Cell types are **CSE** (CSE-119, coho), **CHSE** (CHSE-214, Chinook), and
**RTG** (RTG-2, rainbow trout). Cell wells, fish, tanks, assay reads,
chemical labels, and independent studies are different sample units.
The 7,250 combined raw rows do not represent 7,250 independent chemicals or
a single harmonized training dataset.

The DTSC registry is a **2026-07-27 snapshot**, not a claim about the current
regulatory list. Coverage statements describe only the sources included in
this repository, not the complete published literature.
EPA ECOTOX and CompTox remain planned expansion sources.

### Integrity and attribution

The USGS data release is CC0; repository software is MIT licensed.
Preserve attribution for the Washington report, DTSC page and PubChem records.
Source URLs and expected checksums are in [config/sources.json](config/sources.json).

| Source asset | Checksum type | Expected value |
|---|---|---|
| invivo_data.csv | Published MD5 | bcffc127f53bffb32cb91f83b203c152 |
| invitro_data.csv | Published MD5 | d25a1bef7229d2a18ac5af33ab7ffb21 |
| metadata.xml | Published MD5 | 3782097fca192ee32f24fbc806c75013 |
| Archived report PDF | Repository reference SHA-256 | 102f032f3722f8c06f1cf91cce319f69d2c7128c29d7d936de62d51d11acb933 |

The report hash is **not** a published USGS MD5. The pipeline checks all four
assets and writes [data_inventory.csv](results/data_inventory.csv).
[.gitattributes](.gitattributes) preserves scientific source bytes across
checkouts. No experimental values were edited to improve performance.

## 5. Analysis workflow and exact methods

The executable workflow is in
[pipeline.py](src/sixppd_assessment/pipeline.py).
The authoritative detailed method is
[VALIDATION_PROTOCOL.md](docs/VALIDATION_PROTOCOL.md).
All model and threshold choices are retrospective, not preregistered.

### 5.1 Input contracts

Fish identity combines species, chemical, exposure start, nominal
concentration, tank replicate and fish ID. Mortality must be binary, and
repeated measured concentrations within a tank must agree.
Duplicate fish/wells, invalid numeric values, missing identifiers, and absent
or nonpositive zero-dose controls stop the relevant analysis.

Concentrations are reported in **µg/L**. Missing, estimated, or below-detection
measurements are not silently converted into exact exposures.
The observed fish file is summarized at both tank and nominal-dose levels.

### 5.2 Cell normalization and experimental units

Each measured well is normalized as:

~~~text
relative RFU = measured well RFU / mean zero-dose RFU from the same assay read
~~~

The control match includes **chemical + cell line + plate + exact timestamp +
ozone condition**. Missing ozone labels indicate unozonated samples; t0 and
t25 remain separate conditions. Reused plate labels from different dates or
ozone treatments must not have their controls pooled.

The source metadata describes a six-hour control reference that is absent
from the released observations. Same-read normalization is a documented
alternative. It does **not** reproduce the authors' published EC fitting
procedure, and relative RFU is not assumed to be a calibrated viable-cell
fraction or fish mortality probability.

There are **157 exact assay reads** and **94 conservative date/plate groups**.
Eighty observations outside **22–26 hours** remain in the normalized export
but are excluded from 24-hour modeling and triangulation. Technical wells are
averaged within each read and dose. Zero-dose controls define the target scale
and are excluded from model scoring, yielding **1,377 positive-dose means**.

For validation, **date + plate** keeps shared plates across cell lines and
chemicals together. This grouping is inferred from available metadata; separate
plates are not equivalent to independent laboratories or studies.

### 5.3 Nested machine-learning evaluation

The ML target is the mean relative RFU for one positive dose in one eligible
assay read. Its intended use is predicting responses for replicate plates
under existing chemical/cell/ozone conditions.

| Setting | Implemented value |
|---|---|
| Numeric features | log10(concentration + 0.1), with concentration expressed numerically in µg/L; exposure hours |
| Categorical features | Chemical identity, cell line, ozone condition |
| Preprocessing | Standard scaling for numeric features; one-hot encoding for categorical features |
| Outer evaluation | Five GroupKFold partitions using date/plate groups |
| Inner model selection | Three grouped folds inside each outer training partition |
| Ridge candidates | Regularization alpha 0.1, 1.0, 10.0 |
| Extra Trees candidates | 150 trees; minimum leaf size 3 or 10 |
| Selection objective | Inner out-of-fold mean squared error |
| Baselines | Constant relative RFU of 1.0; training-fold mean response |
| Random seed | 20260909 |
| Primary metrics | RMSE, MAE, R², signed mean residual |
| Uncertainty | 1,000 paired plate-bootstrap resamples of fixed OOF errors |

Preprocessors are fitted within training partitions. Model configuration and
family selection occur in the inner folds; outer held-out responses evaluate
that selection procedure. Family results and the overall selected result are
reported together rather than showing only a favorable model.

Test-plate solvent controls define the observed test target. Treated test
responses do not enter training targets or fitted preprocessing.
The exported applicability flag checks whether the chemical/cell/ozone
combination exists in training and the dose falls within its training range.
Its 100% coverage in this run is **not** 100% molecular applicability to new
chemicals.

The bootstrap intervals condition on existing OOF predictions. They do not
refit the model in each draw or capture new-laboratory uncertainty.

### 5.4 Additional model diagnostics

**Chemical holdout:** hold out one chemical, remove any shared test plates
from training, and evaluate a fixed 150-tree, leaf-size-3 Extra Trees model.
This is a stress test of an identity-based model, not a validated molecular QSAR.

**Dose-order permutations:** shuffle response means within each exact read,
preserving read-specific effects while disrupting dose ordering. Reevaluate
the fixed leaf-size-3 ensemble on the same outer splits. The default has
19 permutations, giving a minimum possible rank resolution of 1/20.
This is an exploratory diagnostic, not a significance test for the full
nested model-selection process. It is not evidence of external validation.

### 5.5 Fish dose-response fitting

The model uses an increasing two-parameter logistic relation to positive
log10 concentration, fitted by a binomial likelihood on tank death counts and
fish denominators. Zero-dose controls are excluded from the log-dose fit.

An LC50 is reported only if at least four nominal treatment levels are
available, observed dose-level mortality brackets 50%, optimization succeeds,
and the fitted LC50 lies within the tested concentration range.
Unsupported or boundary fits remain unestimated.

Two analyses are kept separate:

- **Nominal:** all positive nominal exposures for the product.
- **Measured, unqualified:** positive measured concentrations without missing,
  below-LOD, or estimated (E) qualifiers. No concentration is imputed.

Whole tanks are resampled within nominal-dose/exposure-run strata 300 times.
A percentile interval requires at least 20 successful fits and at least 80%
success. The two concentration analyses include different tanks; their
difference cannot be interpreted purely as a unit conversion or calibration
correction.

Dose-level Wilson intervals are also exported as a descriptive
independent-fish sensitivity. They do not correct shared-tank dependence.
Tank bootstrap intervals and these Wilson intervals must not be conflated.

### 5.6 Orthogonal endpoint triangulation

Compare pure, unozonated quinone CSE responses with separate 24-hour coho
mortality observations for the three products present in both datasets.

~~~text
Cell effect call: an observed dose mean relative RFU is <= 1 - threshold
Fish effect call: an observed dose mortality fraction is >= threshold
Thresholds examined: 0.10, 0.20, 0.30
~~~

Calls inspect observed means somewhere within each assay's tested range.
They are descriptive threshold crossings, not significance tests.
Cell and fish dose ranges differ; the biological endpoints also differ.
Agreement is reported by chemical and threshold, not as a predictive accuracy
score.

Published cell EC20 estimates are contextual columns. Extrapolated estimates
cannot create an observed positive call. Negative-negative agreement means
neither threshold was reached in the included tested ranges; it does not
prove either compound is safe.

### 5.7 Ozonation and decision priorities

The ozone analysis compares matched chemical/cell/dose combinations between
t0 and t25. Plate means are averaged within dates and then dates receive
equal weight. The output is t25 minus t0 relative RFU, with date counts.
Ozone treatment and batch are confounded, so these contrasts are descriptive.
Mixture doses refer to starting parent mass, not measured product concentration.

Candidate readiness depends on evidence coverage and identity.
A separate warning reports deaths in a matched product dataset.
ML predictions do not enter the candidate tiers or produce a safety ranking.

## 6. Verified result tables

The tables below summarize the committed version-0.2 result files. Values are
rounded for reporting; the linked CSVs contain full precision. Recompute these
summaries if the data or analysis snapshot changes.

### 6.1 Candidate evidence coverage

| Measure | Count | Interpretation |
|---|---:|---|
| Official alternatives in registry | 21 | Excludes the additional 6PPD benchmark row |
| Matched product whole-fish evidence | 2/21 | IPPD and CCPD parents map to IPPDQ and CCPDQ |
| Matched product cell evidence | 4/21 | 7PPD, IPPD, 77PD, and CCPD |
| No matched parent/product toxicity evidence | 17/21 | In this repository's included cell/fish sources |
| Unresolved/non-discrete molecular identity | 7/21 | Includes mixtures/materials and candidates lacking disclosed CASRN |

These categories overlap; they are not additive partitions.

| Candidate | Matched product | Current readiness | Reporting implication |
|---|---|---|---|
| IPPD | IPPDQ | Ready for comparative testing | Product mortality is a hazard warning, not a favorable safety finding |
| CCPD | CCPDQ | Ready for comparative testing | No observed deaths in included ranges do not establish safety |
| 7PPD | 7PPDQ | Organism-test evidence gap | Product cell results are insufficient for a fish-safety conclusion |
| 77PD | 77PDQ | Organism-test evidence gap | Product cell results are insufficient for a fish-safety conclusion |

The seven identity-limited entries are DTPD/DPPD, Prophene, Lignin, TMQ,
SP-120 DLD, SA 6000 and Antiozaid L122. The commercial DTPD/DPPD mixture must
**not** be mapped automatically to measurements of pure DPPD/DPPDQ.
The complete 21-candidate roster and next tests are in
[decision_priorities.csv](results/decision_priorities.csv), with supporting
coverage in [evidence_matrix.csv](results/evidence_matrix.csv).

### 6.2 Cellular prediction

Source: [cell_assay_model_metrics.csv](results/cell_assay_model_metrics.csv).
All rows use the same 1,377 dose means and 94 plate groups.

| Model/procedure | RMSE | MAE | R² | Conditional 95% RMSE interval |
|---|---:|---:|---:|---|
| Constant control | 0.0946 | 0.0539 | -0.0523 | 0.0757–0.1116 |
| Training-fold mean | 0.0924 | 0.0551 | -0.0028 | 0.0749–0.1086 |
| Nested-tuned ridge | 0.0838 | 0.0569 | 0.1752 | 0.0712–0.0959 |
| Nested-tuned Extra Trees | 0.0536 | 0.0401 | 0.6625 | 0.0483–0.0587 |
| Nested selected procedure | 0.0536 | 0.0401 | 0.6625 | 0.0483–0.0587 |

All five outer folds selected Extra Trees with leaf size 3. Therefore the
Extra Trees and selected-procedure rows have identical predictions here;
they are not independent replications.

RMSE reduction relative to the training-fold mean is approximately
**41.98%**. The paired plate-bootstrap interval for the absolute RMSE gain is
**0.02435–0.05223** relative-RFU units.
Ridge improves RMSE but not MAE over training-mean, so avoid claiming every
model improves every metric.

In [chemical holdout](results/cell_assay_chemical_holdout_metrics.csv),
6PPDQ RMSE is **0.2144**, versus **0.2152** for its training-mean comparator.
Several other held-out chemicals also do not improve over their comparator.

In the [dose-order diagnostic](results/cell_assay_permutation_diagnostic.csv),
all 19 shuffled RMSEs exceed the unshuffled fixed-model value of 0.0536;
shuffled RMSEs range from **0.0761 to 0.0812**.
Do not report an invented small p-value, broad chemical prediction accuracy,
or external validation success from this result.

### 6.3 Fish LC50 estimates

Source: [fish_dose_response.csv](results/fish_dose_response.csv).

| IPPDQ analysis | Positive-dose tanks / fish | LC50 (µg/L) | Tank-bootstrap 95% interval (µg/L) | Successful fits |
|---|---:|---:|---|---:|
| Nominal concentration | 36 / 288 | 0.8714 | 0.8096–0.9319 | 300/300 |
| Unqualified measured concentration | 19 / 152 | 0.7850 | 0.7136–0.8493 | 300/300 |

No LC50 is reported for CCPDQ, CPPDQ, DPPDQ, HPPDQ or OPPDQ because the
available analysis does not meet the fitting gate. This is **not** an
infinite LC50, proof of non-toxicity, or a quantitative lower-bound estimate.

The full fish data contain 138 recorded deaths across all six products and
all included doses. This pooled count is a descriptive inventory total,
not a single chemical's mortality probability.

### 6.4 Observed cellular/organism comparison

Source:
[orthogonal_endpoint_validation.csv](results/orthogonal_endpoint_validation.csv).

| Product | Maximum cell dose (µg/L) | Lowest observed mean CSE relative RFU | Maximum nominal fish dose (µg/L) | Highest observed dose-level mortality | Agreement at 10% / 20% / 30% |
|---|---:|---:|---:|---:|---|
| CCPDQ | 1,000 | 0.9907 | 50 | 0 | Yes / Yes / Yes |
| DPPDQ | 1,000 | 0.9296 | 10 | 0 | Yes / Yes / Yes |
| IPPDQ | 400 | 0.8996 | 2 | 0.9167 | Yes / No / No |

IPPDQ's approximately 10.04% cellular reduction is very close to the 10%
threshold; the 10% agreement should not be presented as robust biological
equivalence. At 20% and 30%, the cell threshold misses the organism response.

The published CSE EC20 estimates are **4.38 µg/L for 6PPDQ**, **408.01 for
IPPDQ**, and **490.73 for 7PPDQ**. Ratios to the 6PPDQ estimate are approximately
93.2 for IPPDQ and 112.0 for 7PPDQ. Both alternative EC20s exceed their tested
cell maximum of 400 µg/L and are fitted estimates, not observed dose-level
threshold crossings. Nor are these ratios estimates of ecological safety.

The earlier development statement of unqualified “3/3 agreement” is superseded
by the observed-only, threshold-specific analysis above.

## 7. Figure and reporting caption

[validation_overview.png](results/validation_overview.png) is generated by the
pipeline and suitable for inclusion in a report with this explanation:

> **Figure 1. Endpoint triangulation and internal assay prediction.** Panel A
> shows mean same-read normalized CSE RFU by nominal dose for IPPDQ, CCPDQ and
> DPPDQ; the dashed line indicates a 20% signal reduction. Panel B shows
> observed 24-hour coho mortality by nominal dose with a 20% mortality
> threshold. Lines join descriptive means; panels A and B have different dose
> ranges and measure different outcomes. Panel C compares grouped OOF RMSEs,
> with conditional 95% intervals from plate-bootstrap resampling of fixed
> OOF errors. The figure does not establish cross-endpoint interchangeability,
> new-chemical generalization, or safety certification.

Model curves and resampled statistics are derived quantities, not newly
collected experimental measurements. Do not describe this figure as a
dose-matched cell/fish experiment or an external validation trial.

## 8. Limitations and conclusions that the data support

A defensible report should explicitly address:

- **Common study origin and sparse chemical diversity:** six fish labels and
  12 cellular labels, with only three pure-product overlaps. There is no
  untouched independent external set.
- **Alternative normalization:** the six-hour reference is missing; same-read
  RFU normalization is documented but does not reconstruct published EC fits.
- **Experimental dependence:** technical wells and fish sharing tanks are
  clustered. Plate groups are inferred, and plate holdout does not eliminate
  all common-batch or common-study dependence.
- **Exposure uncertainty:** concentrations are mostly nominal, measured
  coverage is incomplete, and qualified measurements are excluded from
  measured-dose sensitivity rather than imputed.
- **Endpoint mismatch:** fluorescence/metabolic response is not organism
  survival; thresholds and tested concentration ranges differ.
- **Conditional uncertainty:** OOF error intervals omit refitting and
  between-study variation; fish bootstrap inference has few replicate tanks
  and does not replace a hierarchical multi-study model.
- **Ozone/batch confounding:** matched-dose contrasts cannot isolate an ozone
  causal effect, and parent mass does not reveal product yields.
- **Incomplete identity curation:** a returned PubChem record is not proof
  of correct molecular representation or product composition.
- **No performance/exposure certification:** the repository does not establish
  commercial tire durability, antiozonant efficacy, real-world environmental
  exposure, long-term toxicity, or human health risk.

A supported conclusion is that the framework identifies evidence gaps and
specific assay/organism discrepancies while demonstrating useful internal
assay prediction. A claim that it discovers a proven safer replacement, a
validated fish-toxicity surrogate, or a general molecular safety predictor
would exceed the evidence.

The [rubric review](docs/REPOSITORY_REVIEW.md) is a subjective software/research
assessment, not a scientific outcome, official competition score, or
independent quality endorsement. It should normally be omitted from a paper's
scientific Results section.

## 9. Repository reading order and source map

For a full report, read the following in order:

1. This README for scope and a verified numerical briefing.
2. [VALIDATION_PROTOCOL.md](docs/VALIDATION_PROTOCOL.md) for exact methods and caveats.
3. [MODEL_CARD.md](docs/MODEL_CARD.md) for model intended use and applicability limits.
4. The linked result CSVs for full-precision statistics and denominators.
5. [data-provenance.md](docs/data-provenance.md), [data-dictionary.md](docs/data-dictionary.md),
   and [metadata.xml](data/raw/usgs/metadata.xml) for source and field definitions.
6. Relevant source modules if an implementation detail needs verification.
7. [PAPER_DRAFT.md](docs/PAPER_DRAFT.md) as editable narrative material, not independent evidence.

### Claim-to-file map

| Claim or report component | Primary repository evidence |
|---|---|
| Candidate roster, CASRN, parent/product mapping | [candidate_registry.csv](data/reference/candidate_registry.csv) |
| Coverage and next decisive tests | [evidence_matrix.csv](results/evidence_matrix.csv), [decision_priorities.csv](results/decision_priorities.csv) |
| Original published cellular estimates | [usgs_report_endpoints.csv](data/reference/usgs_report_endpoints.csv), [cell_endpoint_comparison.csv](results/cell_endpoint_comparison.csv) |
| Control matching, source rows and eligibility | [cell_assay_normalized.csv](results/cell_assay_normalized.csv) |
| Model metrics and conditional uncertainty | [cell_assay_model_metrics.csv](results/cell_assay_model_metrics.csv) |
| Held-out dose predictions and domain flags | [cell_assay_model_oof_predictions.csv](results/cell_assay_model_oof_predictions.csv) |
| Outer split memberships and inner selection | [cell_assay_fold_audit.csv](results/cell_assay_fold_audit.csv) |
| Chemical-transfer stress test | [cell_assay_chemical_holdout_metrics.csv](results/cell_assay_chemical_holdout_metrics.csv), [predictions](results/cell_assay_chemical_holdout_predictions.csv) |
| Dose-order negative diagnostic | [cell_assay_permutation_diagnostic.csv](results/cell_assay_permutation_diagnostic.csv) |
| Fish counts, tank dependence, exposure qualifiers | [invivo_tank_summary.csv](results/invivo_tank_summary.csv), [invivo_mortality_summary.csv](results/invivo_mortality_summary.csv) |
| Supported LC50s and fitted curves | [fish_dose_response.csv](results/fish_dose_response.csv), [fish_dose_response_curves.csv](results/fish_dose_response_curves.csv) |
| Observed endpoint agreement by threshold | [orthogonal_endpoint_validation.csv](results/orthogonal_endpoint_validation.csv) |
| Descriptive ozonation contrasts | [ozone_matched_dose_contrasts.csv](results/ozone_matched_dose_contrasts.csv) |
| Scientific source integrity | [data_inventory.csv](results/data_inventory.csv), [sources.json](config/sources.json) |
| Input/code/output fingerprints and environment | [run_manifest.json](results/run_manifest.json) |

### Code map

| Module | Responsibility |
|---|---|
| [io.py](src/sixppd_assessment/io.py) | Source verification and registry loading |
| [assay.py](src/sixppd_assessment/assay.py) | Cell contracts, normalization, technical-well aggregation and ozone contrasts |
| [modeling.py](src/sixppd_assessment/modeling.py) | Nested CV, bootstrap metrics, chemical holdout and permutations |
| [toxicology.py](src/sixppd_assessment/toxicology.py) | Tank summaries, supported LC50 fitting and endpoint triangulation |
| [analysis.py](src/sixppd_assessment/analysis.py) | Evidence matrix, published endpoint comparison, priorities and impact brief |
| [reporting.py](src/sixppd_assessment/reporting.py) | Figure, receipt generation and receipt verification |
| [pipeline.py](src/sixppd_assessment/pipeline.py) | End-to-end orchestration |
| [cli.py](src/sixppd_assessment/cli.py) | Run/verify commands |

**If sources disagree:** distinguish a rounding difference from a different
snapshot or endpoint definition. Check the receipt, original source definition,
executable method and appropriate CSV together. Do not silently choose the
most favorable number. Identify unresolved discrepancies in the report.
Narrative drafts and previous conversational summaries are not the numerical
source of truth.

## 10. Reproducing or verifying the analysis

Run commands from the repository root. All required scientific source files
are included; no download is needed to analyze the committed snapshot.

Use **Python 3.14** with the pinned tested environment. The package declares
Python 3.11+ support; a separate compatibility workflow runs on Python 3.11
with compatible dependency versions. Do not assume every pinned Python-3.14
package version installs on Python 3.11.

~~~bash
python -m venv .venv
# Activate .venv using the command appropriate for your shell.
python -m pip install -r requirements-tested.txt -e ".[dev]"
python -m sixppd_assessment run
python -m sixppd_assessment verify
python -m pytest
ruff check .
ruff format --check src tests
~~~

For report-only reading, the committed CSVs and figure can be used without
retraining. The verify command checks the saved input/code/output fingerprints;
it does not independently validate the scientific claims or certify identical
results under every environment.

The run command rewrites derived files in results/ and creates a new receipt.
Copy or preserve an existing result snapshot before comparing runs.
The default has 19 dose-order permutations. Use:

~~~bash
python -m sixppd_assessment run --permutations 99
~~~

for a finer exploratory diagnostic, or --permutations 0 for a development run
that skips that diagnostic. Report the actual number from the relevant
receipt; a changed run is not the same snapshot as the tables above.

The [download script](scripts/download_public_data.py) can deliberately
refresh public source assets and PubChem queries. Refreshing identities can
change the snapshot and is not required for report generation.

The verified release has 25 passing tests and passing Python 3.11 and pinned
Python 3.14 GitHub workflows. This is a release verification record, not a
guarantee about future commits. The tests cover scientific input contracts,
group separation, baseline construction, extrapolation handling, tank
accounting, LC50 support gates, ozone matching and receipt integrity.
CI uploads generated results as an artifact.

## 11. Next evidence milestones

The next substantial scientific gains require:

1. Independently curated fish endpoints with verified identities, molar units,
   exposure durations, censoring and study identifiers.
2. Untouched external study/chemical evaluation reserved before additional
   descriptor and model choices.
3. Structure-based models evaluated using chemical/scaffold grouping after
   adequate endpoint and chemical coverage.
4. Transformation-yield, environmental exposure and actual tire-performance
   evidence to connect hazard findings to feasible substitutions.

The [modeling plan](docs/modeling-plan.md) specifies project entry gates of
100 discrete chemicals and 20 transformation products. These are screening
requirements, not universal regulatory thresholds or a statistical power
guarantee. More algorithms cannot resolve absent biological evidence.

## 12. Glossary

| Term | Meaning in this repository |
|---|---|
| 6PPD / 6PPDQ | Parent antiozonant / its quinone transformation product |
| RFU | Relative fluorescence units measured in a cell assay |
| Relative RFU | Well signal divided by its matched zero-dose mean |
| EC20 | Published modeled concentration associated with a 20% cellular effect under the source method |
| LC50 | Modeled concentration associated with 50% mortality over the specified fish exposure |
| OOF | Out-of-fold: predicted only when the observation's group is held out |
| Nested CV | Training-fold model selection inside a separate outer evaluation loop |
| Orthogonal endpoints | Different biological measurements, here cell signal and whole-fish mortality |
| QSAR | Quantitative structure–activity relationship; broad molecular QSAR is not implemented here |
| LOD / E | Limit-of-detection qualifier / laboratory estimated-concentration flag |
| Evidence readiness | Availability and identity criteria for deciding the next test, not a safety score |

## 13. References and citation

1. Greer JB, Dalsky EM, Bachand PT, Hansen JD. 2026.
   *Toxicity of 6PPD alternatives to salmonids*. USGS data release.
   [DOI 10.5066/P1DHCMMZ](https://doi.org/10.5066/P1DHCMMZ).
2. Greer JB, Dalsky EM, Bachand PT, Hansen JD. 2026.
   *Toxicity of 6PPD alternatives to salmonid cell lines*. Washington Department
   of Ecology, 13 pp. [USGS publication record](https://pubs.usgs.gov/publication/70273838).
3. California DTSC. *Motor Vehicle Tires Containing 6PPD*.
   [Source page](https://dtsc.ca.gov/scp/motor_vehicle_tires_containing_6ppd/);
   repository registry snapshot retrieved 2026-07-27.
4. PubChem. [PUG REST documentation](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest).
   Identity responses are preserved in the repository snapshot.
5. Scikit-learn developers.
   [Nested versus non-nested cross-validation](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html).

Cite the software separately using [CITATION.cff](CITATION.cff).
The [paper draft](docs/PAPER_DRAFT.md) is an unpublished computational
reanalysis and acknowledges AI assistance; author review of scientific
interpretation and references remains necessary before submission.
