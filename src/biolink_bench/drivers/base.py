from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from biolink_bench.config import EngineConfig
from biolink_bench.datasets.bundle import DatasetBundle


@dataclass
class SmokeResult:
    engine: str
    model: str
    connected: bool
    health_ok: bool
    server_version: str
    inserted_records: int
    query_ok: bool
    cleanup_ok: bool
    details: dict[str, Any]


class BaseEngineAdapter(ABC):
    """Interfaz mínima común para adaptadores nativos directos sin ORM de aplicación."""

    def __init__(self, config: EngineConfig) -> None:
        self.config = config

    @property
    def engine_name(self) -> str:
        return self.config.name

    @property
    def model_name(self) -> str:
        return self.config.model

    @abstractmethod
    def connect(self) -> None:
        """Establece conexión directa con el motor usando su driver nativo."""

    @abstractmethod
    def disconnect(self) -> None:
        """Cierra la conexión directa."""

    @abstractmethod
    def health_check(self) -> tuple[bool, str]:
        """Verifica disponibilidad directa y retorna (ok, mensaje/versión)."""

    @abstractmethod
    def get_engine_info(self) -> dict[str, Any]:
        """Retorna metadatos exactos reportados por el motor (versión, edición, etc.)."""

    @abstractmethod
    def prepare_schema(self) -> None:
        """Prepara tablas/colecciones/constraints base del modelo."""

    @abstractmethod
    def load_dataset(self, bundle: DatasetBundle) -> dict[str, int]:
        """Carga las entidades lógicas del bundle correspondiente a este paradigma."""

    @abstractmethod
    def create_indexes(self) -> None:
        """Crea índices secundarios en fase separada para medir su costo."""

    @abstractmethod
    def execute_operation(self, op_name: str, params: dict[str, Any]) -> Any:
        """Ejecuta una operación de workload específica y retorna el resultado normalizado."""

    @abstractmethod
    def cleanup_test_data(self, dataset_tag: str) -> int:
        """Elimina registros asociados a un dataset_tag de prueba."""

    @abstractmethod
    def reset_all_data(self) -> None:
        """Limpia completamente las estructuras de prueba del motor."""

    @abstractmethod
    def get_storage_bytes(self) -> int | None:
        """Consulta al motor el almacenamiento reportado en bytes (si está disponible)."""

    @abstractmethod
    def run_smoke_crud(self) -> SmokeResult:
        """Inserta registros de prueba, consulta, valida y limpia dejando la base sin residuos."""
