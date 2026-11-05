export async function obtenerDepartamentos() {
  const respuesta = await fetch('/api/departamentos')
  return respuesta.json()
}

export async function obtenerEmpleados({ busqueda, departamento } = {}) {
  const parametros = new URLSearchParams()
  if (busqueda) parametros.set('busqueda', busqueda)
  if (departamento) parametros.set('departamento', departamento)

  const respuesta = await fetch(`/api/empleados?${parametros.toString()}`)
  const cuerpo = await respuesta.json()
  if (!respuesta.ok) {
    throw new Error(cuerpo.detail || 'Ocurrió un error al consultar los empleados')
  }
  return cuerpo
}

export async function crearEmpleado(datos) {
  const respuesta = await fetch('/api/empleados', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
  const cuerpo = await respuesta.json()
  if (!respuesta.ok) {
    throw new Error(cuerpo.detail || 'Ocurrió un error al registrar al empleado')
  }
  return cuerpo
}

export async function editarEmpleado(numeroEmpleado, datos) {
  const respuesta = await fetch(`/api/empleados/${numeroEmpleado}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
  const cuerpo = await respuesta.json()
  if (!respuesta.ok) {
    throw new Error(cuerpo.detail || 'Ocurrió un error al editar al empleado')
  }
  return cuerpo
}

export async function darDeBajaEmpleado(numeroEmpleado, fechaBaja) {
  const respuesta = await fetch(`/api/empleados/${numeroEmpleado}/baja`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fecha_baja: fechaBaja }),
  })
  const cuerpo = await respuesta.json()
  if (!respuesta.ok) {
    throw new Error(cuerpo.detail || 'Ocurrió un error al dar de baja al empleado')
  }
  return cuerpo
}
