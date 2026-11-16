# Evidencia — Ejecución de pruebas funcionales de la API

- **Fecha de ejecución:** 2026-11-16 10:31
- **Servidor:** http://localhost:8000
- **Resultado:** 25 de 25 pruebas aprobadas
- **Solicitud usada en el flujo completo:** radicado `65106349`

## Resumen

| Prueba | Descripción | Petición | Actor | Esperado | Obtenido | Estado |
|---|---|---|---|---|---|---|
| PF-01 | Registro válido de solicitud | `POST /api/solicitudes` | Solicitante (sin cuenta) | 201 | 201 | Aprobada |
| PF-02 | Registro con datos inválidos | `POST /api/solicitudes` | Solicitante (sin cuenta) | 422 | 422 | Aprobada |
| PF-02b | Registro con tipo de servicio inexistente | `POST /api/solicitudes` | Solicitante (sin cuenta) | 422 | 422 | Aprobada |
| PF-03 | Consulta de solicitud existente | `GET /api/solicitudes/consulta/65106349` | Solicitante (sin cuenta) | 200 | 200 | Aprobada |
| PF-04 | Consulta de solicitud inexistente | `GET /api/solicitudes/consulta/00000000` | Solicitante (sin cuenta) | 404 | 404 | Aprobada |
| PF-04b | Detalle interno de solicitud inexistente | `GET /api/gestion/solicitudes/99999` | Coordinación | 404 | 404 | Aprobada |
| PF-13 | Inicio de sesión con contraseña incorrecta | `POST /api/auth/login` | Personal | 401 | 401 | Aprobada |
| PF-14 | Gestión sin iniciar sesión | `GET /api/gestion/solicitudes` | Anónimo | 401 | 401 | Aprobada |
| PF-05 | Asignación por coordinación (actor autorizado) | `POST /api/gestion/solicitudes/9/asignar` | Coordinación | 200 | 200 | Aprobada |
| PF-06 | Encargado intenta asignar (actor no autorizado) | `POST /api/gestion/solicitudes/9/asignar` | Encargado 1 | 403 | 403 | Aprobada |
| PF-06b | Encargado intenta gestionar una solicitud de otro | `POST /api/gestion/solicitudes/9/evaluar` | Encargado 2 | 403 | 403 | Aprobada |
| PF-06c | Encargado intenta ver el resumen consolidado | `GET /api/reportes/resumen` | Encargado 1 | 403 | 403 | Aprobada |
| PF-15 | Finalizar sin haber evaluado (transición inválida) | `POST /api/gestion/solicitudes/9/finalizar` | Encargado 1 | 409 | 409 | Aprobada |
| PF-05b | Evaluación por el encargado asignado | `POST /api/gestion/solicitudes/9/evaluar` | Encargado 1 | 200 | 200 | Aprobada |
| PF-05c | Registro de seguimiento | `POST /api/gestion/solicitudes/9/seguimiento` | Encargado 1 | 200 | 200 | Aprobada |
| PF-07 | Consulta de estado durante la atención | `GET /api/solicitudes/consulta/65106349` | Solicitante (sin cuenta) | 200 | 200 | Aprobada |
| PF-16 | Finalizar con respuesta vacía | `POST /api/gestion/solicitudes/9/finalizar` | Encargado 1 | 422 | 422 | Aprobada |
| PF-09 | Responder y finalizar el caso | `POST /api/gestion/solicitudes/9/finalizar` | Encargado 1 | 200 | 200 | Aprobada |
| PF-09b | El solicitante consulta la respuesta final | `GET /api/solicitudes/consulta/65106349` | Solicitante (sin cuenta) | 200 | 200 | Aprobada |
| PF-17 | Acción sobre solicitud finalizada | `POST /api/gestion/solicitudes/9/cerrar` | Coordinación | 409 | 409 | Aprobada |
| PF-08 | Historial de atención | `GET /api/gestion/solicitudes/9/historial` | Coordinación | 200 | 200 | Aprobada |
| PF-18 | Cerrar sin motivo | `POST /api/gestion/solicitudes/10/cerrar` | Coordinación | 422 | 422 | Aprobada |
| PF-19 | Cerrar con motivo | `POST /api/gestion/solicitudes/10/cerrar` | Coordinación | 200 | 200 | Aprobada |
| PF-10 | Consulta consolidada | `GET /api/reportes/resumen` | Coordinación | 200 | 200 | Aprobada |
| PF-11 | Persistencia e integridad de relaciones | `SQL sobre la base de datos` | - | - | - | Aprobada |

## Detalle de cada petición y respuesta

### PF-01 — Registro válido de solicitud

- **Actor:** Solicitante (sin cuenta)
- **Petición:** `POST /api/solicitudes`
- **Código esperado:** 201 · **Obtenido:** 201 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "nombre": "Camila Andrea Rosales",
  "cedula": "1085999888",
  "direccion": "Carrera 22 # 14-30, Pasto",
  "telefono": "3165554433",
  "correo": "camila.rosales@correo.com",
  "tipo_id": 3,
  "asunto": "Actualización de datos de contacto",
  "descripcion": "Solicito actualizar mi número de teléfono y correo en los registros de la organización."
}
```

**Respuesta:**
```json
{
  "mensaje": "Solicitud radicada correctamente. Guarde su número de radicado para consultarla.",
  "radicado": "65106349",
  "solicitante": "Camila A. R.",
  "tipo": "Atención administrativa",
  "asunto": "Actualización de datos de contacto",
  "descripcion": "Solicito actualizar mi número de teléfono y correo en los registros de la organización.",
  "estado": "RECIBIDA",
  "estado_etiqueta": "Recibida",
  "respuesta": null,
  "motivo_cierre": null,
  "fecha_creacion": "2026-11-16 10:30:53",
  "fecha_actualizacion": "2026-11-16 10:30:53",
  "fecha_cierre": null,
  "historial": [
    {
      "fecha": "2026-11-16 10:30:53",
      "accion": "REGISTRO",
      "accion_etiqueta": "Registro de la solicitud",
      "descripcion": "Solicitud radicada por el solicitante",
      "estado_nuevo": "RECIBIDA"
    }
  ]
}
```

### PF-02 — Registro con datos inválidos

- **Actor:** Solicitante (sin cuenta)
- **Petición:** `POST /api/solicitudes`
- **Código esperado:** 422 · **Obtenido:** 422 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "nombre": "Ca",
  "cedula": "12AB",
  "direccion": "Carrera 22 # 14-30, Pasto",
  "telefono": "3165554433",
  "correo": "correo-sin-arroba",
  "tipo_id": 3,
  "asunto": "Actualización de datos de contacto",
  "descripcion": "corta"
}
```

**Respuesta:**
```json
{
  "detalle": "Los datos enviados no son válidos",
  "errores": [
    {
      "campo": "nombre",
      "mensaje": "El campo nombre debe tener al menos 3 caracteres"
    },
    {
      "campo": "cedula",
      "mensaje": "El campo cédula debe tener solo números, entre 6 y 10 dígitos"
    },
    {
      "campo": "correo",
      "mensaje": "El campo correo no tiene un formato válido (ejemplo: nombre@dominio.com)"
    },
    {
      "campo": "descripcion",
      "mensaje": "El campo descripción debe tener al menos 10 caracteres"
    }
  ]
}
```

> Verificación en base de datos: solicitudes antes = 9, después = 9 → no se guardó el registro inválido ✅

### PF-02b — Registro con tipo de servicio inexistente

- **Actor:** Solicitante (sin cuenta)
- **Petición:** `POST /api/solicitudes`
- **Código esperado:** 422 · **Obtenido:** 422 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "nombre": "Camila Andrea Rosales",
  "cedula": "1085999888",
  "direccion": "Carrera 22 # 14-30, Pasto",
  "telefono": "3165554433",
  "correo": "camila.rosales@correo.com",
  "tipo_id": 99,
  "asunto": "Actualización de datos de contacto",
  "descripcion": "Solicito actualizar mi número de teléfono y correo en los registros de la organización."
}
```

**Respuesta:**
```json
{
  "detalle": "El tipo de servicio indicado no existe"
}
```

### PF-03 — Consulta de solicitud existente

- **Actor:** Solicitante (sin cuenta)
- **Petición:** `GET /api/solicitudes/consulta/65106349`
- **Código esperado:** 200 · **Obtenido:** 200 · **Resultado:** ✅ Aprobada

**Respuesta:**
```json
{
  "radicado": "65106349",
  "solicitante": "Camila A. R.",
  "tipo": "Atención administrativa",
  "asunto": "Actualización de datos de contacto",
  "descripcion": "Solicito actualizar mi número de teléfono y correo en los registros de la organización.",
  "estado": "RECIBIDA",
  "estado_etiqueta": "Recibida",
  "respuesta": null,
  "motivo_cierre": null,
  "fecha_creacion": "2026-11-16 10:30:53",
  "fecha_actualizacion": "2026-11-16 10:30:53",
  "fecha_cierre": null,
  "historial": [
    {
      "fecha": "2026-11-16 10:30:53",
      "accion": "REGISTRO",
      "accion_etiqueta": "Registro de la solicitud",
      "descripcion": "Solicitud radicada por el solicitante",
      "estado_nuevo": "RECIBIDA"
    }
  ]
}
```

### PF-04 — Consulta de solicitud inexistente

- **Actor:** Solicitante (sin cuenta)
- **Petición:** `GET /api/solicitudes/consulta/00000000`
- **Código esperado:** 404 · **Obtenido:** 404 · **Resultado:** ✅ Aprobada

**Respuesta:**
```json
{
  "detalle": "Solicitud no encontrada. Verifique el número de radicado"
}
```

### PF-04b — Detalle interno de solicitud inexistente

- **Actor:** Coordinación
- **Petición:** `GET /api/gestion/solicitudes/99999`
- **Código esperado:** 404 · **Obtenido:** 404 · **Resultado:** ✅ Aprobada

**Respuesta:**
```json
{
  "detalle": "Solicitud no encontrada"
}
```

### PF-13 — Inicio de sesión con contraseña incorrecta

- **Actor:** Personal
- **Petición:** `POST /api/auth/login`
- **Código esperado:** 401 · **Obtenido:** 401 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "usuario": "coordinacion",
  "contrasena": "********"
}
```

**Respuesta:**
```json
{
  "detalle": "Usuario o contraseña incorrectos"
}
```

### PF-14 — Gestión sin iniciar sesión

- **Actor:** Anónimo
- **Petición:** `GET /api/gestion/solicitudes`
- **Código esperado:** 401 · **Obtenido:** 401 · **Resultado:** ✅ Aprobada

**Respuesta:**
```json
{
  "detalle": "Debe iniciar sesión para realizar esta acción"
}
```

### PF-05 — Asignación por coordinación (actor autorizado)

- **Actor:** Coordinación
- **Petición:** `POST /api/gestion/solicitudes/9/asignar`
- **Código esperado:** 200 · **Obtenido:** 200 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "encargado_id": 2
}
```

**Respuesta:**
```json
{
  "id": 9,
  "radicado": "65106349",
  "estado": "ASIGNADA",
  "estado_etiqueta": "Asignada",
  "tipo_id": 3,
  "tipo": "Atención administrativa",
  "asunto": "Actualización de datos de contacto",
  "descripcion": "Solicito actualizar mi número de teléfono y correo en los registros de la organización.",
  "solicitante": {
    "nombre": "Camila Andrea Rosales",
    "cedula": "1085999888",
    "direccion": "Carrera 22 # 14-30, Pasto",
    "telefono": "3165554433",
    "correo": "camila.rosales@correo.com"
  },
  "encargado": {
    "id": 2,
    "nombre": "Carlos Pérez"
  },
  "respuesta": null,
  "motivo_cierre": null,
  "fecha_creacion": "2026-11-16 10:30:53",
  "fecha_actualizacion": "2026-11-16 10:31:09",
  "fecha_cierre": null,
  "historial": [
    {
      "id": 23,
      "fecha": "2026-11-16 10:30:53",
      "accion": "REGISTRO",
      "accion_etiqueta": "Registro de la solicitud",
      "descripcion": "Solicitud radicada por el solicitante",
      "estado_anterior": null,
      "estado_nuevo": "RECIBIDA",
      "responsable": "Solicitante"
    },
    {
      "id": 24,
      "fecha": "2026-11-16 10:31:09",
      "accion": "ASIGNACION",
      "accion_etiqueta": "Asignación",
      "descripcion": "Asignada a Carlos Pérez",
      "estado_anterior": "RECIBIDA",
      "estado_nuevo": "ASIGNADA",
      "responsable": "Laura Gómez"
    }
  ]
}
```

### PF-06 — Encargado intenta asignar (actor no autorizado)

- **Actor:** Encargado 1
- **Petición:** `POST /api/gestion/solicitudes/9/asignar`
- **Código esperado:** 403 · **Obtenido:** 403 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "encargado_id": 3
}
```

**Respuesta:**
```json
{
  "detalle": "No tiene permisos para realizar esta acción"
}
```

### PF-06b — Encargado intenta gestionar una solicitud de otro

- **Actor:** Encargado 2
- **Petición:** `POST /api/gestion/solicitudes/9/evaluar`
- **Código esperado:** 403 · **Obtenido:** 403 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "observacion": "Intento de evaluar una solicitud ajena."
}
```

**Respuesta:**
```json
{
  "detalle": "No tiene permisos sobre esta solicitud: está asignada a otro encargado"
}
```

### PF-06c — Encargado intenta ver el resumen consolidado

- **Actor:** Encargado 1
- **Petición:** `GET /api/reportes/resumen`
- **Código esperado:** 403 · **Obtenido:** 403 · **Resultado:** ✅ Aprobada

**Respuesta:**
```json
{
  "detalle": "No tiene permisos para realizar esta acción"
}
```

### PF-15 — Finalizar sin haber evaluado (transición inválida)

- **Actor:** Encargado 1
- **Petición:** `POST /api/gestion/solicitudes/9/finalizar`
- **Código esperado:** 409 · **Obtenido:** 409 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "respuesta": "Respuesta antes de tiempo para probar la regla."
}
```

**Respuesta:**
```json
{
  "detalle": "No se puede finalizar una solicitud en estado Asignada"
}
```

### PF-05b — Evaluación por el encargado asignado

- **Actor:** Encargado 1
- **Petición:** `POST /api/gestion/solicitudes/9/evaluar`
- **Código esperado:** 200 · **Obtenido:** 200 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "observacion": "Se revisó la solicitud: los datos nuevos están completos."
}
```

**Respuesta:**
```json
{
  "id": 9,
  "radicado": "65106349",
  "estado": "EN_GESTION",
  "estado_etiqueta": "En gestión",
  "tipo_id": 3,
  "tipo": "Atención administrativa",
  "asunto": "Actualización de datos de contacto",
  "descripcion": "Solicito actualizar mi número de teléfono y correo en los registros de la organización.",
  "solicitante": {
    "nombre": "Camila Andrea Rosales",
    "cedula": "1085999888",
    "direccion": "Carrera 22 # 14-30, Pasto",
    "telefono": "3165554433",
    "correo": "camila.rosales@correo.com"
  },
  "encargado": {
    "id": 2,
    "nombre": "Carlos Pérez"
  },
  "respuesta": null,
  "motivo_cierre": null,
  "fecha_creacion": "2026-11-16 10:30:53",
  "fecha_actualizacion": "2026-11-16 10:31:20",
  "fecha_cierre": null,
  "historial": [
    {
      "id": 23,
      "fecha": "2026-11-16 10:30:53",
      "accion": "REGISTRO",
      "accion_etiqueta": "Registro de la solicitud",
      "descripcion": "Solicitud radicada por el solicitante",
      "estado_anterior": null,
      "estado_nuevo": "RECIBIDA",
      "responsable": "Solicitante"
    },
    {
      "id": 24,
      "fecha": "2026-11-16 10:31:09",
      "accion": "ASIGNACION",
      "accion_etiqueta": "Asignación",
      "descripcion": "Asignada a Carlos Pérez",
      "estado_anterior": "RECIBIDA",
      "estado_nuevo": "ASIGNADA",
      "responsable": "Laura Gómez"
    },
    {
      "id": 25,
      "fecha": "2026-11-16 10:31:20",
      "accion": "EVALUACION",
      "accion_etiqueta": "Evaluación",
      "de
  ... (respuesta recortada)
```

### PF-05c — Registro de seguimiento

- **Actor:** Encargado 1
- **Petición:** `POST /api/gestion/solicitudes/9/seguimiento`
- **Código esperado:** 200 · **Obtenido:** 200 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "nota": "Se actualizó el teléfono; falta confirmar el correo."
}
```

**Respuesta:**
```json
{
  "id": 9,
  "radicado": "65106349",
  "estado": "EN_GESTION",
  "estado_etiqueta": "En gestión",
  "tipo_id": 3,
  "tipo": "Atención administrativa",
  "asunto": "Actualización de datos de contacto",
  "descripcion": "Solicito actualizar mi número de teléfono y correo en los registros de la organización.",
  "solicitante": {
    "nombre": "Camila Andrea Rosales",
    "cedula": "1085999888",
    "direccion": "Carrera 22 # 14-30, Pasto",
    "telefono": "3165554433",
    "correo": "camila.rosales@correo.com"
  },
  "encargado": {
    "id": 2,
    "nombre": "Carlos Pérez"
  },
  "respuesta": null,
  "motivo_cierre": null,
  "fecha_creacion": "2026-11-16 10:30:53",
  "fecha_actualizacion": "2026-11-16 10:31:22",
  "fecha_cierre": null,
  "historial": [
    {
      "id": 23,
      "fecha": "2026-11-16 10:30:53",
      "accion": "REGISTRO",
      "accion_etiqueta": "Registro de la solicitud",
      "descripcion": "Solicitud radicada por el solicitante",
      "estado_anterior": null,
      "estado_nuevo": "RECIBIDA",
      "responsable": "Solicitante"
    },
    {
      "id": 24,
      "fecha": "2026-11-16 10:31:09",
      "accion": "ASIGNACION",
      "accion_etiqueta": "Asignación",
      "descripcion": "Asignada a Carlos Pérez",
      "estado_anterior": "RECIBIDA",
      "estado_nuevo": "ASIGNADA",
      "responsable": "Laura Gómez"
    },
    {
      "id": 25,
      "fecha": "2026-11-16 10:31:20",
      "accion": "EVALUACION",
      "accion_etiqueta": "Evaluación",
      "de
  ... (respuesta recortada)
```

### PF-07 — Consulta de estado durante la atención

- **Actor:** Solicitante (sin cuenta)
- **Petición:** `GET /api/solicitudes/consulta/65106349`
- **Código esperado:** 200 · **Obtenido:** 200 · **Resultado:** ✅ Aprobada

**Respuesta:**
```json
{
  "radicado": "65106349",
  "solicitante": "Camila A. R.",
  "tipo": "Atención administrativa",
  "asunto": "Actualización de datos de contacto",
  "descripcion": "Solicito actualizar mi número de teléfono y correo en los registros de la organización.",
  "estado": "EN_GESTION",
  "estado_etiqueta": "En gestión",
  "respuesta": null,
  "motivo_cierre": null,
  "fecha_creacion": "2026-11-16 10:30:53",
  "fecha_actualizacion": "2026-11-16 10:31:22",
  "fecha_cierre": null,
  "historial": [
    {
      "fecha": "2026-11-16 10:30:53",
      "accion": "REGISTRO",
      "accion_etiqueta": "Registro de la solicitud",
      "descripcion": "Solicitud radicada por el solicitante",
      "estado_nuevo": "RECIBIDA"
    },
    {
      "fecha": "2026-11-16 10:31:09",
      "accion": "ASIGNACION",
      "accion_etiqueta": "Asignación",
      "descripcion": "Asignada a Carlos Pérez",
      "estado_nuevo": "ASIGNADA"
    },
    {
      "fecha": "2026-11-16 10:31:20",
      "accion": "EVALUACION",
      "accion_etiqueta": "Evaluación",
      "descripcion": "Se revisó la solicitud: los datos nuevos están completos.",
      "estado_nuevo": "EN_GESTION"
    },
    {
      "fecha": "2026-11-16 10:31:22",
      "accion": "SEGUIMIENTO",
      "accion_etiqueta": "Seguimiento",
      "descripcion": "Se actualizó el teléfono; falta confirmar el correo.",
      "estado_nuevo": "EN_GESTION"
    }
  ]
}
```

### PF-16 — Finalizar con respuesta vacía

- **Actor:** Encargado 1
- **Petición:** `POST /api/gestion/solicitudes/9/finalizar`
- **Código esperado:** 422 · **Obtenido:** 422 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "respuesta": "  "
}
```

**Respuesta:**
```json
{
  "detalle": "Los datos enviados no son válidos",
  "errores": [
    {
      "campo": "respuesta",
      "mensaje": "El campo respuesta es obligatorio"
    }
  ]
}
```

### PF-09 — Responder y finalizar el caso

- **Actor:** Encargado 1
- **Petición:** `POST /api/gestion/solicitudes/9/finalizar`
- **Código esperado:** 200 · **Obtenido:** 200 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "respuesta": "Sus datos de contacto fueron actualizados correctamente en nuestros registros."
}
```

**Respuesta:**
```json
{
  "id": 9,
  "radicado": "65106349",
  "estado": "FINALIZADA",
  "estado_etiqueta": "Finalizada",
  "tipo_id": 3,
  "tipo": "Atención administrativa",
  "asunto": "Actualización de datos de contacto",
  "descripcion": "Solicito actualizar mi número de teléfono y correo en los registros de la organización.",
  "solicitante": {
    "nombre": "Camila Andrea Rosales",
    "cedula": "1085999888",
    "direccion": "Carrera 22 # 14-30, Pasto",
    "telefono": "3165554433",
    "correo": "camila.rosales@correo.com"
  },
  "encargado": {
    "id": 2,
    "nombre": "Carlos Pérez"
  },
  "respuesta": "Sus datos de contacto fueron actualizados correctamente en nuestros registros.",
  "motivo_cierre": null,
  "fecha_creacion": "2026-11-16 10:30:53",
  "fecha_actualizacion": "2026-11-16 10:31:28",
  "fecha_cierre": "2026-11-16 10:31:28",
  "historial": [
    {
      "id": 23,
      "fecha": "2026-11-16 10:30:53",
      "accion": "REGISTRO",
      "accion_etiqueta": "Registro de la solicitud",
      "descripcion": "Solicitud radicada por el solicitante",
      "estado_anterior": null,
      "estado_nuevo": "RECIBIDA",
      "responsable": "Solicitante"
    },
    {
      "id": 24,
      "fecha": "2026-11-16 10:31:09",
      "accion": "ASIGNACION",
      "accion_etiqueta": "Asignación",
      "descripcion": "Asignada a Carlos Pérez",
      "estado_anterior": "RECIBIDA",
      "estado_nuevo": "ASIGNADA",
      "responsable": "Laura Gómez"
    },
    {
      "id": 25,
      "fecha": "2026-11
  ... (respuesta recortada)
```

### PF-09b — El solicitante consulta la respuesta final

- **Actor:** Solicitante (sin cuenta)
- **Petición:** `GET /api/solicitudes/consulta/65106349`
- **Código esperado:** 200 · **Obtenido:** 200 · **Resultado:** ✅ Aprobada

**Respuesta:**
```json
{
  "radicado": "65106349",
  "solicitante": "Camila A. R.",
  "tipo": "Atención administrativa",
  "asunto": "Actualización de datos de contacto",
  "descripcion": "Solicito actualizar mi número de teléfono y correo en los registros de la organización.",
  "estado": "FINALIZADA",
  "estado_etiqueta": "Finalizada",
  "respuesta": "Sus datos de contacto fueron actualizados correctamente en nuestros registros.",
  "motivo_cierre": null,
  "fecha_creacion": "2026-11-16 10:30:53",
  "fecha_actualizacion": "2026-11-16 10:31:28",
  "fecha_cierre": "2026-11-16 10:31:28",
  "historial": [
    {
      "fecha": "2026-11-16 10:30:53",
      "accion": "REGISTRO",
      "accion_etiqueta": "Registro de la solicitud",
      "descripcion": "Solicitud radicada por el solicitante",
      "estado_nuevo": "RECIBIDA"
    },
    {
      "fecha": "2026-11-16 10:31:09",
      "accion": "ASIGNACION",
      "accion_etiqueta": "Asignación",
      "descripcion": "Asignada a Carlos Pérez",
      "estado_nuevo": "ASIGNADA"
    },
    {
      "fecha": "2026-11-16 10:31:20",
      "accion": "EVALUACION",
      "accion_etiqueta": "Evaluación",
      "descripcion": "Se revisó la solicitud: los datos nuevos están completos.",
      "estado_nuevo": "EN_GESTION"
    },
    {
      "fecha": "2026-11-16 10:31:22",
      "accion": "SEGUIMIENTO",
      "accion_etiqueta": "Seguimiento",
      "descripcion": "Se actualizó el teléfono; falta confirmar el correo.",
      "estado_nuevo": "EN_GESTION"
    },
    {
      "
  ... (respuesta recortada)
```

### PF-17 — Acción sobre solicitud finalizada

- **Actor:** Coordinación
- **Petición:** `POST /api/gestion/solicitudes/9/cerrar`
- **Código esperado:** 409 · **Obtenido:** 409 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "motivo": "Intento de cerrar una solicitud ya finalizada."
}
```

**Respuesta:**
```json
{
  "detalle": "La solicitud está finalizada y no admite más acciones"
}
```

### PF-08 — Historial de atención

- **Actor:** Coordinación
- **Petición:** `GET /api/gestion/solicitudes/9/historial`
- **Código esperado:** 200 · **Obtenido:** 200 · **Resultado:** ✅ Aprobada

**Respuesta:**
```json
[
  {
    "id": 23,
    "fecha": "2026-11-16 10:30:53",
    "accion": "REGISTRO",
    "accion_etiqueta": "Registro de la solicitud",
    "descripcion": "Solicitud radicada por el solicitante",
    "estado_anterior": null,
    "estado_nuevo": "RECIBIDA",
    "responsable": "Solicitante"
  },
  {
    "id": 24,
    "fecha": "2026-11-16 10:31:09",
    "accion": "ASIGNACION",
    "accion_etiqueta": "Asignación",
    "descripcion": "Asignada a Carlos Pérez",
    "estado_anterior": "RECIBIDA",
    "estado_nuevo": "ASIGNADA",
    "responsable": "Laura Gómez"
  },
  {
    "id": 25,
    "fecha": "2026-11-16 10:31:20",
    "accion": "EVALUACION",
    "accion_etiqueta": "Evaluación",
    "descripcion": "Se revisó la solicitud: los datos nuevos están completos.",
    "estado_anterior": "ASIGNADA",
    "estado_nuevo": "EN_GESTION",
    "responsable": "Carlos Pérez"
  },
  {
    "id": 26,
    "fecha": "2026-11-16 10:31:22",
    "accion": "SEGUIMIENTO",
    "accion_etiqueta": "Seguimiento",
    "descripcion": "Se actualizó el teléfono; falta confirmar el correo.",
    "estado_anterior": "EN_GESTION",
    "estado_nuevo": "EN_GESTION",
    "responsable": "Carlos Pérez"
  },
  {
    "id": 27,
    "fecha": "2026-11-16 10:31:28",
    "accion": "RESPUESTA",
    "accion_etiqueta": "Respuesta y finalización",
    "descripcion": "Sus datos de contacto fueron actualizados correctamente en nuestros registros.",
    "estado_anterior": "EN_GESTION",
    "estado_nuevo": "FINALIZADA",
    "responsable": "C
  ... (respuesta recortada)
```

### PF-18 — Cerrar sin motivo

- **Actor:** Coordinación
- **Petición:** `POST /api/gestion/solicitudes/10/cerrar`
- **Código esperado:** 422 · **Obtenido:** 422 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "motivo": ""
}
```

**Respuesta:**
```json
{
  "detalle": "Los datos enviados no son válidos",
  "errores": [
    {
      "campo": "motivo",
      "mensaje": "El campo motivo es obligatorio"
    }
  ]
}
```

### PF-19 — Cerrar con motivo

- **Actor:** Coordinación
- **Petición:** `POST /api/gestion/solicitudes/10/cerrar`
- **Código esperado:** 200 · **Obtenido:** 200 · **Resultado:** ✅ Aprobada

**Cuerpo enviado:**
```json
{
  "motivo": "El solicitante desistió de la solicitud por vía telefónica."
}
```

**Respuesta:**
```json
{
  "id": 10,
  "radicado": "44732327",
  "estado": "CERRADA",
  "estado_etiqueta": "Cerrada",
  "tipo_id": 3,
  "tipo": "Atención administrativa",
  "asunto": "Solicitud para cerrar",
  "descripcion": "Solicito actualizar mi número de teléfono y correo en los registros de la organización.",
  "solicitante": {
    "nombre": "Camila Andrea Rosales",
    "cedula": "1085999888",
    "direccion": "Carrera 22 # 14-30, Pasto",
    "telefono": "3165554433",
    "correo": "camila.rosales@correo.com"
  },
  "encargado": null,
  "respuesta": null,
  "motivo_cierre": "El solicitante desistió de la solicitud por vía telefónica.",
  "fecha_creacion": "2026-11-16 10:31:36",
  "fecha_actualizacion": "2026-11-16 10:31:40",
  "fecha_cierre": "2026-11-16 10:31:40",
  "historial": [
    {
      "id": 28,
      "fecha": "2026-11-16 10:31:36",
      "accion": "REGISTRO",
      "accion_etiqueta": "Registro de la solicitud",
      "descripcion": "Solicitud radicada por el solicitante",
      "estado_anterior": null,
      "estado_nuevo": "RECIBIDA",
      "responsable": "Solicitante"
    },
    {
      "id": 29,
      "fecha": "2026-11-16 10:31:40",
      "accion": "CIERRE",
      "accion_etiqueta": "Cierre",
      "descripcion": "El solicitante desistió de la solicitud por vía telefónica.",
      "estado_anterior": "RECIBIDA",
      "estado_nuevo": "CERRADA",
      "responsable": "Laura Gómez"
    }
  ]
}
```

### PF-10 — Consulta consolidada

- **Actor:** Coordinación
- **Petición:** `GET /api/reportes/resumen`
- **Código esperado:** 200 · **Obtenido:** 200 · **Resultado:** ✅ Aprobada

**Respuesta:**
```json
{
  "total": 10,
  "pendientes": 5,
  "sin_asignar": 2,
  "finalizadas": 3,
  "cerradas": 2,
  "tiempo_promedio_atencion_horas": 22.7,
  "por_estado": [
    {
      "estado": "RECIBIDA",
      "etiqueta": "Recibida",
      "cantidad": 2
    },
    {
      "estado": "ASIGNADA",
      "etiqueta": "Asignada",
      "cantidad": 1
    },
    {
      "estado": "EN_GESTION",
      "etiqueta": "En gestión",
      "cantidad": 2
    },
    {
      "estado": "FINALIZADA",
      "etiqueta": "Finalizada",
      "cantidad": 3
    },
    {
      "estado": "CERRADA",
      "etiqueta": "Cerrada",
      "cantidad": 2
    }
  ],
  "por_tipo": [
    {
      "tipo": "Trámite",
      "cantidad": 2
    },
    {
      "tipo": "Orientación",
      "cantidad": 2
    },
    {
      "tipo": "Atención administrativa",
      "cantidad": 4
    },
    {
      "tipo": "Requerimiento de servicio",
      "cantidad": 2
    }
  ],
  "por_encargado": [
    {
      "encargado": "Ana Martínez",
      "activas": 1,
      "finalizadas": 1,
      "cerradas": 0,
      "total": 2
    },
    {
      "encargado": "Carlos Pérez",
      "activas": 2,
      "finalizadas": 2,
      "cerradas": 0,
      "total": 4
    }
  ]
}
```

### PF-11 — Persistencia e integridad de relaciones

- Acciones sin solicitud asociada: **0**
- Solicitudes sin acción de registro: **0**
- Intento de insertar una acción con `solicitud_id` inexistente: ✅ la base de datos rechazó la acción sin solicitud (FOREIGN KEY constraint failed)
- **Resultado:** ✅ Aprobada
