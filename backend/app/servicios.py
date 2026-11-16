"""Reglas de negocio: flujo de estados, historial y consultas de solicitudes."""
import secrets
import sqlite3

from fastapi import HTTPException

from .database import ahora

ESTADOS = {
    "RECIBIDA": "Recibida",
    "ASIGNADA": "Asignada",
    "EN_GESTION": "En gestión",
    "FINALIZADA": "Finalizada",
    "CERRADA": "Cerrada",
}
ESTADOS_FINALES = {"FINALIZADA", "CERRADA"}
ESTADOS_PENDIENTES = ("RECIBIDA", "ASIGNADA", "EN_GESTION")

ACCIONES = {
    "REGISTRO": "Registro de la solicitud",
    "ASIGNACION": "Asignación",
    "EVALUACION": "Evaluación",
    "SEGUIMIENTO": "Seguimiento",
    "RESPUESTA": "Respuesta y finalización",
    "CIERRE": "Cierre",
}

# Máquina de estados (RN-05): acción -> (estados desde los que se permite, estado resultante, verbo)
TRANSICIONES = {
    "ASIGNACION": ({"RECIBIDA", "ASIGNADA"}, "ASIGNADA", "asignar"),
    "EVALUACION": ({"ASIGNADA"}, "EN_GESTION", "evaluar"),
    "SEGUIMIENTO": ({"EN_GESTION"}, "EN_GESTION", "registrar seguimiento en"),
    "RESPUESTA": ({"EN_GESTION"}, "FINALIZADA", "finalizar"),
    "CIERRE": ({"RECIBIDA", "ASIGNADA", "EN_GESTION"}, "CERRADA", "cerrar"),
}


def validar_transicion(accion: str, estado_actual: str) -> str:
    """Devuelve el estado nuevo o responde 409 si la transición no está permitida."""
    desde, hacia, verbo = TRANSICIONES[accion]
    if estado_actual in ESTADOS_FINALES:
        raise HTTPException(409, f"La solicitud está {ESTADOS[estado_actual].lower()} y no admite más acciones")
    if estado_actual not in desde:
        raise HTTPException(409, f"No se puede {verbo} una solicitud en estado {ESTADOS[estado_actual]}")
    return hacia


def generar_radicado(db: sqlite3.Connection) -> str:
    """Número aleatorio de 8 dígitos, único (SUP-02: evita adivinar radicados ajenos)."""
    while True:
        radicado = str(secrets.randbelow(90_000_000) + 10_000_000)
        if db.execute("SELECT 1 FROM solicitudes WHERE radicado = ?", (radicado,)).fetchone() is None:
            return radicado


def registrar_accion(db, solicitud_id, usuario_id, tipo, descripcion, anterior, nuevo, fecha=None) -> None:
    """RN-09: cada acción queda en el historial."""
    db.execute(
        """INSERT INTO acciones (solicitud_id, usuario_id, tipo_accion, descripcion, estado_anterior, estado_nuevo, fecha)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (solicitud_id, usuario_id, tipo, descripcion, anterior, nuevo, fecha or ahora()),
    )


def obtener_solicitud(db: sqlite3.Connection, solicitud_id: int) -> sqlite3.Row:
    fila = db.execute("SELECT * FROM solicitudes WHERE id = ?", (solicitud_id,)).fetchone()
    if fila is None:
        raise HTTPException(404, "Solicitud no encontrada")
    return fila


def verificar_acceso(solicitud: sqlite3.Row, usuario: dict) -> None:
    """RN-11: el encargado solo accede a las solicitudes que tiene asignadas."""
    if usuario["rol"] == "ENCARGADO" and solicitud["encargado_id"] != usuario["id"]:
        raise HTTPException(403, "No tiene permisos sobre esta solicitud: está asignada a otro encargado")


def historial(db: sqlite3.Connection, solicitud_id: int) -> list[dict]:
    filas = db.execute(
        """SELECT a.id, a.tipo_accion, a.descripcion, a.estado_anterior, a.estado_nuevo, a.fecha,
                  u.nombre AS responsable, u.rol AS rol_responsable
           FROM acciones a LEFT JOIN usuarios u ON u.id = a.usuario_id
           WHERE a.solicitud_id = ? ORDER BY a.fecha, a.id""",
        (solicitud_id,),
    ).fetchall()
    return [
        {
            "id": f["id"],
            "fecha": f["fecha"],
            "accion": f["tipo_accion"],
            "accion_etiqueta": ACCIONES[f["tipo_accion"]],
            "descripcion": f["descripcion"],
            "estado_anterior": f["estado_anterior"],
            "estado_nuevo": f["estado_nuevo"],
            "responsable": f["responsable"] or "Solicitante",
        }
        for f in filas
    ]


def detalle(db: sqlite3.Connection, solicitud_id: int) -> dict:
    """Detalle completo para el personal autorizado."""
    f = db.execute(
        """SELECT s.*, t.nombre AS tipo, so.nombre AS sol_nombre, so.cedula, so.direccion, so.telefono, so.correo,
                  u.nombre AS encargado_nombre
           FROM solicitudes s
           JOIN tipos_servicio t ON t.id = s.tipo_id
           JOIN solicitantes so ON so.id = s.solicitante_id
           LEFT JOIN usuarios u ON u.id = s.encargado_id
           WHERE s.id = ?""",
        (solicitud_id,),
    ).fetchone()
    return {
        "id": f["id"],
        "radicado": f["radicado"],
        "estado": f["estado"],
        "estado_etiqueta": ESTADOS[f["estado"]],
        "tipo_id": f["tipo_id"],
        "tipo": f["tipo"],
        "asunto": f["asunto"],
        "descripcion": f["descripcion"],
        "solicitante": {
            "nombre": f["sol_nombre"],
            "cedula": f["cedula"],
            "direccion": f["direccion"],
            "telefono": f["telefono"],
            "correo": f["correo"],
        },
        "encargado": {"id": f["encargado_id"], "nombre": f["encargado_nombre"]} if f["encargado_id"] else None,
        "respuesta": f["respuesta"],
        "motivo_cierre": f["motivo_cierre"],
        "fecha_creacion": f["fecha_creacion"],
        "fecha_actualizacion": f["fecha_actualizacion"],
        "fecha_cierre": f["fecha_cierre"],
        "historial": historial(db, solicitud_id),
    }


def enmascarar_nombre(nombre: str) -> str:
    """'María Fernanda López' -> 'María F. L.' (RN-12)."""
    partes = nombre.split()
    return " ".join([partes[0]] + [p[0] + "." for p in partes[1:]])


def vista_publica(db: sqlite3.Connection, solicitud_id: int) -> dict:
    """Vista para el solicitante: sin cédula, dirección, teléfono ni correo (RNF-03)."""
    d = detalle(db, solicitud_id)
    return {
        "radicado": d["radicado"],
        "solicitante": enmascarar_nombre(d["solicitante"]["nombre"]),
        "tipo": d["tipo"],
        "asunto": d["asunto"],
        "descripcion": d["descripcion"],
        "estado": d["estado"],
        "estado_etiqueta": d["estado_etiqueta"],
        "respuesta": d["respuesta"],
        "motivo_cierre": d["motivo_cierre"],
        "fecha_creacion": d["fecha_creacion"],
        "fecha_actualizacion": d["fecha_actualizacion"],
        "fecha_cierre": d["fecha_cierre"],
        "historial": [
            {k: h[k] for k in ("fecha", "accion", "accion_etiqueta", "descripcion", "estado_nuevo")}
            for h in d["historial"]
        ],
    }


def aplicar_accion(db, solicitud, usuario, accion, descripcion, **campos) -> None:
    """Cambia el estado y registra la acción en el historial en una sola transacción (RNF-05)."""
    estado_nuevo = validar_transicion(accion, solicitud["estado"])
    momento = ahora()
    cambios = {"estado": estado_nuevo, "fecha_actualizacion": momento, **campos}
    if estado_nuevo in ESTADOS_FINALES:
        cambios["fecha_cierre"] = momento
    asignaciones = ", ".join(f"{k} = ?" for k in cambios)
    with db:  # transacción: o se guarda todo o no se guarda nada
        # "AND estado = ?" evita que dos acciones simultáneas (p. ej. doble clic) cambien el
        # mismo estado: si otra petición ya lo cambió, no se actualiza nada y se responde 409.
        cursor = db.execute(
            f"UPDATE solicitudes SET {asignaciones} WHERE id = ? AND estado = ?",
            (*cambios.values(), solicitud["id"], solicitud["estado"]),
        )
        if cursor.rowcount == 0:
            raise HTTPException(409, "La solicitud cambió de estado mientras se procesaba la acción. Actualice e intente de nuevo")
        registrar_accion(db, solicitud["id"], usuario["id"], accion, descripcion, solicitud["estado"], estado_nuevo, momento)
