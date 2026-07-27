"""Download and verify public source data without generating any observations."""

from __future__ import annotations

import csv
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url, headers={"User-Agent": "6PPD-public-data-research/0.1"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        destination.write_bytes(response.read())


def md5sum(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    digest.update(path.read_bytes())
    return digest.hexdigest()


def sha256sum(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def download_usgs(sources: dict) -> None:
    destination_dir = ROOT / "data" / "raw" / "usgs"
    for filename, metadata in sources["usgs_2026"]["files"].items():
        destination = destination_dir / filename
        if not destination.exists() or md5sum(destination) != metadata["md5"]:
            print(f"Downloading {filename}")
            download(metadata["url"], destination)
        observed = md5sum(destination)
        if observed != metadata["md5"]:
            raise RuntimeError(
                f"Checksum mismatch for {filename}: {observed} != {metadata['md5']}"
            )
    report = sources["usgs_2026"]["report"]
    report_path = destination_dir / report["filename"]
    if not report_path.exists() or sha256sum(report_path) != report["sha256"]:
        print(f"Downloading {report['filename']}")
        download(report["url"], report_path)
    observed_sha256 = sha256sum(report_path)
    if observed_sha256 != report["sha256"]:
        raise RuntimeError(
            f"Checksum mismatch for {report['filename']}: "
            f"{observed_sha256} != {report['sha256']}"
        )
    metadata = sources["usgs_2026"]["metadata"]
    metadata_path = destination_dir / metadata["filename"]
    if not metadata_path.exists() or md5sum(metadata_path) != metadata["md5"]:
        print(f"Downloading {metadata['filename']}")
        download(metadata["url"], metadata_path)
    observed_md5 = md5sum(metadata_path)
    if observed_md5 != metadata["md5"]:
        raise RuntimeError(
            f"Checksum mismatch for {metadata['filename']}: "
            f"{observed_md5} != {metadata['md5']}"
        )


def pubchem_identity(casrn: str, api_base: str) -> dict[str, object]:
    encoded = urllib.parse.quote(casrn, safe="")
    properties = (
        "Title,MolecularFormula,MolecularWeight,CanonicalSMILES,"
        "IsomericSMILES,InChI,InChIKey"
    )
    url = (
        f"{api_base}/compound/name/{encoded}/property/{properties}/JSON"
    )
    try:
        request = urllib.request.Request(
            url, headers={"User-Agent": "6PPD-public-data-research/0.1"}
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.load(response)
        record = payload["PropertyTable"]["Properties"][0]
        return {
            "casrn": casrn,
            "resolved": True,
            "pubchem_cid": record.get("CID"),
            "title": record.get("Title"),
            "molecular_formula": record.get("MolecularFormula"),
            "molecular_weight": record.get("MolecularWeight"),
            "canonical_smiles": record.get("ConnectivitySMILES")
            or record.get("CanonicalSMILES"),
            "isomeric_smiles": record.get("SMILES") or record.get("IsomericSMILES"),
            "inchi": record.get("InChI"),
            "inchikey": record.get("InChIKey"),
            "source_url": url,
        }
    except (urllib.error.HTTPError, KeyError, IndexError) as exc:
        return {
            "casrn": casrn,
            "resolved": False,
            "pubchem_cid": None,
            "title": None,
            "molecular_formula": None,
            "molecular_weight": None,
            "canonical_smiles": None,
            "isomeric_smiles": None,
            "inchi": None,
            "inchikey": None,
            "source_url": url,
            "resolution_note": str(exc),
        }


def download_pubchem(sources: dict) -> None:
    registry = ROOT / "data" / "reference" / "candidate_registry.csv"
    with registry.open(newline="", encoding="utf-8") as stream:
        casrns = [
            row["casrn"]
            for row in csv.DictReader(stream)
            if row["casrn"].strip()
        ]
    records = []
    for index, casrn in enumerate(casrns):
        print(f"PubChem {index + 1}/{len(casrns)}: {casrn}")
        records.append(pubchem_identity(casrn, sources["pubchem"]["api_base"]))
        time.sleep(0.2)

    destination = ROOT / "data" / "processed" / "pubchem_identities.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for record in records for key in record})
    with destination.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    with (ROOT / "config" / "sources.json").open(encoding="utf-8") as stream:
        sources = json.load(stream)
    download_usgs(sources)
    download_pubchem(sources)


if __name__ == "__main__":
    main()
