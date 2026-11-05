"""Pruebas de la API para HU-10: solicitar y consultar vacaciones."""

import uuid
from datetime import date

import httpx


def _datos_empleado(sufijo: str, **overrides) -> dict:
    datos = {
        "nombre": f"Empleado Vacaciones {sufijo}",
        "correo": f"vacaciones.{sufijo}@empresa.com",
        "puesto": "Analista de Datos",
        "departamento": "Tecnología",
        "fecha_ingreso": "2020-01-01",
    }
    datos.update(overrides)
    return datos


def _crear_empleado(url_api: str, sufijo: str, **overrides) -> dict:
    datos = _datos_empleado(sufijo, **overrides)
    respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def _dar_de_baja(url_api: str, numero_empleado: str, fecha_baja: str) -> dict:
    respuesta = httpx.patch(
        f"{url_api}/api/empleados/{numero_empleado}/baja",
        json={"fecha_baja": fecha_baja},
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def _crear_vacacion(url_api: str, empleado_id: int, fecha_inicio: str, fecha_fin: str) -> httpx.Response:
    return httpx.post(
        f"{url_api}/api/empleados/{empleado_id}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )


def test_cp01_registrar_solicitud_valida_descuenta_festivos_y_fines_de_semana(url_api):
    """CP-01: Registrar una solicitud válida descuenta festivos y fines de semana."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2025-12-21")

    respuesta = _crear_vacacion(url_api, emp["id"], "2026-12-21", "2026-12-31")

    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 8
    assert cuerpo["dias_restantes"] == 4
    assert cuerpo["empleado_id"] == emp["id"]


def test_cp03_consultar_saldo_con_solicitudes_registradas(url_api):
    """CP-03: Consultar el saldo del año con solicitudes registradas."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2025-12-21")
    respuesta = _crear_vacacion(url_api, emp["id"], "2026-12-21", "2026-12-31")
    assert respuesta.status_code == 201, respuesta.text

    respuesta = httpx.get(
        f"{url_api}/api/empleados/{emp['id']}/vacaciones", params={"anio": 2026}
    )

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_usados"] == 8
    assert cuerpo["dias_disponibles"] == 4
    assert len(cuerpo["solicitudes"]) == 1
    assert cuerpo["solicitudes"][0]["dias_habiles"] == 8


def test_cp04_consultar_saldo_sin_solicitudes_previas(url_api):
    """CP-04: Consultar el saldo de un año sin solicitudes previas."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    respuesta = httpx.get(
        f"{url_api}/api/empleados/{emp['id']}/vacaciones", params={"anio": 2027}
    )

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_usados"] == 0
    assert cuerpo["dias_disponibles"] == 12
    assert cuerpo["solicitudes"] == []


def test_cp05_consultar_saldo_sin_indicar_anio_usa_anio_en_curso(url_api):
    """CP-05: Consultar el saldo sin indicar el año usa el año en curso."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    respuesta = httpx.get(f"{url_api}/api/empleados/{emp['id']}/vacaciones")

    assert respuesta.status_code == 200, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_usados"] == 0
    assert cuerpo["dias_disponibles"] == 12
    assert cuerpo["anio"] == date.today().year


def test_cp07_registrar_solicitud_empleado_inexistente(url_api):
    """CP-07: Registrar una solicitud para un empleado que no existe."""
    respuesta = _crear_vacacion(url_api, 999999999, "2026-06-01", "2026-06-05")

    assert respuesta.status_code == 404, respuesta.text
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp08_consultar_saldo_empleado_inexistente(url_api):
    """CP-08: Consultar el saldo de un empleado que no existe."""
    respuesta = httpx.get(
        f"{url_api}/api/empleados/999999999/vacaciones", params={"anio": 2026}
    )

    assert respuesta.status_code == 404, respuesta.text
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp09_registrar_solicitud_empleado_dado_de_baja(url_api):
    """CP-09: Registrar una solicitud para un empleado dado de baja."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")
    _dar_de_baja(url_api, emp["numero_empleado"], "2024-05-10")

    respuesta = _crear_vacacion(url_api, emp["id"], "2026-06-01", "2026-06-05")

    assert respuesta.status_code == 409, respuesta.text
    assert (
        respuesta.json()["detail"]
        == "No se pueden solicitar vacaciones para un empleado dado de baja"
    )


def test_cp10_fecha_fin_anterior_a_fecha_inicio(url_api):
    """CP-10: La fecha de fin es anterior a la fecha de inicio."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2025-12-21")

    respuesta = _crear_vacacion(url_api, emp["id"], "2026-07-10", "2026-07-05")

    assert respuesta.status_code == 400, respuesta.text
    assert (
        respuesta.json()["detail"]
        == "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp12_periodo_cruza_de_un_anio_a_otro(url_api):
    """CP-12: El periodo cruza de un año a otro."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    respuesta = _crear_vacacion(url_api, emp["id"], "2026-12-28", "2027-01-08")

    assert respuesta.status_code == 400, respuesta.text
    assert (
        respuesta.json()["detail"]
        == "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp14_anio_fuera_de_la_tabla_de_festivos(url_api):
    """CP-14: El año de la solicitud no está en la tabla de festivos."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    respuesta = _crear_vacacion(url_api, emp["id"], "2028-06-01", "2028-06-05")

    assert respuesta.status_code == 400, respuesta.text
    assert respuesta.json()["detail"] == "Solo se pueden solicitar vacaciones en 2026 y 2027"


def test_cp16_fecha_con_formato_invalido_responde_422(url_api):
    """CP-16: Una fecha con formato inválido responde con el 422 automático de FastAPI."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    respuesta = _crear_vacacion(url_api, emp["id"], "2026-13-01", "2026-13-05")

    assert respuesta.status_code == 422, respuesta.text


def test_cp17_antiguedad_insuficiente_se_rechaza(url_api):
    """CP-17: Antigüedad insuficiente se rechaza."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2025-12-21")

    respuesta = _crear_vacacion(url_api, emp["id"], "2026-12-18", "2026-12-18")

    assert respuesta.status_code == 400, respuesta.text
    assert (
        respuesta.json()["detail"]
        == "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp19_limite_antiguedad_cumplir_exactamente_un_anio_se_acepta(url_api):
    """CP-19: Límite de antigüedad, cumplir exactamente un año se acepta."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2025-12-21")

    respuesta = _crear_vacacion(url_api, emp["id"], "2026-12-21", "2026-12-21")

    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 1
    assert cuerpo["dias_restantes"] == 11


def test_cp21_limite_antiguedad_un_dia_antes_de_cumplir_el_anio_se_rechaza(url_api):
    """CP-21: Límite de antigüedad, un día antes de cumplir el año se rechaza."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2025-12-21")

    respuesta = _crear_vacacion(url_api, emp["id"], "2026-12-20", "2026-12-20")

    assert respuesta.status_code == 400, respuesta.text
    assert (
        respuesta.json()["detail"]
        == "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp23_periodo_sin_ningun_dia_habil_se_rechaza(url_api):
    """CP-23: Un periodo sin ningún día hábil se rechaza."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    respuesta = _crear_vacacion(url_api, emp["id"], "2026-07-11", "2026-07-12")

    assert respuesta.status_code == 400, respuesta.text
    assert respuesta.json()["detail"] == "El periodo no incluye días hábiles"


def test_cp25_limite_tope_anual_usar_exactamente_12_dias_se_acepta(url_api):
    """CP-25: Límite del tope anual, usar exactamente los 12 días disponibles se acepta."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    respuesta = _crear_vacacion(url_api, emp["id"], "2026-06-01", "2026-06-16")

    assert respuesta.status_code == 201, respuesta.text
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 12
    assert cuerpo["dias_restantes"] == 0


def test_cp27_limite_tope_anual_un_dia_mas_de_los_disponibles_se_rechaza(url_api):
    """CP-27: Límite del tope anual, pedir un día hábil más de los disponibles se rechaza."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    respuesta = _crear_vacacion(url_api, emp["id"], "2026-06-01", "2026-06-17")

    assert respuesta.status_code == 400, respuesta.text
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 12 días hábiles"
    )


def test_cp29_ya_no_quedan_dias_disponibles_en_el_anio(url_api):
    """CP-29: Ya no quedan días disponibles en el año."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")
    respuesta = _crear_vacacion(url_api, emp["id"], "2026-06-01", "2026-06-16")
    assert respuesta.status_code == 201, respuesta.text

    respuesta = _crear_vacacion(url_api, emp["id"], "2026-08-03", "2026-08-03")

    assert respuesta.status_code == 400, respuesta.text
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 0 días hábiles"
    )
