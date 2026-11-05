export async function obtenerSaldo(empleadoId, anio) {
  const parametros = new URLSearchParams()
  if (anio) parametros.set('anio', anio)
  const query = parametros.toString()

  const respuesta = await fetch(
    `/api/empleados/${empleadoId}/vacaciones${query ? `?${query}` : ''}`
  )
  const cuerpo = await respuesta.json()
  if (!respuesta.ok) {
    throw new Error(cuerpo.detail || 'Ocurrió un error al consultar el saldo de vacaciones')
  }
  return cuerpo
}

export async function crearVacacion(empleadoId, datos) {
  const respuesta = await fetch(`/api/empleados/${empleadoId}/vacaciones`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
  const cuerpo = await respuesta.json()
  if (!respuesta.ok) {
    throw new Error(cuerpo.detail || 'Ocurrió un error al registrar la solicitud de vacaciones')
  }
  return cuerpo
}
