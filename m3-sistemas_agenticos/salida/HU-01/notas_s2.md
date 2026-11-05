- El ejemplo de la guía (“guarda el correo en minúsculas y valida el formato en el backend”) ya viene en el plan: dice “normaliza correo a minúsculas” y “valida dominio @empresa.com”. Si lo usas, no podrás comprobar si el segundo plan incorpora algo nuevo.
El plan sí tiene un defecto real "validaciones de Pydantic devuelven 422 (FastAPI por defecto)"
Pero contexto/convenciones_app.md dice que los errores deben tener la forma {"detail": "mensaje en español"}. El 422 por defecto de FastAPI devuelve una lista de errores en inglés. Además, el plan solo se compromete con el mensaje exacto del correo no corporativo, no con los demás mensajes de criterios.feature.

No se aprueba plan y se da el siguiente mensaje:

"Los 422 deben responder {"detail": "mensaje en español"} como dice convenciones_app.md, no la lista por defecto de FastAPI. Usa los mensajes exactos de criterios.feature: 409 "El correo ya está registrado", "Usa el correo corporativo @empresa.com", "La fecha de ingreso no puede ser futura" y el de campo inválido."

Sí, lo incorporó: agregó el handler de RequestValidationError y los mensajes exactos.

- El segundo plan incorporó mi comentario, pero agregó el directorio (HU-02) fuera de alcance. Lo rechacé otra vez para mantener HU-01 acotado. La aprobación humana sirvió dos veces: para corregir un defecto contra las convenciones y para frenar trabajo no solicitado.

- Los comentarios de rechazo no son acumulativos: el tercer plan corrigió lo que pedí en el segundo rechazo, pero perdió la corrección del primero. Al revisar un plan hay que validar todo contra los criterios, no solo el último cambio.

Resumen notas:

**Comentario del primer rechazo:** el de los 422 con {"detail": ...} y los mensajes exactos.
**¿El segundo plan lo incorporó?** Sí, pero agregó el directorio (HU-02). Rechacé dos veces más: una para quitarlo y otra porque al quitarlo se perdió la primera corrección y apareció un error en el formulario. Aprobé el plan 4.
**Costo de planificación:** ≈0.39 USD (0.15 + 0.08 × 3).

**Costo total:** 2.15 USD según la consola de Anthropic (planificación ≈0.39 USD; la construcción y los agentes 1 y 2 suman el resto). La traza de la terminal quedó incompleta y no registró la construcción.

### 2C · Revisión manual de la app (HU-01)

| # | Escenario (criterios.feature) | Datos de prueba | Esperado | Resultado |
|---|---|---|---|---|
| 1 | Registro exitoso | Ana López · ana.lopez@empresa.com · Analista de RH · Recursos Humanos · 2024-01-15 | "Empleado EMP-0001 registrado con éxito", estado activo | ✅ Cumple |
| 2 | Correo duplicado | Mismos datos con correo ANA.LOPEZ@EMPRESA.COM | 409 "El correo ya está registrado"; no se crea otro registro | ✅ Cumple |
| 3 | Correo no corporativo | ana.lopez@gmail.com | 422 "Usa el correo corporativo @empresa.com" | ✅ Cumple |
| 4 | Dato inválido | Nombre "A" | 422 mensaje de campo inválido | ✅ Cumple |
| 5 | Fecha de ingreso futura | 2099-12-31 | 422 "La fecha de ingreso no puede ser futura" | ✅ Cumple |

**Resultado:** 5 de 5 criterios cumplidos. Los registros se consultaron directo en `app/backend/datos/empleados.db`, porque la app no tiene directorio: lo excluí del plan por ser parte de HU-02.