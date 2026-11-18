"""Configuración leída desde variables de entorno (archivo .env opcional)."""
import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROYECTO_DIR = BACKEND_DIR.parent

load_dotenv(BACKEND_DIR / ".env")

# Ruta del archivo de base de datos SQLite
DB_PATH = Path(os.getenv("DB_PATH", BACKEND_DIR / "data" / "solicitudes.db"))
if not DB_PATH.is_absolute():
    DB_PATH = BACKEND_DIR / DB_PATH

# Duración de la sesión del personal, en horas
SESSION_HOURS = int(os.getenv("SESSION_HOURS", "8"))

# Carpeta con la interfaz web
FRONTEND_DIR = PROYECTO_DIR / "frontend"
