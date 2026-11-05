"""Pruebas de la API para HU-02: ver y buscar el directorio de empleados."""

import uuid
from datetime import date

import httpx
import pytest


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


def test_cp01_ver_directorio_completo(url_api):
    """CP-01: Ver el directorio completo de empleados."""
    sufijo = uuid.uuid4().hex[:8]
    emp1 = _crear_empleado(url_api, f"{sufijo}-a", departamento="Tecnología", puesto="Analista")
    emp2 = _crear_empleado(url_api, f"{sufijo}-b", departamento="Ventas", puesto="Vendedor")

    respuesta = httpx.get(f"{url_api}/api/empleados")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    correos = {emp1["correo"], emp2["correo"]}
    encontrados = [empleado for empleado in cuerpo if empleado["correo"] in correos]
    assert len(encontrados) == 2
    for empleado in encontrados:
        assert empleado["numero_empleado"]
        assert empleado["nombre"]
        assert empleado["puesto"]
        assert empleado["departamento"]
        assert empleado["estado"] == "activo"


def test_cp03_buscar_empleado_por_nombre(url_api):
    """CP-03: Buscar un empleado por nombre."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, nombre=f"Ana Torres {sufijo}")

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"busqueda": f"Torres {sufijo}"})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["numero_empleado"] == emp["numero_empleado"]
    assert cuerpo[0]["nombre"] == f"Ana Torres {sufijo}"


def test_cp05_buscar_empleado_por_correo(url_api):
    """CP-05: Buscar un empleado por correo."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, nombre=f"Luis Pérez {sufijo}")

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"busqueda": emp["correo"]})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["numero_empleado"] == emp["numero_empleado"]
    assert cuerpo[0]["nombre"] == f"Luis Pérez {sufijo}"


def test_cp07_busqueda_no_distingue_mayusculas(url_api):
    """CP-07: La búsqueda no distingue mayúsculas de minúsculas."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, nombre=f"Ana Torres {sufijo}")

    respuesta = httpx.get(
        f"{url_api}/api/empleados", params={"busqueda": f"ANA TORRES {sufijo}".upper()}
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo) == 1
    assert cuerpo[0]["numero_empleado"] == emp["numero_empleado"]
    assert cuerpo[0]["nombre"] == f"Ana Torres {sufijo}"


def test_cp09_filtrar_por_departamento(url_api):
    """CP-09: Filtrar empleados por departamento."""
    sufijo = uuid.uuid4().hex[:8]
    emp1 = _crear_empleado(
        url_api, f"{sufijo}-a", nombre=f"Tecno Uno {sufijo}", departamento="Tecnología"
    )
    emp2 = _crear_empleado(
        url_api, f"{sufijo}-b", nombre=f"Tecno Dos {sufijo}", departamento="Tecnología"
    )
    _crear_empleado(url_api, f"{sufijo}-c", nombre=f"Ventas Uno {sufijo}", departamento="Ventas")

    # Se combina con "busqueda" (mismo sufijo) para aislar del resto de empleados
    # ya existentes en la base y poder afirmar la cantidad exacta de resultados.
    respuesta = httpx.get(
        f"{url_api}/api/empleados",
        params={"departamento": "Tecnología", "busqueda": sufijo},
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo) == 2
    numeros = {empleado["numero_empleado"] for empleado in cuerpo}
    assert numeros == {emp1["numero_empleado"], emp2["numero_empleado"]}
    assert all(empleado["departamento"] == "Tecnología" for empleado in cuerpo)


def test_cp11_buscar_texto_sin_coincidencias(url_api):
    """CP-11: Buscar un texto que no coincide con ningún empleado."""
    sufijo = uuid.uuid4().hex[:8]
    _crear_empleado(url_api, sufijo)

    respuesta = httpx.get(
        f"{url_api}/api/empleados",
        params={"busqueda": f"sin-coincidencia-{uuid.uuid4().hex}"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_cp13_empleado_dado_de_baja_aparece_en_directorio(url_api):
    """CP-13: Un empleado dado de baja sigue apareciendo en el directorio."""
    pytest.skip(
        "No existe en la API una forma de dar de baja a un empleado "
        "(POST /api/empleados siempre crea estado='activo' y no hay otro endpoint "
        "para cambiar el estado); no se puede preparar la precondición sin "
        "modificar la aplicación."
    )
