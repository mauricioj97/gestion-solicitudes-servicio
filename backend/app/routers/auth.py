"""Inicio y cierre de sesión del personal."""
import secrets
import sqlite3
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Response
from fastapi.security import HTTPAuthorizationCredentials

from ..config import SESSION_HOURS
from ..database import ahora, get_db
from ..schemas import LoginEntrada
from ..security import bearer, no_autenticado, usuario_actual, verificar_password

router = APIRouter(prefix="/api/auth", tags=["Autenticación (personal)"])


@router.post("/login", summary="Iniciar sesión")
def login(datos: LoginEntrada, db: sqlite3.Connection = Depends(get_db)):
    fila = db.execute("SELECT * FROM usuarios WHERE usuario = ?", (datos.usuario.strip().lower(),)).fetchone()
    # Mismo mensaje si el usuario no existe o la contraseña es incorrecta: no revela cuál falló.
    if fila is None or not fila["activo"] or not verificar_password(datos.contrasena, fila["password_hash"]):
        raise no_autenticado("Usuario o contraseña incorrectos")
    token = secrets.token_urlsafe(32)
    expira = (datetime.now() + timedelta(hours=SESSION_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
    with db:
        db.execute("DELETE FROM sesiones WHERE expira_en < ?", (ahora(),))
        db.execute(
            "INSERT INTO sesiones (token, usuario_id, creada_en, expira_en) VALUES (?, ?, ?, ?)",
            (token, fila["id"], ahora(), expira),
        )
    return {
        "token": token,
        "tipo": "Bearer",
        "expira_en": expira,
        "usuario": {"id": fila["id"], "nombre": fila["nombre"], "usuario": fila["usuario"], "rol": fila["rol"]},
    }


@router.post("/logout", status_code=204, summary="Cerrar sesión")
def logout(
    _: dict = Depends(usuario_actual),
    credenciales: HTTPAuthorizationCredentials = Depends(bearer),
    db: sqlite3.Connection = Depends(get_db),
):
    with db:
        db.execute("DELETE FROM sesiones WHERE token = ?", (credenciales.credentials,))
    return Response(status_code=204)


@router.get("/yo", summary="Datos del usuario con sesión activa")
def yo(usuario: dict = Depends(usuario_actual)):
    return usuario
