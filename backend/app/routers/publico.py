"""Endpoints públicos: el solicitante radica y consulta sin cuenta."""
import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from ..database import ahora, get_db
from ..schemas import SolicitudCrear
from ..servicios import generar_radicado, registrar_accion, vista_publica

router = APIRouter(prefix="/api", tags=["Público (solicitante)"])


@router.get("/tipos-servicio", summary="Listar tipos de servicio")
def listar_tipos(db: sqlite3.Connection = Depends(get_db)):
    return [dict(f) for f in db.execute("SELECT id, nombre FROM tipos_servicio ORDER BY id")]


@router.post("/solicitudes", status_code=201, summary="Radicar una solicitud (CA-01)")
def radicar(datos: SolicitudCrear, db: sqlite3.Connection = Depends(get_db)):
    if db.execute("SELECT 1 FROM tipos_servicio WHERE id = ?", (datos.tipo_id,)).fetchone() is None:
        raise HTTPException(422, "El tipo de servicio indicado no existe")
    momento = ahora()
    with db:  # transacción: solicitante + solicitud + historial
        # RN-13: siempre se inserta un registro nuevo. Nunca se actualizan los datos de una
        # cédula existente, porque la radicación es pública y cualquiera podría escribir la
        # cédula de otra persona y cambiarle el nombre o el teléfono.
        solicitante_id = db.execute(
            "INSERT INTO solicitantes (cedula, nombre, direccion, telefono, correo) VALUES (?, ?, ?, ?, ?)",
            (datos.cedula, datos.nombre, datos.direccion, datos.telefono, datos.correo),
        ).lastrowid
        radicado = generar_radicado(db)
        solicitud_id = db.execute(
            """INSERT INTO solicitudes (radicado, solicitante_id, tipo_id, asunto, descripcion, estado,
                                        fecha_creacion, fecha_actualizacion)
               VALUES (?, ?, ?, ?, ?, 'RECIBIDA', ?, ?)""",
            (radicado, solicitante_id, datos.tipo_id, datos.asunto, datos.descripcion, momento, momento),
        ).lastrowid
        registrar_accion(db, solicitud_id, None, "REGISTRO", "Solicitud radicada por el solicitante", None, "RECIBIDA", momento)
    return {
        "mensaje": "Solicitud radicada correctamente. Guarde su número de radicado para consultarla.",
        **vista_publica(db, solicitud_id),
    }


@router.get("/solicitudes/consulta/{radicado}", summary="Consultar una solicitud por radicado (CA-03, CA-05)")
def consultar(radicado: str, db: sqlite3.Connection = Depends(get_db)):
    fila = db.execute("SELECT id FROM solicitudes WHERE radicado = ?", (radicado.strip(),)).fetchone()
    if fila is None:
        raise HTTPException(404, "Solicitud no encontrada. Verifique el número de radicado")
    return vista_publica(db, fila["id"])
