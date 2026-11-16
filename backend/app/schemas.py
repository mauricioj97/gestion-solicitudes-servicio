"""Modelos de entrada de la API con sus validaciones (mensajes en español)."""
import re

from pydantic import BaseModel, ConfigDict, field_validator

RE_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+$")
RE_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


def validar_texto(valor: str, campo: str, minimo: int, maximo: int) -> str:
    valor = valor.strip()
    if not valor:
        raise ValueError(f"El campo {campo} es obligatorio")
    if len(valor) < minimo:
        raise ValueError(f"El campo {campo} debe tener al menos {minimo} caracteres")
    if len(valor) > maximo:
        raise ValueError(f"El campo {campo} debe tener máximo {maximo} caracteres")
    return valor


def validar_digitos(valor: str, campo: str, minimo: int, maximo: int) -> str:
    valor = valor.strip()
    if not valor.isdigit() or not (minimo <= len(valor) <= maximo):
        raise ValueError(f"El campo {campo} debe tener solo números, entre {minimo} y {maximo} dígitos")
    return valor


class SolicitudCrear(BaseModel):
    nombre: str
    cedula: str
    direccion: str
    telefono: str
    correo: str
    tipo_id: int
    asunto: str
    descripcion: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "María Fernanda López",
                "cedula": "1085123456",
                "direccion": "Calle 18 # 25-40, Pasto",
                "telefono": "3104567890",
                "correo": "maria.lopez@correo.com",
                "tipo_id": 1,
                "asunto": "Certificado de residencia",
                "descripcion": "Solicito un certificado de residencia para presentar en mi trabajo.",
            }
        }
    )

    @field_validator("nombre")
    @classmethod
    def v_nombre(cls, v: str) -> str:
        v = " ".join(validar_texto(v, "nombre", 3, 100).split())
        if not RE_NOMBRE.match(v):
            raise ValueError("El campo nombre solo admite letras y espacios")
        return v

    @field_validator("cedula")
    @classmethod
    def v_cedula(cls, v: str) -> str:
        return validar_digitos(v, "cédula", 6, 10)

    @field_validator("direccion")
    @classmethod
    def v_direccion(cls, v: str) -> str:
        return validar_texto(v, "dirección", 5, 150)

    @field_validator("telefono")
    @classmethod
    def v_telefono(cls, v: str) -> str:
        return validar_digitos(v, "teléfono", 7, 10)

    @field_validator("correo")
    @classmethod
    def v_correo(cls, v: str) -> str:
        v = v.strip().lower()
        if not RE_CORREO.match(v) or len(v) > 120:
            raise ValueError("El campo correo no tiene un formato válido (ejemplo: nombre@dominio.com)")
        return v

    @field_validator("asunto")
    @classmethod
    def v_asunto(cls, v: str) -> str:
        return validar_texto(v, "asunto", 5, 120)

    @field_validator("descripcion")
    @classmethod
    def v_descripcion(cls, v: str) -> str:
        return validar_texto(v, "descripción", 10, 2000)


class LoginEntrada(BaseModel):
    usuario: str
    contrasena: str

    model_config = ConfigDict(json_schema_extra={"example": {"usuario": "coordinacion", "contrasena": "********"}})


class AsignarEntrada(BaseModel):
    encargado_id: int

    model_config = ConfigDict(json_schema_extra={"example": {"encargado_id": 2}})


class EvaluarEntrada(BaseModel):
    observacion: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"observacion": "Solicitud revisada: la información está completa y procede."}}
    )

    @field_validator("observacion")
    @classmethod
    def v(cls, v: str) -> str:
        return validar_texto(v, "observación", 10, 2000)


class SeguimientoEntrada(BaseModel):
    nota: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"nota": "Se verificaron los datos en el sistema interno."}}
    )

    @field_validator("nota")
    @classmethod
    def v(cls, v: str) -> str:
        return validar_texto(v, "nota", 10, 2000)


class FinalizarEntrada(BaseModel):
    respuesta: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"respuesta": "Su certificado fue expedido y puede descargarlo en la sede principal."}}
    )

    @field_validator("respuesta")
    @classmethod
    def v(cls, v: str) -> str:
        return validar_texto(v, "respuesta", 10, 2000)


class CerrarEntrada(BaseModel):
    motivo: str

    model_config = ConfigDict(
        json_schema_extra={"example": {"motivo": "Solicitud duplicada: ya existe el radicado 51842093."}}
    )

    @field_validator("motivo")
    @classmethod
    def v(cls, v: str) -> str:
        return validar_texto(v, "motivo", 10, 2000)
