# Research plan

Version 0.2 status: evidence mapping, retrospective cell modeling, tank-level
dose response and orthogonal endpoint triangulation are implemented. The
[validation protocol](VALIDATION_PROTOCOL.md) records their exact scope.
Environmental fate, quantum descriptors and independent external validation
remain planned. The mechanistic hypothesis below is not established by these
data; neither electrophilicity nor transformation yield has been measured here.

## Question

Which publicly identified 6PPD alternatives should receive priority for
experimental testing, and which have evidence consistent with a regrettable
substitution risk?

## Hypothesis

The hazard of a tire antiozonant cannot be estimated from the parent compound
alone. Candidates whose ozonated transformation products retain a quinone-like
electrophilic structure will produce stronger adverse responses in sensitive
salmonids than candidates without that transformation pathway.

## Scientific contribution

The project links four layers:

1. candidate identity and chemical class;
2. measured parent-compound response;
3. measured transformation-product response; and
4. environmental fate and molecular descriptors.

The original contribution is an evidence-gated testing-priority framework,
followed by a small interpretable model only where comparable public endpoints
support it.

## Phase 1: measured evidence

- Reproduce the USGS in-vivo mortality summaries.
- Reproduce the report's cell-line endpoint table from raw data where possible.
- Keep species, cell line, exposure duration, endpoint, and parent/product
  identity explicit.
- Identify candidates absent from the measured datasets.

## Phase 2: chemical identity

- Resolve discrete candidates through PubChem using CASRN.
- Do not force polymers, mixtures, materials, or proprietary products into a
  single-molecule representation.
- Record unresolved identity as an evidence gap.

## Phase 3: environmental evidence

- Retrieve measured ECOTOX fish endpoints under a prespecified protocol.
- Retrieve measured CompTox physicochemical values separately from predictions.
- Preserve qualifiers, exposure durations, species, units, and citations.

## Phase 4: restrained modeling

- Use one regularized and interpretable model.
- Train only on harmonized, measured organism-level endpoints.
- Reserve new, independently sourced studies for external evaluation before
  further feature selection. The inspected 2026 USGS release can no longer
  serve as an untouched external test set.
- Report coefficients, grouped cross-validation, bootstrap intervals,
  applicability domain, and a median-only baseline.

## Phase 5: focused quantum chemistry

Calculate a small mechanistic descriptor set for 6PPD and no more than six
well-defined finalists:

- frontier orbital energies;
- vertical ionization energy;
- global electrophilicity;
- parent-to-quinone reaction free energy.

Quantum calculations guide chemical interpretation; they do not replace
measured toxicity.

## Decision tiers

- **Ready for comparative testing:** parent identity and transformation-product
  evidence are available, with organism or validated cell-line response.
- **Priority evidence gap:** plausible high-impact candidate missing one
  decisive experiment.
- **Potential regrettable substitution:** measured warning signal or hazardous
  identity/fate evidence warrants caution.
- **Not assessable:** identity or evidence is too incomplete for a conclusion.

These are evidence-readiness tiers, not declarations of safety.
