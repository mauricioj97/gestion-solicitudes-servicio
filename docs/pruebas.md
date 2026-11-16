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
| PF-08 | Historial de atención (8) | RF-13 · CA-04 | `GET .../{id}/historial` | 200 · 5 acciones en orden | 200 · 5 acciones | ✅ Aprobada |
| PF-09 | Finalización del caso (9) | RF-10 · CA-05 | `POST .../{id}/finalizar` + consulta pública | 200 · respuesta visible | 200 | ✅ Aprobada |
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

**Resultado: 25 de 25 pruebas aprobadas.** El registro completo de cada petición y respuesta está en [`evidencias/resultados_pruebas_api.md`](../evidencias/resultados_pruebas_api.md).

---

## 3. Detalle de las pruebas mínimas del enunciado

> Condición inicial común: servidor en ejecución y base de datos preparada con `python -m app.seed --reset --demo`.

### PF-01 — Registro válido de solicitud
- **Requisito:** RF-01, CA-01.
- **Pasos:** en Swagger, `POST /api/solicitudes` → Try it out → usar el ejemplo → Execute.
- **Entrada:** nombre "Camila Andrea Rosales", cédula "1085999888", dirección, teléfono "3165554433", correo "camila.rosales@correo.com", tipo_id 3, asunto y descripción válidos.
- **Resultado esperado:** `201 Created`, estado `RECIBIDA` y un radicado de 8 dígitos. La solicitud se puede recuperar con PF-03.
- **Resultado obtenido:** `201`, estado `RECIBIDA`, radicado generado.
- **Evidencia:** `evidencias/resultados_pruebas_api.md` (PF-01) y `evidencias/capturas/03-radicar-exito.png`.

### PF-02 — Registro con datos inválidos
- **Requisito:** RF-02, RN-01.
- **Pasos:** `POST /api/solicitudes` con datos erróneos. Después, contar las solicitudes en la base de datos.
- **Entrada:** nombre "Ca", cédula "12AB", correo "correo-sin-arroba", descripción "corta".
- **Resultado esperado:** `422` con la lista de los 4 campos inválidos y su mensaje en español. La cantidad de solicitudes no cambia.
- **Resultado obtenido:** `422` con 4 errores. Solicitudes antes = después (no se guardó nada).
- **Evidencia:** `resultados_pruebas_api.md` (PF-02) y `capturas/02-radicar-validacion.png`.

### PF-03 — Consulta de solicitud existente
- **Requisito:** RF-03, CA-03.
- **Pasos:** `GET /api/solicitudes/consulta/{radicado}` con el radicado de PF-01.
- **Resultado esperado:** `200` con los datos de esa solicitud. **No** incluye cédula, dirección, teléfono ni correo.
- **Resultado obtenido:** `200`, datos correctos y nombre enmascarado (por ejemplo, "Camila A. R.").
- **Evidencia:** `resultados_pruebas_api.md` (PF-03) y `capturas/04-consulta-recibida.png`.

### PF-04 — Consulta de solicitud inexistente
- **Requisito:** RF-03.
- **Pasos:** `GET /api/solicitudes/consulta/00000000`.
- **Resultado esperado:** `404` con `{"detalle": "Solicitud no encontrada. Verifique el número de radicado"}`.
- **Resultado obtenido:** `404` con el mensaje esperado.
- **Evidencia:** `resultados_pruebas_api.md` (PF-04).

### PF-05 — Gestión por actor autorizado
- **Requisito:** RF-07, CA-02.
- **Pasos:** iniciar sesión como `coordinacion`, autorizar y ejecutar `POST /api/gestion/solicitudes/{id}/asignar` con `{"encargado_id": 2}`.
- **Resultado esperado:** `200`, estado `ASIGNADA`, encargado Carlos Pérez y la acción `ASIGNACION` en el historial.
- **Resultado obtenido:** `200`, estado `ASIGNADA`.
- **Evidencia:** `resultados_pruebas_api.md` (PF-05) y `capturas/07-asignar.png`.

### PF-06 — Gestión por actor no autorizado
- **Requisito:** RN-03, RN-04, CA-02.
- **Pasos:** iniciar sesión como `encargado1` y ejecutar `POST .../{id}/asignar`.
- **Resultado esperado:** `403` con "No tiene permisos para realizar esta acción". La solicitud no cambia.
- **Resultado obtenido:** `403`. Las variantes PF-06b (encargado sobre solicitud ajena) y PF-06c (encargado pide el resumen) también responden `403`.
- **Evidencia:** `resultados_pruebas_api.md` (PF-06, PF-06b, PF-06c) y `capturas/12-swagger-403.png`.

### PF-07 — Consulta de estado
- **Requisito:** RF-03, CA-03.
- **Pasos:** después de evaluar y registrar un seguimiento (PF-05b, PF-05c), consultar por radicado.
- **Resultado esperado:** estado `EN_GESTION`, coherente con las acciones realizadas.
- **Resultado obtenido:** `200`, estado `EN_GESTION`.
- **Evidencia:** `resultados_pruebas_api.md` (PF-07).

### PF-08 — Historial de atención
- **Requisito:** RF-12, RF-13, CA-04.
- **Pasos:** `GET /api/gestion/solicitudes/{id}/historial` como coordinación.
- **Resultado esperado:** acciones en orden: REGISTRO → ASIGNACION → EVALUACION → SEGUIMIENTO → RESPUESTA, con fecha, responsable y estados.
- **Resultado obtenido:** las 5 acciones en el orden esperado.
- **Evidencia:** `resultados_pruebas_api.md` (PF-08) y `capturas/09-detalle-historial.png`.

### PF-09 — Finalización del caso
- **Requisito:** RF-10, CA-05.
- **Pasos:** como `encargado1`, `POST .../{id}/finalizar` con una respuesta. Después, consultar por radicado sin sesión.
- **Resultado esperado:** estado `FINALIZADA` y el solicitante ve la respuesta.
- **Resultado obtenido:** `200`, estado `FINALIZADA`, respuesta visible en la consulta pública.
- **Evidencia:** `resultados_pruebas_api.md` (PF-09, PF-09b) y `capturas/10-consulta-finalizada.png`.

### PF-10 — Consulta consolidada
- **Requisito:** RF-14, CA-06.
- **Pasos:** como `coordinacion`, `GET /api/reportes/resumen`.
- **Resultado esperado:** total de solicitudes; cantidades por estado (5), por tipo (4) y por encargado; pendientes y tiempo promedio.
- **Resultado obtenido:** `200` con toda la información integrada.
- **Evidencia:** `resultados_pruebas_api.md` (PF-10) y `capturas/11-resumen.png`.

### PF-11 — Persistencia e integridad de relaciones
- **Requisito:** RNF-05.
- **Pasos:** sobre `backend/data/solicitudes.db`:
  1. Contar acciones sin solicitud asociada.
  2. Contar solicitudes sin acción de registro.
  3. Intentar insertar una acción con `solicitud_id = 999999`.
- **Resultado esperado:** 0, 0 y rechazo por `FOREIGN KEY constraint failed`.
- **Resultado obtenido:** 0, 0 y rechazo de la base de datos.
- **Evidencia:** `resultados_pruebas_api.md` (PF-11).

### PF-12 — Integración interfaz–API–base de datos
- **Requisito:** RNF-01, CA-01 a CA-06.
- **Pasos (en el navegador, `http://localhost:8000`):**
  1. Radicar una solicitud en **Radicar** y anotar el radicado.
  2. Consultarla en **Consultar** (estado Recibida).
  3. Ingresar como `coordinacion`, abrir la solicitud y asignarla a Carlos Pérez.
  4. Cerrar sesión e ingresar como `encargado1`: la solicitud aparece en "Mis solicitudes asignadas".
  5. Evaluar, agregar un seguimiento y responder.
  6. Consultar de nuevo por radicado: estado Finalizada, historial completo y respuesta.
  7. Ingresar como `coordinacion` y abrir **Resumen consolidado**: los totales incluyen la nueva solicitud.
- **Resultado esperado:** cada paso se refleja en el siguiente, porque los datos viajan por la API y quedan guardados en la base de datos.
- **Resultado obtenido:** flujo completo exitoso.
- **Evidencia:** `evidencias/capturas/01` a `11`.

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

El script imprime `25/25 pruebas aprobadas` y actualiza `evidencias/resultados_pruebas_api.md`.
