"""Ejecuta las pruebas funcionales de la API contra el servidor en ejecución y guarda la evidencia.

No es obligatorio (las pruebas también se pueden hacer a mano en http://localhost:8000/docs);
este script solo repite los mismos pasos de docs/pruebas.md y deja el registro de cada
petición y respuesta en evidencias/resultados_pruebas_api.md.

Uso (con el servidor encendido y la base de datos de demostración recién cargada):
    python pruebas/ejecutar_pruebas.py

Para usar otro puerto, definir la variable PRUEBAS_URL, por ejemplo (PowerShell):
    $env:PRUEBAS_URL = "http://localhost:8010"; python pruebas/ejecutar_pruebas.py
"""
import json
import os
import sqlite3
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = os.environ.get("PRUEBAS_URL", "http://localhost:8000").rstrip("/")
RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "evidencias" / "resultados_pruebas_api.md"
DB = RAIZ / "backend" / "data" / "solicitudes.db"

# Credenciales FICTICIAS de demostración (definidas en backend/app/seed.py)
COORDINACION = {"usuario": "coordinacion", "contrasena": "Coordina2026!"}
ENCARGADO1 = {"usuario": "encargado1", "contrasena": "Atencion2026!"}
ENCARGADO2 = {"usuario": "encargado2", "contrasena": "Atencion2026!"}

registro: list[str] = []
resultados: list[tuple] = []


def peticion(metodo, ruta, cuerpo=None, token=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(BASE + ruta, data=datos, method=metodo)
    if datos:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as r:
            texto = r.read().decode()
            return r.status, json.loads(texto) if texto else None
    except urllib.error.HTTPError as e:
        texto = e.read().decode()
        return e.code, json.loads(texto) if texto else None


def recortar(obj, limite=1500):
    texto = json.dumps(obj, ensure_ascii=False, indent=2)
    return texto if len(texto) <= limite else texto[:limite] + "\n  ... (respuesta recortada)"


def paso(id_prueba, nombre, metodo, ruta, cuerpo=None, token=None, esperado=200, verificar=None, rol="-"):
    codigo, respuesta = peticion(metodo, ruta, cuerpo, token)
    ok = codigo == esperado and (verificar is None or verificar(respuesta))
    resultados.append((id_prueba, nombre, f"{metodo} {ruta}", rol, esperado, codigo, "Aprobada" if ok else "FALLIDA"))
    registro.append(f"### {id_prueba} — {nombre}\n")
    registro.append(f"- **Actor:** {rol}\n- **Petición:** `{metodo} {ruta}`\n- **Código esperado:** {esperado} · **Obtenido:** {codigo} · **Resultado:** {'✅ Aprobada' if ok else '❌ FALLIDA'}\n")
    if cuerpo is not None:
        cuerpo_mostrado = {k: ("********" if k == "contrasena" else v) for k, v in cuerpo.items()}
        registro.append(f"**Cuerpo enviado:**\n```json\n{recortar(cuerpo_mostrado)}\n```\n")
    registro.append(f"**Respuesta:**\n```json\n{recortar(respuesta)}\n```\n")
    return respuesta


def login(cred):
    return peticion("POST", "/api/auth/login", cred)[1]["token"]


def main():
    t_coord, t_enc1, t_enc2 = login(COORDINACION), login(ENCARGADO1), login(ENCARGADO2)
    nueva = {
        "nombre": "Camila Andrea Rosales", "cedula": "1000000010", "direccion": "Carrera 22 # 14-30, Pasto",
        "telefono": "3000000010", "correo": "camila.rosales@ejemplo.com", "tipo_id": 3,
        "asunto": "Actualización de datos de contacto",
        "descripcion": "Solicito actualizar mi número de teléfono y correo en los registros de la organización.",
    }

    # PF-01 Registro válido
    r = paso("PF-01", "Registro válido de solicitud", "POST", "/api/solicitudes", nueva, esperado=201,
             verificar=lambda r: r["estado"] == "RECIBIDA" and len(r["radicado"]) == 8, rol="Solicitante (sin cuenta)")
    radicado = r["radicado"]
    con = sqlite3.connect(DB)
    sid = con.execute("SELECT id FROM solicitudes WHERE radicado = ?", (radicado,)).fetchone()[0]
    total_antes = con.execute("SELECT COUNT(*) FROM solicitudes").fetchone()[0]

    # PF-02 Registro inválido (no debe guardar nada)
    invalida = {**nueva, "nombre": "Ca", "cedula": "12AB", "correo": "correo-sin-arroba", "descripcion": "corta"}
    paso("PF-02", "Registro con datos inválidos", "POST", "/api/solicitudes", invalida, esperado=422,
         verificar=lambda r: len(r["errores"]) == 4, rol="Solicitante (sin cuenta)")
    total_despues = con.execute("SELECT COUNT(*) FROM solicitudes").fetchone()[0]
    registro.append(f"> Verificación en base de datos: solicitudes antes = {total_antes}, después = {total_despues} → "
                    f"{'no se guardó el registro inválido ✅' if total_antes == total_despues else 'SE GUARDÓ ❌'}\n")
    paso("PF-02b", "Registro con tipo de servicio inexistente", "POST", "/api/solicitudes", {**nueva, "tipo_id": 99},
         esperado=422, rol="Solicitante (sin cuenta)")

    # PF-03 / PF-04 Consulta
    paso("PF-03", "Consulta de solicitud existente", "GET", f"/api/solicitudes/consulta/{radicado}",
         verificar=lambda r: r["radicado"] == radicado and "cedula" not in json.dumps(r), rol="Solicitante (sin cuenta)")
    paso("PF-04", "Consulta de solicitud inexistente", "GET", "/api/solicitudes/consulta/00000000", esperado=404,
         rol="Solicitante (sin cuenta)")
    paso("PF-04b", "Detalle interno de solicitud inexistente", "GET", "/api/gestion/solicitudes/99999", token=t_coord,
         esperado=404, rol="Coordinación")

    # Autenticación
    paso("PF-13", "Inicio de sesión con contraseña incorrecta", "POST", "/api/auth/login",
         {"usuario": "coordinacion", "contrasena": "incorrecta"}, esperado=401, rol="Personal")
    paso("PF-14", "Gestión sin iniciar sesión", "GET", "/api/gestion/solicitudes", esperado=401, rol="Anónimo")

    # PF-05 / PF-06 Gestión autorizada y no autorizada
    paso("PF-05", "Asignación por coordinación (actor autorizado)", "POST", f"/api/gestion/solicitudes/{sid}/asignar",
         {"encargado_id": 2}, token=t_coord, verificar=lambda r: r["estado"] == "ASIGNADA", rol="Coordinación")
    paso("PF-06", "Encargado intenta asignar (actor no autorizado)", "POST", f"/api/gestion/solicitudes/{sid}/asignar",
         {"encargado_id": 3}, token=t_enc1, esperado=403, rol="Encargado 1")
    paso("PF-06b", "Encargado intenta gestionar una solicitud de otro", "POST", f"/api/gestion/solicitudes/{sid}/evaluar",
         {"observacion": "Intento de evaluar una solicitud ajena."}, token=t_enc2, esperado=403, rol="Encargado 2")
    paso("PF-06c", "Encargado intenta ver el resumen consolidado", "GET", "/api/reportes/resumen", token=t_enc1,
         esperado=403, rol="Encargado 1")

    # Reglas de negocio del flujo
    paso("PF-15", "Finalizar sin haber evaluado (transición inválida)", "POST", f"/api/gestion/solicitudes/{sid}/finalizar",
         {"respuesta": "Respuesta antes de tiempo para probar la regla."}, token=t_enc1, esperado=409, rol="Encargado 1")
    paso("PF-05b", "Evaluación por el encargado asignado", "POST", f"/api/gestion/solicitudes/{sid}/evaluar",
         {"observacion": "Se revisó la solicitud: los datos nuevos están completos."}, token=t_enc1,
         verificar=lambda r: r["estado"] == "EN_GESTION", rol="Encargado 1")
    paso("PF-05c", "Registro de seguimiento", "POST", f"/api/gestion/solicitudes/{sid}/seguimiento",
         {"nota": "Se actualizó el teléfono; falta confirmar el correo."}, token=t_enc1,
         verificar=lambda r: r["estado"] == "EN_GESTION", rol="Encargado 1")

    # PF-07 Estado coherente
    paso("PF-07", "Consulta de estado durante la atención", "GET", f"/api/solicitudes/consulta/{radicado}",
         verificar=lambda r: r["estado"] == "EN_GESTION", rol="Solicitante (sin cuenta)")
    paso("PF-16", "Finalizar con respuesta vacía", "POST", f"/api/gestion/solicitudes/{sid}/finalizar",
         {"respuesta": "  "}, token=t_enc1, esperado=422, rol="Encargado 1")

    # PF-09 Finalización
    paso("PF-09", "Responder y finalizar el caso", "POST", f"/api/gestion/solicitudes/{sid}/finalizar",
         {"respuesta": "Sus datos de contacto fueron actualizados correctamente en nuestros registros."},
         token=t_enc1, verificar=lambda r: r["estado"] == "FINALIZADA" and r["respuesta"], rol="Encargado 1")
    paso("PF-09b", "El solicitante consulta la respuesta final", "GET", f"/api/solicitudes/consulta/{radicado}",
         verificar=lambda r: r["estado"] == "FINALIZADA" and r["respuesta"], rol="Solicitante (sin cuenta)")
    paso("PF-17", "Acción sobre solicitud finalizada", "POST", f"/api/gestion/solicitudes/{sid}/cerrar",
         {"motivo": "Intento de cerrar una solicitud ya finalizada."}, token=t_coord, esperado=409, rol="Coordinación")

    # PF-08 Historial
    paso("PF-08", "Historial de atención", "GET", f"/api/gestion/solicitudes/{sid}/historial", token=t_coord,
         verificar=lambda r: [a["accion"] for a in r] == ["REGISTRO", "ASIGNACION", "EVALUACION", "SEGUIMIENTO", "RESPUESTA"],
         rol="Coordinación")

    # Cierre con motivo
    otra = peticion("POST", "/api/solicitudes", {**nueva, "asunto": "Solicitud para cerrar"})[1]
    otra_id = con.execute("SELECT id FROM solicitudes WHERE radicado = ?", (otra["radicado"],)).fetchone()[0]
    paso("PF-18", "Cerrar sin motivo", "POST", f"/api/gestion/solicitudes/{otra_id}/cerrar", {"motivo": ""},
         token=t_coord, esperado=422, rol="Coordinación")
    paso("PF-19", "Cerrar con motivo", "POST", f"/api/gestion/solicitudes/{otra_id}/cerrar",
         {"motivo": "El solicitante desistió de la solicitud por vía telefónica."}, token=t_coord,
         verificar=lambda r: r["estado"] == "CERRADA" and r["motivo_cierre"], rol="Coordinación")

    # PF-20 Una radicación con una cédula ya registrada no altera los datos de otra solicitud (RN-13)
    original = con.execute(
        """SELECT so.nombre, so.telefono FROM solicitudes s JOIN solicitantes so ON so.id = s.solicitante_id
           WHERE s.radicado = '51842093'"""
    ).fetchone()
    suplantacion = {**nueva, "nombre": "Persona Diferente", "cedula": "1000000001", "telefono": "3000000099",
                    "asunto": "Radicación con cédula repetida"}
    paso("PF-20", "Radicar con una cédula ya registrada no modifica solicitudes anteriores", "POST", "/api/solicitudes",
         suplantacion, esperado=201, rol="Solicitante (sin cuenta)")
    despues = con.execute(
        """SELECT so.nombre, so.telefono FROM solicitudes s JOIN solicitantes so ON so.id = s.solicitante_id
           WHERE s.radicado = '51842093'"""
    ).fetchone()
    intacto = original is not None and original == despues
    registro.append(f"> Verificación en base de datos: datos del solicitante del radicado 51842093 antes = {original}, "
                    f"después = {despues} → {'sin cambios ✅' if intacto else 'MODIFICADOS ❌'}\n")
    if not intacto:
        resultados[-1] = resultados[-1][:-1] + ("FALLIDA",)

    # PF-10 Consolidado
    paso("PF-10", "Consulta consolidada", "GET", "/api/reportes/resumen", token=t_coord,
         verificar=lambda r: r["total"] >= 2 and len(r["por_estado"]) == 5, rol="Coordinación")

    # PF-11 Integridad
    huerfanas = con.execute(
        """SELECT COUNT(*) FROM acciones a LEFT JOIN solicitudes s ON s.id = a.solicitud_id WHERE s.id IS NULL"""
    ).fetchone()[0]
    sin_registro = con.execute(
        """SELECT COUNT(*) FROM solicitudes s WHERE NOT EXISTS
           (SELECT 1 FROM acciones a WHERE a.solicitud_id = s.id AND a.tipo_accion = 'REGISTRO')"""
    ).fetchone()[0]
    try:
        con.execute("PRAGMA foreign_keys = ON")
        con.execute("INSERT INTO acciones (solicitud_id, tipo_accion, descripcion, estado_nuevo, fecha) "
                    "VALUES (999999, 'SEGUIMIENTO', 'x', 'EN_GESTION', '2026-01-01')")
        fk = "❌ la base de datos aceptó una acción sin solicitud"
        con.rollback()
    except sqlite3.IntegrityError as e:
        fk = f"✅ la base de datos rechazó la acción sin solicitud ({e})"
    ok11 = huerfanas == 0 and sin_registro == 0 and fk.startswith("✅")
    resultados.append(("PF-11", "Persistencia e integridad de relaciones", "SQL sobre la base de datos", "-", "-", "-",
                       "Aprobada" if ok11 else "FALLIDA"))
    registro.append("### PF-11 — Persistencia e integridad de relaciones\n")
    registro.append(f"- Acciones sin solicitud asociada: **{huerfanas}**\n- Solicitudes sin acción de registro: **{sin_registro}**\n"
                    f"- Intento de insertar una acción con `solicitud_id` inexistente: {fk}\n"
                    f"- **Resultado:** {'✅ Aprobada' if ok11 else '❌ FALLIDA'}\n")
    con.close()

    aprobadas = sum(1 for r in resultados if r[-1] == "Aprobada")
    tabla = ["| Prueba | Descripción | Petición | Actor | Esperado | Obtenido | Estado |", "|---|---|---|---|---|---|---|"]
    tabla += [f"| {a} | {b} | `{c}` | {d} | {e} | {f} | {g} |" for a, b, c, d, e, f, g in resultados]
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(
        "# Evidencia — Ejecución de pruebas funcionales de la API\n\n"
        f"- **Fecha de ejecución:** {datetime.now():%Y-%m-%d %H:%M}\n- **Servidor:** {BASE}\n"
        f"- **Resultado:** {aprobadas} de {len(resultados)} pruebas aprobadas\n"
        f"- **Solicitud usada en el flujo completo:** radicado `{radicado}`\n\n"
        "## Resumen\n\n" + "\n".join(tabla) + "\n\n## Detalle de cada petición y respuesta\n\n" + "\n".join(registro),
        encoding="utf-8",
    )
    print(f"{aprobadas}/{len(resultados)} pruebas aprobadas. Evidencia: {SALIDA}")
    for r in resultados:
        if r[-1] != "Aprobada":
            print("  FALLIDA:", r)


if __name__ == "__main__":
    main()
