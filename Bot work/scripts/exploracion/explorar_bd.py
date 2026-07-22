"""
Script para explorar la estructura de la base de datos
"""
from sshtunnel import SSHTunnelForwarder
import mysql.connector

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

def explorar_base_datos():
    """Explora la estructura de la tabla maximo"""
    tunnel = None
    connection = None
    
    try:
        print("🔌 Conectando al servidor SSH...")
        tunnel = SSHTunnelForwarder(
            (SSH_CONFIG["host"], 22),
            ssh_username=SSH_CONFIG["user"],
            ssh_password=SSH_CONFIG["password"],
            remote_bind_address=(DB_CONFIG["host"], DB_CONFIG["port"])
        )
        tunnel.start()
        print("✅ Túnel SSH establecido")
        
        print("\n🔌 Conectando a MySQL...")
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        print("✅ Conexión a MySQL establecida")
        
        cursor = connection.cursor()
        
        # Obtener estructura de la tabla
        print("\n" + "="*80)
        print("📋 ESTRUCTURA DE LA TABLA 'maximo'")
        print("="*80)
        
        cursor.execute("DESCRIBE maximo")
        columnas_info = cursor.fetchall()
        
        print(f"\n{'#':<4} {'COLUMNA':<40} {'TIPO':<20} {'NULO':<6}")
        print("-"*80)
        
        for idx, col in enumerate(columnas_info, 1):
            nombre = col[0]
            tipo = col[1]
            nulo = col[2]
            print(f"{idx:<4} {nombre:<40} {tipo:<20} {nulo:<6}")
        
        print(f"\n✅ Total de columnas: {len(columnas_info)}")
        
        # Obtener un registro de ejemplo
        print("\n" + "="*80)
        print("🔍 REGISTRO DE EJEMPLO (primeras 5 columnas)")
        print("="*80)
        
        cursor.execute("SELECT * FROM maximo LIMIT 1")
        columnas = [desc[0] for desc in cursor.description]
        ejemplo = cursor.fetchone()
        
        if ejemplo:
            print("\nMostrando primeras columnas del primer registro:")
            print("-"*80)
            for i, (col, val) in enumerate(zip(columnas[:10], ejemplo[:10])):
                print(f"{col:<40}: {str(val)[:50]}")
            print("\n... (mostrando solo primeras 10 columnas)")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM maximo")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total de registros en la tabla: {total}")
        
        # Verificar si existe la columna 'familia'
        print("\n" + "="*80)
        print("🔎 VERIFICACIÓN DE COLUMNAS ESPECÍFICAS")
        print("="*80)
        
        columnas_buscar = ['familia', 'Familia', 'FAMILIA', 'tipo_accion', 'tipo_familia']
        columnas_existentes = [col[0] for col in columnas_info]
        
        for col_buscar in columnas_buscar:
            if col_buscar in columnas_existentes:
                print(f"✅ Columna '{col_buscar}' EXISTE")
                
                # Mostrar valores únicos
                cursor.execute(f"SELECT DISTINCT `{col_buscar}` FROM maximo WHERE `{col_buscar}` IS NOT NULL LIMIT 10")
                valores = cursor.fetchall()
                if valores:
                    print(f"   Valores únicos encontrados: {', '.join([str(v[0]) for v in valores])}")
            else:
                print(f"❌ Columna '{col_buscar}' NO existe")
        
        # Listar TODAS las columnas disponibles
        print("\n" + "="*80)
        print("📝 LISTA COMPLETA DE COLUMNAS (para copiar al backend)")
        print("="*80)
        print("\nColumnas disponibles:")
        for col in columnas_existentes:
            print(f"  - {col}")
        
        cursor.close()
        connection.close()
        tunnel.stop()
        
        print("\n✅ Exploración completada exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error durante la exploración: {str(e)}")
        if connection:
            connection.close()
        if tunnel:
            tunnel.stop()
        raise

if __name__ == "__main__":
    print("🚀 Iniciando exploración de base de datos...")
    print("="*80)
    explorar_base_datos()
