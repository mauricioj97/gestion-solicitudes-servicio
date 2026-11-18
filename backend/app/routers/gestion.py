"""Gestión de solicitudes por el personal (coordinación y encargados)."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from ..database import get_db
from ..schemas import AsignarEntrada, CerrarEntrada, EvaluarEntrada, FinalizarEntrada, SeguimientoEntrada
from ..security import requiere_rol, usuario_actual
from ..servicios import ESTADOS, aplicar_accion, detalle, historial, obtener_solicitud, verificar_acceso

router = APIRouter(prefix="/api/gestion", tags=["Gestión (personal)"])

COORDINADOR = requiere_rol("COORDINADOR")
ENCARGADO = requiere_rol("ENCARGADO")
PERSONAL = requiere_rol("COORDINADOR", "ENCARGADO")


@router.get("/solicitudes", summary="Listar solicitudes según el rol")
def listar(
    estado: str | None = Query(None, description="RECIBIDA, ASIGNADA, EN_GESTION, FINALIZADA o CERRADA"),
    usuario: dict = Depends(PERSONAL),
    db: sqlite3.Connection = Depends(get_db),
):
    condiciones, parametros = [], []
    if usuario["rol"] == "ENCARGADO":  # RN-11
        condiciones.append("s.encargado_id = ?")
        parametros.append(usuario["id"])
    if estado:
        if estado not in ESTADOS:
            raise HTTPException(422, f"Estado no válido. Use uno de: {', '.join(ESTADOS)}")
        condiciones.append("s.estado = ?")
        parametros.append(estado)
    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""
    filas = db.execute(
        f"""SELECT s.id, s.radicado, s.asunto, s.estado, s.fecha_creacion, s.fecha_actualizacion,
                   t.nombre AS tipo, so.nombre AS solicitante, u.nombre AS encargado
            FROM solicitudes s
            JOIN tipos_servicio t ON t.id = s.tipo_id
            JOIN solicitantes so ON so.id = s.solicitante_id
            LEFT JOIN usuarios u ON u.id = s.encargado_id
            {where} ORDER BY s.fecha_creacion DESC, s.id DESC""",
        parametros,
    ).fetchall()
    return [{**dict(f), "estado_etiqueta": ESTADOS[f["estado"]]} for f in filas]


@router.get("/solicitudes/{solicitud_id}", summary="Detalle de una solicitud")
def ver_detalle(solicitud_id: int, usuario: dict = Depends(PERSONAL), db: sqlite3.Connection = Depends(get_db)):
    verificar_acceso(obtener_solicitud(db, solicitud_id), usuario)
    return detalle(db, solicitud_id)


@router.get("/solicitudes/{solicitud_id}/historial", summary="Historial de acciones (CA-04)")
def ver_historial(solicitud_id: int, usuario: dict = Depends(PERSONAL), db: sqlite3.Connection = Depends(get_db)):
    verificar_acceso(obtener_solicitud(db, solicitud_id), usuario)
    return historial(db, solicitud_id)


@router.post("/solicitudes/{solicitud_id}/asignar", summary="Asignar o reasignar encargado (solo coordinación)")
def asignar(
    solicitud_id: int,
    datos: AsignarEntrada,
    usuario: dict = Depends(COORDINADOR),
    db: sqlite3.Connection = Depends(get_db),
):
    solicitud = obtener_solicitud(db, solicitud_id)
    encargado = db.execute(
        "SELECT id, nombre FROM usuarios WHERE id = ? AND rol = 'ENCARGADO' AND activo = 1", (datos.encargado_id,)
    ).fetchone()
    if encargado is None:
        raise HTTPException(422, "El encargado indicado no existe o no está activo")
    if solicitud["encargado_id"] == encargado["id"]:
        raise HTTPException(409, f"La solicitud ya está asignada a {encargado['nombre']}")
    verbo = "Reasignada" if solicitud["encargado_id"] else "Asignada"
    aplicar_accion(db, solicitud, usuario, "ASIGNACION", f"{verbo} a {encargado['nombre']}", encargado_id=encargado["id"])
    return detalle(db, solicitud_id)


@router.post("/solicitudes/{solicitud_id}/evaluar", summary="Evaluar (revisar) e iniciar gestión")
def evaluar(
    solicitud_id: int,
    datos: EvaluarEntrada,
    usuario: dict = Depends(ENCARGADO),
    db: sqlite3.Connection = Depends(get_db),
):
    solicitud = obtener_solicitud(db, solicitud_id)
    verificar_acceso(solicitud, usuario)
    aplicar_accion(db, solicitud, usuario, "EVALUACION", datos.observacion)
    return detalle(db, solicitud_id)


@router.post("/solicitudes/{solicitud_id}/seguimiento", summary="Registrar nota de seguimiento")
def seguimiento(
    solicitud_id: int,
    datos: SeguimientoEntrada,
    usuario: dict = Depends(ENCARGADO),
    db: sqlite3.Connection = Depends(get_db),
):
    solicitud = obtener_solicitud(db, solicitud_id)
    verificar_acceso(solicitud, usuario)
    aplicar_accion(db, solicitud, usuario, "SEGUIMIENTO", datos.nota)
    return detalle(db, solicitud_id)


@router.post("/solicitudes/{solicitud_id}/finalizar", summary="Responder y finalizar (CA-05)")
def finalizar(
    solicitud_id: int,
    datos: FinalizarEntrada,
    usuario: dict = Depends(ENCARGADO),
    db: sqlite3.Connection = Depends(get_db),
):
    solicitud = obtener_solicitud(db, solicitud_id)
    verificar_acceso(solicitud, usuario)
    aplicar_accion(db, solicitud, usuario, "RESPUESTA", datos.respuesta, respuesta=datos.respuesta)
    return detalle(db, solicitud_id)


@router.post("/solicitudes/{solicitud_id}/cerrar", summary="Cerrar con motivo (coordinación o encargado asignado)")
def cerrar(
    solicitud_id: int,
    datos: CerrarEntrada,
    usuario: dict = Depends(PERSONAL),
    db: sqlite3.Connection = Depends(get_db),
):
    solicitud = obtener_solicitud(db, solicitud_id)
    verificar_acceso(solicitud, usuario)
    aplicar_accion(db, solicitud, usuario, "CIERRE", datos.motivo, motivo_cierre=datos.motivo)
    return detalle(db, solicitud_id)
