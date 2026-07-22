import { useState, useEffect } from 'react'

const FILTROS_INIT = {
  segmento: 'todos',
  familia: 'todos',
  aliado: 'todos',
  estado: 'todos',
  estado_oym: 'todos',
  prioridad: 'todos',
  departamento: 'todos',
  tipo_de_trabajo: 'todos',
}

export default function Filters({ ordenes, onAplicarFiltros }) {
  const [filtros, setFiltros] = useState(FILTROS_INIT)

  // Extraer opciones únicas de cada campo
  const opciones = (campo) => {
    const vals = [...new Set(ordenes.map(o => o[campo]).filter(Boolean))].sort()
    return vals
  }

  useEffect(() => {
    onAplicarFiltros(filtros)
  }, [filtros])

  const cambiar = (campo, valor) => {
    setFiltros(prev => ({ ...prev, [campo]: valor }))
  }

  const limpiar = () => setFiltros(FILTROS_INIT)

  const hayFiltrosActivos = Object.values(filtros).some(v => v !== 'todos')

  return (
    <div className="filters-panel">
      <div className="filters-row">
        <Select label="Segmento" campo="segmento" filtros={filtros} opciones={opciones} onChange={cambiar} />
        <Select label="Familia" campo="familia" filtros={filtros} opciones={opciones} onChange={cambiar} />
        <Select label="Jefe Integral" campo="aliado" filtros={filtros} opciones={opciones} onChange={cambiar} />
        <Select label="Estado Maximo" campo="estado" filtros={filtros} opciones={opciones} onChange={cambiar} />
        <Select label="Estado Workforce" campo="estado_oym" filtros={filtros} opciones={opciones} onChange={cambiar} />
        <Select label="Prioridad" campo="prioridad" filtros={filtros} opciones={opciones} onChange={cambiar} />
        <Select label="Departamento" campo="departamento" filtros={filtros} opciones={opciones} onChange={cambiar} />
        <Select label="Red" campo="tipo_de_trabajo" filtros={filtros} opciones={opciones} onChange={cambiar} />
        {hayFiltrosActivos && (
          <button className="toolbar-btn limpiar-btn" onClick={limpiar}>
            ✕ Limpiar
          </button>
        )}
      </div>
    </div>
  )
}

function Select({ label, campo, filtros, opciones, onChange }) {
  return (
    <div className="filter-group">
      <label className="filter-label">{label}</label>
      <select
        className="filter-select"
        value={filtros[campo]}
        onChange={e => onChange(campo, e.target.value)}
      >
        <option value="todos">Todos</option>
        {opciones(campo).map(op => (
          <option key={op} value={op}>{op}</option>
        ))}
      </select>
    </div>
  )
}
