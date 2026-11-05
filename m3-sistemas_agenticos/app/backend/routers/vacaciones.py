"""Rutas de la API para solicitar y consultar vacaciones."""

from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import obtener_db
from festivos import FESTIVOS, dias_habiles_en_periodo
from models import Empleado, Vacacion
from schemas import SaldoVacaciones, SolicitudResumen, VacacionCrear, VacacionRespuesta

router = APIRouter(prefix="/api")

DIAS_DISPONIBLES_POR_ANIO = 12


def _obtener_empleado_o_404(empleado_id: int, db: Session) -> Empleado:
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


def _sumar_anios(fecha: date, anios: int) -> date:
    try:
        return fecha.replace(year=fecha.year + anios)
    except ValueError:
        # fecha_ingreso es 29 de febrero y el año destino no es bisiesto.
        return date(fecha.year + anios, 3, 1)


def _solicitudes_del_anio(empleado_id: int, anio: int, db: Session) -> list[Vacacion]:
    return (
        db.query(Vacacion)
        .filter(Vacacion.empleado_id == empleado_id)
        .filter(Vacacion.fecha_inicio >= date(anio, 1, 1))
        .filter(Vacacion.fecha_inicio <= date(anio, 12, 31))
        .order_by(Vacacion.id)
        .all()
    )


@router.post(
    "/empleados/{empleado_id}/vacaciones",
    response_model=VacacionRespuesta,
    status_code=201,
)
def crear_vacacion(
    empleado_id: int, datos: VacacionCrear, db: Session = Depends(obtener_db)
) -> VacacionRespuesta:
    empleado = _obtener_empleado_o_404(empleado_id, db)

    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409,
            detail="No se pueden solicitar vacaciones para un empleado dado de baja",
        )

    if datos.fecha_fin < datos.fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha de fin no puede ser anterior a la fecha de inicio",
        )

    if datos.fecha_inicio.year != datos.fecha_fin.year:
        raise HTTPException(
            status_code=400,
            detail="Las vacaciones deben estar dentro de un mismo año calendario",
        )

    anio = datos.fecha_inicio.year
    if anio not in FESTIVOS:
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden solicitar vacaciones en 2026 y 2027",
        )

    if datos.fecha_inicio < _sumar_anios(empleado.fecha_ingreso, 1):
        raise HTTPException(
            status_code=400,
            detail="Se requiere al menos un año de antigüedad a la fecha de inicio",
        )

    dias_habiles = dias_habiles_en_periodo(datos.fecha_inicio, datos.fecha_fin)
    if dias_habiles == 0:
        raise HTTPException(status_code=400, detail="El periodo no incluye días hábiles")

    dias_usados = sum(s.dias_habiles for s in _solicitudes_del_anio(empleado_id, anio, db))
    dias_disponibles = DIAS_DISPONIBLES_POR_ANIO - dias_usados
    if dias_habiles > dias_disponibles:
        raise HTTPException(
            status_code=400,
            detail=(
                "La solicitud excede los días disponibles: "
                f"quedan {dias_disponibles} días hábiles"
            ),
        )

    vacacion = Vacacion(
        empleado_id=empleado_id,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        dias_habiles=dias_habiles,
    )
    db.add(vacacion)
    db.commit()
    db.refresh(vacacion)

    return VacacionRespuesta(
        id=vacacion.id,
        empleado_id=vacacion.empleado_id,
        fecha_inicio=vacacion.fecha_inicio,
        fecha_fin=vacacion.fecha_fin,
        dias_habiles=vacacion.dias_habiles,
        dias_restantes=dias_disponibles - dias_habiles,
    )


@router.get("/empleados/{empleado_id}/vacaciones", response_model=SaldoVacaciones)
def consultar_saldo(
    empleado_id: int,
    anio: int | None = Query(default=None),
    db: Session = Depends(obtener_db),
) -> SaldoVacaciones:
    _obtener_empleado_o_404(empleado_id, db)

    anio_consulta = anio if anio is not None else datetime.now().year
    solicitudes = _solicitudes_del_anio(empleado_id, anio_consulta, db)
    dias_usados = sum(s.dias_habiles for s in solicitudes)

    return SaldoVacaciones(
        empleado_id=empleado_id,
        anio=anio_consulta,
        dias_usados=dias_usados,
        dias_disponibles=DIAS_DISPONIBLES_POR_ANIO - dias_usados,
        solicitudes=[
            SolicitudResumen(
                id=s.id,
                fecha_inicio=s.fecha_inicio,
                fecha_fin=s.fecha_fin,
                dias_habiles=s.dias_habiles,
            )
            for s in solicitudes
        ],
    )
