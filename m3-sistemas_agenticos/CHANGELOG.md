# Changelog

Cambios relevantes a la fábrica: agentes, validadores, flujos y hooks. El código de `app/` y los artefactos de `salida/` los generan los agentes y no se registran aquí.

## [2.0.0] · 2026-11-03 · Reto HU-10 Solicitar vacaciones

### Contexto
- Se agregaron `reglas_vacaciones.md` al final de `contexto/reglas_negocio.md` y `convenciones_vacaciones.md` al final de `contexto/convenciones_app.md`.
- También se copiaron como `contexto/reglas_vacaciones.md` y `contexto/convenciones_vacaciones.md`, porque la historia HU-10 los cita por nombre.

### Analista (`agentes/analista.py`)
- `SISTEMA`: ahora lee también `convenciones_app.md` y todo archivo de `contexto/` que cite la historia; exige un escenario por fila de la tabla de errores con código y mensaje letra por letra, escenarios de límite (justo en el límite y rebasado por uno) y cubrir cada endpoint con método y ruta concretos.
- Nuevas funciones `mensajes_requeridos()` y `rutas_requeridas()`: extraen los mensajes de error 4xx y los endpoints de los archivos de contexto citados por la historia.
- `validar_gherkin()` acepta `mensajes` y `rutas` y reporta los que falten (la `N` de un mensaje acepta cualquier número). Antes de la ejecución final rechazó una versión de los criterios sin las rutas POST y GET.

### Bucle común (`agentes/base.py`)
- `max_tokens` de 16000 a 32000 y `timeout=900` en el cliente: los criterios de HU-10 se cortaban por `max_tokens`.

### Desarrollador (`agentes/desarrollador.py`)
- `INSTRUCCIONES`: en funciones nuevas, CLAUDE.md manda sobre los patrones del código existente (rutas, campos, códigos, mensajes y `data-testid`, por ejemplo el `id` numérico), sin cambiar historias anteriores; las reglas y los cálculos van en el backend.

### Automatizador (`agentes/automatizador.py`)
- `TAREA`: cada prueba crea su propio empleado y usa el `id` que devuelve la API (nunca un `EMP-0001` fijo) y fija una `fecha_ingreso` explícita cuando el caso depende de la antigüedad.

### Verificación
- Nuevo `verificar_hu10.py`: comprueba la API desplegada contra `convenciones_vacaciones.md`, independiente de las pruebas generadas por la fábrica (15 de 15).

### Hooks
- Sin cambios: los hooks de seguridad se mantienen intactos y la ejecución final se hizo con defensas.

## [1.3.0] · [2026-10-31] · Laboratorio 4 · Seguridad y triage
- Se usó `flujo_s4` (filtro de la historia, pruebas E2E y triage con `MAX_CICLOS = 2`) para procesar HU-03.
- HU-99 quedó bloqueada por `filtrar_historia`; reporte en `salida/seguridad.md`.
- `.gitignore`: se excluye `app/backend/uvicorn.log`.

## [1.2.0] · [2026-10-30] · Laboratorio 3 · Despliegue y pruebas en paralelo
- `flujos/verificacion.py`: en Windows, `subprocess.run(["npm", ...])` no encontraba `npm.cmd`; ahora resuelve la ruta con `shutil.which`.
- Nuevo `buscar_denegados.py`: lista los intentos de escritura fuera de rol registrados en `auditoria.jsonl`.

## [1.1.0] · [2026-10-24] · Laboratorio 2 · Flujo con aprobación humana
- Se usó `flujo_s2` con `interrupt` para aprobar el plan antes de construir HU-01.

## [1.0.0] · [2026-10-23] · Laboratorio 1 · Bucle y agentes 1 y 2
- `agentes/base.py`: bucle `ejecutar_agente` (ReAct) con límite de pasos, errores de herramienta devueltos al modelo con `is_error` y un error explícito cuando la respuesta se corta por `max_tokens`.
- Analista y diseñador de pruebas sobre HU-01.
