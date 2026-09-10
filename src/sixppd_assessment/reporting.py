"""Export a compact scientific figure and an auditable run receipt."""

import hashlib
import importlib.metadata
import json
import platform
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .assay import aggregate_cell_doses


def write_figure(path, assay, mortality, metrics):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), constrained_layout=True)
    colors = {"IPPDQ": "#b23c45", "CCPDQ": "#226e91", "DPPDQ": "#788047"}
    doses = aggregate_cell_doses(assay)
    for chem, color in colors.items():
        cell = doses.loc[
            doses.antiozonant.eq(chem)
            & doses.cell_type.eq("CSE")
            & doses.in_24h_window
            & doses.concentration.gt(0)
        ]
        mean = cell.groupby("concentration").relative_rfu.mean()
        axes[0].plot(mean.index, mean, "o-", color=color, label=chem, markersize=4)
        fish = mortality.loc[
            mortality.exposure_chemical.eq(chem) & mortality.nominal_conc.gt(0)
        ]
        axes[1].plot(
            fish.nominal_conc,
            fish.observed_mortality,
            "o-",
            color=color,
            label=chem,
            markersize=4,
        )
    axes[0].axhline(0.8, color="#555555", ls="--", lw=1)
    axes[0].set(
        title="A  CSE cell response",
        xlabel="Nominal concentration (µg/L)",
        ylabel="Same-read normalized RFU",
        xscale="log",
        ylim=(0.5, 1.2),
    )
    axes[0].legend(frameon=False)
    axes[1].axhline(0.2, color="#555555", ls="--", lw=1)
    axes[1].set(
        title="B  Coho mortality at 24 hours",
        xlabel="Nominal concentration (µg/L)",
        ylabel="Observed mortality fraction",
        xscale="log",
        ylim=(-0.03, 1),
    )
    names = ["Control", "Train mean", "Ridge", "Extra Trees", "Nested selected"]
    y = np.arange(len(metrics))
    axes[2].barh(y, metrics.rmse, color=["#9aabb5"] * 2 + ["#226e91"] * 3)
    axes[2].errorbar(
        metrics.rmse,
        y,
        xerr=[metrics.rmse - metrics.rmse_ci_low, metrics.rmse_ci_high - metrics.rmse],
        fmt="none",
        color="#222222",
        capsize=3,
    )
    axes[2].set(
        yticks=y,
        yticklabels=names,
        xlabel="OOF RMSE (lower is better)",
        title="C  Nested plate-group validation",
    )
    axes[2].invert_yaxis()
    fig.suptitle(
        "Endpoint triangulation and assay prediction | different dose ranges; no safety certification",
        fontsize=12,
    )
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=0.12)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def write_manifest(root, outputs, permutations):
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    files = [
        root / p
        for p in [
            "config/sources.json",
            "docs/VALIDATION_PROTOCOL.md",
            "pyproject.toml",
            "requirements-tested.txt",
        ]
    ]
    files += sorted((root / "data").rglob("*.csv"))
    files += sorted((root / "data/raw/usgs").glob("*.xml")) + sorted(
        (root / "data/raw/usgs").glob("*.pdf")
    )
    receipt = {
        "schema_version": 1,
        "protocol": "docs/VALIDATION_PROTOCOL.md",
        "seed": 20260909,
        "permutations": permutations,
        "python": platform.python_version(),
        "dependencies": {
            name: importlib.metadata.version(name)
            for name in ["numpy", "pandas", "scipy", "scikit-learn", "matplotlib"]
        },
        "input_sha256": {p.relative_to(root).as_posix(): sha(p) for p in files},
        "code_sha256": {
            p.relative_to(root).as_posix(): sha(p)
            for p in sorted((root / "src").rglob("*.py"))
        },
        "output_sha256": {
            p.relative_to(root).as_posix(): sha(p) for p in outputs.values()
        },
        "normalization": "same-read zero-dose solvent controls; six-hour reference absent",
        "scope": "retrospective internal reanalysis; not independent external validation",
    }
    path = root / "results/run_manifest.json"
    path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return path


def verify_manifest(root):
    """Verify archived inputs, implementation and outputs against the receipt."""
    root = root.resolve()
    receipt = json.loads(
        (root / "results/run_manifest.json").read_text(encoding="utf-8")
    )
    if receipt.get("schema_version") != 1:
        raise ValueError("Unsupported run manifest schema")
    count = 0
    for section in ["input_sha256", "code_sha256", "output_sha256"]:
        for name, expected in receipt[section].items():
            path = (root / name).resolve()
            if not path.is_relative_to(root):
                raise ValueError("Manifest path escapes repository")
            if (
                not path.is_file()
                or hashlib.sha256(path.read_bytes()).hexdigest() != expected
            ):
                raise ValueError(f"Run manifest mismatch: {name}")
            count += 1
    return count
