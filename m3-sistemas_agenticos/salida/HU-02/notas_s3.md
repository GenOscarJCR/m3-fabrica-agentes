# Notas · Sesión 3 · Sistemas multiagente (HU-02)

## 3A · Agentes 4 y 5 y el paralelismo

**Cómo se paraleliza en `flujos/flujo_s3.py`:**
- **Abanico** (línea 55): si `app_ok`, `despues_de_verificar` devuelve la lista `["desplegar", "automatizar"]` y LangGraph ejecuta ambos nodos a la vez.
- **Unión** (línea 79): `add_edge(["desplegar", "automatizar"], "listo")`; `listo` espera a que terminen las dos ramas.
- **Si la app falla** (línea 56): regresa a `construir` mientras haya intentos (evaluador-optimizador, igual que en el Lab 2).

| | Despliegue (agente 4) | Automatizador (agente 5) |
|---|---|---|
| **Lee** | El código de la app | Casos de prueba de la HU, código y convenciones (`data-testid`) |
| **Escribe** (`ESCRITURA`) | `docker-compose.yml`, Dockerfiles, `.dockerignore`, `nginx.conf` | Solo `tests/*` |
| **Puede ejecutar** (`PROGRAMAS`) | `docker`, `curl`, `sleep` | `python`, `pytest` |
| **Tiene prohibido** | Modificar el código de la app | Modificar el código de la app; si una prueba falla, lo reporta, no lo arregla |

**Límites en dos capas:** `INSTRUCCIONES` (el prompt) pide no tocar el código; `ESCRITURA` y `PROGRAMAS` (los hooks en código) lo impiden aunque el modelo quiera. El límite que vale es el que impone el código (igual que `_dentro_de` en el Lab 1).

**¿Por qué el automatizador puede ir en paralelo con el despliegue?**
Porque para escribir las pruebas no necesita la app desplegada: le bastan los casos y los `data-testid` de las convenciones. Además, cada uno escribe en archivos distintos (`tests/*` frente a los archivos de Docker), así que no se pisan.

**¿Por qué el desarrollador no puede ir en paralelo con ellos?**
Porque ambos dependen de su resultado: no se puede empaquetar ni probar código que todavía no existe. El orden lo marca la dependencia.

## 3B · Ejecución con HU-02

**Plan:** lo aprobé al primer intento. Dijo que extendía HU-01 sin cambios al modelo ni a `EmpleadoSalida` y "sin romper el flujo de alta existente". Agregó `GET /api/empleados` con búsqueda y filtro, `DirectorioEmpleados.jsx` y los `data-testid` de HU-02. A diferencia del Lab 2 (3 rechazos), aquí salió bien a la primera porque la app ya existía y el desarrollador leyó el código antes de planear: más contexto, mejor plan.

**Observación pendiente (resuelta en 3C):** el directorio no se actualiza solo; hay que recargar la página para ver un empleado recién dado de alta. El plan no lo pedía y los criterios de HU-02 tampoco: es una mejora de UX para una historia futura.

**Problema y solución (Windows):** `verificar` falló con `FileNotFoundError: [WinError 2]` porque `subprocess.run(["npm", ...])` no encuentra `npm.cmd` sin shell. Lo corregí en `flujos/verificacion.py` resolviendo la ruta con `shutil.which`. Verifiqué la app sin LLM (`verificar_app()`) antes de relanzar para no gastar crédito. El flujo se tuvo que repetir porque el checkpointer (`InMemorySaver`) guarda en memoria y se perdió al cortarse el proceso.

**Paralelismo observado en la traza:** sí. [despliegue] y [automatizador] arrancaron al mismo tiempo y terminaron por separado (21 turnos · 0.23 USD y 31 turnos · 0.68 USD); después, `listo` unió las ramas.

**Contrato entre agentes:** en la segunda corrida, el plan cambió los data-testid de `fila-empleado-{id}` a `fila-empleado-{numero_empleado}` para coincidir con los casos del diseñador, aunque convenciones_app.md dice `{id}`. El diseñador interpretó el contrato distinto y el desarrollador adaptó la app a las pruebas. Las pruebas pasan, pero ambas se apartan de la convención. Aprobé el plan sin contrastar ese cambio: es el riesgo de los multiagentes, donde el error de un agente se propaga al siguiente.

**Costo:** primera corrida: desarrollador 0.27 USD (se cortó en verificar). Total según la consola: 2.05

## 3C · Inspección

**`docker compose ps`:**
(m3-sistemas_agenticos) PS C:\Proyectos\ProyectosAprendizaje\modulo_3\modulo3\m3-sistemas_agenticos\app> docker compose ps                               
NAME             IMAGE          COMMAND                  SERVICE    CREATED          STATUS                    PORTS
app-backend-1    app-backend    "uvicorn main:app --…"   backend    15 minutes ago   Up 15 minutes (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
app-frontend-1   app-frontend   "/docker-entrypoint.…"   frontend   15 minutes ago   Up 15 minutes             0.0.0.0:8080->80/tcp, [::]:8080->80/tcp

**`pytest tests -q`:**       
12 passed, 2 skipped en 147 s. Las 2 omitidas (una de API y una E2E) prueban el mismo escenario: mostrar un empleado dado de baja. No se ejecutaron porque la API todavía no tiene forma de dar de baja a un empleado, y el automatizador no puede modificar la app (su rol solo escribe en `tests/*` y su instrucción es reportar, no arreglar). Así que la omitió y explicó el motivo. Esto muestra tres cosas: el límite de rol funcionó; un criterio de HU-02 depende de una capacidad de otra historia (nadie lo marcó como pregunta abierta); y ese escenario queda sin evidencia en esta entrega.


**Comparación con mi tabla manual de `notas_s2.md`:** no se pueden comparar directamente. Las pruebas automatizadas solo cubren HU-02, porque el automatizador no existía en el Lab 2. Los 5 criterios de HU-01 solo tienen mi verificación manual, lo que deja un riesgo de regresión: si una historia futura rompe el alta, ninguna prueba lo detectaría.

**Intento fuera de rol (`buscar_denegados.py`):** 

(m3-sistemas_agenticos) PS C:\Proyectos\ProyectosAprendizaje\modulo_3\modulo3\m3-sistemas_agenticos> python buscar_denegados.py                                                                               
Ningún intento de escritura fuera de rol: los agentes respetaron sus carpetas en esta ejecución.

### Detalle
El Dockerfile del backend venía en el repo base (commit del profesor); el agente de despliegue creó docker-compose.yml, frontend/Dockerfile y nginx.conf.