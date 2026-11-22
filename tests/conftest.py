from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--engine",
        action="store",
        default="all",
        help="Motor objetivo para pruebas live (mysql, postgresql, mongodb, couchdb, neo4j, memgraph o all)",
    )


@pytest.fixture
def target_engine(request: pytest.FixtureRequest) -> str:
    return str(request.config.getoption("--engine"))
