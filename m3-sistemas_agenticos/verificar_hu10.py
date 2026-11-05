"""Verificación independiente de HU-10 contra convenciones_vacaciones.md (no usa las pruebas de la fábrica)."""
import uuid

import httpx

API = "http://localhost:8000/api"
resultados = []


def empleado(fecha_ingreso="2024-01-15"):
    r = httpx.post(f"{API}/empleados", json={
        "nombre": "Prueba Vacaciones", "correo": f"v{uuid.uuid4().hex[:8]}@empresa.com",
        "puesto": "Analista", "departamento": "Ventas", "fecha_ingreso": fecha_ingreso})
    r.raise_for_status()
    return r.json()


def solicitar(eid, inicio, fin):
    return httpx.post(f"{API}/empleados/{eid}/vacaciones", json={"fecha_inicio": inicio, "fecha_fin": fin})


def revisar(nombre, r, codigo, detail=None, **campos):
    cuerpo = r.json()
    bien = (r.status_code == codigo and (detail is None or cuerpo.get("detail") == detail)
            and all(cuerpo.get(k) == v for k, v in campos.items()))
    resultados.append(bien)
    print("PASA " if bien else "FALLA", nombre, "" if bien else f"-> {r.status_code} {cuerpo}")


e = empleado()
revisar("Alta válida 21-31 dic (8 días, festivo)", solicitar(e["id"], "2026-12-21", "2026-12-31"), 201,
        dias_habiles=8, dias_restantes=4, empleado_id=e["id"], fecha_inicio="2026-12-21")
revisar("GET saldo 2026", httpx.get(f"{API}/empleados/{e['id']}/vacaciones", params={"anio": 2026}), 200,
        empleado_id=e["id"], anio=2026, dias_usados=8, dias_disponibles=4)
revisar("Rebasa por uno (5 con 4 disponibles)", solicitar(e["id"], "2026-07-06", "2026-07-10"), 400,
        "La solicitud excede los días disponibles: quedan 4 días hábiles")
revisar("Usa exactamente lo que queda (4)", solicitar(e["id"], "2026-07-06", "2026-07-09"), 201, dias_restantes=0)
revisar("Tope agotado", solicitar(e["id"], "2026-07-13", "2026-07-13"), 400,
        "La solicitud excede los días disponibles: quedan 0 días hábiles")

e2 = empleado()
revisar("Festivo 2027 (15-19 mar = 4)", solicitar(e2["id"], "2027-03-15", "2027-03-19"), 201, dias_habiles=4)
revisar("Empleado no existe", solicitar(999999, "2026-07-06", "2026-07-10"), 404, "Empleado no encontrado")
revisar("Fin antes de inicio", solicitar(e2["id"], "2026-07-10", "2026-07-06"), 400,
        "La fecha de fin no puede ser anterior a la fecha de inicio")
revisar("Cruza de año", solicitar(e2["id"], "2026-12-28", "2027-01-08"), 400,
        "Las vacaciones deben estar dentro de un mismo año calendario")
revisar("Año fuera de tabla", solicitar(e2["id"], "2028-07-03", "2028-07-04"), 400,
        "Solo se pueden solicitar vacaciones en 2026 y 2027")
revisar("Sin días hábiles", solicitar(e2["id"], "2026-07-11", "2026-07-12"), 400, "El periodo no incluye días hábiles")
revisar("Formato inválido -> 422", solicitar(e2["id"], "21-12-2026", "2026-12-22"), 422)

nuevo = empleado("2025-12-21")
revisar("Antigüedad exacta (aniversario)", solicitar(nuevo["id"], "2026-12-21", "2026-12-21"), 201, dias_habiles=1)
nuevo2 = empleado("2025-12-21")
revisar("Antigüedad insuficiente", solicitar(nuevo2["id"], "2026-12-18", "2026-12-18"), 400,
        "Se requiere al menos un año de antigüedad a la fecha de inicio")

baja = empleado()
httpx.patch(f"{API}/empleados/{baja['numero_empleado']}/baja", json={"fecha_baja": "2026-10-01"}).raise_for_status()
revisar("Empleado dado de baja", solicitar(baja["id"], "2026-07-06", "2026-07-10"), 409,
        "No se pueden solicitar vacaciones para un empleado dado de baja")

print(f"\n{sum(resultados)} de {len(resultados)} pasan")