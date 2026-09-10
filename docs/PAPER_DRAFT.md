# TREADSENTINEL
## Cross-Endpoint Toxicity Assessment and Evidence-Gated Screening of 6PPD Alternatives

Joseph Reggy · Unpublished working manuscript · Version 0.2 · September 2026

This draft describes a retrospective analysis of public measurements. All
experimental data and published endpoint estimates are attributed to their
original authors. The software, reanalysis and decision framework are the
contributions of this project. Author review and independent validation remain
necessary before submission.

## Abstract

Replacing the tire antiozonant 6PPD requires simultaneous consideration of
chemical performance, transformation products and environmental hazards.
We developed TREADSENTINEL, a reproducible evidence-prioritization framework
linking a 21-candidate registry to 1,006 whole-coho observations and 6,244
salmonid cellular measurements from a public USGS release. The workflow
verifies source integrity, preserves incomplete identities, separates ozone
conditions, and evaluates orthogonal biological endpoints without substituting
predicted effects for observations. A nested grouped comparison of ridge and
Extra Trees modeled 1,377 normalized cellular dose means across 94 conservative
plate groups. The selected model achieved RMSE 0.0536 (conditional plate-bootstrap
95% interval 0.0483–0.0587), compared with 0.0924 for a training-mean baseline.
Chemical holdout exposed substantial transfer limitations. At a 20% response
threshold, observed cell/fish calls agreed for two of three overlapping products;
IPPDQ was discordant, with fish mortality despite an absent observed cellular
threshold crossing. Its nominal 24-hour LC50 was 0.871 µg/L (tank-bootstrap
interval 0.810–0.932), while the unqualified measured-dose subset yielded
0.785 µg/L (0.714–0.849). Seventeen registry alternatives lacked matched toxicity
evidence in the included files. TREADSENTINEL supports transparent selection of
follow-up tests while showing why internal assay prediction, extrapolated
cellular endpoints and incomplete coverage cannot establish replacement safety.

## 1. Introduction

The environmental concern motivating substitution is the toxicity of the
6PPD transformation product 6PPD-quinone. Public research has therefore begun
evaluating both proposed parent antiozonants and their ozonated products [1,2].
A practical computational question is which alternatives have sufficient
evidence for comparative testing and which require additional identity,
transformation or organism-level measurements.

This work addresses that question through three linked analyses: an explicit
evidence-coverage registry; an observed-only comparison of cellular and
whole-organism effects; and an internally validated model of cellular assay
responses. A key design requirement is that favorable predictions cannot
replace missing measurements or certify an alternative as safe.

## 2. Methods

### Data and provenance

The public USGS release supplies coho mortality observations and cellular
fluorescence from coho CSE, Chinook CHSE and rainbow trout RTG cell lines [1].
A July 2026 registry snapshot transcribes 21 DTSC alternatives plus 6PPD [3].
CASRN-based PubChem records supply identity fields, with explicit exclusion of
mixtures, polymers and undisclosed compositions from single-structure claims.
Published cellular EC5/10/20 values are retained separately from raw observations [2].

Two source CSVs and metadata XML are checked against published MD5 hashes.
The archived report is checked against a repository-recorded SHA-256. A
machine-readable receipt fingerprints every analysis input, source module and
generated output. No synthetic observational or training data are introduced.

### Cellular analysis

Control means match chemical, cell line, plate, read timestamp and ozone
condition. The released file does not contain the six-hour reference described
in the metadata; the present analysis uses same-read solvent normalization.
Relative RFU therefore measures a specific assay signal and is not assumed to
be a calibrated cell-survival fraction. Eighty observations outside 22–26 hours
remain in the normalized export but are excluded from 24-hour comparisons.

Technical wells are averaged within each read and dose. Model evaluation
uses positive doses only, since zero-dose controls define the normalization.
Date plus plate forms the conservative group so shared plates across cell
lines or chemicals cannot enter opposing train and test partitions.

### Model comparison

Inputs are log nominal concentration, exposure hours, chemical identity, cell
line and ozone condition. Five outer grouped folds evaluate a three-fold inner
selection among ridge regularization strengths and Extra Trees leaf sizes.
Preprocessing fits within each training partition. Nested selection limits
the optimistic bias arising from choosing models on their test scores [4].
Constant-control and training-mean baselines use the same held-out observations.

We report RMSE, MAE, R², signed residual and complete fold membership. Paired
bootstrap resampling of 94 plate groups, using 1,000 draws of fixed OOF errors,
provides conditional error intervals. Chemical holdout removes the held-out
identity and any shared test plates from training. Nineteen within-read
dose permutations probe dependence on dose ordering using a fixed ensemble.
These are retrospective diagnostics, not independent study replication.

### Organism response and orthogonal triangulation

Fish are summarized within tanks before fitting an increasing logistic
concentration–mortality relation. LC50 estimates require observed dose-level
mortality to bracket 50%, at least four nominal levels and a successful fit
inside the tested range. Three hundred bootstrap resamples retain whole tanks
within nominal dose/exposure-run strata. Separate nominal and unqualified
measured-dose analyses preserve missingness and detection/estimation qualifiers.

For pure quinones with both CSE and coho measurements, observed means are
compared at exploratory 10%, 20% and 30% effect thresholds. Published EC20s
are contextual estimates; those beyond measured doses cannot create positive
observed-effect calls. The comparison spans distinct biological endpoints
and dose ranges within one source study. All choices are retrospective.
The full protocol is [documented separately](VALIDATION_PROTOCOL.md).

## 3. Results

### Evidence coverage

Two of 21 registry alternatives have explicitly matched product whole-fish
records and four have matched product cellular evidence. Seventeen have no
matched toxicity evidence in the included files. Seven have unresolved or
non-discrete identity for the purposes of molecular representation. These
counts describe repository coverage, not all available literature.

### Assay model performance and transfer limits

All five outer folds select Extra Trees through the inner evaluations. Nested
OOF RMSE is 0.0536 versus 0.0924 for training-mean and 0.0838 for ridge; R² is
0.662. The conditional plate-bootstrap interval for selected-model RMSE is
0.0483–0.0587. The improvement over training-mean is approximately 42%.
Technical-well aggregation and corrected controls change the target relative
to the earlier well-level implementation; errors should not be compared across
those implementations as a model-only improvement.

Holding out 6PPDQ yields RMSE approximately 0.214, versus 0.215 for the
training-mean comparator. Several other held-out chemicals also fail to improve
over their comparator. Good replicate-plate prediction therefore does not
establish transfer to untested alternatives. All 19 dose-order permutations
give higher RMSE than the fixed ensemble's unshuffled evaluation, supporting
a contribution of dose pattern while retaining the limits of a coarse diagnostic.

### Cross-endpoint discrepancy and fish dose response

At the 20% threshold, CCPDQ and DPPDQ do not cross either endpoint's threshold
within the included tested ranges. IPPDQ produces substantial coho mortality
but no observed 20% reduction in mean CSE RFU. Its published EC20 of 408.01 µg/L
is beyond the maximum tested CSE dose of 400 µg/L. Consequently observed
agreement is two of three at 20% and 30%, changing to three of three at 10%.
The latter call is close to its threshold and should not be treated as strong
evidence of assay equivalence.

IPPDQ nominal LC50 is 0.871 µg/L (0.810–0.932); the measured, unqualified
subset gives 0.785 µg/L (0.714–0.849), with 300 successful tank-bootstrap fits
for each. The subsets differ in included tanks, so the difference is not solely
a concentration-scale effect. Other products do not meet the LC50 fitting gate.

![Observed endpoint contrast and grouped model performance](../results/validation_overview.png)

**Figure 1.** A: CSE same-read normalized RFU, with 20% signal-reduction
threshold. B: coho mortality by nominal dose, with 20% mortality threshold.
Lines connect descriptive means and do not imply shared potency across assays.
C: OOF model RMSE; bars show conditional 95% plate-bootstrap intervals.
The axes in A and B span different concentration ranges. No new experimental
measurements are represented by model curves or bootstrap resamples.

## 4. Discussion

The principal result is the separation of three questions often conflated in
computational substitution studies: whether evidence exists, whether an assay
response is predictable, and whether a replacement is safe in realistic use.
TREADSENTINEL improves the first two while exposing limits on the third.
IPPDQ illustrates why an apparently weak cellular response at a chosen threshold
cannot negate whole-organism toxicity. Descriptive agreement across three
products cannot establish a validated surrogate, sensitivity or specificity.

The reanalysis is limited by common study provenance, few chemical identities,
nominal exposure, inferred plate grouping, a missing six-hour cellular reference,
and small replicate counts. Fish likelihood fitting assumes conditional binomial
responses; tank resampling captures some clustering but does not replace a
hierarchical study model or independent replication. Ozonation contrasts are
exported descriptively with date-balanced means, because batch and ozone
treatment are confounded. Tire performance, actual transformation yields and
environmental exposure are not measured by this repository.

Further work should independently curate comparable fish endpoints, reserve
untouched studies and chemicals, and assess structure-based models only after
adequate chemical diversity and endpoint harmonization. Chemical performance
and environmental exposure evidence must then accompany hazard estimates.

## Data, code and disclosure

Code and generated results are in the repository. Raw USGS data retain their
CC0 attribution; software is MIT licensed. Machine learning and bootstrap
outputs are labeled derived results. The analysis and manuscript were developed
with AI assistance; the listed author should verify code, citations, scientific
interpretation and journal disclosure requirements before submission.

## References

1. Greer JB, Dalsky EM, Bachand PT, Hansen JD. 2026. Toxicity of 6PPD alternatives
   to salmonids. USGS data release. [DOI 10.5066/P1DHCMMZ](https://doi.org/10.5066/P1DHCMMZ).
2. Greer JB, Dalsky EM, Bachand PT, Hansen JD. 2026. Toxicity of 6PPD alternatives
   to salmonid cell lines. Washington Department of Ecology, 13 pp.
   [USGS publication record](https://pubs.usgs.gov/publication/70273838).
3. California DTSC. Motor Vehicle Tires Containing 6PPD. Candidate registry
   snapshot retrieved 2026-07-27. [Source](https://dtsc.ca.gov/scp/motor_vehicle_tires_containing_6ppd/).
4. Scikit-learn developers. Nested versus non-nested cross-validation.
   [Documentation](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html).
