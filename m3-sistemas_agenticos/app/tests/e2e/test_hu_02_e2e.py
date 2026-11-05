"""Pruebas end-to-end para HU-02: ver y buscar el directorio de empleados."""

import uuid
from datetime import date

import httpx
import pytest
from playwright.sync_api import expect


def _datos_empleado(sufijo: str, **overrides) -> dict:
    datos = {
        "nombre": f"Empleado Prueba {sufijo}",
        "correo": f"empleado.{sufijo}@empresa.com",
        "puesto": "Analista",
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


def test_cp02_ver_directorio_completo_e2e(page, url_web, url_api):
    """CP-02: Ver el directorio completo de empleados."""
    sufijo = uuid.uuid4().hex[:8]
    emp1 = _crear_empleado(url_api, f"{sufijo}-a", departamento="Tecnología", puesto="Analista")
    emp2 = _crear_empleado(url_api, f"{sufijo}-b", departamento="Ventas", puesto="Vendedor")

    page.goto(url_web)

    expect(page.get_by_test_id("tabla-empleados")).to_be_visible()

    for empleado in (emp1, emp2):
        numero = empleado["numero_empleado"]
        expect(page.get_by_test_id(f"fila-empleado-{numero}")).to_be_visible()
        expect(page.get_by_test_id(f"numero-empleado-{numero}")).to_be_visible()
        expect(page.get_by_test_id(f"estado-empleado-{numero}")).to_be_visible()


def test_cp04_buscar_empleado_por_nombre_e2e(page, url_web, url_api):
    """CP-04: Buscar un empleado por nombre."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, nombre=f"Ana Torres {sufijo}")

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(f"Torres {sufijo}")

    filas = page.locator('[data-testid^="fila-empleado-"]')
    expect(filas).to_have_count(1)
    expect(page.get_by_test_id(f"numero-empleado-{emp['numero_empleado']}")).to_be_visible()


def test_cp06_buscar_empleado_por_correo_e2e(page, url_web, url_api):
    """CP-06: Buscar un empleado por correo."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, nombre=f"Luis Pérez {sufijo}")

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(emp["correo"])

    filas = page.locator('[data-testid^="fila-empleado-"]')
    expect(filas).to_have_count(1)
    expect(page.get_by_test_id(f"numero-empleado-{emp['numero_empleado']}")).to_be_visible()


def test_cp08_busqueda_no_distingue_mayusculas_e2e(page, url_web, url_api):
    """CP-08: La búsqueda no distingue mayúsculas de minúsculas."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, nombre=f"Ana Torres {sufijo}")

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(f"ANA TORRES {sufijo}".upper())

    filas = page.locator('[data-testid^="fila-empleado-"]')
    expect(filas).to_have_count(1)
    expect(page.get_by_test_id(f"numero-empleado-{emp['numero_empleado']}")).to_be_visible()


def test_cp10_filtrar_por_departamento_e2e(page, url_web, url_api):
    """CP-10: Filtrar empleados por departamento."""
    sufijo = uuid.uuid4().hex[:8]
    emp1 = _crear_empleado(
        url_api, f"{sufijo}-a", nombre=f"Tecno Uno {sufijo}", departamento="Tecnología"
    )
    emp2 = _crear_empleado(
        url_api, f"{sufijo}-b", nombre=f"Tecno Dos {sufijo}", departamento="Tecnología"
    )
    _crear_empleado(url_api, f"{sufijo}-c", nombre=f"Ventas Uno {sufijo}", departamento="Ventas")

    page.goto(url_web)
    # Se combina con la búsqueda (mismo sufijo) para aislar del resto de
    # empleados ya existentes y poder afirmar la cantidad exacta de filas.
    page.get_by_test_id("buscar-empleados").fill(sufijo)
    page.get_by_test_id("filtro-departamento").select_option("Tecnología")

    for empleado in (emp1, emp2):
        fila = page.get_by_test_id(f"fila-empleado-{empleado['numero_empleado']}")
        expect(fila).to_be_visible()
        expect(fila).to_contain_text("Tecnología")

    filas = page.locator('[data-testid^="fila-empleado-"]')
    expect(filas).to_have_count(2)


def test_cp12_buscar_texto_sin_coincidencias_e2e(page, url_web, url_api):
    """CP-12: Buscar un texto que no coincide con ningún empleado."""
    sufijo = uuid.uuid4().hex[:8]
    _crear_empleado(url_api, sufijo)

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(f"sin-coincidencia-{uuid.uuid4().hex}")

    expect(page.get_by_test_id("sin-resultados")).to_be_visible()
    expect(page.get_by_test_id("sin-resultados")).to_have_text("No se encontraron empleados")
    expect(page.get_by_test_id("tabla-empleados")).not_to_be_visible()


def test_cp14_empleado_dado_de_baja_aparece_en_directorio_e2e(page, url_web, url_api):
    """CP-14: Un empleado dado de baja sigue apareciendo en el directorio."""
    pytest.skip(
        "No existe en la API una forma de dar de baja a un empleado "
        "(POST /api/empleados siempre crea estado='activo' y no hay otro endpoint "
        "para cambiar el estado); no se puede preparar la precondición sin "
        "modificar la aplicación."
    )
