import { Fragment, useEffect, useState } from 'react'
import { darDeBajaEmpleado, obtenerDepartamentos, obtenerEmpleados } from '../api/empleados'
import FormularioEmpleado from './FormularioEmpleado'
import FormularioVacaciones from './FormularioVacaciones'

const ESTADOS = {
  activo: 'Activo',
  baja: 'Baja',
}

function DirectorioEmpleados({ edicionActiva, onIniciarEdicion, onTerminarEdicion }) {
  const [busqueda, setBusqueda] = useState('')
  const [departamento, setDepartamento] = useState('')
  const [departamentos, setDepartamentos] = useState([])
  const [empleados, setEmpleados] = useState([])
  const [mensajeError, setMensajeError] = useState('')
  const [bajaActiva, setBajaActiva] = useState(null)
  const [fechaBaja, setFechaBaja] = useState('')
  const [mensajeExitoBaja, setMensajeExitoBaja] = useState('')
  const [mensajeErrorBaja, setMensajeErrorBaja] = useState('')
  const [mensajeExitoEdicion, setMensajeExitoEdicion] = useState('')
  const [vacacionesActiva, setVacacionesActiva] = useState(null)

  useEffect(() => {
    obtenerDepartamentos().then(setDepartamentos)
  }, [])

  function cargarEmpleados() {
    let cancelado = false

    obtenerEmpleados({ busqueda, departamento })
      .then((resultado) => {
        if (cancelado) return
        setEmpleados(resultado)
        setMensajeError('')
      })
      .catch((error) => {
        if (cancelado) return
        setEmpleados([])
        setMensajeError(error.message)
      })

    return () => {
      cancelado = true
    }
  }

  useEffect(() => cargarEmpleados(), [busqueda, departamento])

  function iniciarEdicion(numeroEmpleado) {
    setBajaActiva(null)
    setVacacionesActiva(null)
    setMensajeExitoEdicion('')
    onIniciarEdicion(numeroEmpleado)
  }

  function terminarEdicion(empleado) {
    setMensajeExitoEdicion(`Empleado ${empleado.numero_empleado} actualizado con éxito`)
    onTerminarEdicion()
    cargarEmpleados()
  }

  function iniciarBaja(numeroEmpleado) {
    onTerminarEdicion()
    setVacacionesActiva(null)
    setBajaActiva(numeroEmpleado)
    setFechaBaja('')
    setMensajeExitoBaja('')
    setMensajeErrorBaja('')
  }

  function alternarVacaciones(empleadoId) {
    onTerminarEdicion()
    setBajaActiva(null)
    setVacacionesActiva((anterior) => (anterior === empleadoId ? null : empleadoId))
  }

  async function confirmarBaja(numeroEmpleado) {
    setMensajeExitoBaja('')
    setMensajeErrorBaja('')
    try {
      await darDeBajaEmpleado(numeroEmpleado, fechaBaja)
      setMensajeExitoBaja(`Empleado ${numeroEmpleado} dado de baja con éxito`)
      setBajaActiva(null)
      cargarEmpleados()
    } catch (error) {
      setMensajeErrorBaja(error.message)
    }
  }

  return (
    <section>
      <h1>Directorio de empleados</h1>

      <input
        data-testid="buscar-empleados"
        type="text"
        placeholder="Buscar por nombre o correo"
        value={busqueda}
        onChange={(evento) => setBusqueda(evento.target.value)}
      />

      <select
        data-testid="filtro-departamento"
        value={departamento}
        onChange={(evento) => setDepartamento(evento.target.value)}
      >
        <option value="">Todos los departamentos</option>
        {departamentos.map((item) => (
          <option key={item} value={item}>
            {item}
          </option>
        ))}
      </select>

      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
      {mensajeExitoEdicion && <p data-testid="mensaje-exito">{mensajeExitoEdicion}</p>}
      {mensajeExitoBaja && <p data-testid="mensaje-exito">{mensajeExitoBaja}</p>}
      {mensajeErrorBaja && <p data-testid="mensaje-error">{mensajeErrorBaja}</p>}

      {empleados.length === 0 ? (
        <p data-testid="sin-resultados">No se encontraron empleados</p>
      ) : (
        <table data-testid="tabla-empleados">
          <thead>
            <tr>
              <th>Número</th>
              <th>Nombre</th>
              <th>Puesto</th>
              <th>Departamento</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {empleados.map((empleado) => (
              <Fragment key={empleado.id}>
                <tr data-testid={`fila-empleado-${empleado.numero_empleado}`}>
                  <td data-testid={`numero-empleado-${empleado.numero_empleado}`}>
                    {empleado.numero_empleado}
                  </td>
                  <td>{empleado.nombre}</td>
                  <td>{empleado.puesto}</td>
                  <td>{empleado.departamento}</td>
                  <td data-testid={`estado-empleado-${empleado.numero_empleado}`}>
                    {ESTADOS[empleado.estado] || empleado.estado}
                  </td>
                  <td>
                    <button
                      type="button"
                      data-testid={`editar-empleado-${empleado.numero_empleado}`}
                      onClick={() => iniciarEdicion(empleado.numero_empleado)}
                    >
                      Editar
                    </button>
                    {empleado.estado === 'activo' && (
                      <button
                        type="button"
                        data-testid={`baja-empleado-${empleado.numero_empleado}`}
                        onClick={() => iniciarBaja(empleado.numero_empleado)}
                      >
                        Dar de baja
                      </button>
                    )}
                    {empleado.estado === 'activo' && (
                      <button
                        type="button"
                        data-testid={`vacaciones-abrir-${empleado.id}`}
                        onClick={() => alternarVacaciones(empleado.id)}
                      >
                        Solicitar vacaciones
                      </button>
                    )}
                  </td>
                </tr>
                {edicionActiva === empleado.numero_empleado && (
                  <tr>
                    <td colSpan={6}>
                      <FormularioEmpleado
                        empleadoExistente={empleado}
                        onGuardado={terminarEdicion}
                      />
                    </td>
                  </tr>
                )}
                {bajaActiva === empleado.numero_empleado && (
                  <tr>
                    <td colSpan={6}>
                      <label htmlFor="empleado-fecha-baja">Fecha de baja</label>
                      <input
                        id="empleado-fecha-baja"
                        data-testid="empleado-fecha-baja"
                        type="date"
                        value={fechaBaja}
                        onChange={(evento) => setFechaBaja(evento.target.value)}
                        required
                      />
                      <button
                        type="button"
                        data-testid="confirmar-baja"
                        onClick={() => confirmarBaja(empleado.numero_empleado)}
                      >
                        Confirmar baja
                      </button>
                    </td>
                  </tr>
                )}
                {vacacionesActiva === empleado.id && (
                  <tr>
                    <td colSpan={6}>
                      <FormularioVacaciones empleado={empleado} />
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}

export default DirectorioEmpleados
