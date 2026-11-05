"""Pruebas de la API para HU-03: editar y dar de baja a un empleado."""

import uuid
from datetime import date

import httpx


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


def test_cp01_editar_puesto_y_departamento(url_api):
    """CP-01: Editar correctamente el puesto y el departamento de un empleado activo."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo)
    numero = emp["numero_empleado"]

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{numero}",
        json={"puesto": "Líder de Datos", "departamento": "Finanzas"},
    )

    assert respuesta.status_code == 200, respuesta.text

    respuesta = httpx.get(f"{url_api}/api/empleados/{numero}")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["puesto"] == "Líder de Datos"
    assert cuerpo["departamento"] == "Finanzas"
    assert cuerpo["numero_empleado"] == numero
    assert cuerpo["correo"] == emp["correo"]


def test_cp03_dar_de_baja_empleado_activo(url_api):
    """CP-03: Dar de baja correctamente a un empleado activo."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2022-03-01")
    numero = emp["numero_empleado"]

    respuesta = httpx.patch(
        f"{url_api}/api/empleados/{numero}/baja",
        json={"fecha_baja": "2024-05-10"},
    )

    assert respuesta.status_code == 200, respuesta.text

    respuesta = httpx.get(f"{url_api}/api/empleados/{numero}")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "baja"
    assert cuerpo["fecha_baja"] == "2024-05-10"

    respuesta = httpx.get(f"{url_api}/api/empleados")
    assert respuesta.status_code == 200
    numeros = {empleado["numero_empleado"] for empleado in respuesta.json()}
    assert numero in numeros


def test_cp05_editar_con_puesto_invalido(url_api):
    """CP-05: Intentar editar un empleado con un puesto inválido."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo)
    numero = emp["numero_empleado"]

    respuesta = httpx.put(f"{url_api}/api/empleados/{numero}", json={"puesto": "A"})

    assert respuesta.status_code == 422, respuesta.text
    assert "puesto" in respuesta.json()["detail"]


def test_cp07_editar_empleado_dado_de_baja(url_api):
    """CP-07: Intentar editar a un empleado que ya está dado de baja."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2022-03-01")
    numero = emp["numero_empleado"]
    _dar_de_baja(url_api, numero, "2024-05-10")

    respuesta = httpx.put(
        f"{url_api}/api/empleados/{numero}",
        json={"puesto": "Gerente de Ventas", "departamento": "Ventas"},
    )

    assert respuesta.status_code == 409, respuesta.text
    assert respuesta.json()["detail"] == "No se puede editar a un empleado dado de baja"


def test_cp09_dar_de_baja_con_fecha_anterior_a_ingreso(url_api):
    """CP-09: Intentar dar de baja con una fecha de baja anterior a la fecha de ingreso."""
    sufijo = uuid.uuid4().hex[:8]
    emp = _crear_empleado(url_api, sufijo, fecha_ingreso="2022-03-01")
    numero = emp["numero_empleado"]

    respuesta = httpx.patch(
        f"{url_api}/api/empleados/{numero}/baja",
        json={"fecha_baja": "2021-01-01"},
    )

    assert respuesta.status_code == 422, respuesta.text
    assert "fecha_baja" in respuesta.json()["detail"]
