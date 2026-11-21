from __future__ import annotations

from pathlib import Path

from biolink_bench.datasets.synthetic_generator import (
    SYNTHETIC_TAG,
    build_synthetic_bundle,
    export_synthetic_dataset,
    load_synthetic_dataset,
)

REAL_SPECIES_NAMES = {
    "Artibeus lituratus",
    "Carollia perspicillata",
    "Sturnira lilium",
    "Cecropia obtusifolia",
    "Cecropia peltata",
    "Piper auritum",
    "Piper hispidum",
    "Licania platypus",
    "Pouteria sapota",
    "Tapirus bairdii",
}


def test_synthetic_generator_is_deterministic() -> None:
    b1 = build_synthetic_bundle(target_assertions=50, seed=42)
    b2 = build_synthetic_bundle(target_assertions=50, seed=42)
    assert b1.assertions == b2.assertions
    assert b1.taxa == b2.taxa
    assert b1.taxon_dossiers == b2.taxon_dossiers


def test_synthetic_avoids_real_names_and_tags_all_entities() -> None:
    bundle = build_synthetic_bundle(target_assertions=60, seed=99)
    assert bundle.dataset_tag == SYNTHETIC_TAG
    assert len(bundle.assertions) == 60
    assert len(bundle.published_assertions) < len(bundle.assertions)

    taxon_names = {t["accepted_name"] for t in bundle.taxa}
    assert taxon_names.isdisjoint(REAL_SPECIES_NAMES)
    assert all(t["dataset_tag"] == SYNTHETIC_TAG for t in bundle.taxa)
    assert all(a["dataset_tag"] == SYNTHETIC_TAG for a in bundle.assertions)
    assert all(d["dataset_tag"] == SYNTHETIC_TAG for d in bundle.taxon_dossiers)

    taxa_ids = {t["taxon_id"] for t in bundle.taxa}
    for a in bundle.assertions:
        assert a["actor_taxon_id"] in taxa_ids
        assert a["target_taxon_id"] in taxa_ids


def test_synthetic_export_and_checksum_verification(tmp_path: Path) -> None:
    out_dir = tmp_path / "synthetic"
    manifest_dir = tmp_path / "manifests"
    bundle, manifest_path = export_synthetic_dataset(out_dir, manifest_dir, target_assertions=40, seed=1234)
    assert manifest_path.exists()

    reloaded = load_synthetic_dataset(out_dir / bundle.dataset_id, manifest_path)
    assert reloaded.entity_counts() == bundle.entity_counts()
    assert reloaded.assertions == bundle.assertions
