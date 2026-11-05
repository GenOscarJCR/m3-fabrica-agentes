# language: es
Característica: Registrar empleado
  Como persona del área de Recursos Humanos
  quiero registrar a un empleado con su nombre, correo corporativo, puesto, departamento y fecha de ingreso
  para darlo de alta en la empresa

  Escenario: Registro exitoso de un empleado con datos válidos
    Dado que no existe ningún empleado con el correo "ana.lopez@empresa.com"
    Cuando registro un empleado con los siguientes datos:
      | nombre        | correo                     | puesto           | departamento | fecha_ingreso |
      | Ana López     | Ana.Lopez@empresa.com      | Analista de RH   | Recursos Humanos | 2024-03-01   |
    Entonces el sistema responde con código 201
    Y el empleado se guarda con correo "ana.lopez@empresa.com" en minúsculas
    Y el empleado se guarda con estado "activo"
    Y el sistema asigna un número de empleado con formato "EMP-0001"
    Y la pantalla muestra el mensaje de confirmación "Empleado EMP-0001 registrado con éxito"

  Escenario: Error al registrar un empleado con un correo ya registrado
    Dado que existe un empleado registrado con el correo "carlos.ruiz@empresa.com"
    Cuando intento registrar otro empleado con los siguientes datos:
      | nombre        | correo                     | puesto      | departamento | fecha_ingreso |
      | Carlos Ruiz   | CARLOS.RUIZ@empresa.com    | Vendedor    | Ventas       | 2024-05-10   |
    Entonces el sistema responde con código 409
    Y la pantalla muestra el mensaje "El correo ya está registrado"
    Y no se crea un nuevo empleado

  Escenario: Error al registrar un empleado con un correo que no es corporativo
    Dado que no existe ningún empleado con el correo "laura.perez@gmail.com"
    Cuando intento registrar un empleado con los siguientes datos:
      | nombre        | correo                   | puesto      | departamento | fecha_ingreso |
      | Laura Pérez   | laura.perez@gmail.com    | Contadora   | Finanzas     | 2024-04-15   |
    Entonces el sistema responde con código 422
    Y la pantalla muestra el mensaje "Usa el correo corporativo @empresa.com"
    Y no se crea un nuevo empleado

  Escenario: Error al registrar un empleado con un departamento que no existe en el catálogo
    Dado que no existe ningún empleado con el correo "mario.diaz@empresa.com"
    Cuando intento registrar un empleado con los siguientes datos:
      | nombre        | correo                     | puesto      | departamento | fecha_ingreso |
      | Mario Díaz    | mario.diaz@empresa.com    | Diseñador   | Marketing    | 2024-02-20   |
    Entonces el sistema responde con código 422
    Y la pantalla muestra qué campo corregir: "departamento"
    Y no se crea un nuevo empleado

  Escenario: Error al registrar un empleado con una fecha de ingreso futura
    Dado que no existe ningún empleado con el correo "sofia.torres@empresa.com"
    Cuando intento registrar un empleado con los siguientes datos:
      | nombre        | correo                     | puesto         | departamento | fecha_ingreso |
      | Sofía Torres  | sofia.torres@empresa.com  | Desarrolladora | Tecnología   | 2999-01-01   |
    Entonces el sistema responde con código 422
    Y la pantalla muestra el mensaje "La fecha de ingreso no puede ser futura"
    Y no se crea un nuevo empleado

# Preguntas abiertas
# - No se especifica el límite exacto de caracteres a mostrar en el mensaje de confirmación; se asumió el formato "Empleado {numero_empleado} registrado con éxito".
# - No se detalla el formato exacto del mensaje de error de campo inválido (regla 3) cuando el campo es "departamento"; se asumió que indica el nombre del campo a corregir.
