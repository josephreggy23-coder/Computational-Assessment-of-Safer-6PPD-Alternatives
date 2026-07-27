# Computational Assessment of Safer 6PPD Alternatives

A fully computational, public-data-only chemistry project for identifying
which proposed tire antiozonants should be tested first and which may create a
regrettable substitution.

## The impact question

6PPD protects tire rubber from ozone, but its transformation product
6PPD-quinone is acutely toxic to coho salmon. Replacing 6PPD without examining
the replacement's transformation products could exchange one environmental
hazard for another.

This project asks:

> Which publicly identified 6PPD alternatives have enough evidence to justify
> priority testing, which show warning signals, and which cannot yet be judged?

The intended users are environmental researchers, regulators, watershed
managers, and material scientists deciding where limited testing resources
should go next.

## Design principles

- **Zero synthetic data.** No generated molecules, invented measurements,
  simulated observations, or synthetic training rows.
- **Measured evidence first.** Direct USGS organism and cell-line measurements
  are reported before any model output.
- **Transformation products matter.** Parent chemicals are never treated as
  adequate proxies for their ozonated products.
- **No false precision.** Missing evidence stays missing. It is not silently
  imputed into a safety claim.
- **Decision usefulness.** Outputs emphasize testing priority, evidence gaps,
  and uncertainty rather than leaderboard accuracy.
- **Full provenance.** Every source has a URL, retrieval date, license, and
  integrity check when one is published.

## Public evidence currently included

1. **USGS 2026 toxicity release**
   - 1,006 in-vivo coho salmon records
   - 6,244 salmonid cell-line records
   - CC0 public-domain dedication
   - DOI: <https://doi.org/10.5066/P1DHCMMZ>
2. **California DTSC candidate list**
   - 21 alternatives selected for detailed evaluation by manufacturers
   - Source: <https://dtsc.ca.gov/scp/motor_vehicle_tires_containing_6ppd/>
3. **PubChem**
   - Public chemical identity and structure records retrieved by CASRN
   - API documentation: <https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest>

EPA ECOTOX and CompTox are defined as expansion sources, but their values are
not included in a result unless downloaded, filtered, and provenance-checked.

## What the first release does

The current pipeline:

1. verifies the official USGS files against their published MD5 hashes;
2. validates the real candidate registry;
3. summarizes measured in-vivo mortality by chemical and concentration;
4. maps which official candidates have parent, transformation-product,
   organism, cell-line, and structure evidence;
5. compares published alternative-quinone cell effects with the 6PPDQ benchmark;
6. assigns an **evidence-readiness tier**, not a safety score;
7. names the next decision-changing test for every candidate;
8. writes an impact brief showing the most consequential evidence gaps.

The pipeline does **not** yet fit a toxicity model. Modeling begins only after
the endpoint harmonization and sample-size gates in
[`docs/modeling-plan.md`](docs/modeling-plan.md) are satisfied.

## Run

Python 3.11 or newer is recommended.

```bash
python -m pip install -e ".[dev]"
python scripts/download_public_data.py
python -m sixppd_assessment run
pytest
```

The analysis writes:

- `results/data_inventory.csv`
- `results/invivo_mortality_summary.csv`
- `results/evidence_matrix.csv`
- `results/cell_endpoint_comparison.csv`
- `results/decision_priorities.csv`
- `results/impact_brief.md`

## Repository map

```text
.
├── config/sources.json
├── data/
│   ├── raw/usgs/
│   └── reference/
├── docs/
├── results/
├── scripts/
├── src/sixppd_assessment/
└── tests/
```

## Interpretation boundary

This project prioritizes candidates for further testing. It does not certify a
chemical as safe or prove that it will perform in a commercial tire.
