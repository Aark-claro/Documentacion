export default function ColumnManager({ columnas, onToggleColumna, onCerrar }) {
  const grupos = [
    {
      label: '📌 Principales',
      keys: ['orden_de_trabajo', 'dias', 'segmento', 'familia', 'aliado', 'ciudad___municipio', 'prioridad'],
    },
    {
      label: '📊 Estado',
      keys: ['estado', 'estado_oym', 'descripcion_estado', 'estado_incidente'],
    },
    {
      label: '🔧 Trabajo',
      keys: ['tipo_de_trabajo', 'clasificacion', 'ruta_de_clasificacion', 'descripcion', 'incidente_relacionado', 'completado_por_contratista'],
    },
    {
      label: '📍 Ubicación',
      keys: ['ubicacion', 'regional', 'departamento', 'articulo_de_configuracion', 'smu'],
    },
    {
      label: '👤 Responsables',
      keys: ['propietario', 'grupo_site_owner', 'descripcion_grupo', 'ot_wfm'],
    },
    {
      label: '📅 Fechas',
      keys: ['fecha_de_creacion', 'inicio_real', 'finalizacion_real', 'inicio_programado', 'finalizacion_programada', 'fecha_actualizacion', 'fecha_carga'],
    },
  ]

  const colMap = Object.fromEntries(columnas.map(c => [c.key, c]))

  const visibles = columnas.filter(c => c.visible).length
  const total = columnas.length

  return (
    <div className="cm-overlay" onClick={onCerrar}>
      <div className="cm-panel" onClick={e => e.stopPropagation()}>

        <div className="cm-header">
          <div className="cm-title">
            <span className="cm-title-icon">⚙</span>
            Gestionar columnas
            <span className="cm-badge">{visibles}/{total}</span>
          </div>
          <button className="cm-cerrar" onClick={onCerrar}>✕</button>
        </div>

        <div className="cm-body">
          {grupos.map(grupo => {
            const colsDelGrupo = grupo.keys.map(k => colMap[k]).filter(Boolean)
            return (
              <div key={grupo.label} className="cm-grupo">
                <div className="cm-grupo-label">{grupo.label}</div>
                <div className="cm-grupo-items">
                  {colsDelGrupo.map(col => (
                    <label
                      key={col.key}
                      className={`cm-item ${col.fixed ? 'cm-fixed' : ''} ${col.visible ? 'cm-checked' : ''}`}
                    >
                      <input
                        type="checkbox"
                        checked={col.visible}
                        disabled={col.fixed}
                        onChange={() => onToggleColumna(col.key)}
                      />
                      <span className="cm-item-label">{col.label}</span>
                      {col.fixed && <span className="cm-fixed-tag">fija</span>}
                    </label>
                  ))}
                </div>
              </div>
            )
          })}
        </div>

        <div className="cm-footer">
          <button
            className="cm-btn-secondary"
            onClick={() => columnas.filter(c => !c.fixed && c.visible).forEach(c => onToggleColumna(c.key))}
          >
            Ocultar todas
          </button>
          <button
            className="cm-btn-primary"
            onClick={() => columnas.filter(c => !c.fixed && !c.visible).forEach(c => onToggleColumna(c.key))}
          >
            Mostrar todas
          </button>
        </div>

      </div>
    </div>
  )
}
