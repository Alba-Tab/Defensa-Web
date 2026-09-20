from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.dominio.modelos import Usuario
from app.seguridad import LimitadorLogin

CLAVE_PRUEBAS = "secreto-de-pruebas-con-longitud-suficiente"


def login(cliente: TestClient, usuario: str = "admin", contrasena: str = "contrasena-de-pruebas"):
    return cliente.post(
        "/api/auth/login",
        json={"usuario": usuario, "contrasena": contrasena},
    )


def test_login_valido_emite_token_de_ocho_horas(cliente: TestClient) -> None:
    respuesta = login(cliente)

    assert respuesta.status_code == 200
    contenido = jwt.decode(
        respuesta.json()["access_token"],
        CLAVE_PRUEBAS,
        algorithms=["HS256"],
    )
    assert respuesta.json()["expires_in"] == 8 * 60 * 60
    assert contenido["exp"] - contenido["iat"] == 8 * 60 * 60


def test_login_invalido_usa_un_mensaje_unico(cliente: TestClient) -> None:
    usuario_inexistente = login(cliente, usuario="nadie")
    clave_incorrecta = login(cliente, contrasena="incorrecta")

    assert usuario_inexistente.status_code == 401
    assert clave_incorrecta.status_code == 401
    assert usuario_inexistente.json() == clave_incorrecta.json()


def test_todas_las_rutas_protegidas_rechazan_tokens_ausentes_alterados_y_vencidos(
    cliente: TestClient,
) -> None:
    vencido = jwt.encode(
        {
            "sub": "1",
            "nombre": "admin",
            "iat": datetime.now(UTC) - timedelta(hours=9),
            "exp": datetime.now(UTC) - timedelta(hours=1),
        },
        CLAVE_PRUEBAS,
        algorithm="HS256",
    )
    token_valido = login(cliente).json()["access_token"]
    alterado = f"{token_valido[:-1]}{'a' if token_valido[-1] != 'a' else 'b'}"
    rutas = [
        ("GET", "/api/salud"),
        ("POST", "/api/simulacion/eventos"),
        ("GET", "/api/incidentes"),
        ("GET", "/api/incidentes/1"),
        ("GET", "/api/baneos"),
        ("POST", "/api/baneos/192.0.2.1/liberar"),
        ("POST", "/api/dispositivos"),
        ("GET", "/api/eventos"),
    ]

    for metodo, ruta in rutas:
        sin_token = cliente.request(metodo, ruta)
        con_token_alterado = cliente.request(
            metodo, ruta, headers={"Authorization": f"Bearer {alterado}"}
        )
        con_token_vencido = cliente.request(
            metodo, ruta, headers={"Authorization": f"Bearer {vencido}"}
        )
        assert sin_token.status_code == 401, ruta
        assert con_token_alterado.status_code == 401, ruta
        assert con_token_vencido.status_code == 401, ruta


def test_contrasena_se_persiste_como_hash(cliente: TestClient) -> None:
    with Session(cliente.app.state.motor) as sesion:
        usuario = sesion.exec(select(Usuario).where(Usuario.nombre == "admin")).one()

    assert usuario.hash_contrasena != "contrasena-de-pruebas"
    assert usuario.hash_contrasena.startswith("$argon2")


def test_sexto_intento_fallido_se_rechaza_y_el_bloqueo_dura_cinco_minutos(
    cliente: TestClient,
) -> None:
    respuestas = [login(cliente, contrasena="incorrecta") for _ in range(6)]

    assert [respuesta.status_code for respuesta in respuestas[:5]] == [401] * 5
    assert respuestas[5].status_code == 429

    limitador = LimitadorLogin(max_intentos=5, ventana_segundos=60, bloqueo_segundos=300)
    inicio = datetime(2026, 9, 19, tzinfo=UTC)
    for _ in range(5):
        limitador.registrar_fallo("192.0.2.10", inicio)
    assert limitador.bloqueado("192.0.2.10", inicio)
    assert limitador.bloqueado("192.0.2.10", inicio + timedelta(seconds=299))
    assert not limitador.bloqueado("192.0.2.10", inicio + timedelta(seconds=300))
