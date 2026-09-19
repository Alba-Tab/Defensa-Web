from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from threading import Lock
from uuid import uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError


class ServicioContrasenas:
    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    def crear_hash(self, contrasena: str) -> str:
        return self._hasher.hash(contrasena)

    def verificar(self, hash_contrasena: str, contrasena: str) -> bool:
        try:
            return self._hasher.verify(hash_contrasena, contrasena)
        except (VerifyMismatchError, InvalidHashError):
            return False


class ServicioTokens:
    def __init__(self, secreto: str, minutos: int) -> None:
        self._secreto = secreto
        self._duracion = timedelta(minutes=minutos)

    @property
    def duracion_segundos(self) -> int:
        return int(self._duracion.total_seconds())

    def crear(self, usuario_id: int, nombre: str) -> str:
        ahora = datetime.now(UTC)
        return jwt.encode(
            {
                "sub": str(usuario_id),
                "nombre": nombre,
                "iat": ahora,
                "exp": ahora + self._duracion,
                "jti": str(uuid4()),
            },
            self._secreto,
            algorithm="HS256",
        )

    def decodificar(self, token: str) -> dict[str, object]:
        return jwt.decode(token, self._secreto, algorithms=["HS256"])


class LimitadorLogin:
    def __init__(self, max_intentos: int = 5, ventana_segundos: int = 60) -> None:
        self._max_intentos = max_intentos
        self._ventana = timedelta(seconds=ventana_segundos)
        self._intentos: defaultdict[str, deque[datetime]] = defaultdict(deque)
        self._lock = Lock()

    def bloqueado(self, ip: str, ahora: datetime) -> bool:
        with self._lock:
            intentos = self._intentos[ip]
            limite = ahora - self._ventana
            while intentos and intentos[0] < limite:
                intentos.popleft()
            return len(intentos) >= self._max_intentos

    def registrar_fallo(self, ip: str, ahora: datetime) -> None:
        with self._lock:
            self._intentos[ip].append(ahora)

    def limpiar(self, ip: str) -> None:
        with self._lock:
            self._intentos.pop(ip, None)
