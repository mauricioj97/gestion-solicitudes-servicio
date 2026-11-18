"""Datos iniciales FICTICIOS.

Uso (desde la carpeta backend, con el entorno virtual activo):
    python -m app.seed               -> crea tablas, tipos y usuarios si no existen
    python -m app.seed --demo        -> además carga solicitudes de ejemplo
    python -m app.seed --reset --demo -> borra la base de datos y la crea de nuevo con ejemplos

Credenciales de prueba (solo para desarrollo y demostración, no son datos reales):
    coordinacion / Coordina2026!   -> rol COORDINADOR
    encargado1   / Atencion2026!   -> rol ENCARGADO
    encargado2   / Atencion2026!   -> rol ENCARGADO
"""
import argparse
from datetime import datetime, timedelta

from .config import DB_PATH
from .database import conectar, inicializar_bd
from .security import hash_password

USUARIOS_BASE = [
    ("Laura Gómez", "coordinacion", "Coordina2026!", "COORDINADOR"),
    ("Carlos Pérez", "encargado1", "Atencion2026!", "ENCARGADO"),
    ("Ana Martínez", "encargado2", "Atencion2026!", "ENCARGADO"),
]


def crear_usuarios_base(conn) -> None:
    for nombre, usuario, contrasena, rol in USUARIOS_BASE:
        conn.execute(
            "INSERT OR IGNORE INTO usuarios (nombre, usuario, password_hash, rol) VALUES (?, ?, ?, ?)",
            (nombre, usuario, hash_password(contrasena), rol),
        )


# Datos 100 % ficticios (cédulas 10000000xx, teléfonos 30000000xx, dominio ejemplo.com).
# (radicado, nombre, cédula, dirección, teléfono, correo, tipo_id, asunto, descripción, días atrás, pasos)
# Cada paso: (horas después de radicar, acción, usuario, descripción)
SOLICITUDES_DEMO = [
    ("51842093", "María Fernanda López", "1000000001", "Calle 18 # 25-40, Pasto", "3000000001",
     "maria.lopez@ejemplo.com", 1, "Certificado de residencia",
     "Solicito un certificado de residencia para presentarlo en mi trabajo.", 6,
     [(1, "ASIGNACION", "coordinacion", "Asignada a Carlos Pérez"),
      (3, "EVALUACION", "encargado1", "Solicitud revisada: la información está completa y procede."),
      (24, "SEGUIMIENTO", "encargado1", "Se verificó la dirección en la base de datos de la organización."),
      (48, "RESPUESTA", "encargado1", "Su certificado fue expedido. Puede reclamarlo en la sede principal de lunes a viernes.")]),
    ("73019458", "Jorge Andrés Rosero", "1000000002", "Carrera 27 # 12-08, Pasto", "3000000002",
     "jorge.rosero@ejemplo.com", 2, "Orientación sobre convocatoria",
     "Necesito orientación sobre los requisitos de la convocatoria de becas.", 5,
     [(2, "ASIGNACION", "coordinacion", "Asignada a Ana Martínez"),
      (4, "EVALUACION", "encargado2", "Se revisó la consulta; corresponde a orientación general."),
      (20, "RESPUESTA", "encargado2", "Los requisitos son: documento de identidad, certificado de notas y carta de motivación.")]),
    ("64250187", "María Fernanda López", "1000000001", "Calle 18 # 25-40, Pasto", "3000000001",
     "maria.lopez@ejemplo.com", 1, "Certificado de residencia (repetida)",
     "Solicito nuevamente el certificado de residencia para mi trabajo.", 5,
     [(5, "CIERRE", "coordinacion", "Solicitud duplicada: ya existe el radicado 51842093 con la misma petición.")]),
    ("38571920", "Diana Carolina Benavides", "1000000003", "Avenida Panamericana # 5-60, Pasto", "3000000003",
     "diana.benavides@ejemplo.com", 4, "Mantenimiento de equipo",
     "El equipo asignado a mi oficina no enciende desde ayer y necesito soporte técnico.", 3,
     [(1, "ASIGNACION", "coordinacion", "Asignada a Carlos Pérez"),
      (2, "EVALUACION", "encargado1", "Se confirma la falla; se programa visita técnica."),
      (26, "SEGUIMIENTO", "encargado1", "Visita realizada: se requiere cambiar la fuente de poder.")]),
    ("29468315", "Luis Eduardo Paz", "1000000004", "Calle 20 # 30-15, Pasto", "3000000004",
     "luis.paz@ejemplo.com", 3, "Corrección de datos personales",
     "Mi apellido aparece mal escrito en el registro administrativo y necesito corregirlo.", 2,
     [(3, "ASIGNACION", "coordinacion", "Asignada a Ana Martínez"),
      (5, "EVALUACION", "encargado2", "Se solicitó copia del documento de identidad para verificar.")]),
    ("85130642", "Sandra Milena Ortiz", "1000000005", "Barrio Las Cuadras, Pasto", "3000000005",
     "sandra.ortiz@ejemplo.com", 2, "Información de horarios",
     "Quisiera conocer los horarios de atención de la oficina de servicios.", 1,
     [(2, "ASIGNACION", "coordinacion", "Asignada a Carlos Pérez")]),
    ("47702951", "Andrés Felipe Erazo", "1000000006", "Carrera 40 # 18-22, Pasto", "3000000006",
     "andres.erazo@ejemplo.com", 3, "Constancia de vinculación",
     "Requiero una constancia de mi vinculación con la organización.", 1, []),
    ("92614378", "Paola Andrea Muñoz", "1000000007", "Calle 12 # 8-31, Pasto", "3000000007",
     "paola.munoz@ejemplo.com", 4, "Instalación de software",
     "Solicito la instalación del programa de contabilidad en el equipo de mi área.", 0, []),
]

ESTADO_RESULTANTE = {
    "ASIGNACION": "ASIGNADA", "EVALUACION": "EN_GESTION", "SEGUIMIENTO": "EN_GESTION",
    "RESPUESTA": "FINALIZADA", "CIERRE": "CERRADA",
}


def cargar_demo(conn) -> None:
    ids = {f["usuario"]: f["id"] for f in conn.execute("SELECT id, usuario FROM usuarios")}
    for (radicado, nombre, cedula, direccion, telefono, correo, tipo_id, asunto, descripcion, dias, pasos) in SOLICITUDES_DEMO:
        if conn.execute("SELECT 1 FROM solicitudes WHERE radicado = ?", (radicado,)).fetchone():
            continue
        inicio = (datetime.now() - timedelta(days=dias)).replace(hour=8, minute=30, second=0)
        fmt = lambda d: d.strftime("%Y-%m-%d %H:%M:%S")  # noqa: E731
        solicitante_id = conn.execute(
            "INSERT INTO solicitantes (cedula, nombre, direccion, telefono, correo) VALUES (?, ?, ?, ?, ?)",
            (cedula, nombre, direccion, telefono, correo),
        ).lastrowid
        sid = conn.execute(
            """INSERT INTO solicitudes (radicado, solicitante_id, tipo_id, asunto, descripcion, estado,
                                        fecha_creacion, fecha_actualizacion)
               VALUES (?, ?, ?, ?, ?, 'RECIBIDA', ?, ?)""",
            (radicado, solicitante_id, tipo_id, asunto, descripcion, fmt(inicio), fmt(inicio)),
        ).lastrowid
        conn.execute(
            """INSERT INTO acciones (solicitud_id, usuario_id, tipo_accion, descripcion, estado_anterior, estado_nuevo, fecha)
               VALUES (?, NULL, 'REGISTRO', 'Solicitud radicada por el solicitante', NULL, 'RECIBIDA', ?)""",
            (sid, fmt(inicio)),
        )
        estado = "RECIBIDA"
        for horas, accion, usuario, texto in pasos:
            momento = fmt(inicio + timedelta(hours=horas))
            nuevo = ESTADO_RESULTANTE[accion]
            conn.execute(
                """INSERT INTO acciones (solicitud_id, usuario_id, tipo_accion, descripcion, estado_anterior, estado_nuevo, fecha)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (sid, ids[usuario], accion, texto, estado, nuevo, momento),
            )
            cambios = {"estado": nuevo, "fecha_actualizacion": momento}
            if accion == "ASIGNACION":
                cambios["encargado_id"] = ids["encargado1" if "Carlos" in texto else "encargado2"]
            if accion == "RESPUESTA":
                cambios.update(respuesta=texto, fecha_cierre=momento)
            if accion == "CIERRE":
                cambios.update(motivo_cierre=texto, fecha_cierre=momento)
            conn.execute(
                f"UPDATE solicitudes SET {', '.join(f'{k} = ?' for k in cambios)} WHERE id = ?",
                (*cambios.values(), sid),
            )
            estado = nuevo


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepara la base de datos con datos ficticios")
    parser.add_argument("--reset", action="store_true", help="borra la base de datos actual")
    parser.add_argument("--demo", action="store_true", help="carga solicitudes de ejemplo")
    args = parser.parse_args()

    if args.reset and DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Base de datos eliminada: {DB_PATH}")
    inicializar_bd()
    if args.demo:
        conn = conectar()
        with conn:
            cargar_demo(conn)
        conn.close()
        print("Solicitudes de ejemplo cargadas.")
    print(f"Base de datos lista: {DB_PATH}")


if __name__ == "__main__":
    main()
