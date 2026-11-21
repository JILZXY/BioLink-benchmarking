from __future__ import annotations

from biolink_bench.config import PROJECT_ROOT
from biolink_bench.datasets.scientific_fixture import load_scientific_fixture


def test_scientific_fixture_integrity_and_rules() -> None:
    bundle, manifest = load_scientific_fixture(PROJECT_ROOT / "datasets" / "scientific_fixture")
    assert bundle.dataset_tag == "SCIENTIFIC_FIXTURE"
    assert len(bundle.sources) == 2
    assert len(bundle.localities) == 2
    assert len(bundle.taxa) == 32
    assert len(bundle.assertions) == 21
    assert manifest["counts"]["assertions"] == 21

    locs = {loc["locality_id"]: loc for loc in bundle.localities}
    assert locs["LOC_RBMA_SOUTH"]["spatial_validation_status"] == "INSIDE_ANP"
    assert locs["LOC_PDLG"]["spatial_validation_status"] == "OUTSIDE_ANP"

    # Las morfoespecies/géneros permanecen en su rango sin interacciones inventadas
    taxa_by_id = {t["taxon_id"]: t for t in bundle.taxa}
    assert taxa_by_id["TAX_PL_004"]["taxonomic_rank"] == "GENUS"
    assert taxa_by_id["TAX_PL_017"]["taxonomic_rank"] == "MORPHOSPECIES"
    target_ids_with_interactions = {a["target_taxon_id"] for a in bundle.assertions}
    assert "TAX_PL_004" not in target_ids_with_interactions
    assert "TAX_PL_013" not in target_ids_with_interactions
    assert "TAX_PL_017" not in target_ids_with_interactions
    assert "TAX_PL_018" not in target_ids_with_interactions

    # Sturnira lilium + Piper hispidum en BAT2007 solo aparece en PDLG, nunca en RBMA
    sturnira_locs = {a["locality_id"] for a in bundle.assertions if a["actor_taxon_id"] == "TAX_AN_003"}
    assert sturnira_locs == {"LOC_PDLG"}
