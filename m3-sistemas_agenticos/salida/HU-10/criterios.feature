# language: es
Característica: Solicitar vacaciones

  # ============================================================
  # Camino feliz
  # ============================================================

  Escenario: Registrar una solicitud válida descuenta festivos y fines de semana
    Dado que existe el empleado con id 7, estado "activo" y fecha_ingreso "2025-12-21"
    Y el empleado 7 no tiene solicitudes de vacaciones registradas en 2026
    Cuando envío POST /api/empleados/7/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31" }
      """
    Entonces la API responde con código 201
    Y el campo "dias_habiles" de la respuesta es 8
    Y el campo "dias_restantes" de la respuesta es 4
    Y el campo "empleado_id" de la respuesta es 7

  Escenario: Consultar el saldo del año con solicitudes registradas
    Dado que existe el empleado con id 7, estado "activo" y fecha_ingreso "2025-12-21"
    Y el empleado 7 tiene registrada una solicitud de vacaciones del "2026-12-21" al "2026-12-31" con 8 días hábiles
    Cuando envío GET /api/empleados/7/vacaciones?anio=2026
    Entonces la API responde con código 200
    Y el campo "dias_usados" de la respuesta es 8
    Y el campo "dias_disponibles" de la respuesta es 4
    Y la lista "solicitudes" de la respuesta tiene 1 elemento con "dias_habiles" igual a 8

  Escenario: Consultar el saldo de un año sin solicitudes previas
    Dado que existe el empleado con id 9, estado "activo" y fecha_ingreso "2020-01-01"
    Y el empleado 9 no tiene solicitudes de vacaciones registradas en 2027
    Cuando envío GET /api/empleados/9/vacaciones?anio=2027
    Entonces la API responde con código 200
    Y el campo "dias_usados" de la respuesta es 0
    Y el campo "dias_disponibles" de la respuesta es 12
    Y la lista "solicitudes" de la respuesta está vacía

  Escenario: Consultar el saldo sin indicar el año usa el año en curso
    Dado que existe el empleado con id 10, estado "activo" y fecha_ingreso "2020-01-01"
    Y el empleado 10 no tiene solicitudes de vacaciones registradas en el año en curso
    Cuando envío GET /api/empleados/10/vacaciones
    Entonces la API responde con código 200
    Y el campo "dias_usados" de la respuesta es 0
    Y el campo "dias_disponibles" de la respuesta es 12
    Y el campo "anio" de la respuesta coincide con el año en curso en formato AAAA

  # ============================================================
  # Errores: empleado no existe / dado de baja
  # ============================================================

  Escenario: Registrar una solicitud para un empleado que no existe
    Dado que no existe ningún empleado con id 999
    Cuando envío POST /api/empleados/999/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2026-06-01", "fecha_fin": "2026-06-05" }
      """
    Entonces la API responde con código 404
    Y el campo "detail" de la respuesta es "Empleado no encontrado"

  Escenario: Consultar el saldo de un empleado que no existe
    Dado que no existe ningún empleado con id 999
    Cuando envío GET /api/empleados/999/vacaciones?anio=2026
    Entonces la API responde con código 404
    Y el campo "detail" de la respuesta es "Empleado no encontrado"

  Escenario: Registrar una solicitud para un empleado dado de baja
    Dado que existe el empleado con id 8, estado "baja" y fecha_ingreso "2020-01-01"
    Cuando envío POST /api/empleados/8/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2026-06-01", "fecha_fin": "2026-06-05" }
      """
    Entonces la API responde con código 409
    Y el campo "detail" de la respuesta es "No se pueden solicitar vacaciones para un empleado dado de baja"

  # ============================================================
  # Errores: validaciones de fechas
  # ============================================================

  Escenario: La fecha de fin es anterior a la fecha de inicio
    Dado que existe el empleado con id 7, estado "activo" y fecha_ingreso "2025-12-21"
    Cuando envío POST /api/empleados/7/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2026-07-10", "fecha_fin": "2026-07-05" }
      """
    Entonces la API responde con código 400
    Y el campo "detail" de la respuesta es "La fecha de fin no puede ser anterior a la fecha de inicio"

  Escenario: El periodo cruza de un año a otro
    Dado que existe el empleado con id 7, estado "activo" y fecha_ingreso "2020-01-01"
    Cuando envío POST /api/empleados/7/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2026-12-28", "fecha_fin": "2027-01-08" }
      """
    Entonces la API responde con código 400
    Y el campo "detail" de la respuesta es "Las vacaciones deben estar dentro de un mismo año calendario"

  Escenario: El año de la solicitud no está en la tabla de festivos
    Dado que existe el empleado con id 7, estado "activo" y fecha_ingreso "2020-01-01"
    Cuando envío POST /api/empleados/7/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2028-06-01", "fecha_fin": "2028-06-05" }
      """
    Entonces la API responde con código 400
    Y el campo "detail" de la respuesta es "Solo se pueden solicitar vacaciones en 2026 y 2027"

  Escenario: Una fecha con formato inválido responde con el 422 automático de FastAPI
    Dado que existe el empleado con id 7, estado "activo" y fecha_ingreso "2020-01-01"
    Cuando envío POST /api/empleados/7/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2026-13-01", "fecha_fin": "2026-13-05" }
      """
    Entonces la API responde con código 422

  # ============================================================
  # Regla 1 · Antigüedad
  # ============================================================

  Escenario: Antigüedad insuficiente se rechaza
    Dado que existe el empleado con id 7, estado "activo" y fecha_ingreso "2025-12-21"
    Cuando envío POST /api/empleados/7/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2026-12-18", "fecha_fin": "2026-12-18" }
      """
    Entonces la API responde con código 400
    Y el campo "detail" de la respuesta es "Se requiere al menos un año de antigüedad a la fecha de inicio"

  Escenario: Límite de antigüedad, cumplir exactamente un año se acepta
    Dado que existe el empleado con id 7, estado "activo" y fecha_ingreso "2025-12-21"
    Y el empleado 7 no tiene solicitudes de vacaciones registradas en 2026
    Cuando envío POST /api/empleados/7/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-21" }
      """
    Entonces la API responde con código 201
    Y el campo "dias_habiles" de la respuesta es 1
    Y el campo "dias_restantes" de la respuesta es 11

  Escenario: Límite de antigüedad, un día antes de cumplir el año se rechaza
    Dado que existe el empleado con id 7, estado "activo" y fecha_ingreso "2025-12-21"
    Cuando envío POST /api/empleados/7/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2026-12-20", "fecha_fin": "2026-12-20" }
      """
    Entonces la API responde con código 400
    Y el campo "detail" de la respuesta es "Se requiere al menos un año de antigüedad a la fecha de inicio"

  # ============================================================
  # Regla 3 · Días hábiles
  # ============================================================

  Escenario: Un periodo sin ningún día hábil se rechaza
    Dado que existe el empleado con id 7, estado "activo" y fecha_ingreso "2020-01-01"
    Cuando envío POST /api/empleados/7/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2026-07-11", "fecha_fin": "2026-07-12" }
      """
    Entonces la API responde con código 400
    Y el campo "detail" de la respuesta es "El periodo no incluye días hábiles"

  # ============================================================
  # Regla 2 · Tope anual
  # ============================================================

  Escenario: Límite del tope anual, usar exactamente los 12 días disponibles se acepta
    Dado que existe el empleado con id 11, estado "activo" y fecha_ingreso "2020-01-01"
    Y el empleado 11 no tiene solicitudes de vacaciones registradas en 2026
    Cuando envío POST /api/empleados/11/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2026-06-01", "fecha_fin": "2026-06-16" }
      """
    Entonces la API responde con código 201
    Y el campo "dias_habiles" de la respuesta es 12
    Y el campo "dias_restantes" de la respuesta es 0

  Escenario: Límite del tope anual, pedir un día hábil más de los disponibles se rechaza
    Dado que existe el empleado con id 12, estado "activo" y fecha_ingreso "2020-01-01"
    Y el empleado 12 no tiene solicitudes de vacaciones registradas en 2026
    Cuando envío POST /api/empleados/12/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2026-06-01", "fecha_fin": "2026-06-17" }
      """
    Entonces la API responde con código 400
    Y el campo "detail" de la respuesta es "La solicitud excede los días disponibles: quedan 12 días hábiles"

  Escenario: Ya no quedan días disponibles en el año
    Dado que existe el empleado con id 13, estado "activo" y fecha_ingreso "2020-01-01"
    Y el empleado 13 tiene registrada una solicitud de vacaciones del "2026-06-01" al "2026-06-16" con 12 días hábiles
    Cuando envío POST /api/empleados/13/vacaciones con cuerpo:
      """
      { "fecha_inicio": "2026-08-03", "fecha_fin": "2026-08-03" }
      """
    Entonces la API responde con código 400
    Y el campo "detail" de la respuesta es "La solicitud excede los días disponibles: quedan 0 días hábiles"

# Preguntas abiertas
# - El archivo de convenciones no especifica el comportamiento de
#   GET /api/empleados/{id}/vacaciones cuando el empleado no existe. Se asumió,
#   por analogía con el resto de la API, que responde 404 con el mismo mensaje
#   "Empleado no encontrado" que usa el POST. Confirmar con el equipo.
# - El caso del aniversario del 29 de febrero (documentado en reglas_vacaciones.md)
#   no se pudo cubrir con un escenario verificable: el único año bisiesto cercano
#   a 2026-2027 es 2024 (o 2028), y su primer aniversario cae en 2025 o 2029,
#   fuera del rango de años soportado por la API (2026 y 2027). Falta definir
#   cómo probar esta regla dentro del rango soportado, o si se amplía la tabla
#   de festivos/años válidos para poder ejercitarla.
