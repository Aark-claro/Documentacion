"""
Script para verificar que BD, Backend y Frontend estén alineados
"""
from sshtunnel import SSHTunnelForwarder
import mysql.connector
import re
import os

# Raíz del proyecto (dos niveles arriba de este script)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Configuración SSH
SSH_CONFIG = {
    "host": "186.147.60.119",
    "user": "ccot",
    "password": "Siesconmigo*"
}

# Configuración MySQL
DB_CONFIG = {
    "user": "otc_app",
    "password": "22122012Elf@",
    "database": "contingencia",
    "host": "127.0.0.1",
    "port": 3307
}

def obtener_columnas_bd():
    """Obtiene las columnas de la tabla maximo en la BD"""
    tunnel = None
    connection = None
    
    try:
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
        
        cursor = connection.cursor()
        cursor.execute("DESCRIBE maximo")
        columnas_info = cursor.fetchall()
        
        columnas = {}
        for col in columnas_info:
            nombre = col[0]
            tipo = col[1]
            nulo = col[2]
            columnas[nombre] = {
                'tipo': tipo,
                'nulo': nulo == 'YES'
            }
        
        cursor.close()
        connection.close()
        tunnel.stop()
        
        return columnas
        
    except Exception as e:
        print(f"❌ Error al conectar a BD: {str(e)}")
        if connection:
            connection.close()
        if tunnel:
            tunnel.stop()
        return {}

def obtener_columnas_backend():
    """Lee el modelo del backend"""
    columnas = []
    try:
        with open(os.path.join(PROJECT_ROOT, 'backend', 'main.py'), 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        # Buscar el modelo Orden
        patron = r'class Orden\(BaseModel\):.*?(?=class |def |if __name__|$)'
        match = re.search(patron, contenido, re.DOTALL)
        
        if match:
            modelo = match.group()
            # Extraer los campos
            patron_campos = r'(\w+):\s*Optional\[.*?\]|(\w+):\s*int'
            campos = re.findall(patron_campos, modelo)
            columnas = [c[0] or c[1] for c in campos if (c[0] or c[1]) not in ['model_config']]
        
        return columnas
        
    except Exception as e:
        print(f"❌ Error al leer backend: {str(e)}")
        return []

def obtener_columnas_frontend():
    """Lee las columnas definidas en el frontend"""
    columnas = []
    try:
        with open(os.path.join(PROJECT_ROOT, 'frontend', 'src', 'App.jsx'), 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        # Buscar TODAS_LAS_COLUMNAS
        patron = r'const TODAS_LAS_COLUMNAS = \[(.*?)\]'
        match = re.search(patron, contenido, re.DOTALL)
        
        if match:
            columnas_def = match.group(1)
            # Extraer los keys
            patron_key = r"key:\s*'(\w+)'"
            columnas = re.findall(patron_key, columnas_def)
        
        return columnas
        
    except Exception as e:
        print(f"❌ Error al leer frontend: {str(e)}")
        return []

def main():
    print("="*100)
    print("🔍 VERIFICACIÓN DE ALINEACIÓN: BD ↔ BACKEND ↔ FRONTEND")
    print("="*100)
    
    print("\n📥 Obteniendo columnas de la base de datos...")
    columnas_bd = obtener_columnas_bd()
    print(f"✅ BD: {len(columnas_bd)} columnas")
    
    print("\n📥 Analizando modelo del backend...")
    columnas_backend = obtener_columnas_backend()
    print(f"✅ Backend: {len(columnas_backend)} campos")
    
    print("\n📥 Analizando definición del frontend...")
    columnas_frontend = obtener_columnas_frontend()
    print(f"✅ Frontend: {len(columnas_frontend)} columnas")
    
    # Comparación BD vs Backend
    print("\n" + "="*100)
    print("📊 COMPARACIÓN: BASE DE DATOS vs BACKEND")
    print("="*100)
    
    campos_calculados = {'familia', 'dias'}  # Campos que no vienen de BD
    
    # Campos de BD no en Backend
    faltantes_backend = set(columnas_bd.keys()) - set(columnas_backend)
    if faltantes_backend:
        print(f"\n⚠️  Campos en BD pero NO en Backend ({len(faltantes_backend)}):")
        for campo in sorted(faltantes_backend):
            print(f"   - {campo}")
    else:
        print("\n✅ Todos los campos de BD están en el Backend")
    
    # Campos de Backend no en BD (excluyendo calculados)
    extra_backend = set(columnas_backend) - set(columnas_bd.keys()) - campos_calculados
    if extra_backend:
        print(f"\n⚠️  Campos en Backend pero NO en BD ({len(extra_backend)}):")
        for campo in sorted(extra_backend):
            print(f"   - {campo}")
    else:
        print("\n✅ Backend no tiene campos extra (aparte de los calculados)")
    
    print(f"\n💡 Campos calculados en Backend: {', '.join(sorted(campos_calculados))}")
    
    # Comparación Backend vs Frontend
    print("\n" + "="*100)
    print("📊 COMPARACIÓN: BACKEND vs FRONTEND")
    print("="*100)
    
    # Campos de Backend no en Frontend
    faltantes_frontend = set(columnas_backend) - set(columnas_frontend)
    if faltantes_frontend:
        print(f"\n⚠️  Campos en Backend pero NO en Frontend ({len(faltantes_frontend)}):")
        for campo in sorted(faltantes_frontend):
            print(f"   - {campo}")
    else:
        print("\n✅ Todos los campos de Backend están en el Frontend")
    
    # Campos de Frontend no en Backend
    extra_frontend = set(columnas_frontend) - set(columnas_backend)
    if extra_frontend:
        print(f"\n⚠️  Campos en Frontend pero NO en Backend ({len(extra_frontend)}):")
        for campo in sorted(extra_frontend):
            print(f"   - {campo}")
    else:
        print("\n✅ Frontend no tiene campos extra")
    
    # Resumen final
    print("\n" + "="*100)
    print("📋 RESUMEN")
    print("="*100)
    print(f"Base de Datos:  {len(columnas_bd)} columnas")
    print(f"Backend:        {len(columnas_backend)} campos (incluye {len(campos_calculados)} calculados)")
    print(f"Frontend:       {len(columnas_frontend)} columnas")
    
    # Estado general
    if not faltantes_backend and not extra_backend and not faltantes_frontend and not extra_frontend:
        print("\n✅ ¡TODO ESTÁ PERFECTAMENTE ALINEADO!")
    else:
        print("\n⚠️  Hay algunas inconsistencias que revisar")
    
    # Mostrar todas las columnas
    print("\n" + "="*100)
    print("📝 LISTA DETALLADA DE COLUMNAS")
    print("="*100)
    
    todas = sorted(set(list(columnas_bd.keys()) + columnas_backend + columnas_frontend))
    
    print(f"\n{'#':<4} {'COLUMNA':<35} {'BD':<6} {'BACKEND':<10} {'FRONTEND':<10}")
    print("-"*100)
    
    for idx, col in enumerate(todas, 1):
        en_bd = '✓' if col in columnas_bd else ('calc' if col in campos_calculados else '✗')
        en_backend = '✓' if col in columnas_backend else '✗'
        en_frontend = '✓' if col in columnas_frontend else '✗'
        
        print(f"{idx:<4} {col:<35} {en_bd:<6} {en_backend:<10} {en_frontend:<10}")
    
    print("\n✅ Verificación completada\n")

if __name__ == "__main__":
    main()
