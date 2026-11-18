# Pruebas Funcionales de API, Reglas de Negocio e Integración

## 1. Estrategia

- **Tipo de prueba:** funcional, de caja negra, sobre la aplicación en ejecución.
- **Herramientas:**
  - **Swagger UI** (`http://localhost:8000/docs`): documentación interactiva de la API, para enviar peticiones y ver código HTTP y respuesta.
  - **Navegador web:** pruebas de integración interfaz → API → base de datos.
  - **Script de apoyo** [`pruebas/ejecutar_pruebas.py`](../pruebas/ejecutar_pruebas.py), opcional: repite las mismas peticiones y guarda el registro completo de peticiones y respuestas en [`evidencias/resultados_pruebas_api.md`](../evidencias/resultados_pruebas_api.md). No reemplaza la ejecución manual; solo facilita la reproducción.
- **Datos:** ficticios, cargados con `python -m app.seed --reset --demo`.
- **Usuarios de prueba:** `coordinacion` (Coordinación), `encargado1` (Carlos Pérez, id 2) y `encargado2` (Ana Martínez, id 3). Las contraseñas están en el README, sección 5.

### Cómo enviar una petición con sesión en Swagger
1. Abrir `http://localhost:8000/docs`.
2. Ejecutar `POST /api/auth/login` con el usuario de prueba y copiar el valor de `token`.
3. Pulsar **Authorize** (arriba a la derecha), pegar el token y aceptar.
4. Ejecutar el endpoint que se va a probar ("Try it out" → "Execute").

---

## 2. Resumen de resultados

| ID | Prueba (enunciado #) | Requisito | Método y ruta | Código esperado | Código obtenido | Estado |
|---|---|---|---|---|---|---|
| PF-01 | Registro válido de solicitud (1) | RF-01 · CA-01 | `POST /api/solicitudes` | 201 | 201 | ✅ Aprobada |
| PF-02 | Registro con datos inválidos (2) | RF-02 · CA-01 | `POST /api/solicitudes` | 422 | 422 | ✅ Aprobada |
| PF-02b | Tipo de servicio inexistente | RF-02 | `POST /api/solicitudes` | 422 | 422 | ✅ Aprobada |
| PF-03 | Consulta de solicitud existente (3) | RF-03 · CA-03 | `GET /api/solicitudes/consulta/{radicado}` | 200 | 200 | ✅ Aprobada |
| PF-04 | Consulta de solicitud inexistente (4) | RF-03 | `GET /api/solicitudes/consulta/00000000` | 404 | 404 | ✅ Aprobada |
| PF-04b | Detalle interno inexistente | RF-06 | `GET /api/gestion/solicitudes/99999` | 404 | 404 | ✅ Aprobada |
| PF-05 | Gestión por actor autorizado (5) | RF-07 · CA-02 | `POST /api/gestion/solicitudes/{id}/asignar` | 200 | 200 | ✅ Aprobada |
| PF-05b | Evaluación por encargado asignado | RF-08 · CA-02 | `POST .../{id}/evaluar` | 200 | 200 | ✅ Aprobada |
| PF-05c | Registro de seguimiento | RF-09 · CA-04 | `POST .../{id}/seguimiento` | 200 | 200 | ✅ Aprobada |
| PF-06 | Gestión por actor no autorizado (6) | RN-03 · CA-02 | `POST .../{id}/asignar` (con token de encargado) | 403 | 403 | ✅ Aprobada |
| PF-06b | Encargado gestiona solicitud ajena | RN-04 | `POST .../{id}/evaluar` (encargado 2) | 403 | 403 | ✅ Aprobada |
| PF-06c | Encargado consulta resumen | RF-14 | `GET /api/reportes/resumen` (encargado) | 403 | 403 | ✅ Aprobada |
| PF-07 | Consulta de estado (7) | RF-03 · CA-03 | `GET /api/solicitudes/consulta/{radicado}` | 200 · EN_GESTION | 200 · EN_GESTION | ✅ Aprobada |
| PF-08 | Historial de atención (8) | RF-12, RF-13 · CA-04 | `GET .../{id}/historial` | 200 · 5 acciones en orden | 200 · 5 acciones | ✅ Aprobada |
| PF-09 | Finalización del caso (9) | RF-10 · CA-05 | `POST .../{id}/finalizar` | 200 · FINALIZADA | 200 · FINALIZADA | ✅ Aprobada |
| PF-09b | El solicitante ve la respuesta final | RF-03 · CA-05 | `GET /api/solicitudes/consulta/{radicado}` | 200 · respuesta visible | 200 · respuesta visible | ✅ Aprobada |
| PF-10 | Consulta consolidada (10) | RF-14 · CA-06 | `GET /api/reportes/resumen` | 200 | 200 | ✅ Aprobada |
| PF-11 | Persistencia e integridad de relaciones (11) | RNF-05 | Consultas SQL sobre la BD | Sin huérfanos; FK rechaza referencia inválida | Cumple | ✅ Aprobada |
| PF-12 | Integración interfaz–API–BD (12) | RNF-01 · CA-01 a CA-06 | Flujo completo en el navegador | Flujo de principio a fin | Cumple | ✅ Aprobada |
| PF-13 | Login con contraseña incorrecta | RF-04 | `POST /api/auth/login` | 401 | 401 | ✅ Aprobada |
| PF-14 | Gestión sin sesión | RNF-02 | `GET /api/gestion/solicitudes` (sin token) | 401 | 401 | ✅ Aprobada |
| PF-15 | Finalizar sin evaluar (transición inválida) | RN-05 | `POST .../{id}/finalizar` en estado ASIGNADA | 409 | 409 | ✅ Aprobada |
| PF-16 | Finalizar con respuesta vacía | RN-06 | `POST .../{id}/finalizar` | 422 | 422 | ✅ Aprobada |
| PF-17 | Acción sobre solicitud finalizada | RN-08 | `POST .../{id}/cerrar` | 409 | 409 | ✅ Aprobada |
| PF-18 | Cerrar sin motivo | RN-07 | `POST .../{id}/cerrar` | 422 | 422 | ✅ Aprobada |
| PF-19 | Cerrar con motivo | RF-11 · CA-05 | `POST .../{id}/cerrar` | 200 · CERRADA | 200 · CERRADA | ✅ Aprobada |
| PF-20 | Radicar con una cédula ya registrada no altera solicitudes anteriores | RN-13 · RNF-05 | `POST /api/solicitudes` + verificación en BD | 201 · datos anteriores intactos | 201 · intactos | ✅ Aprobada |

**Resultado: 27 de 27 pruebas aprobadas** (26 ejecutadas por API y PF-12 en el navegador). Las 12 pruebas mínimas del enunciado están marcadas con su número entre paréntesis. El registro completo de cada petición y respuesta está en [`evidencias/resultados_pruebas_api.md`](../evidencias/resultados_pruebas_api.md).

---

## 3. Detalle de las pruebas mínimas del enunciado

**Preparación común:** servidor encendido (`python -m uvicorn app.main:app --port 8000`) y base de datos recién cargada con `python -m app.seed --reset --demo`. Esa base trae 8 solicitudes de ejemplo (ids 1 a 8), así que **la primera solicitud que se radique recibe el id 9**. Las pruebas se ejecutan en el orden de este documento, porque varias continúan el caso creado en PF-01.

Usuarios: `coordinacion` (Coordinación), `encargado1` (Carlos Pérez, id 2), `encargado2` (Ana Martínez, id 3). Para enviar el token en Swagger, ver la sección 1.

### PF-01 — Registro válido de solicitud (prueba mínima 1)

| Campo | Detalle |
|---|---|
| Identificador | PF-01 |
| Requisito asociado | RF-01, RN-01, RN-02 · CA-01 |
| Condiciones iniciales | Preparación común. Sin sesión (el solicitante no tiene cuenta). |
| Pasos | 1. En Swagger abrir `POST /api/solicitudes` → **Try it out**. 2. Pegar el cuerpo de "Datos de entrada". 3. **Execute**. 4. Anotar el `radicado` de la respuesta. |
| Datos de entrada | `{"nombre": "Camila Andrea Rosales", "cedula": "1000000010", "direccion": "Carrera 22 # 14-30, Pasto", "telefono": "3000000010", "correo": "camila.rosales@ejemplo.com", "tipo_id": 3, "asunto": "Actualización de datos de contacto", "descripcion": "Solicito actualizar mi número de teléfono y correo en los registros de la organización."}` |
| Resultado esperado | Código 201, `estado` = `RECIBIDA` y un `radicado` de 8 dígitos. La solicitud se puede recuperar (PF-03). |
| Resultado obtenido | 201, estado `RECIBIDA`, radicado de 8 dígitos generado (id interno 9). |
| Estado | ✅ Aprobada |
| Evidencia | [`resultados_pruebas_api.md`](../evidencias/resultados_pruebas_api.md) (PF-01) · `capturas/03-radicar-exito.png` |
| Método y código HTTP | `POST /api/solicitudes` → **201 Created** |

### PF-02 — Registro con datos inválidos (prueba mínima 2)

| Campo | Detalle |
|---|---|
| Identificador | PF-02 |
| Requisito asociado | RF-02, RN-01 · CA-01 |
| Condiciones iniciales | PF-01 ejecutada. Se conoce el total de solicitudes (9). |
| Pasos | 1. `POST /api/solicitudes` con los datos de entrada. 2. Revisar la lista de errores. 3. Verificar en la base de datos: `SELECT COUNT(*) FROM solicitudes;` (o en el panel de coordinación) que sigue habiendo 9. |
| Datos de entrada | Igual a PF-01, pero con `"nombre": "Ca"`, `"cedula": "12AB"`, `"correo": "correo-sin-arroba"`, `"descripcion": "corta"`. |
| Resultado esperado | Código 422 con `errores` para los 4 campos (nombre, cédula, correo, descripción) y mensajes en español. El total de solicitudes no cambia. |
| Resultado obtenido | 422 con 4 errores. Solicitudes antes = 9, después = 9: no se guardó nada. |
| Estado | ✅ Aprobada |
| Evidencia | `resultados_pruebas_api.md` (PF-02, incluye la verificación en BD) · `capturas/02-radicar-validacion.png` (misma validación en el navegador) |
| Método y código HTTP | `POST /api/solicitudes` → **422 Unprocessable Entity** |

### PF-03 — Consulta de solicitud existente (prueba mínima 3)

| Campo | Detalle |
|---|---|
| Identificador | PF-03 |
| Requisito asociado | RF-03, RN-12 · CA-03 |
| Condiciones iniciales | PF-01 ejecutada; se tiene su radicado. Sin sesión. |
| Pasos | 1. Abrir `GET /api/solicitudes/consulta/{radicado}` → **Try it out**. 2. Escribir el radicado de PF-01. 3. **Execute**. |
| Datos de entrada | `radicado` = el devuelto por PF-01 (en la ejecución registrada, ver la cabecera de `resultados_pruebas_api.md`). |
| Resultado esperado | Código 200 con el radicado, tipo, asunto, estado `RECIBIDA` e historial. El nombre aparece enmascarado y **no** aparecen cédula, dirección, teléfono ni correo. |
| Resultado obtenido | 200, datos de la solicitud correctos, nombre "Camila A. R." y sin datos sensibles. |
| Estado | ✅ Aprobada |
| Evidencia | `resultados_pruebas_api.md` (PF-03) · `capturas/04-consulta-recibida.png` |
| Método y código HTTP | `GET /api/solicitudes/consulta/{radicado}` → **200 OK** |

### PF-04 — Consulta de solicitud inexistente (prueba mínima 4)

| Campo | Detalle |
|---|---|
| Identificador | PF-04 |
| Requisito asociado | RF-03, RNF-04 |
| Condiciones iniciales | Preparación común. Sin sesión. |
| Pasos | `GET /api/solicitudes/consulta/{radicado}` con el radicado de entrada → **Execute**. |
| Datos de entrada | `radicado` = `00000000` (no existe). |
| Resultado esperado | Código 404 con `{"detalle": "Solicitud no encontrada. Verifique el número de radicado"}`. El servidor no se cae ni muestra detalles internos. |
| Resultado obtenido | 404 con el mensaje esperado. |
| Estado | ✅ Aprobada |
| Evidencia | `resultados_pruebas_api.md` (PF-04) |
| Método y código HTTP | `GET /api/solicitudes/consulta/00000000` → **404 Not Found** |

### PF-05 — Gestión por actor autorizado (prueba mínima 5)

| Campo | Detalle |
|---|---|
| Identificador | PF-05 |
| Requisito asociado | RF-07, RN-03, RN-09 · CA-02 |
| Condiciones iniciales | Solicitud id 9 (de PF-01) en estado `RECIBIDA`. Sesión de `coordinacion` autorizada en Swagger. |
| Pasos | 1. `POST /api/auth/login` como `coordinacion`, copiar el token y pulsar **Authorize**. 2. `POST /api/gestion/solicitudes/{id}/asignar` con id `9` y el cuerpo de entrada. 3. **Execute**. |
| Datos de entrada | `id` = 9 · cuerpo `{"encargado_id": 2}` (Carlos Pérez). |
| Resultado esperado | Código 200, `estado` = `ASIGNADA`, encargado Carlos Pérez y una acción `ASIGNACION` nueva en el historial. |
| Resultado obtenido | 200, estado `ASIGNADA`, encargado Carlos Pérez, acción registrada. |
| Estado | ✅ Aprobada |
| Evidencia | `resultados_pruebas_api.md` (PF-05) · `capturas/07-asignar.png` |
| Método y código HTTP | `POST /api/gestion/solicitudes/9/asignar` → **200 OK** |

### PF-06 — Gestión por actor no autorizado (prueba mínima 6)

| Campo | Detalle |
|---|---|
| Identificador | PF-06 (variantes PF-06b y PF-06c) |
| Requisito asociado | RN-03 · CA-02 (PF-06b: RN-04 · PF-06c: RF-14) |
| Condiciones iniciales | Solicitud id 9 en estado `ASIGNADA` (después de PF-05). Sesión de `encargado1` autorizada en Swagger. |
| Pasos | 1. Login como `encargado1`, **Authorize** con su token. 2. `POST /api/gestion/solicitudes/{id}/asignar` con id `9` y el cuerpo de entrada. 3. Verificar con `GET /api/gestion/solicitudes/9` (como coordinación) que el encargado sigue siendo Carlos Pérez. |
| Datos de entrada | `id` = 9 · cuerpo `{"encargado_id": 3}`. PF-06b: `encargado2` ejecuta `POST .../9/evaluar` con `{"observacion": "Intento de evaluar una solicitud ajena."}`. PF-06c: `encargado1` ejecuta `GET /api/reportes/resumen`. |
| Resultado esperado | Código 403 con "No tiene permisos para realizar esta acción". La solicitud no cambia. |
| Resultado obtenido | 403 en los tres casos; la solicitud conserva su estado y su encargado. |
| Estado | ✅ Aprobada |
| Evidencia | `resultados_pruebas_api.md` (PF-06, PF-06b, PF-06c) · `capturas/12-swagger-403.png` |
| Método y código HTTP | `POST /api/gestion/solicitudes/9/asignar` → **403 Forbidden** |

### PF-07 — Consulta de estado (prueba mínima 7)

| Campo | Detalle |
|---|---|
| Identificador | PF-07 |
| Requisito asociado | RF-03, RN-05 · CA-03 |
| Condiciones iniciales | Solicitud id 9 evaluada (PF-05b) y con un seguimiento (PF-05c) por `encargado1`. Sin sesión. |
| Pasos | 1. Como `encargado1`: `POST .../9/evaluar` con `{"observacion": "Se revisó la solicitud: los datos nuevos están completos."}` y `POST .../9/seguimiento` con `{"nota": "Se actualizó el teléfono; falta confirmar el correo."}`. 2. Sin sesión: `GET /api/solicitudes/consulta/{radicado}` con el radicado de PF-01. |
| Datos de entrada | `radicado` de PF-01. |
| Resultado esperado | Código 200 y `estado` = `EN_GESTION`, coherente con las acciones realizadas (Recibida → Asignada → En gestión). |
| Resultado obtenido | 200, estado `EN_GESTION`. |
| Estado | ✅ Aprobada |
| Evidencia | `resultados_pruebas_api.md` (PF-05b, PF-05c, PF-07) |
| Método y código HTTP | `GET /api/solicitudes/consulta/{radicado}` → **200 OK** |

### PF-08 — Historial de atención (prueba mínima 8)

| Campo | Detalle |
|---|---|
| Identificador | PF-08 |
| Requisito asociado | RF-12, RF-13, RN-09 · CA-04 |
| Condiciones iniciales | Solicitud id 9 finalizada (después de PF-09). Sesión de `coordinacion`. |
| Pasos | `GET /api/gestion/solicitudes/{id}/historial` con id `9` → **Execute**. |
| Datos de entrada | `id` = 9. |
| Resultado esperado | Código 200 con 5 acciones en orden: REGISTRO → ASIGNACION → EVALUACION → SEGUIMIENTO → RESPUESTA, cada una con fecha, responsable, estado anterior, estado nuevo y descripción. Todas pertenecen a la solicitud 9. |
| Resultado obtenido | 200 con las 5 acciones en el orden esperado. |
| Estado | ✅ Aprobada |
| Evidencia | `resultados_pruebas_api.md` (PF-08) · `capturas/09-detalle-historial.png` |
| Método y código HTTP | `GET /api/gestion/solicitudes/9/historial` → **200 OK** |

### PF-09 — Finalización del caso (prueba mínima 9)

| Campo | Detalle |
|---|---|
| Identificador | PF-09 (y PF-09b) |
| Requisito asociado | RF-10, RN-06 · CA-05 |
| Condiciones iniciales | Solicitud id 9 en estado `EN_GESTION` (después de PF-07). Sesión de `encargado1`. |
| Pasos | 1. `POST /api/gestion/solicitudes/{id}/finalizar` con id `9` y el cuerpo de entrada. 2. PF-09b: sin sesión, `GET /api/solicitudes/consulta/{radicado}` con el radicado de PF-01. |
| Datos de entrada | `id` = 9 · cuerpo `{"respuesta": "Sus datos de contacto fueron actualizados correctamente en nuestros registros."}` |
| Resultado esperado | Código 200 y `estado` = `FINALIZADA`. En la consulta pública aparece la respuesta. |
| Resultado obtenido | 200, estado `FINALIZADA`; la consulta pública (PF-09b, 200) muestra la respuesta. |
| Estado | ✅ Aprobada |
| Evidencia | `resultados_pruebas_api.md` (PF-09, PF-09b) · `capturas/10-consulta-finalizada.png` |
| Método y código HTTP | `POST /api/gestion/solicitudes/9/finalizar` → **200 OK** |

### PF-10 — Consulta consolidada (prueba mínima 10)

| Campo | Detalle |
|---|---|
| Identificador | PF-10 |
| Requisito asociado | RF-14 · CA-06 |
| Condiciones iniciales | Base con las 8 solicitudes de ejemplo y las creadas en las pruebas anteriores. Sesión de `coordinacion`. |
| Pasos | `GET /api/reportes/resumen` → **Execute**. |
| Datos de entrada | Ninguno (solo el token). |
| Resultado esperado | Código 200 con `total`, `pendientes`, `sin_asignar`, `finalizadas`, `cerradas`, `tiempo_promedio_atencion_horas` y los conteos `por_estado` (5 estados), `por_tipo` (4 tipos) y `por_encargado`. |
| Resultado obtenido | 200 con toda la información integrada de varias solicitudes. |
| Estado | ✅ Aprobada |
| Evidencia | `resultados_pruebas_api.md` (PF-10) · `capturas/11-resumen.png` |
| Método y código HTTP | `GET /api/reportes/resumen` → **200 OK** |

### PF-11 — Persistencia e integridad de relaciones (prueba mínima 11)

| Campo | Detalle |
|---|---|
| Identificador | PF-11 |
| Requisito asociado | RNF-05, RN-09 |
| Condiciones iniciales | Pruebas anteriores ejecutadas. Acceso al archivo `backend/data/solicitudes.db` (por ejemplo, con [DB Browser for SQLite](https://sqlitebrowser.org/) o con el script). |
| Pasos | Ejecutar las tres consultas de "Datos de entrada" sobre la base de datos. |
| Datos de entrada | 1. `SELECT COUNT(*) FROM acciones a LEFT JOIN solicitudes s ON s.id = a.solicitud_id WHERE s.id IS NULL;` 2. `SELECT COUNT(*) FROM solicitudes s WHERE NOT EXISTS (SELECT 1 FROM acciones a WHERE a.solicitud_id = s.id AND a.tipo_accion = 'REGISTRO');` 3. `PRAGMA foreign_keys = ON; INSERT INTO acciones (solicitud_id, tipo_accion, descripcion, estado_nuevo, fecha) VALUES (999999, 'SEGUIMIENTO', 'x', 'EN_GESTION', '2026-01-01');` |
| Resultado esperado | 1 → 0 acciones huérfanas. 2 → 0 solicitudes sin registro. 3 → la base de datos rechaza la inserción con `FOREIGN KEY constraint failed`. |
| Resultado obtenido | 0, 0 y rechazo por `FOREIGN KEY constraint failed`. |
| Estado | ✅ Aprobada |
| Evidencia | `resultados_pruebas_api.md` (PF-11) |
| Método y código HTTP | No aplica (consultas SQL directas) |

### PF-12 — Integración interfaz–API–base de datos (prueba mínima 12)

| Campo | Detalle |
|---|---|
| Identificador | PF-12 |
| Requisito asociado | RNF-01, RN-11 · CA-01 a CA-06 |
| Condiciones iniciales | Preparación común. Navegador en `http://localhost:8000`. |
| Pasos | 1. **Radicar** con los datos de entrada y anotar el radicado. 2. **Consultar** ese radicado (estado Recibida). 3. **Personal** → ingresar como `coordinacion`: se ven todas las solicitudes; abrir la nueva y asignarla a Carlos Pérez. 4. En otra pestaña, ingresar como `encargado1`: solo aparecen sus solicitudes asignadas. Abrir la nueva → **Evaluar** → **Agregar seguimiento** → **Responder y finalizar**. 5. **Consultar** de nuevo: estado Finalizada, historial completo y respuesta. 6. Como `coordinacion`, abrir **Resumen consolidado**: los totales incluyen la solicitud nueva. |
| Datos de entrada | Nombre "Valentina Ortega Ruiz", cédula "1000000099", dirección "Calle 15 # 22-10, Pasto", teléfono "3000000099", correo "valentina.ortega@ejemplo.com", tipo Trámite, asunto "Certificado laboral", descripción "Solicito un certificado laboral con funciones y tiempo de servicio." Textos de evaluación, seguimiento y respuesta de al menos 10 caracteres. |
| Resultado esperado | Cada paso se refleja en el siguiente, porque los datos viajan por la API y quedan guardados en la base de datos. |
| Resultado obtenido | Flujo completo exitoso de principio a fin. |
| Estado | ✅ Aprobada |
| Evidencia | `capturas/01-inicio.png`, `03-radicar-exito.png`, `04-consulta-recibida.png` y de `06-panel-coordinacion.png` a `11-resumen.png` |
| Método y código HTTP | Peticiones que hace la interfaz: `POST /api/solicitudes` (201), `GET .../consulta/{radicado}` (200), `POST /api/auth/login` (200), `POST .../asignar`, `.../evaluar`, `.../seguimiento`, `.../finalizar` (200), `GET /api/reportes/resumen` (200) |

### PF-20 — Radicar con una cédula ya registrada (regla adicional RN-13)

| Campo | Detalle |
|---|---|
| Identificador | PF-20 |
| Requisito asociado | RN-13 · RNF-05 |
| Condiciones iniciales | Preparación común: el radicado de ejemplo `51842093` pertenece a "María Fernanda López", cédula `1000000001`. |
| Pasos | 1. `POST /api/solicitudes` con la cédula de María y otro nombre y teléfono. 2. `GET /api/solicitudes/consulta/51842093`. 3. Verificar en la base de datos el nombre y el teléfono del solicitante del radicado `51842093`. |
| Datos de entrada | Igual a PF-01, pero con `"nombre": "Persona Diferente"`, `"cedula": "1000000001"`, `"telefono": "3000000099"`. |
| Resultado esperado | 201 para la nueva radicación. Los datos de la solicitud `51842093` no cambian (el nombre sigue siendo "María F. L."). |
| Resultado obtenido | 201; nombre y teléfono del radicado `51842093` sin cambios. |
| Estado | ✅ Aprobada |
| Evidencia | `resultados_pruebas_api.md` (PF-20, incluye la verificación en BD) |
| Método y código HTTP | `POST /api/solicitudes` → **201 Created** |

---

## 4. Cómo reproducir todas las pruebas

```bash
cd backend
python -m app.seed --reset --demo          # base de datos limpia con datos ficticios
python -m uvicorn app.main:app --port 8000 # dejar esta terminal abierta
```

En otra terminal, desde la raíz del proyecto:

```bash
python pruebas/ejecutar_pruebas.py
```

El script imprime `26/26 pruebas aprobadas` (PF-12 se hace en el navegador) y actualiza `evidencias/resultados_pruebas_api.md`.
