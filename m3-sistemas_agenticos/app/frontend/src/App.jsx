import { useState } from 'react'
import DirectorioEmpleados from './componentes/DirectorioEmpleados'
import FormularioEmpleado from './componentes/FormularioEmpleado'

function App() {
  const [edicionActiva, setEdicionActiva] = useState(null)

  return (
    <>
      {!edicionActiva && <FormularioEmpleado />}
      <DirectorioEmpleados
        edicionActiva={edicionActiva}
        onIniciarEdicion={setEdicionActiva}
        onTerminarEdicion={() => setEdicionActiva(null)}
      />
    </>
  )
}

export default App
