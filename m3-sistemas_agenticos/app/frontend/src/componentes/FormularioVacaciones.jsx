import { useEffect, useState } from 'react'
import { crearVacacion, obtenerSaldo } from '../api/vacaciones'

function FormularioVacaciones({ empleado }) {
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [saldo, setSaldo] = useState(null)
  const [mensaje, setMensaje] = useState('')

  useEffect(() => {
    obtenerSaldo(empleado.id)
      .then(setSaldo)
      .catch((error) => setMensaje(error.message))
  }, [empleado.id])

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensaje('')
    try {
      const resultado = await crearVacacion(empleado.id, {
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
      })
      const anio = fechaInicio.slice(0, 4)
      setMensaje(
        `Solicitud registrada: ${resultado.dias_habiles} días hábiles. ` +
          `Te quedan ${resultado.dias_restantes} días hábiles en ${anio}.`
      )
      const actualizado = await obtenerSaldo(empleado.id)
      setSaldo(actualizado)
    } catch (error) {
      setMensaje(error.message)
    }
  }

  return (
    <form onSubmit={manejarEnvio}>
      <h2>Solicitar vacaciones</h2>

      <p>
        Días disponibles: <span data-testid="vacaciones-disponibles">{saldo ? saldo.dias_disponibles : ''}</span>
      </p>

      <label htmlFor={`vacaciones-fecha-inicio-${empleado.id}`}>Fecha de inicio</label>
      <input
        id={`vacaciones-fecha-inicio-${empleado.id}`}
        data-testid="vacaciones-fecha-inicio"
        type="date"
        value={fechaInicio}
        onChange={(evento) => setFechaInicio(evento.target.value)}
        required
      />

      <label htmlFor={`vacaciones-fecha-fin-${empleado.id}`}>Fecha de fin</label>
      <input
        id={`vacaciones-fecha-fin-${empleado.id}`}
        data-testid="vacaciones-fecha-fin"
        type="date"
        value={fechaFin}
        onChange={(evento) => setFechaFin(evento.target.value)}
        required
      />

      <button type="submit" data-testid="vacaciones-enviar">
        Enviar
      </button>

      {mensaje && <p data-testid="vacaciones-mensaje">{mensaje}</p>}
    </form>
  )
}

export default FormularioVacaciones
