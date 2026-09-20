from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from app.config import Ajustes
from app.database import crear_motor
from app.main import crear_aplicacion


@pytest.fixture
def cliente(tmp_path: Path) -> Iterator[TestClient]:
    ajustes = Ajustes(
        entorno="pruebas",
        modo="simulado",
        database_url=f"sqlite:///{tmp_path / 'pruebas.db'}",
        jwt_secret="secreto-de-pruebas-con-longitud-suficiente",
        admin_usuario="admin",
        admin_password="contrasena-de-pruebas",
        modelo_clasificador=None,
        fcm_credenciales=None,
        openrouter_api_key=None,
        openrouter_modelo=None,
    )
    motor = crear_motor(ajustes)
    SQLModel.metadata.create_all(motor)
    motor.dispose()
    aplicacion = crear_aplicacion(ajustes)
    with TestClient(aplicacion) as cliente_pruebas:
        yield cliente_pruebas
