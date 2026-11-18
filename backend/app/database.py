"""Conexión a la base de datos SQLite y creación de tablas."""
import sqlite3
from datetime import datetime
from pathlib import Path

from .config import DB_PATH

SCHEMA_PATH = Path(__file__).with_name("schema.sql")

TIPOS_SERVICIO = ["Trámite", "Orientación", "Atención administrativa", "Requerimiento de servicio"]


def ahora() -> str:
    """Fecha y hora actual en formato AAAA-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    """Dependencia de FastAPI: abre una conexión por petición y la cierra al terminar."""
    conn = conectar()
    try:
        yield conn
    finally:
        conn.close()


def inicializar_bd() -> None:
    """Crea las tablas si no existen y carga los datos base (tipos y usuarios)."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = conectar()
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        for nombre in TIPOS_SERVICIO:
            conn.execute("INSERT OR IGNORE INTO tipos_servicio (nombre) VALUES (?)", (nombre,))
        conn.commit()
        if conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
            from .seed import crear_usuarios_base

            crear_usuarios_base(conn)
            conn.commit()
    finally:
        conn.close()
