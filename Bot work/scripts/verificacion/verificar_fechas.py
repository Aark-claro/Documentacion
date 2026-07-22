"""
Script para verificar el formato de las fechas
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

def verificar_fechas():
    """Verifica el formato de las columnas de fecha"""
    tunnel = None
    connection = None
    
    try:
        print("🔌 Conectando...")
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
        print("✅ Conectado\n")
        
        cursor = connection.cursor()
        
        # Obtener ejemplos de fechas
        cursor.execute("""
            SELECT 
                id,
                orden_de_trabajo,
                fecha_de_creacion,
                fecha_actualizacion,
                fecha_carga,
                inicio_real,
                finalizacion_real
            FROM maximo 
            LIMIT 10
        """)
        
        resultados = cursor.fetchall()
        
        print("="*120)
        print("📅 EJEMPLOS DE FECHAS EN LA BASE DE DATOS")
        print("="*120)
        
        for orden in resultados:
            print(f"\n🔹 Orden: {orden[1]}")
            print(f"   fecha_de_creacion:    {repr(orden[2])} (tipo: {type(orden[2]).__name__})")
            print(f"   fecha_actualizacion:  {repr(orden[3])} (tipo: {type(orden[3]).__name__})")
            print(f"   fecha_carga:          {repr(orden[4])} (tipo: {type(orden[4]).__name__})")
            print(f"   inicio_real:          {repr(orden[5])} (tipo: {type(orden[5]).__name__})")
            print(f"   finalizacion_real:    {repr(orden[6])} (tipo: {type(orden[6]).__name__})")
        
        # Verificar si hay valores nulos
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(fecha_de_creacion) as con_fecha_creacion,
                COUNT(fecha_actualizacion) as con_fecha_actualizacion,
                COUNT(fecha_carga) as con_fecha_carga
            FROM maximo
        """)
        
        stats = cursor.fetchone()
        
        print("\n" + "="*120)
        print("📊 ESTADÍSTICAS DE FECHAS")
        print("="*120)
        print(f"Total de registros:               {stats[0]}")
        print(f"Con fecha_de_creacion:            {stats[1]} ({stats[1]*100/stats[0]:.1f}%)")
        print(f"Con fecha_actualizacion:          {stats[2]} ({stats[2]*100/stats[0]:.1f}%)")
        print(f"Con fecha_carga:                  {stats[3]} ({stats[3]*100/stats[0]:.1f}%)")
        
        cursor.close()
        connection.close()
        tunnel.stop()
        
        print("\n✅ Verificación completada")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if connection:
            connection.close()
        if tunnel:
            tunnel.stop()
        raise

if __name__ == "__main__":
    verificar_fechas()
