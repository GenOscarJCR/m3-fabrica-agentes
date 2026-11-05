# Reporte · HU-03

**Estado:** LISTA
**Costo de agentes:** 2.34 USD
**Ciclos de corrección:** 2

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan rechazado: Casi aprobado. Usa numero_empleado en TODOS los data-testid nuevos (editar-empleado-{numero_empleado} y baja-empleado-{numero_empleado}), igual que fila-empleado de HU-02; corrige la sección que dice {id}. No cambies el comportamiento de HU-01 y HU-02: sin la prop empleadoExistente, el formulario de alta debe funcionar igual que hoy. Mantén lo demás: 409 al editar un empleado en baja, PUT /api/empleados/{numero_empleado}, PATCH .../baja con fecha_baja >= fecha_ingreso, y empleado-fecha-baja y confirmar-baja.
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (10 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 3 failed, 19 passed, 2 skipped in 265.70s (0:04:25)
- Triage → desarrollador: El formulario de edición de empleado renderiza dos elementos con el mismo data-testid="empleado-puesto" (uno vacío y otro con el valor actual), lo que provoca una violación de modo estricto en Playwright al intentar interactuar con el campo de puesto. Esto indica un defecto de la aplicación: probablemente el formulario está duplicando el input (por ejemplo, un formulario oculto o un render duplicado al abrir el modal/edición) en lugar de mostrar un único campo editable.
- Código corregido; redespliegue OK
- Pruebas E2E: 2 failed, 20 passed, 2 skipped in 266.96s (0:04:26)
- Triage → desarrollador: Al editar el puesto y departamento de un empleado activo (EMP-0007), tras guardar los cambios la aplicación no muestra el mensaje de éxito (get_by_test_id("mensaje-exito")) y en su lugar la pantalla permanece en el formulario de "Registrar empleado", lo que indica que el flujo de edición no está completando correctamente la operación de guardado ni redirigiendo/renderizando la confirmación esperada según el criterio de aceptación "Editar correctamente el puesto y el departamento de un empleado activo".
- Código corregido; redespliegue OK
- Pruebas E2E: 22 passed, 2 skipped in 240.13s (0:04:00)

## Última ejecución de pruebas
```
22 passed, 2 skipped in 240.13s (0:04:00)

```