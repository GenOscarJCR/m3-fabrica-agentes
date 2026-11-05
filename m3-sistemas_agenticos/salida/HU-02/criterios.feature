# language: es
# HU-02 · Consultar el directorio de empleados

Característica: Consultar el directorio de empleados
  Como persona del área de Recursos Humanos
  Quiero ver el directorio de empleados, buscarlos por nombre o correo y filtrarlos por departamento
  Para encontrar rápido a una persona

  Escenario: Ver el directorio completo de empleados
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | puesto           | departamento      | estado |
      | EMP-0001        | Ana Torres    | Analista         | Tecnología        | activo |
      | EMP-0002        | Luis Pérez    | Vendedor         | Ventas            | activo |
    Cuando abro el directorio de empleados
    Entonces veo una lista con 2 empleados
    Y cada fila muestra número de empleado, nombre, puesto, departamento y estado

  Escenario: Buscar un empleado por nombre
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | correo                  | departamento | estado |
      | EMP-0001        | Ana Torres    | ana.torres@empresa.com  | Tecnología   | activo |
      | EMP-0002        | Luis Pérez    | luis.perez@empresa.com  | Ventas       | activo |
    Cuando busco por el texto "Torres"
    Entonces veo 1 resultado
    Y el resultado corresponde al empleado "EMP-0001" con nombre "Ana Torres"

  Escenario: Buscar un empleado por correo
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | correo                  | departamento | estado |
      | EMP-0001        | Ana Torres    | ana.torres@empresa.com  | Tecnología   | activo |
      | EMP-0002        | Luis Pérez    | luis.perez@empresa.com  | Ventas       | activo |
    Cuando busco por el texto "luis.perez@empresa.com"
    Entonces veo 1 resultado
    Y el resultado corresponde al empleado "EMP-0002" con nombre "Luis Pérez"

  Escenario: La búsqueda no distingue mayúsculas de minúsculas
    Dado que existe el empleado "EMP-0001" con nombre "Ana Torres" y correo "ana.torres@empresa.com"
    Cuando busco por el texto "ANA TORRES"
    Entonces veo 1 resultado
    Y el resultado corresponde al empleado "EMP-0001" con nombre "Ana Torres"

  Escenario: Filtrar empleados por departamento
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | departamento | estado |
      | EMP-0001        | Ana Torres    | Tecnología   | activo |
      | EMP-0002        | Luis Pérez    | Ventas       | activo |
      | EMP-0003        | Rosa Díaz     | Tecnología   | activo |
    Cuando filtro por el departamento "Tecnología"
    Entonces veo 2 resultados
    Y todos los resultados tienen el departamento "Tecnología"

  Escenario: Buscar un texto que no coincide con ningún empleado
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | correo                  | departamento | estado |
      | EMP-0001        | Ana Torres    | ana.torres@empresa.com  | Tecnología   | activo |
    Cuando busco por el texto "Martínez"
    Entonces veo el mensaje "No se encontraron empleados"
    Y la lista de resultados está vacía

  Escenario: Un empleado dado de baja sigue apareciendo en el directorio
    Dado que existe el empleado "EMP-0001" con nombre "Ana Torres" y estado "baja"
    Cuando abro el directorio de empleados
    Entonces veo al empleado "EMP-0001" en la lista
    Y su estado se muestra como "baja"

# Preguntas abiertas
# - No se especifica si la búsqueda por nombre/correo admite coincidencias parciales o solo exactas; se asumió coincidencia parcial.
# - No se especifica si el filtro por departamento se puede combinar con la búsqueda por texto al mismo tiempo.
# - No se especifica si existe paginación cuando el directorio tiene muchos empleados.
