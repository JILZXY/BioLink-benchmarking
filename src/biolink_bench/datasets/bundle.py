from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DatasetBundle:
    """Representación lógica común del dataset para los tres modelos de BD."""

    dataset_id: str
    dataset_tag: str
    seed: int | None = None
    taxa: list[dict[str, Any]] = field(default_factory=list)
    taxon_names: list[dict[str, Any]] = field(default_factory=list)
    taxon_identifiers: list[dict[str, Any]] = field(default_factory=list)
    localities: list[dict[str, Any]] = field(default_factory=list)
    sources: list[dict[str, Any]] = field(default_factory=list)
    source_versions: list[dict[str, Any]] = field(default_factory=list)
    interaction_types: list[dict[str, Any]] = field(default_factory=list)
    evidences: list[dict[str, Any]] = field(default_factory=list)
    assertions: list[dict[str, Any]] = field(default_factory=list)
    assertion_evidences: list[dict[str, Any]] = field(default_factory=list)
    import_batches: list[dict[str, Any]] = field(default_factory=list)
    import_records: list[dict[str, Any]] = field(default_factory=list)
    review_events: list[dict[str, Any]] = field(default_factory=list)
    taxon_dossiers: list[dict[str, Any]] = field(default_factory=list)
    study_dossiers: list[dict[str, Any]] = field(default_factory=list)
    raw_source_records: list[dict[str, Any]] = field(default_factory=list)

    @property
    def published_assertions(self) -> list[dict[str, Any]]:
        """Solo afirmaciones PUBLISHED pueden proyectarse al grafo."""
        return [a for a in self.assertions if a.get("status") == "PUBLISHED"]

    def entity_counts(self) -> dict[str, int]:
        return {
            "taxa": len(self.taxa),
            "taxon_names": len(self.taxon_names),
            "taxon_identifiers": len(self.taxon_identifiers),
            "localities": len(self.localities),
            "sources": len(self.sources),
            "source_versions": len(self.source_versions),
            "interaction_types": len(self.interaction_types),
            "evidences": len(self.evidences),
            "assertions": len(self.assertions),
            "published_assertions": len(self.published_assertions),
            "assertion_evidences": len(self.assertion_evidences),
            "import_batches": len(self.import_batches),
            "import_records": len(self.import_records),
            "review_events": len(self.review_events),
            "taxon_dossiers": len(self.taxon_dossiers),
            "study_dossiers": len(self.study_dossiers),
            "raw_source_records": len(self.raw_source_records),
        }
