# Reporte · HU-10

**Estado:** LISTA
**Costo de agentes:** 2.06 USD
**Ciclos de corrección:** 0

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan rechazado: Casi aprobado; mantén todo lo demás tal cual: festivos.py, routers/vacaciones.py, los schemas, el id numérico en las rutas y en vacaciones-abrir-{empleado.id}, FormularioVacaciones con sus 6 data-testid y el orden de validación de la tabla. Agrega explícitamente: todos los errores de vacaciones se lanzan con HTTPException desde el endpoint, con el código y el detail exactos de la tabla de CLAUDE.md (404, 409 y 400), nunca con validadores de Pydantic, que darían 422; VacacionCrear solo valida el formato de las fechas. El mensaje de éxito es exactamente "Solicitud registrada: N días hábiles. Te quedan M días hábiles en AAAA."
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (30 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 52 passed, 2 skipped in 34.87s

## Última ejecución de pruebas
```
52 passed, 2 skipped in 34.87s

```