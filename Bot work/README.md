# 🤖 Bot Work — Panel de Órdenes de Trabajo Claro

Sistema de monitoreo y gestión de órdenes de trabajo (OTs) de Maximo, con descarga automatizada desde Oracle Cloud Field Service y visualización en tiempo real a través de una API REST y un dashboard web.

---

## 📁 Estructura del Proyecto

```
Bot work/
│
├── backend/                        # API REST en FastAPI
│   ├── main.py                     # Servidor principal, endpoints y lógica de negocio
│   └── requirements.txt            # Dependencias Python del backend
│
├── frontend/                       # Dashboard web en React + Vite
│   ├── src/
│   │   ├── App.jsx                 # Componente principal
│   │   ├── App.css                 # Estilos globales
│   │   └── components/
│   │       ├── Filters.jsx         # Componente de filtros
│   │       └── ColumnManager.jsx   # Gestor de columnas visibles
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── scripts/                        # Scripts de utilidad y diagnóstico
│   ├── exploracion/                # Exploran estructura de la BD
│   │   ├── explorar_bd.py          # Estructura y columnas de tabla maximo
│   │   ├── explorar_oym.py         # Estructura de tabla oym_fijo
│   │   └── explorar_todo.py        # Exploración completa de todas las tablas
│   │
│   ├── busqueda/                   # Buscan datos o columnas específicas
│   │   ├── buscar_familia.py       # Ubica la columna de familia en la BD
│   │   ├── buscar_segmento*.py     # Iteraciones para hallar la fuente del segmento
│   │   ├── buscar_sla*.py          # Iteraciones para hallar fuente de SLA
│   │   └── check_segmento.py       # Verifica distribución de ruta_de_clasificacion
│   │
│   ├── verificacion/               # Validan integridad y alineación
│   │   ├── verificar_alineacion.py # Compara BD ↔ Backend ↔ Frontend
│   │   ├── verificar_bd.py         # Prueba conexión y JOINs del backend
│   │   ├── verificar_fechas.py     # Inspecciona formatos de fecha en la BD
│   │   ├── verificar_oym_duplicados.py  # Detecta OTs duplicadas en oym_fijo
│   │   ├── verificar_oym_estados.py     # Analiza estados de OTs en oym_fijo
│   │   ├── verificar_reportes_aliados.py # Cruza maximo con reportes_tecnicos_aliados
│   │   └── verificar_sla_activo.py      # Verifica cobertura SLA en tablas WFM
│   │
│   └── descarga/                   # Automatizan descarga desde Oracle Cloud
│       ├── descarga_bds_oracle.py  # Descarga las 4 BDs (Recursos, Pymes, Region, DTH)
│       └── descarga_oym.py         # Descarga archivos OYM
│
├── BDS_work/                       # Archivos Excel descargados desde Oracle
│   ├── Recursos_Occidente/
│   ├── Pymes_Occidente/
│   ├── Region_Occidente/
│   └── DTH_Occidente/
│
├── docs/                           # Documentación del proyecto
│   ├── README_INSTRUCCIONES.md     # Guía de instalación y uso
│   ├── CHANGELOG_DISENO.md         # Historial de cambios visuales del frontend
│   ├── DOCUMENTACION_PROYECTO.md   # Documentación técnica completa
│   └── FALLAS_Y_SOLUCIONES.md      # Guía de troubleshooting
│
├── requirements.txt                # Dependencias raíz (descarga + scripts)
└── README.md                       # Este archivo
```

---

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
# Scripts de utilidad (raíz del proyecto)
pip install -r requirements.txt

# Backend
cd backend
pip install -r requirements.txt
```

### 2. Levantar el backend

```bash
cd backend
python main.py
# API disponible en http://localhost:8000
# Documentación en http://localhost:8000/docs
```

### 3. Levantar el frontend

```bash
cd frontend
npm install
npm run dev
# Dashboard en http://localhost:5173
```

---

## 🔧 Componentes Principales

| Componente | Tecnología | Puerto | Descripción |
|---|---|---|---|
| Backend API | FastAPI + Uvicorn | 8000 | Consulta BD vía SSH y expone REST |
| Frontend | React 18 + Vite | 5173 | Dashboard con filtros y KPIs |
| BD Contingencia | MySQL (vía SSH) | 3307 | Fuente de datos principal |
| Descarga Oracle | Selenium + Edge | — | Automatiza exportación de reportes |

---

## 📊 Fuentes de Datos

- **`maximo`** — Tabla principal de órdenes de trabajo
- **`oym_fijo`** — Estado O&M del campo (estado externo)
- **`Region_Occidente`** / **`pymes`** / **`dth`** — Tablas WFM con datos de SLA
- **`reportes_tecnicos_aliados`** — Reportes de aliados de campo

---

## 📖 Documentación Adicional

- [Instrucciones de instalación](docs/README_INSTRUCCIONES.md)
- [Documentación técnica](docs/DOCUMENTACION_PROYECTO.md)
- [Guía de fallas y soluciones](docs/FALLAS_Y_SOLUCIONES.md)
- [Changelog de diseño](docs/CHANGELOG_DISENO.md)

---

## ⚠️ Seguridad

Este proyecto contiene credenciales embebidas en el código (SSH, MySQL, Oracle). Antes de subir a cualquier repositorio o compartir:

1. Mover todas las credenciales a un archivo `.env`
2. Agregar `.env` al `.gitignore`
3. Usar `python-dotenv` para cargarlas en runtime
