"""Punto de entrada de la aplicación: API REST + interfaz web."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import FRONTEND_DIR
from .database import inicializar_bd
from .routers import auth, coordinacion, gestion, publico

logger = logging.getLogger("solicitudes")

MENSAJES_VALIDACION = {
    "missing": "Este campo es obligatorio",
    "string_type": "Debe ser un texto",
    "int_parsing": "Debe ser un número entero",
    "int_type": "Debe ser un número entero",
    "json_invalid": "El cuerpo de la petición no es un JSON válido",
    "model_attributes_type": "El cuerpo de la petición debe ser un objeto JSON",
}


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    inicializar_bd()
    yield


app = FastAPI(
    title="API — Gestión de Solicitudes de Servicio",
    version="1.0.0",
    description=(
        "API REST para radicar, evaluar, gestionar, hacer seguimiento y finalizar solicitudes de servicio.\n\n"
        "**Cómo probar endpoints protegidos:** ejecute `POST /api/auth/login`, copie el `token` "
        "y péguelo en el botón **Authorize** (arriba a la derecha)."
    ),
    lifespan=ciclo_de_vida,
)


@app.exception_handler(StarletteHTTPException)
async def error_http(_: Request, exc: StarletteHTTPException):
    detalle = exc.detail if exc.status_code != 404 or exc.detail != "Not Found" else "Recurso no encontrado"
    return JSONResponse({"detalle": detalle}, status_code=exc.status_code, headers=getattr(exc, "headers", None))


@app.exception_handler(RequestValidationError)
async def error_validacion(_: Request, exc: RequestValidationError):
    errores = []
    for e in exc.errors():
        campo = str(e["loc"][-1]) if e.get("loc") else "body"
        mensaje = MENSAJES_VALIDACION.get(e["type"]) or str(e["msg"]).removeprefix("Value error, ")
        errores.append({"campo": campo, "mensaje": mensaje})
    return JSONResponse({"detalle": "Los datos enviados no son válidos", "errores": errores}, status_code=422)


@app.exception_handler(Exception)
async def error_interno(_: Request, exc: Exception):
    logger.exception("Error no controlado")  # el detalle queda en el log del servidor, no se envía al cliente
    return JSONResponse({"detalle": "Error interno del servidor"}, status_code=500)


app.include_router(publico.router)
app.include_router(auth.router)
app.include_router(gestion.router)
app.include_router(coordinacion.router)

# La interfaz web se sirve desde el mismo servidor (va al final para no tapar las rutas /api y /docs)
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
