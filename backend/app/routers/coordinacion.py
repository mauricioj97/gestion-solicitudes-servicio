"""Consultas exclusivas de la coordinación: encargados y resumen consolidado."""
import sqlite3

from fastapi import APIRouter, Depends

from ..database import get_db
from ..security import requiere_rol
from ..servicios import ESTADOS

router = APIRouter(prefix="/api", tags=["Coordinación"])

COORDINADOR = requiere_rol("COORDINADOR")


@router.get("/usuarios/encargados", summary="Listar encargados activos (para asignar)")
def encargados(_: dict = Depends(COORDINADOR), db: sqlite3.Connection = Depends(get_db)):
    filas = db.execute(
        """SELECT u.id, u.nombre, u.usuario,
                  COUNT(s.id) AS solicitudes_activas
           FROM usuarios u
           LEFT JOIN solicitudes s ON s.encargado_id = u.id AND s.estado IN ('ASIGNADA', 'EN_GESTION')
           WHERE u.rol = 'ENCARGADO' AND u.activo = 1
           GROUP BY u.id ORDER BY u.nombre"""
    ).fetchall()
    return [dict(f) for f in filas]


@router.get("/reportes/resumen", summary="Resumen consolidado del proceso (CA-06)")
def resumen(_: dict = Depends(COORDINADOR), db: sqlite3.Connection = Depends(get_db)):
    conteo = {f["estado"]: f["n"] for f in db.execute("SELECT estado, COUNT(*) AS n FROM solicitudes GROUP BY estado")}
    por_estado = [{"estado": e, "etiqueta": et, "cantidad": conteo.get(e, 0)} for e, et in ESTADOS.items()]

    por_tipo = [
        dict(f)
        for f in db.execute(
            """SELECT t.nombre AS tipo, COUNT(s.id) AS cantidad
               FROM tipos_servicio t LEFT JOIN solicitudes s ON s.tipo_id = t.id
               GROUP BY t.id ORDER BY t.id"""
        )
    ]

    por_encargado = [
        dict(f)
        for f in db.execute(
            """SELECT u.nombre AS encargado,
                      SUM(s.estado IN ('ASIGNADA', 'EN_GESTION')) AS activas,
                      SUM(s.estado = 'FINALIZADA') AS finalizadas,
                      SUM(s.estado = 'CERRADA') AS cerradas,
                      COUNT(s.id) AS total
               FROM usuarios u LEFT JOIN solicitudes s ON s.encargado_id = u.id
               WHERE u.rol = 'ENCARGADO'
               GROUP BY u.id ORDER BY u.nombre"""
        )
    ]
    for fila in por_encargado:
        for clave in ("activas", "finalizadas", "cerradas"):
            fila[clave] = fila[clave] or 0

    promedio = db.execute(
        """SELECT AVG((julianday(fecha_cierre) - julianday(fecha_creacion)) * 24)
           FROM solicitudes WHERE estado = 'FINALIZADA'"""
    ).fetchone()[0]

    total = sum(conteo.values())
    return {
        "total": total,
        "pendientes": sum(conteo.get(e, 0) for e in ("RECIBIDA", "ASIGNADA", "EN_GESTION")),
        "sin_asignar": conteo.get("RECIBIDA", 0),
        "finalizadas": conteo.get("FINALIZADA", 0),
        "cerradas": conteo.get("CERRADA", 0),
        "tiempo_promedio_atencion_horas": round(promedio, 1) if promedio is not None else None,
        "por_estado": por_estado,
        "por_tipo": por_tipo,
        "por_encargado": por_encargado,
    }
