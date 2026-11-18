"""Contraseñas, sesiones y control de acceso por rol."""
import hashlib
import hmac
import secrets
import sqlite3

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .database import ahora, get_db

ITERACIONES = 200_000

bearer = HTTPBearer(auto_error=False, description="Token entregado por POST /api/auth/login")


def hash_password(password: str) -> str:
    sal = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(sal), ITERACIONES).hex()
    return f"pbkdf2_sha256${ITERACIONES}${sal}${digest}"


def verificar_password(password: str, guardado: str) -> bool:
    try:
        _, iteraciones, sal, digest = guardado.split("$")
        calculado = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(sal), int(iteraciones)).hex()
        return hmac.compare_digest(calculado, digest)
    except ValueError:
        return False


def no_autenticado(mensaje: str) -> HTTPException:
    return HTTPException(status_code=401, detail=mensaje, headers={"WWW-Authenticate": "Bearer"})


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    """Devuelve el usuario dueño del token o responde 401."""
    if credenciales is None:
        raise no_autenticado("Debe iniciar sesión para realizar esta acción")
    fila = db.execute(
        """SELECT u.id, u.nombre, u.usuario, u.rol, u.activo, s.expira_en
           FROM sesiones s JOIN usuarios u ON u.id = s.usuario_id
           WHERE s.token = ?""",
        (credenciales.credentials,),
    ).fetchone()
    if fila is None or fila["expira_en"] < ahora() or not fila["activo"]:
        raise no_autenticado("La sesión no es válida o ha vencido. Inicie sesión nuevamente")
    return {"id": fila["id"], "nombre": fila["nombre"], "usuario": fila["usuario"], "rol": fila["rol"]}


def requiere_rol(*roles: str):
    """Dependencia que permite el acceso solo a los roles indicados (si no, 403)."""

    def verificar(usuario: dict = Depends(usuario_actual)) -> dict:
        if usuario["rol"] not in roles:
            raise HTTPException(status_code=403, detail="No tiene permisos para realizar esta acción")
        return usuario

    return verificar
