-- Esquema de la base de datos (SQLite)
-- Sistema de Gestión de Solicitudes de Servicio

PRAGMA foreign_keys = ON;

-- Personal que inicia sesión (coordinación y encargados de atención)
CREATE TABLE IF NOT EXISTS usuarios (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre        TEXT    NOT NULL,
    usuario       TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    rol           TEXT    NOT NULL CHECK (rol IN ('COORDINADOR', 'ENCARGADO')),
    activo        INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1))
);

-- Sesiones abiertas (token con vencimiento)
CREATE TABLE IF NOT EXISTS sesiones (
    token      TEXT    PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios (id) ON DELETE CASCADE,
    creada_en  TEXT    NOT NULL,
    expira_en  TEXT    NOT NULL
);

-- Lista fija de tipos de servicio
CREATE TABLE IF NOT EXISTS tipos_servicio (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT    NOT NULL UNIQUE
);

-- Personas que presentan solicitudes (no inician sesión)
CREATE TABLE IF NOT EXISTS solicitantes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    cedula    TEXT    NOT NULL UNIQUE,
    nombre    TEXT    NOT NULL,
    direccion TEXT    NOT NULL,
    telefono  TEXT    NOT NULL,
    correo    TEXT    NOT NULL
);

-- Solicitudes de servicio
CREATE TABLE IF NOT EXISTS solicitudes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    radicado            TEXT    NOT NULL UNIQUE,
    solicitante_id      INTEGER NOT NULL REFERENCES solicitantes (id),
    tipo_id             INTEGER NOT NULL REFERENCES tipos_servicio (id),
    asunto              TEXT    NOT NULL,
    descripcion         TEXT    NOT NULL,
    estado              TEXT    NOT NULL DEFAULT 'RECIBIDA'
                        CHECK (estado IN ('RECIBIDA', 'ASIGNADA', 'EN_GESTION', 'FINALIZADA', 'CERRADA')),
    encargado_id        INTEGER REFERENCES usuarios (id),
    respuesta           TEXT,
    motivo_cierre       TEXT,
    fecha_creacion      TEXT    NOT NULL,
    fecha_actualizacion TEXT    NOT NULL,
    fecha_cierre        TEXT
);

-- Historial (trazabilidad): una fila por cada acción realizada
CREATE TABLE IF NOT EXISTS acciones (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    solicitud_id    INTEGER NOT NULL REFERENCES solicitudes (id),
    usuario_id      INTEGER REFERENCES usuarios (id),  -- NULL cuando la acción la hace el solicitante
    tipo_accion     TEXT    NOT NULL
                    CHECK (tipo_accion IN ('REGISTRO', 'ASIGNACION', 'EVALUACION', 'SEGUIMIENTO', 'RESPUESTA', 'CIERRE')),
    descripcion     TEXT    NOT NULL,
    estado_anterior TEXT,
    estado_nuevo    TEXT    NOT NULL,
    fecha           TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_solicitudes_estado    ON solicitudes (estado);
CREATE INDEX IF NOT EXISTS idx_solicitudes_encargado ON solicitudes (encargado_id);
CREATE INDEX IF NOT EXISTS idx_acciones_solicitud    ON acciones (solicitud_id);
