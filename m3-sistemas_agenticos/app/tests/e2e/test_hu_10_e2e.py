"""Pruebas end-to-end para HU-10: solicitar y consultar vacaciones."""

import uuid

import httpx
from playwright.sync_api import expect


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


def _crear_vacacion(url_api: str, empleado_id: int, fecha_inicio: str, fecha_fin: str) -> httpx.Response:
    return httpx.post(
        f"{url_api}/api/empleados/{empleado_id}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )


def test_cp02_registrar_solicitud_valida_e2e(page, url_web, url_api):
    """CP-02: Registrar una solicitud válida descuenta festivos y fines de semana."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2025-12-21")

    page.goto(url_web)

    page.get_by_test_id(f"vacaciones-abrir-{emp['id']}").click()
    expect(page.get_by_test_id("vacaciones-disponibles")).to_have_text("12")
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-21")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-31")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    expect(mensaje).to_have_text(
        "Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026."
    )


def test_cp06_consultar_saldo_sin_indicar_anio_usa_anio_en_curso_e2e(page, url_web, url_api):
    """CP-06: Consultar el saldo sin indicar el año usa el año en curso."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    page.goto(url_web)

    page.get_by_test_id(f"vacaciones-abrir-{emp['id']}").click()

    expect(page.get_by_test_id("vacaciones-disponibles")).to_have_text("12")


def test_cp11_fecha_fin_anterior_a_fecha_inicio_e2e(page, url_web, url_api):
    """CP-11: La fecha de fin es anterior a la fecha de inicio."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2025-12-21")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{emp['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-10")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-05")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    expect(mensaje).to_have_text("La fecha de fin no puede ser anterior a la fecha de inicio")


def test_cp13_periodo_cruza_de_un_anio_a_otro_e2e(page, url_web, url_api):
    """CP-13: El periodo cruza de un año a otro."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{emp['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-28")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2027-01-08")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    expect(mensaje).to_have_text("Las vacaciones deben estar dentro de un mismo año calendario")


def test_cp15_anio_fuera_de_la_tabla_de_festivos_e2e(page, url_web, url_api):
    """CP-15: El año de la solicitud no está en la tabla de festivos."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{emp['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2028-06-01")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2028-06-05")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    expect(mensaje).to_have_text("Solo se pueden solicitar vacaciones en 2026 y 2027")


def test_cp18_antiguedad_insuficiente_se_rechaza_e2e(page, url_web, url_api):
    """CP-18: Antigüedad insuficiente se rechaza."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2025-12-21")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{emp['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-18")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-18")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    expect(mensaje).to_have_text("Se requiere al menos un año de antigüedad a la fecha de inicio")


def test_cp20_limite_antiguedad_cumplir_exactamente_un_anio_se_acepta_e2e(page, url_web, url_api):
    """CP-20: Límite de antigüedad, cumplir exactamente un año se acepta."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2025-12-21")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{emp['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-21")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-21")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    expect(mensaje).to_have_text(
        "Solicitud registrada: 1 días hábiles. Te quedan 11 días hábiles en 2026."
    )


def test_cp22_limite_antiguedad_un_dia_antes_de_cumplir_el_anio_se_rechaza_e2e(page, url_web, url_api):
    """CP-22: Límite de antigüedad, un día antes de cumplir el año se rechaza."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2025-12-21")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{emp['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-20")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-20")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    expect(mensaje).to_have_text("Se requiere al menos un año de antigüedad a la fecha de inicio")


def test_cp24_periodo_sin_ningun_dia_habil_se_rechaza_e2e(page, url_web, url_api):
    """CP-24: Un periodo sin ningún día hábil se rechaza."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{emp['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-11")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-12")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    expect(mensaje).to_have_text("El periodo no incluye días hábiles")


def test_cp26_limite_tope_anual_usar_exactamente_12_dias_se_acepta_e2e(page, url_web, url_api):
    """CP-26: Límite del tope anual, usar exactamente los 12 días disponibles se acepta."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{emp['id']}").click()
    expect(page.get_by_test_id("vacaciones-disponibles")).to_have_text("12")
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-06-01")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-06-16")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    expect(mensaje).to_have_text(
        "Solicitud registrada: 12 días hábiles. Te quedan 0 días hábiles en 2026."
    )


def test_cp28_limite_tope_anual_un_dia_mas_de_los_disponibles_se_rechaza_e2e(page, url_web, url_api):
    """CP-28: Límite del tope anual, pedir un día hábil más de los disponibles se rechaza."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{emp['id']}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-06-01")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-06-17")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    expect(mensaje).to_have_text(
        "La solicitud excede los días disponibles: quedan 12 días hábiles"
    )


def test_cp30_ya_no_quedan_dias_disponibles_en_el_anio_e2e(page, url_web, url_api):
    """CP-30: Ya no quedan días disponibles en el año."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2020-01-01")
    respuesta = _crear_vacacion(url_api, emp["id"], "2026-06-01", "2026-06-16")
    assert respuesta.status_code == 201, respuesta.text

    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{emp['id']}").click()
    expect(page.get_by_test_id("vacaciones-disponibles")).to_have_text("0")
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-08-03")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-08-03")
    page.get_by_test_id("vacaciones-enviar").click()

    mensaje = page.get_by_test_id("vacaciones-mensaje")
    expect(mensaje).to_have_text(
        "La solicitud excede los días disponibles: quedan 0 días hábiles"
    )
