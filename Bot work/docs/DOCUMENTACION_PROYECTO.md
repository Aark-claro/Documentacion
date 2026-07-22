# 📘 Documentación Técnica — Bot Work

**Versión:** 2.0  
**Última actualización:** Julio 2026  
**Sistema:** Panel de Órdenes de Trabajo — Claro Colombia, Región Occidente

---

## 1. Visión General

Este proyecto automatiza dos procesos clave del área de operaciones:

1. **Descarga automatizada** de reportes de actividades desde Oracle Cloud Field Service (OFS), usando Selenium con Microsoft Edge.
2. **Visualización y monitoreo** de órdenes de trabajo (OTs) activas de Maximo, a través de una API REST (FastAPI) y un dashboard web (React).

---

## 2. Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                     Usuario Final                        │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (puerto 5173)
┌────────────────────────▼────────────────────────────────┐
│              Frontend — React + Vite                     │
│  Dashboard con KPIs, filtros, tabla paginada, gestor    │
│  de columnas y búsqueda en tiempo real                  │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (puerto 8000)
┌────────────────────────▼────────────────────────────────┐
│              Backend — FastAPI (Python)                  │
│  Endpoints: GET /api/ordenes, GET /api/ordenes/{id}     │
│  Lógica: cálculo de familia, segmento, días, horas      │
└────────────────────────┬────────────────────────────────┘
                         │ SSH Tunnel (puerto 3307)
┌────────────────────────▼────────────────────────────────┐
│         BD Contingencia — MySQL en servidor remoto       │
│  Tablas: maximo, oym_fijo, Region_Occidente, pymes...   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Script Descarga — Selenium (Edge, modo InPrivate)       │
│  Oracle Cloud Field Service (OFS)                        │
│  → Exporta .xlsx a BDS_work/ cada 15 minutos            │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Backend (FastAPI)

### 3.1 Archivo principal: `backend/main.py`

#### Conexión a la base de datos

La conexión se realiza a través de un **túnel SSH** hacia el servidor remoto:

| Parámetro | Valor |
|---|---|
| Host SSH | `186.147.60.119` |
| Usuario SSH | `ccot` |
| BD | `contingencia` (MySQL) |
| Puerto MySQL (remoto) | `3307` |
| Usuario MySQL | `otc_app` |

> ⚠️ Las credenciales están actualmente embebidas. Ver sección de seguridad.

#### Endpoint principal: `GET /api/ordenes`

Ejecuta el siguiente JOIN:

```sql
SELECT m.*, o.estado AS estado_oym
FROM maximo m
LEFT JOIN oym_fijo o ON m.orden_de_trabajo = o.orden_de_trabajo
    AND o.fin = (
        SELECT MAX(o2.fin) FROM oym_fijo o2
        WHERE o2.orden_de_trabajo = m.orden_de_trabajo
    )
WHERE 1=1
-- Filtros opcionales: estado, prioridad, aliado, departamento, tipo_de_trabajo
```

El subquery `MAX(o2.fin)` garantiza que cuando una OT tiene múltiples registros en `oym_fijo`, solo se toma el estado más reciente (el del último cierre de actividad).

#### Campos calculados

Estos campos **no existen en la BD** — se calculan en Python antes de responder:

| Campo | Fuente | Lógica |
|---|---|---|
| `familia` | `ruta_de_clasificacion` | Detecta "DEGRADACION", "RECLAMACION", "NOTIFICACION", "AFECTACION" |
| `segmento` | `ruta_de_clasificacion` | Lee el primer nivel antes de `\` para determinar segmento de negocio |
| `dias` | `fecha_de_creacion` | Diferencia en días entre creación y ahora |
| `horas` | `fecha_de_creacion` | Diferencia en horas entre creación y ahora |

#### Lógica de segmento

```python
primer_nivel = ruta_upper.split('\\')[0].strip()

"EMPRESAS Y NEGOCIOS" / "EYN"  → "Empresas y Negocios"
"SERVICIOS MOVILES"            → "Móviles"
"ODH 5G" / "5G"                → "Sin clasificar"
"REDES NEUTRAS"                → "Redes Neutras"
"SERVICIOS FIJOS"              → "Residencial"
```

#### Lógica de familia

```python
ruta_upper contiene:
  "DEGRADACION"  → "Degradación"
  "RECLAMACION"  → "Reclamación"
  "NOTIFICACION" → "Notificación"
  "AFECTACION"   → "Afectación de Servicio"
  (ninguno)      → "Sin clasificar"
```

### 3.2 Dependencias del backend

```
fastapi
uvicorn
sshtunnel
paramiko<3.0
mysql-connector-python
pydantic
```

---

## 4. Frontend (React + Vite)

### 4.1 Componentes

| Archivo | Responsabilidad |
|---|---|
| `App.jsx` | Estado global, fetch a la API, filtros, tabla, paginación, KPIs |
| `Filters.jsx` | Controles de filtros (estado, prioridad, aliado, departamento) |
| `ColumnManager.jsx` | Permite mostrar/ocultar columnas de la tabla |
| `App.css` | Estilos globales — paleta corporativa Claro |

### 4.2 Configuración de URL del backend

En `App.jsx`:

```javascript
const API_URL = 'http://localhost:8000/api'
```

Cambiar esta constante si el backend corre en otro host o puerto.

### 4.3 KPIs calculados en frontend

- **Total de órdenes** — `ordenes.length`
- **Alta prioridad** — filtro por `prioridad === 'Alto'`
- **En progreso** — filtro por estados activos (ASIGNADO, INICIADO)
- **Días promedio** — promedio de `orden.dias`

### 4.4 Paleta de colores

| Color | Hex | Uso |
|---|---|---|
| Claro Red | `#E30613` | Header, acciones principales |
| Claro Red Dark | `#c00510` | Hover states |
| Background | `#f5f7fa` | Fondo general |
| Text Primary | `#1f2937` | Texto de contenido |
| Success | `#10b981` | OTs nuevas / SLA OK |
| Warning | `#f59e0b` | OTs en proceso |
| Danger | `#E30613` | OTs críticas |

---

## 5. Scripts de Utilidad

### 5.1 Exploración (`scripts/exploracion/`)

Scripts de diagnóstico puntual. **No se usan en producción.**

| Script | Qué hace |
|---|---|
| `explorar_bd.py` | Lista columnas de `maximo`, muestra un registro de ejemplo |
| `explorar_oym.py` | Lista columnas de `oym_fijo` y muestra un registro |
| `explorar_todo.py` | Recorre todas las tablas, cuenta registros, detecta columnas SLA |

### 5.2 Búsqueda (`scripts/busqueda/`)

Scripts iterativos usados durante el desarrollo para descubrir qué columna/tabla contiene un dato.

| Script | Dato buscado |
|---|---|
| `buscar_familia.py` | Columna origen de "familia" de la OT |
| `buscar_segmento*.py` | Columna/tabla que da el segmento (Residencial, Pymes, etc.) |
| `buscar_sla*.py` | Fuente de datos SLA para OTs activas |
| `check_segmento.py` | Distribución de `ruta_de_clasificacion` en producción |

### 5.3 Verificación (`scripts/verificacion/`)

Scripts para validar integridad antes o después de cambios.

| Script | Qué valida |
|---|---|
| `verificar_alineacion.py` | Que BD, Backend y Frontend tengan los mismos campos |
| `verificar_bd.py` | Que el JOIN del backend funciona correctamente |
| `verificar_fechas.py` | Formato y cobertura de columnas de fecha |
| `verificar_oym_duplicados.py` | OTs con múltiples filas en `oym_fijo` |
| `verificar_oym_estados.py` | Estados de OTs duplicadas en `oym_fijo` |
| `verificar_reportes_aliados.py` | Cruce con tabla `reportes_tecnicos_aliados` |
| `verificar_sla_activo.py` | Cobertura de SLA en tablas WFM para OTs activas |

### 5.4 Descarga (`scripts/descarga/`)

| Script | Qué hace |
|---|---|
| `descarga_bds_oracle.py` | Loop de 15 min: descarga 4 BDs de Oracle Cloud OFS (≈105 archivos) |
| `descarga_oym.py` | Descarga archivos OYM desde Oracle Cloud OFS |

#### Bases de datos descargadas

| BD en Oracle OFS | Carpeta destino | Fechas |
|---|---|---|
| RECURSOS OCCIDENTE (INTEGRAL) SEG FIJA | `BDS_work/Recursos_Occidente/` | Ayer y hoy (2 archivos) |
| PYMES OCCIDENTE | `BDS_work/Pymes_Occidente/` | Hoy + 20 días (21 archivos) |
| REGION OCCIDENTE | `BDS_work/Region_Occidente/` | Hoy + 20 días (21 archivos) |
| DTH OCCIDENTE (O) | `BDS_work/DTH_Occidente/` | Hoy + 60 días (61 archivos) |

---

## 6. Base de Datos

### 6.1 Tabla `maximo` (principal)

Contiene todas las OTs activas sincronizadas desde Maximo IBM. Campos clave:

| Columna | Descripción |
|---|---|
| `id` | PK autoincremental |
| `orden_de_trabajo` | ID de OT (ej: OT5212072) |
| `estado` | Estado en Maximo (ASIGNADO, INICIADO, ESPERA, SUSPENDIDO) |
| `prioridad` | Alto / Medio / Bajo |
| `aliado` | Empresa contratista responsable |
| `ruta_de_clasificacion` | Jerarquía de clasificación — fuente de `familia` y `segmento` |
| `fecha_de_creacion` | Timestamp de creación de la OT |
| `ot_wfm` | ID de la OT en el sistema WFM |

### 6.2 Tabla `oym_fijo`

Registros de actividades de campo (O&M). Puede tener múltiples registros por OT.

| Columna | Descripción |
|---|---|
| `orden_de_trabajo` | FK hacia `maximo` |
| `estado` | Estado en O&M (puede diferir del estado Maximo) |
| `fin` | Timestamp de cierre de actividad — usado para obtener el más reciente |
| `fecha` | Fecha del registro |

### 6.3 Tablas WFM (Region_Occidente, pymes, dth)

Generadas a partir de los archivos descargados de Oracle OFS. Contienen datos de SLA por OT.

| Columna relevante | Descripción |
|---|---|
| `orden_de_trabajo` | FK para cruce con `maximo` |
| `estado_sla` | Estado del SLA (DENTRO, FUERA, etc.) |
| `sla_suscriptor` | Tiempo SLA comprometido con el suscriptor (horas) |
| `sla_cumplimiento` | Tiempo de cumplimiento real (horas) |

---

## 7. Flujo de Datos

```
Oracle Cloud OFS
      │  (Selenium cada 15 min)
      ▼
BDS_work/*.xlsx  ─────────────────────────────►  BD MySQL (contingencia)
                                                        │
                                              (túnel SSH + mysql-connector)
                                                        │
                                                  FastAPI backend
                                                        │
                                              GET /api/ordenes (JSON)
                                                        │
                                               React frontend
                                                        │
                                                 Dashboard web
```

---

## 8. Seguridad y Configuración

### 8.1 Estado actual (desarrollo)

Las credenciales están embebidas directamente en el código:

```python
SSH_CONFIG = {"host": "...", "user": "ccot", "password": "..."}
DB_CONFIG  = {"user": "otc_app", "password": "..."}
```

### 8.2 Recomendado (producción)

Crear un archivo `.env` en la raíz del proyecto:

```ini
SSH_HOST=186.147.60.119
SSH_USER=ccot
SSH_PASSWORD=...

DB_USER=otc_app
DB_PASSWORD=...
DB_NAME=contingencia

ORACLE_EMAIL=38101491@claro.com.co
ORACLE_PASSWORD=...
```

Cargarlas en Python con `python-dotenv`:

```python
from dotenv import load_dotenv
import os
load_dotenv()
SSH_CONFIG = {"host": os.getenv("SSH_HOST"), ...}
```

Y agregar al `.gitignore`:

```
.env
BDS_work/
```

---

## 9. Cómo Ejecutar el Sistema Completo

```bash
# Terminal 1 — Backend
cd backend
pip install -r requirements.txt
python main.py

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev

# Terminal 3 (opcional) — Descarga automática
cd scripts/descarga
python descarga_bds_oracle.py
```

Abrir `http://localhost:5173` en el navegador.

---

## 10. Glosario

| Término | Significado |
|---|---|
| OT | Orden de Trabajo |
| WFM | Workforce Management (sistema de gestión de campo) |
| OFS | Oracle Field Service |
| OYM | Operación y Mantenimiento |
| SLA | Service Level Agreement (acuerdo de nivel de servicio) |
| BD | Base de Datos |
| SSO | Single Sign-On (autenticación corporativa Microsoft) |
| DTH | Direct To Home (servicio de televisión satelital) |
| Maximo | IBM Maximo — sistema EAM de gestión de activos |
