"""Esquemas Pydantic para la aplicación de empleados."""

from datetime import date, datetime

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator

from departamentos import DEPARTAMENTOS


class EmpleadoCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=80)
    correo: str
    puesto: str = Field(min_length=2, max_length=60)
    departamento: str
    fecha_ingreso: date

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor: str) -> str:
        valor = valor.strip().lower()
        if not valor.endswith("@empresa.com"):
            raise HTTPException(
                status_code=422, detail="Usa el correo corporativo @empresa.com"
            )
        return valor

    @field_validator("departamento")
    @classmethod
    def validar_departamento(cls, valor: str) -> str:
        if valor not in DEPARTAMENTOS:
            raise ValueError("departamento inválido")
        return valor

    @field_validator("fecha_ingreso")
    @classmethod
    def validar_fecha_ingreso(cls, valor: date) -> date:
        if valor > date.today():
            raise HTTPException(
                status_code=422, detail="La fecha de ingreso no puede ser futura"
            )
        return valor


class EmpleadoEditar(BaseModel):
    puesto: str = Field(min_length=2, max_length=60)
    departamento: str

    @field_validator("departamento")
    @classmethod
    def validar_departamento(cls, valor: str) -> str:
        if valor not in DEPARTAMENTOS:
            raise ValueError("departamento inválido")
        return valor


class EmpleadoBaja(BaseModel):
    fecha_baja: date


class EmpleadoSalida(BaseModel):
    id: int
    numero_empleado: str
    nombre: str
    correo: str
    puesto: str
    departamento: str
    fecha_ingreso: date
    estado: str
    fecha_baja: date | None
    creado_en: datetime

    model_config = {"from_attributes": True}


class VacacionCrear(BaseModel):
    fecha_inicio: date
    fecha_fin: date


class VacacionRespuesta(BaseModel):
    id: int
    empleado_id: int
    fecha_inicio: date
    fecha_fin: date
    dias_habiles: int
    dias_restantes: int

    model_config = {"from_attributes": True}


class SolicitudResumen(BaseModel):
    id: int
    fecha_inicio: date
    fecha_fin: date
    dias_habiles: int

    model_config = {"from_attributes": True}


class SaldoVacaciones(BaseModel):
    empleado_id: int
    anio: int
    dias_usados: int
    dias_disponibles: int
    solicitudes: list[SolicitudResumen]
