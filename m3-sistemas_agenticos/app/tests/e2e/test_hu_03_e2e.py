"""Pruebas end-to-end para HU-03: editar y dar de baja a un empleado."""

import uuid
from datetime import date

import httpx
from playwright.sync_api import expect


def _datos_empleado(sufijo: str, **overrides) -> dict:
    datos = {
        "nombre": f"Empleado Prueba {sufijo}",
        "correo": f"empleado.{sufijo}@empresa.com",
        "puesto": "Analista de Datos",
        "departamento": "Tecnología",
        "fecha_ingreso": date.today().isoformat(),
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


def test_cp02_editar_puesto_y_departamento_e2e(page, url_web, url_api):
    """CP-02: Editar correctamente el puesto y el departamento de un empleado activo."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo)
    numero = emp["numero_empleado"]

    page.goto(url_web)

    fila = page.get_by_test_id(f"fila-empleado-{numero}")
    expect(fila).to_be_visible()
    page.get_by_test_id(f"editar-empleado-{numero}").click()

    page.get_by_test_id("empleado-puesto").fill("Líder de Datos")
    page.get_by_test_id("empleado-departamento").select_option("Finanzas")
    page.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    fila = page.get_by_test_id(f"fila-empleado-{numero}")
    expect(fila).to_contain_text("Líder de Datos")
    expect(fila).to_contain_text("Finanzas")
    expect(page.get_by_test_id(f"numero-empleado-{numero}")).to_have_text(numero)


def test_cp04_dar_de_baja_empleado_activo_e2e(page, url_web, url_api):
    """CP-04: Dar de baja correctamente a un empleado activo."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2022-03-01")
    numero = emp["numero_empleado"]

    page.goto(url_web)

    fila = page.get_by_test_id(f"fila-empleado-{numero}")
    expect(fila).to_be_visible()
    page.get_by_test_id(f"baja-empleado-{numero}").click()

    page.get_by_test_id("empleado-fecha-baja").fill("2024-05-10")
    page.get_by_test_id("confirmar-baja").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    expect(page.get_by_test_id(f"estado-empleado-{numero}")).to_have_text("Baja")
    expect(page.get_by_test_id(f"fila-empleado-{numero}")).to_be_visible()


def test_cp06_editar_con_puesto_invalido_e2e(page, url_web, url_api):
    """CP-06: Intentar editar un empleado con un puesto inválido."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo)
    numero = emp["numero_empleado"]

    page.goto(url_web)

    page.get_by_test_id(f"editar-empleado-{numero}").click()
    page.get_by_test_id("empleado-puesto").fill("A")
    page.get_by_test_id("empleado-guardar").click()

    mensaje = page.get_by_test_id("mensaje-error")
    expect(mensaje).to_be_visible()
    expect(mensaje).to_contain_text("puesto")


def test_cp08_editar_empleado_dado_de_baja_e2e(page, url_web, url_api):
    """CP-08: Intentar editar a un empleado que ya está dado de baja."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2022-03-01")
    numero = emp["numero_empleado"]
    _dar_de_baja(url_api, numero, "2024-05-10")

    page.goto(url_web)

    fila = page.get_by_test_id(f"fila-empleado-{numero}")
    expect(fila).to_be_visible()
    expect(page.get_by_test_id(f"estado-empleado-{numero}")).to_have_text("Baja")

    page.get_by_test_id(f"editar-empleado-{numero}").click()
    page.get_by_test_id("empleado-puesto").fill("Gerente de Ventas")
    page.get_by_test_id("empleado-guardar").click()

    mensaje = page.get_by_test_id("mensaje-error")
    expect(mensaje).to_be_visible()
    expect(mensaje).to_contain_text("No se puede editar a un empleado dado de baja")


def test_cp10_dar_de_baja_con_fecha_anterior_a_ingreso_e2e(page, url_web, url_api):
    """CP-10: Intentar dar de baja con una fecha de baja anterior a la fecha de ingreso."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2022-03-01")
    numero = emp["numero_empleado"]

    page.goto(url_web)

    page.get_by_test_id(f"baja-empleado-{numero}").click()
    page.get_by_test_id("empleado-fecha-baja").fill("2021-01-01")
    page.get_by_test_id("confirmar-baja").click()

    mensaje = page.get_by_test_id("mensaje-error")
    expect(mensaje).to_be_visible()
    expect(mensaje).to_contain_text("fecha_baja")
