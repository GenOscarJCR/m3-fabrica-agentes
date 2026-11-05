### 1A · El bucle

¿Por qué PermissionError? 
herramientas_archivos recibe una lista blanca de carpetas: lectura solo en historias/ y escritura solo en salida/HU-01/. Antes de tocar el disco, _dentro_de resuelve la ruta completa con .resolve(), lo que también neutraliza trucos como ../, y la rechaza si no cae dentro de una carpeta permitida. secretos_demo.txt está en la raíz, fuera de la lista, así que se bloquea. Es el principio de mínimo privilegio aplicado a las herramientas: el límite lo impone el código, no las instrucciones del modelo. Dentro del bucle, ese error no tumba al agente: regresa al modelo como tool_result con is_error: True para que se corrija.

### 1B · Agente 1, el analista

- **Pasos:** 3 llamadas al modelo. En la primera leyó 2 archivos en paralelo; en la segunda escribió el .feature; en la tercera respondió sin herramientas.
- **Qué corrigió el validador:** nada. El primer intento ya cumplía, así que no se activó el ciclo de reflexión.
- **Qué cambiaría en sus instrucciones:** Que no asuma un sistema vacío (EMP-0001 fijo) y use un número genérico o el patrón EMP-NNNN, porque con datos previos las pruebas fallarían. Y que, si la historia no define un mensaje exacto, lo marque como pregunta abierta en lugar de proponer un texto.

### 1C · Agente 2, el diseñador de pruebas
- **Pasos:** 3 llamadas al modelo. En la primera leyó 2 archivos en paralelo (criterios y convenciones); en la segunda guardó los casos con guardar_casos; en la tercera respondió sin herramientas.
- **Qué corrigió la validación:** nada. Los 10 casos cumplieron el esquema CasoPrueba en el intento 1.
- **Resultado:** 10 casos para 5 escenarios (5 api y 5 e2e); los e2e usan los data-testid de convenciones_app.md.
- **Qué cambiaría en sus instrucciones:** exigir datos de prueba únicos por caso (por ejemplo, un sufijo único en el correo), porque reutilizar el mismo correo hará fallar las pruebas por la regla de correo único cuando corran juntas.


