# language: es

Característica: Editar y dar de baja a un empleado
  Como persona del área de Recursos Humanos
  quiero cambiar el puesto y el departamento de un empleado, y poder darlo de baja
  para mantener el directorio al día sin perder el historial

  Escenario: Editar correctamente el puesto y el departamento de un empleado activo
    Dado que existe el empleado "EMP-0007" "Carla Soto" con correo "carla.soto@empresa.com", puesto "Analista de Datos", departamento "Tecnología" y estado "activo"
    Cuando edito su puesto a "Líder de Datos" y su departamento a "Finanzas"
    Entonces el sistema guarda los cambios
    Y el empleado "EMP-0007" muestra puesto "Líder de Datos" y departamento "Finanzas"
    Y su número de empleado sigue siendo "EMP-0007" y su correo sigue siendo "carla.soto@empresa.com"

  Escenario: Dar de baja correctamente a un empleado activo
    Dado que existe el empleado "EMP-0007" "Carla Soto" con estado "activo" y fecha_ingreso "2022-03-01"
    Cuando doy de baja al empleado "EMP-0007" con fecha_baja "2024-05-10"
    Entonces el sistema cambia el estado del empleado "EMP-0007" a "baja"
    Y registra la fecha_baja "2024-05-10"
    Y el empleado "EMP-0007" sigue apareciendo en el directorio

  Escenario: Intentar editar un empleado con un puesto inválido
    Dado que existe el empleado "EMP-0007" "Carla Soto" con puesto "Analista de Datos" y estado "activo"
    Cuando intento editar su puesto a "A"
    Entonces el sistema responde con error 422
    Y la pantalla indica que el campo "puesto" debe corregirse

  Escenario: Intentar editar a un empleado que ya está dado de baja
    Dado que existe el empleado "EMP-0010" "Luis Pérez" con estado "baja"
    Cuando intento editar su puesto a "Gerente de Ventas"
    Entonces el sistema responde con error 409 y el mensaje "No se puede editar a un empleado dado de baja"

  Escenario: Intentar dar de baja con una fecha de baja anterior a la fecha de ingreso
    Dado que existe el empleado "EMP-0007" "Carla Soto" con estado "activo" y fecha_ingreso "2022-03-01"
    Cuando doy de baja al empleado "EMP-0007" con fecha_baja "2021-01-01"
    Entonces el sistema responde con error 422
    Y la pantalla indica que el campo "fecha_baja" debe corregirse

# Preguntas abiertas
# - No se especifica el mensaje exacto de error que debe mostrarse cuando el puesto o el departamento
#   son inválidos al editar (regla 3 solo indica que "la pantalla muestra qué campo corregir").
# - No se especifica si el sistema debe rechazar explícitamente (con error) los intentos de modificar
#   numero_empleado o correo, o simplemente ignorar esos campos en la edición.
