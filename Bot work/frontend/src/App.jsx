import { useState, useEffect } from 'react'
import './App.css'
import ColumnManager from './components/ColumnManager'
import Filters from './components/Filters'
import claroLogo from '../imagenes/logo.png'

const API_URL = '/api'

const TODAS_LAS_COLUMNAS = [
  { key: 'orden_de_trabajo', label: 'N° ORDEN', visible: true, fixed: true },
  { key: 'dias', label: 'TIEMPO', visible: true, fixed: true },
  { key: 'segmento', label: 'SEGMENTO', visible: true },
  { key: 'familia', label: 'FAMILIA', visible: true },
  { key: 'aliado', label: 'JEFE INTEGRAL', visible: true },
  { key: 'ciudad___municipio', label: 'CIUDAD', visible: true },
  { key: 'prioridad', label: 'PRIORIDAD', visible: true },
  { key: 'incidente_relacionado', label: 'INCIDENTE REL.', visible: true },
  { key: 'estado', label: 'ESTADO MÁXIMO', visible: true },
  { key: 'estado_oym', label: 'ESTADO WORKFORCE', visible: true },
  { key: 'tipo_de_trabajo', label: 'RED', visible: true },
  { key: 'clasificacion', label: 'TIPIFICACIÓN', visible: false },
  { key: 'descripcion', label: 'DESCRIPCIÓN', visible: false },
  { key: 'articulo_de_configuracion', label: 'ARTÍCULO CONFIG.', visible: false },
  { key: 'ubicacion', label: 'UBICACIÓN', visible: false },
  { key: 'regional', label: 'REGIONAL', visible: false },
  { key: 'departamento', label: 'DEPARTAMENTO', visible: false },
  { key: 'ot_wfm', label: 'OT WFM', visible: false },
  { key: 'descripcion_estado', label: 'DESC. ESTADO', visible: false },
  { key: 'completado_por_contratista', label: 'COMPLETADO POR', visible: false },
  { key: 'estado_incidente', label: 'ESTADO INCIDENTE', visible: false },
  { key: 'ruta_de_clasificacion', label: 'RUTA CLASIFICACIÓN', visible: false },
  { key: 'propietario', label: 'PROPIETARIO', visible: false },
  { key: 'grupo_site_owner', label: 'GRUPO OWNER', visible: false },
  { key: 'descripcion_grupo', label: 'DESC. GRUPO', visible: false },
  { key: 'smu', label: 'SMU', visible: false },
  { key: 'fecha_de_creacion', label: 'FECHA CREACIÓN', visible: false },
  { key: 'inicio_real', label: 'INICIO REAL', visible: false },
  { key: 'finalizacion_real', label: 'FIN REAL', visible: false },
  { key: 'inicio_programado', label: 'INICIO PROG.', visible: false },
  { key: 'finalizacion_programada', label: 'FIN PROG.', visible: false },
  { key: 'fecha_actualizacion', label: 'ACTUALIZACIÓN', visible: false },
  { key: 'fecha_carga', label: 'FECHA CARGA', visible: false },
]

function KpiCard({ label, value, color, icon }) {
  return (
    <div className={`kpi-card kpi-${color}`}>
      <span className="kpi-icon">{icon}</span>
      <div className="kpi-data">
        <span className="kpi-value">{value}</span>
        <span className="kpi-label">{label}</span>
      </div>
    </div>
  )
}

function App() {
  const [ordenes, setOrdenes] = useState([])
  const [ordenesFiltradas, setOrdenesFiltradas] = useState([])
  const [loading, setLoading] = useState(true)
  const [paginaActual, setPaginaActual] = useState(1)
  const [columnas, setColumnas] = useState(TODAS_LAS_COLUMNAS)
  const [mostrarColumnManager, setMostrarColumnManager] = useState(false)
  const [mostrarFiltros, setMostrarFiltros] = useState(false)
  const [busqueda, setBusqueda] = useState('')
  const [ultimaActualizacion, setUltimaActualizacion] = useState(null)
  const [refrescando, setRefrescando] = useState(false)

  const ordenesPerPage = 10

  useEffect(() => {
    cargarOrdenes()
    const intervalo = setInterval(() => cargarOrdenes(true), 5 * 60 * 1000)
    return () => clearInterval(intervalo)
  }, [])

  const cargarOrdenes = async (esAutoRefresh = false) => {
    if (!esAutoRefresh) setLoading(true)
    else setRefrescando(true)
    try {
      const res = await fetch(`${API_URL}/ordenes`)
      const data = await res.json()
      const ordenadas = data.ordenes.sort((a, b) => {
        // Afectaciones primero
        const aAfect = a.familia === 'Afectación de Servicio' ? 0 : 1
        const bAfect = b.familia === 'Afectación de Servicio' ? 0 : 1
        if (aAfect !== bAfect) return aAfect - bAfect
        // Dentro de cada grupo, más antiguas primero
        return new Date(a.fecha_de_creacion) - new Date(b.fecha_de_creacion)
      })
      setOrdenes(ordenadas)
      setOrdenesFiltradas(ordenadas)
      setUltimaActualizacion(new Date())
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
      setRefrescando(false)
    }
  }

  const refrescarManual = () => {
    cargarOrdenes()
    setPaginaActual(1)
  }

  const formatearHora = () => {
    if (!ultimaActualizacion) return ''
    return ultimaActualizacion.toLocaleTimeString('es-CO', {
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    })
  }

  const aplicarFiltros = (filtros) => {
    let resultado = [...ordenes]

    if (busqueda) {
      resultado = resultado.filter(orden =>
        Object.values(orden).some(valor =>
          String(valor).toLowerCase().includes(busqueda.toLowerCase())
        )
      )
    }

    if (filtros.estado_oym && filtros.estado_oym !== 'todos')
      resultado = resultado.filter(o => o.estado_oym === filtros.estado_oym)
    if (filtros.segmento && filtros.segmento !== 'todos')
      resultado = resultado.filter(o => o.segmento === filtros.segmento)
    if (filtros.familia && filtros.familia !== 'todos')
      resultado = resultado.filter(o => o.familia === filtros.familia)
    if (filtros.aliado && filtros.aliado !== 'todos')
      resultado = resultado.filter(o => o.aliado === filtros.aliado)
    if (filtros.estado && filtros.estado !== 'todos')
      resultado = resultado.filter(o => o.estado === filtros.estado)
    if (filtros.prioridad && filtros.prioridad !== 'todos')
      resultado = resultado.filter(o => o.prioridad === filtros.prioridad)
    if (filtros.departamento && filtros.departamento !== 'todos')
      resultado = resultado.filter(o => o.departamento === filtros.departamento)
    if (filtros.tipo_de_trabajo && filtros.tipo_de_trabajo !== 'todos')
      resultado = resultado.filter(o => o.tipo_de_trabajo === filtros.tipo_de_trabajo)

    setOrdenesFiltradas(resultado)
    setPaginaActual(1)
  }

  const cambiarVisibilidadColumna = (key) => {
    setColumnas(prev =>
      prev.map(col => col.key === key && !col.fixed ? { ...col, visible: !col.visible } : col)
    )
  }

  // KPIs calculados
  const kpis = {
    total: ordenesFiltradas.length,
    afectacion: ordenesFiltradas.filter(o => o.familia === 'Afectación de Servicio').length,
    iniciadas: ordenesFiltradas.filter(o => o.estado?.toLowerCase() === 'iniciado').length,
    sinAgenda: ordenesFiltradas.filter(o => !o.estado_oym).length,
  }

  const columnasVisibles = columnas.filter(col => col.visible)
  const totalPaginas = Math.ceil(ordenesFiltradas.length / ordenesPerPage)
  const inicio = (paginaActual - 1) * ordenesPerPage
  const ordenesActuales = ordenesFiltradas.slice(inicio, inicio + ordenesPerPage)

  const filaDiasClass = (orden) => {
    const dias = orden.dias || 0
    if (dias > 30) return 'fila-critica'
    if (dias > 7) return 'fila-alta'
    if (dias === 0) return 'fila-nueva'
    return ''
  }

  const formatearValor = (key, valor, orden) => {
    if (key === 'estado_oym') {
      if (!valor) return <span className="badge-estado-oym sin-agenda">Sin agenda</span>
      const cls = valor.toLowerCase().replace(/\s+/g, '-')
      const iconMap = {
        'completado': '✓',
        'suspendido': '⏸',
        'pendiente': '◷',
        'cancelado': '✕',
      }
      const icon = iconMap[valor.toLowerCase()] || '●'
      return (
        <span className={`badge-estado-oym ${cls}`}>
          {icon} {valor}
        </span>
      )
    }

    if (!valor && valor !== 0) return <span className="valor-vacio">—</span>

    if (key === 'dias') {
      const dias = orden.dias || 0
      const horas = orden.horas || 0
      if (dias === 0) {
        return (
          <span className="badge-dias nuevo">
            {horas}h
          </span>
        )
      }
      return (
        <span className={`badge-dias ${dias > 30 ? 'critico' : dias > 7 ? 'alto' : 'normal'}`}>
          {dias}d
        </span>
      )
    }

    if (key === 'familia') {
      const claseMap = {
        'Degradación': 'degradacion',
        'Reclamación': 'reclamacion',
        'Notificación': 'notificacion',
        'Afectación de Servicio': 'afectacion',
      }
      return (
        <span className={`badge-familia ${claseMap[valor] || ''}`}>
          {valor}
        </span>
      )
    }

    if (key === 'segmento') {
      const claseMap = {
        'Residencial': 'residencial',
        'Empresas y Negocios': 'empresas',
        'Móviles': 'moviles',
        '5G': 'fiveg',
        'Redes Neutras': 'redes-neutras',
      }
      const iconMap = {
        'Residencial': '🏠',
        'Empresas y Negocios': '🏢',
        'Móviles': '📱',
        '5G': '⚡',
        'Redes Neutras': '🔗',
      }
      return (
        <span className={`badge-segmento ${claseMap[valor] || ''}`}>
          {iconMap[valor] || '●'} {valor}
        </span>
      )
    }

    if (key === 'prioridad') {
      return (
        <span className={`badge-prioridad ${valor === 'Alto' ? 'p1' : valor === 'Medio' ? 'p2' : 'p3'}`}>
          {valor === 'Alto' ? '▲ Alto' : valor === 'Medio' ? '● Medio' : '▼ Bajo'}
        </span>
      )
    }

    if (key === 'estado') {
      return (
        <span className={`badge-estado ${valor?.toLowerCase()}`}>
          {valor}
        </span>
      )
    }

    if (key === 'orden_de_trabajo') {
      return <span className="orden">{valor}</span>
    }

    if (key.includes('fecha') || key.includes('inicio') || key.includes('finalizacion')) {
      return valor ? new Date(valor).toLocaleDateString('es-CO', {
        year: 'numeric', month: '2-digit', day: '2-digit'
      }) : '—'
    }

    return valor
  }

  if (loading) return (
    <div className="loading-screen">
      <div className="loading-spinner"></div>
      <span>Cargando órdenes...</span>
    </div>
  )

  return (
    <div className="app">
      {/* HEADER */}
      <header className="header">
        <div className="header-brand">
          <img src={claroLogo} alt="Claro" className="brand-logo-img" />
          <div>
            <h1>Panel de Órdenes de Trabajo</h1>
            <p>Sistema Máximo · Regional Occidente</p>
          </div>
        </div>

        <div className="header-kpis">
          <KpiCard label="Total OTs"           value={kpis.total}      color="blanco"   icon="📋" />
          <KpiCard label="Afectaciones"        value={kpis.afectacion} color="rojo"     icon="⚠️" />
          <KpiCard label="Iniciadas"           value={kpis.iniciadas}  color="verde"    icon="▶" />
          <KpiCard label="Sin Agenda"          value={kpis.sinAgenda}  color="gris"     icon="○" />
        </div>

        <div className="header-nav">
          <div className="info-registros">
            {ordenesFiltradas.length} de {ordenes.length} órdenes
          </div>
          <div className="paginacion">
            <button onClick={() => setPaginaActual(1)} disabled={paginaActual === 1} title="Primera">«</button>
            <button onClick={() => setPaginaActual(p => Math.max(1, p - 1))} disabled={paginaActual === 1}>‹</button>
            <span className="pagina-info">{paginaActual} / {totalPaginas}</span>
            <button onClick={() => setPaginaActual(p => Math.min(totalPaginas, p + 1))} disabled={paginaActual === totalPaginas}>›</button>
            <button onClick={() => setPaginaActual(totalPaginas)} disabled={paginaActual === totalPaginas} title="Última">»</button>
          </div>
        </div>
      </header>

      {/* TOOLBAR */}
      <div className="toolbar">
        <div className="busqueda-container">
          <span className="busqueda-icon">🔍</span>
          <input
            type="text"
            placeholder="Buscar en todas las columnas..."
            value={busqueda}
            onChange={(e) => { setBusqueda(e.target.value); aplicarFiltros({}) }}
            className="busqueda-input"
          />
          {busqueda && (
            <button className="busqueda-limpiar" onClick={() => { setBusqueda(''); aplicarFiltros({}) }}>✕</button>
          )}
        </div>
        <div className="toolbar-right">
          {ultimaActualizacion && (
            <span className="ultima-act">
              <span className={`dot-live ${refrescando ? 'pulsando' : ''}`}></span>
              {formatearHora()}
            </span>
          )}
          <button className="toolbar-btn" onClick={refrescarManual} disabled={loading || refrescando}>
            <span className={refrescando ? 'spinning' : ''}>↻</span>
            {refrescando ? 'Actualizando…' : 'Refrescar'}
          </button>
          <button className={`toolbar-btn ${mostrarFiltros ? 'active' : ''}`} onClick={() => setMostrarFiltros(!mostrarFiltros)}>
            ⚡ Filtros
          </button>
          <button className={`toolbar-btn ${mostrarColumnManager ? 'active' : ''}`} onClick={() => setMostrarColumnManager(!mostrarColumnManager)}>
            ⚙ Columnas ({columnasVisibles.length})
          </button>
        </div>
      </div>

      {/* FILTROS */}
      {mostrarFiltros && (
        <Filters ordenes={ordenes} onAplicarFiltros={aplicarFiltros} />
      )}

      {/* COLUMN MANAGER */}
      {mostrarColumnManager && (
        <ColumnManager
          columnas={columnas}
          onToggleColumna={cambiarVisibilidadColumna}
          onCerrar={() => setMostrarColumnManager(false)}
        />
      )}

      {/* TABLA */}
      <div className="tabla-wrapper">
        <table className="tabla">
          <thead>
            <tr>
              <th className="th-num">#</th>
              {columnasVisibles.map(col => (
                <th key={col.key}>{col.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ordenesActuales.map((orden, idx) => (
              <tr key={orden.id} className={filaDiasClass(orden)}>
                <td className="td-num">{inicio + idx + 1}</td>
                {columnasVisibles.map(col => (
                  <td key={col.key} className={`col-${col.key}`}>
                    {formatearValor(col.key, orden[col.key], orden)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>

        {ordenesFiltradas.length === 0 && (
          <div className="empty-state">
            <span className="empty-icon">🔎</span>
            <p>No se encontraron órdenes con los criterios seleccionados</p>
          </div>
        )}
      </div>

      {/* FOOTER PAGINACION */}
      <div className="footer-paginacion">
        <span className="footer-info">
          Mostrando {inicio + 1}–{Math.min(inicio + ordenesPerPage, ordenesFiltradas.length)} de {ordenesFiltradas.length} órdenes
        </span>
        <div className="paginacion">
          <button onClick={() => setPaginaActual(1)} disabled={paginaActual === 1}>«</button>
          <button onClick={() => setPaginaActual(p => Math.max(1, p - 1))} disabled={paginaActual === 1}>‹</button>
          {Array.from({ length: Math.min(5, totalPaginas) }, (_, i) => {
            let page
            if (totalPaginas <= 5) page = i + 1
            else if (paginaActual <= 3) page = i + 1
            else if (paginaActual >= totalPaginas - 2) page = totalPaginas - 4 + i
            else page = paginaActual - 2 + i
            return (
              <button
                key={page}
                onClick={() => setPaginaActual(page)}
                className={paginaActual === page ? 'active' : ''}
              >{page}</button>
            )
          })}
          <button onClick={() => setPaginaActual(p => Math.min(totalPaginas, p + 1))} disabled={paginaActual === totalPaginas}>›</button>
          <button onClick={() => setPaginaActual(totalPaginas)} disabled={paginaActual === totalPaginas}>»</button>
        </div>
      </div>
    </div>
  )
}

export default App
