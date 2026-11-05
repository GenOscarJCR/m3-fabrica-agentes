# Decisiones · HU-10 Solicitar vacaciones

## 1. ¿Qué pasos son workflow y cuáles son agente?
`flujo_s4` es workflow: el código fija el orden filtro → analista → diseñador → plan → aprobación → construir → verificar → despliegue ‖ automatizador → pruebas → triage, y las aristas condicionales deciden reintentos y escalamiento. Dentro hay agentes: el analista y el diseñador deciden qué leer y cuándo escribir en su bucle ReAct (en la ejecución final, el analista leyó la historia, listó `contexto/` y leyó 4 archivos antes de escribir 18 escenarios); el desarrollador, el despliegue y el automatizador son Claude Code con su propio bucle. Los ciclos que los rodean son workflow: el código decide si el analista reintenta según `validar_gherkin`, y `verificar` es código sin LLM.

## 2. ¿Cómo se validó cada salida? ¿Qué atrapó algún validador?
- **Criterios:** amplié `validar_gherkin` para exigir cada mensaje de error (letra por letra) y cada endpoint de los archivos de contexto que cita la historia. Antes de ejecutar rechazó la versión previa: faltaban las rutas POST y GET y no había escenario de consulta del saldo. En la ejecución final pasó en el intento 1: la instrucción previene y el validador garantiza.
- **Casos:** `PlanPruebas` (Pydantic) más un caso por escenario: 30 casos en el intento 1.
- **Código:** `verificar_app` OK en la construcción 1; pruebas API y E2E: 52 passed, 2 skipped (las 2 omitidas son de HU-02 y no tocan vacaciones). Como esas pruebas salen de mis propios criterios, verifiqué además la API contra `convenciones_vacaciones.md` con un script independiente (`verificar_hu10.py`): 15 de 15, incluidos límites, festivos de 2027, antigüedad exacta y empleado dado de baja.

## 3. ¿Dónde intervine como persona y qué vi para decidir?
Antes de ejecutar revisé los criterios (faltaba el GET). En las preguntas abiertas continué: eran supuestos razonables (404 en el GET; el aniversario del 29 de febrero no se puede probar en 2026-2027). El primer plan detectó por sí mismo el conflicto id/numero_empleado, pero no decía cómo se lanzarían los errores; con validadores de Pydantic saldrían 422 en lugar de 400. Lo rechacé pidiendo HTTPException con los códigos exactos y enumerando lo que debía conservarse; el segundo plan lo incorporó y lo aprobé (bitácora: «Plan rechazado…» y luego «Plan aprobado por una persona»).

## 4. ¿Qué arquitectura de orquestación y por qué no otra?
Orquestador con flujo fijo (supervisor determinista): las etapas no cambian entre historias, así que un supervisor LLM agregaría costo y variación sin ganar nada. Despliegue y automatizador van en paralelo porque no dependen entre sí; el triage solo enruta fallos (aquí no hizo falta: 0 ciclos). `salida/HU-10/` funciona como pizarra en disco. Traspasos o red no aplican: no hay conversación ni exploración abierta.

## 5. ¿Qué corregí en el agente y por qué no en su resultado?
- El analista no leía los mensajes exactos (estaban en `convenciones_app.md`) y la historia citaba archivos inexistentes: ajusté su `SISTEMA` y copié los dos archivos a `contexto/`.
- Se cortó por `max_tokens` (16000): subí el límite a 32000 en `base.py`, sin recortar criterios.
- Mi app usa `numero_empleado` desde HU-02, pero vacaciones exige el `id` numérico: le indiqué al desarrollador que CLAUDE.md manda sobre los patrones existentes. El plan lo aplicó sin que lo pidiera.
- El automatizador ahora crea un empleado por prueba y fija `fecha_ingreso`, porque los días se acumulan por empleado.

El resultado se regenera en cada ejecución: un arreglo a mano se pierde, rompe la integridad (`auditoria.jsonl`) y no mejora la fábrica. Por eso la ejecución final terminó LISTA con 0 ciclos de corrección (2.06 USD).