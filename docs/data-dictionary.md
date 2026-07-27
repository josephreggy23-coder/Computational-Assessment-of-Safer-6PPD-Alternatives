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
| `nominal_conc` | Nominal exposure concentration as supplied by USGS |
| `time_of_death` | Recorded death time where applicable |
| `mass_g` | Fish mass in grams |
| `length_cm` | Fish length in centimeters |
| `mortality` | Observed binary mortality field |
| `initial_or_final` | Sampling-time qualifier |
| `fish_nofish` | Analytical sample qualifier |
| `measured_conc` | Measured concentration field |
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

RFU is not treated as toxicity without the control normalization and
quality-control procedure defined by the source study.

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

