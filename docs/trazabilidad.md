# Matriz de Trazabilidad

Relaciona cada condición obligatoria con los requisitos aprobados, la implementación, el *pull request* que la integró y las pruebas que la verifican.

**Repositorio:** https://github.com/mauricioj97/gestion-solicitudes-servicio

## 1. Condiciones obligatorias

| Condición | Requisito aprobado | Implementación (ruta / componente) | Pull request | Prueba |
|---|---|---|---|---|
| **CA-01** Una persona puede presentar una solicitud | RF-01, RF-02, RN-01, RN-02 · HU-01 | `POST /api/solicitudes` → `routers/publico.py::radicar()`; validación en `schemas.py::SolicitudCrear`; tablas `solicitantes`, `solicitudes` y `acciones`; pantalla `frontend/radicar.html` + `js/radicar.js` | [#3](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/3), [#4](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/4) | PF-01, PF-02, PF-02b, PF-12 |
| **CA-02** El personal autorizado puede evaluar y gestionar | RF-04, RF-05, RF-07, RF-08, RF-09, RF-11, RN-03, RN-04 · HU-03, HU-04, HU-05 | `POST /api/auth/login`; `POST /api/gestion/solicitudes/{id}/asignar`, `/evaluar`, `/seguimiento`, `/cerrar` → `routers/gestion.py`; permisos en `security.py::requiere_rol()` y `servicios.py::verificar_acceso()`; pantalla `frontend/panel.html` | [#3](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/3), [#4](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/4) | PF-05, PF-05b, PF-05c, PF-06, PF-06b, PF-13, PF-14 |
| **CA-03** Consultar el estado durante la atención | RF-03, RF-06, RN-05 · HU-02 | `GET /api/solicitudes/consulta/{radicado}` → `routers/publico.py::consultar()`; `GET /api/gestion/solicitudes/{id}`; máquina de estados en `servicios.py::TRANSICIONES`; pantalla `frontend/consultar.html` | [#3](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/3), [#4](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/4) | PF-03, PF-04, PF-07, PF-15 |
| **CA-04** Trazabilidad de las acciones de atención | RF-12, RF-13, RN-09, RN-10 · HU-05 | Tabla `acciones`; `servicios.py::aplicar_accion()` y `registrar_accion()` (transacción); `GET /api/gestion/solicitudes/{id}/historial`; línea de tiempo en `panel.html` y `consultar.html` | [#3](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/3), [#4](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/4) | PF-08, PF-11 |
| **CA-05** El solicitante consulta la respuesta y la finalización | RF-10, RF-11, RN-06, RN-07, RN-08, RN-12 · HU-02, HU-05, HU-06 | `POST /api/gestion/solicitudes/{id}/finalizar` y `/cerrar`; `servicios.py::vista_publica()`; caja de respuesta o motivo en `consultar.html` | [#3](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/3), [#4](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/4) | PF-09, PF-16, PF-17, PF-18, PF-19 |
| **CA-06** La coordinación consulta información consolidada | RF-14, RF-15 · HU-07 | `GET /api/reportes/resumen` → `routers/coordinacion.py::resumen()`; pestaña "Resumen consolidado" en `panel.html` | [#3](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/3), [#4](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/4) | PF-10, PF-06c |

## 2. Documentación y pruebas

| Elemento | Archivo | Pull request |
|---|---|---|
| Requisitos, entrevista e historias de usuario | [requisitos.md](requisitos.md) | [#1](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/1) |
| Diseño, modelo de datos y especificación de API | [diseno.md](diseno.md) | [#2](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/2) |
| Plan y resultados de pruebas, evidencias | [pruebas.md](pruebas.md), [../evidencias/](../evidencias/) | [#5](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/5) |
| Informe (README) y esta matriz | [../README.md](../README.md), trazabilidad.md | [#6](https://github.com/mauricioj97/gestion-solicitudes-servicio/pull/6) |

## 3. Requisitos no funcionales

| Requisito | Implementación | Prueba |
|---|---|---|
| RNF-01 Cliente-servidor | `frontend/` + `backend/app/` + SQLite | PF-12 |
| RNF-02 Seguridad | `security.py` (PBKDF2, token con vencimiento, roles) | PF-06, PF-13, PF-14 |
| RNF-03 Privacidad | `servicios.py::vista_publica()`, `enmascarar_nombre()` | PF-03 |
| RNF-04 Códigos y errores | Manejadores en `main.py` | PF-02, PF-04, PF-06, PF-15 |
| RNF-05 Integridad | `schema.sql` (FK, CHECK, UNIQUE), transacciones | PF-11 |
| RNF-06 Usabilidad | `frontend/css/styles.css` (adaptable) | PF-12 |
| RNF-07 Reproducibilidad | README, `requirements.txt`, `seed.py`, `.env.example` | Instalación desde cero |
| RNF-08 Documentación de API | Swagger UI en `/docs` | Todas las pruebas de API |
