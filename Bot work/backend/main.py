from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sshtunnel import SSHTunnelForwarder
import mysql.connector
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(title="Maximo API", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración SSH y MySQL
SSH_CONFIG = {
    "host": "186.147.60.119",
    "user": "ccot",
    "password": "Siesconmigo*"
}

DB_CONFIG = {
    "user": "otc_app",
    "password": "22122012Elf@",
    "database": "contingencia",
    "host": "127.0.0.1",
    "port": 3307
}

# Modelos Pydantic
class Orden(BaseModel):
    model_config = {"from_attributes": True}
    
    id: int
    fecha_actualizacion: Optional[str] = None
    fecha_carga: Optional[str] = None
    orden_de_trabajo: Optional[str] = None
    descripcion: Optional[str] = None
    prioridad: Optional[str] = None
    articulo_de_configuracion: Optional[str] = None
    ubicacion: Optional[str] = None
    regional: Optional[str] = None
    departamento: Optional[str] = None
    ciudad___municipio: Optional[str] = None
    aliado: Optional[str] = None
    familia: Optional[str] = None
    ot_wfm: Optional[str] = None
    tipo_de_trabajo: Optional[str] = None
    estado: Optional[str] = None
    descripcion_estado: Optional[str] = None
    completado_por_contratista: Optional[str] = None
    incidente_relacionado: Optional[str] = None
    estado_incidente: Optional[str] = None
    clasificacion: Optional[str] = None
    ruta_de_clasificacion: Optional[str] = None
    propietario: Optional[str] = None
    grupo_site_owner: Optional[str] = None
    descripcion_grupo: Optional[str] = None
    smu: Optional[str] = None
    fecha_de_creacion: Optional[str] = None
    inicio_real: Optional[str] = None
    finalizacion_real: Optional[str] = None
    inicio_programado: Optional[str] = None
    finalizacion_programada: Optional[str] = None
    dias: Optional[int] = None  # Campo calculado
    horas: Optional[int] = None  # Horas totales desde creación
    estado_oym: Optional[str] = None  # Estado desde oym_fijo
    segmento: Optional[str] = None  # Campo calculado desde ruta_de_clasificacion

class OrdenesResponse(BaseModel):
    total: int
    ordenes: List[Orden]

def calcular_familia(ruta: str) -> str:
    """Extrae la familia a partir de ruta_de_clasificacion."""
    ruta_upper = (ruta or '').upper()
    if 'DEGRADACION' in ruta_upper or 'DEGRADACIÓN' in ruta_upper:
        return 'Degradación'
    elif 'RECLAMACION' in ruta_upper or 'RECLAMACIÓN' in ruta_upper:
        return 'Reclamación'
    elif 'NOTIFICACION' in ruta_upper or 'NOTIFICACIÓN' in ruta_upper:
        return 'Notificación'
    elif 'AFECTACION' in ruta_upper or 'AFECTACIÓN' in ruta_upper:
        return 'Afectación de Servicio'
    return 'Sin clasificar'


def calcular_segmento(ruta: str) -> str:
    """
    Determina el segmento a partir del primer nivel de ruta_de_clasificacion.
    Ejemplos:
      'SERVICIOS FIJOS \\ ...'         → 'Residencial'
      'EMPRESAS Y NEGOCIOS \\ ...'     → 'Empresas y Negocios'
      'SERVICIOS MOVILES \\ ...'       → 'Móviles'
      'ODH 5G \\ ...'                  → '5G'
      'REDES NEUTRAS_EYN \\ ...'       → 'Redes Neutras'
    """
    ruta_upper = (ruta or '').upper().strip()
    if not ruta_upper:
        return 'Sin clasificar'
    primer_nivel = ruta_upper.split('\\')[0].strip()
    if 'EMPRESAS Y NEGOCIOS' in primer_nivel or 'EYN' in primer_nivel:
        return 'Empresas y Negocios'
    if 'SERVICIOS MOVILES' in primer_nivel or 'MOVILES' in primer_nivel:
        return 'Móviles'
    if 'ODH 5G' in primer_nivel or '5G' in primer_nivel:
        return 'Sin clasificar'
    if 'REDES NEUTRAS' in primer_nivel:
        return 'Redes Neutras'
    if 'SERVICIOS FIJOS' in primer_nivel:
        return 'Residencial'
    return 'Sin clasificar'


def get_db_connection():
    """Establece conexión con la BD a través de SSH"""
    tunnel = SSHTunnelForwarder(
        (SSH_CONFIG["host"], 22),
        ssh_username=SSH_CONFIG["user"],
        ssh_password=SSH_CONFIG["password"],
        remote_bind_address=(DB_CONFIG["host"], DB_CONFIG["port"])
    )
    tunnel.start()
    
    connection = mysql.connector.connect(
        host='127.0.0.1',
        port=tunnel.local_bind_port,
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )
    
    return tunnel, connection

@app.get("/")
def root():
    """Endpoint raíz"""
    return {
        "message": "Maximo API",
        "version": "1.0.0",
        "endpoints": {
            "ordenes": "/api/ordenes",
            "orden": "/api/ordenes/{id}"
        }
    }

@app.get("/api/ordenes", response_model=OrdenesResponse)
def get_ordenes(
    estado: Optional[str] = None,
    prioridad: Optional[str] = None,
    aliado: Optional[str] = None,
    departamento: Optional[str] = None,
    tipo_de_trabajo: Optional[str] = None
):
    """
    Obtiene todas las órdenes con filtros opcionales
    Nota: El filtro 'familia' se aplica en el frontend ya que es un campo calculado
    """
    """
    Obtiene todas las órdenes con filtros opcionales
    """
    tunnel = None
    connection = None
    
    try:
        tunnel, connection = get_db_connection()
        cursor = connection.cursor()
        
        # Construir query con filtros usando LEFT JOIN para traer estado de oym_fijo.
        # Se usa subquery para evitar duplicados: toma el estado del registro con fin más reciente.
        query = """
            SELECT m.*, o.estado AS estado_oym
            FROM maximo m
            LEFT JOIN oym_fijo o ON m.orden_de_trabajo = o.orden_de_trabajo
                AND o.fin = (
                    SELECT MAX(o2.fin)
                    FROM oym_fijo o2
                    WHERE o2.orden_de_trabajo = m.orden_de_trabajo
                )
            WHERE 1=1
        """
        params = []
        
        if estado:
            query += " AND m.estado = %s"
            params.append(estado)
        
        if prioridad:
            query += " AND m.prioridad = %s"
            params.append(prioridad)
        
        if aliado:
            query += " AND m.aliado = %s"
            params.append(aliado)
        
        if departamento:
            query += " AND m.departamento = %s"
            params.append(departamento)
        
        if tipo_de_trabajo:
            query += " AND m.tipo_de_trabajo = %s"
            params.append(tipo_de_trabajo)
        
        cursor.execute(query, params)
        columnas = [desc[0] for desc in cursor.description]
        resultados = cursor.fetchall()
        
        # Convertir a lista de diccionarios
        ordenes = []
        for fila in resultados:
            orden_dict = {}
            for idx, col in enumerate(columnas):
                valor = fila[idx]
                # Convertir datetime a string
                if isinstance(valor, datetime):
                    valor = valor.strftime('%Y-%m-%d %H:%M:%S')
                orden_dict[col] = valor
            
            # Extraer "familia" de ruta_de_clasificacion
            ruta = orden_dict.get('ruta_de_clasificacion', '') or ''
            orden_dict['familia'] = calcular_familia(ruta)
            orden_dict['segmento'] = calcular_segmento(ruta)
            
            # Calcular tiempo desde fecha_de_creacion
            fecha_creacion_str = orden_dict.get('fecha_de_creacion', '')
            dias = 0
            horas = 0
            if fecha_creacion_str:
                try:
                    fecha_creacion = datetime.strptime(fecha_creacion_str, '%Y-%m-%d %H:%M:%S')
                    diff = datetime.now() - fecha_creacion
                    dias = diff.days
                    horas = int(diff.total_seconds() // 3600)
                except (ValueError, TypeError):
                    dias = 0
                    horas = 0
            
            orden_dict['dias'] = dias
            orden_dict['horas'] = horas
            ordenes.append(orden_dict)
        
        cursor.close()
        connection.close()
        tunnel.stop()
        
        return {
            "total": len(ordenes),
            "ordenes": ordenes
        }
        
    except Exception as e:
        if connection:
            connection.close()
        if tunnel:
            tunnel.stop()
        raise HTTPException(status_code=500, detail=f"Error al consultar BD: {str(e)}")

@app.get("/api/ordenes/{orden_id}")
def get_orden_by_id(orden_id: int):
    """
    Obtiene una orden específica por ID
    """
    tunnel = None
    connection = None
    
    try:
        tunnel, connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT m.*, o.estado AS estado_oym
            FROM maximo m
            LEFT JOIN oym_fijo o ON m.orden_de_trabajo = o.orden_de_trabajo
                AND o.fin = (
                    SELECT MAX(o2.fin)
                    FROM oym_fijo o2
                    WHERE o2.orden_de_trabajo = m.orden_de_trabajo
                )
            WHERE m.id = %s
        """, (orden_id,))
        columnas = [desc[0] for desc in cursor.description]
        resultado = cursor.fetchone()
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        
        # Convertir a diccionario
        orden_dict = {}
        for idx, col in enumerate(columnas):
            valor = resultado[idx]
            if isinstance(valor, datetime):
                valor = valor.strftime('%Y-%m-%d %H:%M:%S')
            orden_dict[col] = valor
        
        # Extraer "familia" de ruta_de_clasificacion
        ruta = orden_dict.get('ruta_de_clasificacion', '') or ''
        orden_dict['familia'] = calcular_familia(ruta)
        orden_dict['segmento'] = calcular_segmento(ruta)
        
        # Calcular tiempo desde fecha_de_creacion
        fecha_creacion_str = orden_dict.get('fecha_de_creacion', '')
        dias = 0
        horas = 0
        if fecha_creacion_str:
            try:
                fecha_creacion = datetime.strptime(fecha_creacion_str, '%Y-%m-%d %H:%M:%S')
                diff = datetime.now() - fecha_creacion
                dias = diff.days
                horas = int(diff.total_seconds() // 3600)
            except (ValueError, TypeError):
                dias = 0
                horas = 0
        
        orden_dict['dias'] = dias
        orden_dict['horas'] = horas
        
        cursor.close()
        connection.close()
        tunnel.stop()
        
        return orden_dict
        
    except HTTPException:
        raise
    except Exception as e:
        if connection:
            connection.close()
        if tunnel:
            tunnel.stop()
        raise HTTPException(status_code=500, detail=f"Error al consultar BD: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
