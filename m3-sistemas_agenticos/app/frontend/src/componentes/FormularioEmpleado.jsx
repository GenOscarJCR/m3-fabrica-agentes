import { useEffect, useState } from 'react'
import { crearEmpleado, editarEmpleado, obtenerDepartamentos } from '../api/empleados'

const DATOS_INICIALES = {
  nombre: '',
  correo: '',
  puesto: '',
  departamento: '',
  fecha_ingreso: '',
}

function FormularioEmpleado({ empleadoExistente, onGuardado }) {
  const esEdicion = Boolean(empleadoExistente)
  const [datos, setDatos] = useState(
    esEdicion
      ? { puesto: empleadoExistente.puesto, departamento: empleadoExistente.departamento }
      : DATOS_INICIALES
  )
  const [departamentos, setDepartamentos] = useState([])
  const [mensajeExito, setMensajeExito] = useState('')
  const [mensajeError, setMensajeError] = useState('')

  useEffect(() => {
    obtenerDepartamentos().then(setDepartamentos)
  }, [])

  function actualizarCampo(campo, valor) {
    setDatos((anterior) => ({ ...anterior, [campo]: valor }))
  }

  async function manejarEnvio(evento) {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')
    try {
      if (esEdicion) {
        const empleado = await editarEmpleado(empleadoExistente.numero_empleado, datos)
        onGuardado?.(empleado)
      } else {
        const empleado = await crearEmpleado(datos)
        setMensajeExito(`Empleado ${empleado.numero_empleado} registrado con éxito`)
        setDatos(DATOS_INICIALES)
      }
    } catch (error) {
      setMensajeError(error.message)
    }
  }

  return (
    <form onSubmit={manejarEnvio}>
      <h1>{esEdicion ? 'Editar empleado' : 'Registrar empleado'}</h1>

      {!esEdicion && (
        <>
          <label htmlFor="empleado-nombre">Nombre</label>
          <input
            id="empleado-nombre"
            data-testid="empleado-nombre"
            type="text"
            value={datos.nombre}
            onChange={(evento) => actualizarCampo('nombre', evento.target.value)}
            required
          />

          <label htmlFor="empleado-correo">Correo</label>
          <input
            id="empleado-correo"
            data-testid="empleado-correo"
            type="text"
            value={datos.correo}
            onChange={(evento) => actualizarCampo('correo', evento.target.value)}
            required
          />
        </>
      )}

      <label htmlFor="empleado-puesto">Puesto</label>
      <input
        id="empleado-puesto"
        data-testid="empleado-puesto"
        type="text"
        value={datos.puesto}
        onChange={(evento) => actualizarCampo('puesto', evento.target.value)}
        required
      />

      <label htmlFor="empleado-departamento">Departamento</label>
      <select
        id="empleado-departamento"
        data-testid="empleado-departamento"
        value={datos.departamento}
        onChange={(evento) => actualizarCampo('departamento', evento.target.value)}
        required
      >
        <option value="">Selecciona un departamento</option>
        {departamentos.map((departamento) => (
          <option key={departamento} value={departamento}>
            {departamento}
          </option>
        ))}
      </select>

      {!esEdicion && (
        <>
          <label htmlFor="empleado-fecha-ingreso">Fecha de ingreso</label>
          <input
            id="empleado-fecha-ingreso"
            data-testid="empleado-fecha-ingreso"
            type="date"
            value={datos.fecha_ingreso}
            onChange={(evento) => actualizarCampo('fecha_ingreso', evento.target.value)}
            required
          />
        </>
      )}

      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  )
}

export default FormularioEmpleado
