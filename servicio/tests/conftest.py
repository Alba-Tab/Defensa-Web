from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from app.config import Ajustes
from app.main import crear_aplicacion


@pytest.fixture
def cliente(tmp_path: Path) -> Iterator[TestClient]:
    ajustes = Ajustes(
        entorno="pruebas",
        modo="simulado",
        database_url=f"sqlite:///{tmp_path / 'pruebas.db'}",
    )
    aplicacion = crear_aplicacion(ajustes)
    with TestClient(aplicacion) as cliente_pruebas:
        SQLModel.metadata.create_all(aplicacion.state.motor)
        yield cliente_pruebas
