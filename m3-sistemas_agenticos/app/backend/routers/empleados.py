"""Rutas de la API para la gestión de empleados."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import obtener_db
from departamentos import DEPARTAMENTOS
from models import Empleado
from schemas import EmpleadoBaja, EmpleadoCrear, EmpleadoEditar, EmpleadoSalida

router = APIRouter(prefix="/api")


@router.get("/departamentos")
def listar_departamentos() -> list[str]:
    return DEPARTAMENTOS


@router.get("/empleados", response_model=list[EmpleadoSalida])
def listar_empleados(
    busqueda: str | None = Query(default=None),
    departamento: str | None = Query(default=None),
    db: Session = Depends(obtener_db),
) -> list[Empleado]:
    if departamento is not None and departamento not in DEPARTAMENTOS:
        raise HTTPException(status_code=422, detail="Selecciona un departamento válido")

    consulta = db.query(Empleado)

    if busqueda:
        texto = f"%{busqueda.lower()}%"
        consulta = consulta.filter(
            func.lower(Empleado.nombre).like(texto)
            | func.lower(Empleado.correo).like(texto)
        )

    if departamento is not None:
        consulta = consulta.filter(Empleado.departamento == departamento)

    return consulta.order_by(Empleado.id).all()


@router.post("/empleados", response_model=EmpleadoSalida, status_code=201)
def crear_empleado(datos: EmpleadoCrear, db: Session = Depends(obtener_db)) -> Empleado:
    existente = (
        db.query(Empleado).filter(func.lower(Empleado.correo) == datos.correo).first()
    )
    if existente is not None:
        raise HTTPException(status_code=409, detail="El correo ya está registrado")

    total = db.query(func.count(Empleado.id)).scalar() or 0
    numero_empleado = f"EMP-{total + 1:04d}"

    empleado = Empleado(
        numero_empleado=numero_empleado,
        nombre=datos.nombre,
        correo=datos.correo,
        puesto=datos.puesto,
        departamento=datos.departamento,
        fecha_ingreso=datos.fecha_ingreso,
        estado="activo",
    )
    db.add(empleado)
    db.commit()
    db.refresh(empleado)
    return empleado


def _obtener_empleado_o_404(numero_empleado: str, db: Session) -> Empleado:
    empleado = (
        db.query(Empleado)
        .filter(Empleado.numero_empleado == numero_empleado)
        .first()
    )
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


@router.get("/empleados/{numero_empleado}", response_model=EmpleadoSalida)
def obtener_empleado(numero_empleado: str, db: Session = Depends(obtener_db)) -> Empleado:
    return _obtener_empleado_o_404(numero_empleado, db)


@router.put("/empleados/{numero_empleado}", response_model=EmpleadoSalida)
def editar_empleado(
    numero_empleado: str, datos: EmpleadoEditar, db: Session = Depends(obtener_db)
) -> Empleado:
    empleado = _obtener_empleado_o_404(numero_empleado, db)
    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409, detail="No se puede editar a un empleado dado de baja"
        )

    empleado.puesto = datos.puesto
    empleado.departamento = datos.departamento
    db.commit()
    db.refresh(empleado)
    return empleado


@router.patch("/empleados/{numero_empleado}/baja", response_model=EmpleadoSalida)
def dar_de_baja_empleado(
    numero_empleado: str, datos: EmpleadoBaja, db: Session = Depends(obtener_db)
) -> Empleado:
    empleado = _obtener_empleado_o_404(numero_empleado, db)
    if datos.fecha_baja < empleado.fecha_ingreso:
        raise HTTPException(
            status_code=422,
            detail="El campo fecha_baja es inválido: no puede ser anterior a la fecha de ingreso",
        )

    empleado.estado = "baja"
    empleado.fecha_baja = datos.fecha_baja
    db.commit()
    db.refresh(empleado)
    return empleado
