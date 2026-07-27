"""Measured-evidence summaries and decision-readiness analysis."""

from __future__ import annotations

import pandas as pd


def summarize_invivo_mortality(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize observed mortality without fitting or imputing a model."""
    fish = frame.loc[frame["fish_id"].notna()].copy()
    fish["mortality"] = pd.to_numeric(fish["mortality"], errors="raise")
    fish["nominal_conc"] = pd.to_numeric(fish["nominal_conc"], errors="raise")

    summary = (
        fish.groupby(
            ["species", "exposure_chemical", "nominal_conc"], dropna=False
        )
        .agg(
            fish_n=("fish_id", "count"),
            deaths=("mortality", "sum"),
            observed_mortality=("mortality", "mean"),
        )
        .reset_index()
        .sort_values(["species", "exposure_chemical", "nominal_conc"])
    )
    return summary


def build_evidence_matrix(
    candidates: pd.DataFrame,
    invivo: pd.DataFrame,
    invitro: pd.DataFrame,
    pubchem: pd.DataFrame | None,
) -> pd.DataFrame:
    """Map actual evidence coverage; no safety score is calculated."""
    matrix = candidates.copy()
    invivo_labels = set(invivo["exposure_chemical"].dropna().astype(str))
    invitro_labels = set(invitro["antiozonant"].dropna().astype(str))

    matrix["has_parent_cell_data"] = matrix["usgs_parent_label"].map(
        lambda value: pd.notna(value) and str(value) in invitro_labels
    )
    matrix["has_product_cell_data"] = matrix["usgs_product_label"].map(
        lambda value: pd.notna(value) and str(value) in invitro_labels
    )
    matrix["has_product_invivo_data"] = matrix["usgs_product_label"].map(
        lambda value: pd.notna(value) and str(value) in invivo_labels
    )
    matrix["has_discrete_identity"] = (
        matrix["casrn"].notna()
        & ~matrix["candidate_class"].isin(
            {
                "PPD_mixture",
                "carbon_material",
                "biopolymer",
                "quinoline_polymer",
                "phenol_mixture",
                "proprietary",
            }
        )
    )

    if pubchem is None or pubchem.empty:
        matrix["has_pubchem_structure"] = False
    else:
        resolved = set(pubchem.loc[pubchem["resolved"], "casrn"].astype(str))
        matrix["has_pubchem_structure"] = (
            matrix["casrn"].astype(str).isin(resolved)
            & matrix["has_discrete_identity"]
        )

    evidence_columns = [
        "has_parent_cell_data",
        "has_product_cell_data",
        "has_product_invivo_data",
        "has_pubchem_structure",
    ]
    matrix["evidence_domains_n"] = matrix[evidence_columns].sum(axis=1)

    def readiness(row: pd.Series) -> str:
        if not row["has_discrete_identity"]:
            return "Not assessable: identity"
        if row["has_product_invivo_data"]:
            return "Ready for comparative testing"
        if row["has_product_cell_data"]:
            return "Priority evidence gap: organism test"
        if row["has_parent_cell_data"]:
            return "Priority evidence gap: transformation product"
        return "Priority evidence gap: toxicity"

    matrix["evidence_readiness"] = matrix.apply(readiness, axis=1)
    return matrix


def compare_published_cell_endpoints(endpoints: pd.DataFrame) -> pd.DataFrame:
    """Compare published effects with 6PPDQ within the same endpoint and cell line."""
    required = {
        "cell_type",
        "chemical",
        "endpoint",
        "effect_concentration_ug_l",
        "source_url",
    }
    missing = required - set(endpoints.columns)
    if missing:
        raise ValueError(f"Endpoint table missing columns: {sorted(missing)}")

    benchmark = (
        endpoints.loc[endpoints["chemical"].eq("6PPDQ")]
        .set_index(["cell_type", "endpoint"])["effect_concentration_ug_l"]
        .rename("benchmark_6ppdq_ug_l")
    )
    comparison = endpoints.merge(
        benchmark,
        left_on=["cell_type", "endpoint"],
        right_index=True,
        how="left",
        validate="many_to_one",
    )
    comparison["concentration_ratio_vs_6ppdq"] = (
        comparison["effect_concentration_ug_l"]
        / comparison["benchmark_6ppdq_ug_l"]
    )
    comparison["interpretation"] = comparison.apply(
        lambda row: (
            "6PPDQ benchmark"
            if row["chemical"] == "6PPDQ"
            else (
                f"{row['concentration_ratio_vs_6ppdq']:.1f}x higher "
                f"concentration than 6PPDQ for the same {row['endpoint']} effect"
            )
        ),
        axis=1,
    )
    return comparison


def build_decision_priorities(matrix: pd.DataFrame) -> pd.DataFrame:
    """Name the next decision-changing test without assigning a safety score."""

    def next_test(row: pd.Series) -> str:
        if not row["has_discrete_identity"]:
            return "Resolve composition and identity before molecular modeling"
        if row["has_product_invivo_data"]:
            return (
                "Identify and test the complete ozonated mixture against the "
                "purified product"
            )
        if row["has_product_cell_data"]:
            return (
                "Run a concentration-confirmed whole-fish salmonid test of the "
                "transformation product"
            )
        if row["has_parent_cell_data"]:
            return "Identify, quantify, and test ozonation products"
        return (
            "Establish comparable parent performance and transformation-product "
            "toxicity evidence"
        )

    priorities = matrix.copy()
    priorities["next_decisive_test"] = priorities.apply(next_test, axis=1)
    columns = [
        "candidate_id",
        "short_name",
        "candidate_class",
        "role",
        "evidence_readiness",
        "next_decisive_test",
        "has_discrete_identity",
        "has_pubchem_structure",
        "has_parent_cell_data",
        "has_product_cell_data",
        "has_product_invivo_data",
        "source_url",
    ]
    return priorities[columns]


def build_impact_brief(
    inventory: pd.DataFrame,
    matrix: pd.DataFrame,
    mortality: pd.DataFrame,
    endpoint_comparison: pd.DataFrame,
) -> str:
    official = matrix.loc[matrix["role"].eq("official_candidate")]
    organism_covered = int(official["has_product_invivo_data"].sum())
    product_cell_covered = int(official["has_product_cell_data"].sum())
    unresolved_identity = int((~official["has_discrete_identity"]).sum())
    no_toxicity = int(
        (
            ~official[
                [
                    "has_parent_cell_data",
                    "has_product_cell_data",
                    "has_product_invivo_data",
                ]
            ].any(axis=1)
        ).sum()
    )
    exposed_chemicals = mortality["exposure_chemical"].nunique()
    deaths = int(mortality["deaths"].sum())
    fish_n = int(mortality["fish_n"].sum())
    ec20 = endpoint_comparison.loc[
        endpoint_comparison["endpoint"].eq("EC20")
        & ~endpoint_comparison["chemical"].eq("6PPDQ")
    ].sort_values("concentration_ratio_vs_6ppdq")
    ec20_finding = "; ".join(
        (
            f"{row.chemical} required {row.concentration_ratio_vs_6ppdq:.1f}x "
            "the 6PPDQ concentration"
        )
        for row in ec20.itertuples()
    )

    lines = [
        "# Impact brief",
        "",
        "## Decision headline",
        "",
        (
            f"Only **{organism_covered} of 21** official alternatives currently map "
            "to an explicitly matched transformation-product organism dataset in "
            "this first framework release."
        ),
        "",
        (
            f"**{product_cell_covered} of 21** have matched transformation-product "
            "cell-line evidence, while "
            f"**{no_toxicity} of 21** have no matched toxicity evidence in the "
            "included USGS cell or organism files."
        ),
        "",
        (
            f"**{unresolved_identity} of 21** are mixtures, polymers, materials, or "
            "proprietary products that cannot be responsibly represented as one "
            "molecular structure."
        ),
        "",
        "## Measured evidence analyzed",
        "",
        (
            f"The in-vivo file contains observations covering **{exposed_chemicals} "
            f"chemical labels**, **{fish_n} fish records**, and **{deaths} recorded "
            "deaths** across the tested concentrations."
        ),
        "",
        "The cell-line and whole-fish evidence are kept separate because they are "
        "not interchangeable endpoints.",
        "",
        "## Measured benchmark comparison",
        "",
        (
            "In published coho CSE-119 cell results at EC20, "
            f"{ec20_finding}. This indicates lower potency in that assay, not proof "
            "of ecological safety."
        ),
        "",
        "## Highest-impact next experiment",
        "",
        "For each candidate with a defined identity, identify its actual ozonation "
        "products and test the complete product mixture in a sensitive salmonid "
        "system. Parent-only testing is insufficient: the USGS report found that "
        "ozonated mixtures could be more biologically active than purified quinones.",
        "",
        "## Interpretation boundary",
        "",
        "These results rank evidence needs, not chemical safety. A candidate with "
        "little data remains unranked; it is not treated as low risk.",
        "",
        "## Integrity",
        "",
        (
            f"All {int(inventory['checksum_valid'].sum())} included USGS files "
            "passed their published MD5 checksums. No synthetic observations or "
            "generated molecules were used."
        ),
        "",
    ]
    return "\n".join(lines)
