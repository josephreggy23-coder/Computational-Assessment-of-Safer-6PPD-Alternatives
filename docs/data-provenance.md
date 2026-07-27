# Data provenance

## USGS 2026 release

Citation:

> Greer, J.B., Dalsky, E.M., Bachand, P., and Hansen, J.D., 2026,
> Toxicity of 6PPD alternatives to salmonids: U.S. Geological Survey data
> release, <https://doi.org/10.5066/P1DHCMMZ>.

License: CC0-1.0 public-domain dedication.

| File | Records | Published MD5 |
|---|---:|---|
| `invivo_data.csv` | 1,006 | `bcffc127f53bffb32cb91f83b203c152` |
| `invitro_data.csv` | 6,244 | `d25a1bef7229d2a18ac5af33ab7ffb21` |

The repository download script verifies these hashes before analysis.
The accompanying `metadata.xml` is also preserved and verified against its
published MD5, `3782097fca192ee32f24fbc806c75013`.

The metadata defines both nominal and measured in-vivo concentrations as
micrograms per liter and states that mortality was monitored for 24 hours.

## USGS/Washington report

The report table in `data/reference/usgs_report_endpoints.csv` was transcribed
from Table 2 and visually checked against the rendered PDF. It contains only
published values; it is not synthetic data.

Report:
<https://www.ezview.wa.gov/Portals/_1962/Documents/6ppd/WDOE%20USGS%20Alts%20Final%20Report%20submitted.pdf>

Repository SHA-256:
`102f032f3722f8c06f1cf91cce319f69d2c7128c29d7d936de62d51d11acb933`

## California DTSC list

`data/reference/candidate_registry.csv` transcribes the 21 alternatives named
on the California Department of Toxic Substances Control page as selected for
detailed evaluation, plus 6PPD as the benchmark.

Source:
<https://dtsc.ca.gov/scp/motor_vehicle_tires_containing_6ppd/>

Products without a disclosed CASRN, polymers, mixtures, and materials are
explicitly labeled. They are not converted into invented discrete structures.

## PubChem

The download script queries PubChem by CASRN and stores returned identity and
structure fields. A missing PubChem match remains missing.

No PubChem record is treated as proof of tire performance or safety.
