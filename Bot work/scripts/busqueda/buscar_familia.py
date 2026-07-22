"""
Script para buscar en qué columna está la información de "familia"
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

def buscar_familia():
    """Busca valores únicos en columnas que podrían contener familia"""
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
        
        # Columnas candidatas
        columnas_candidatas = [
            'clasificacion',
            'ruta_de_clasificacion',
            'descripcion',
            'tipo_de_trabajo',
            'descripcion_estado',
            'descripcion_grupo'
        ]
        
        print("="*80)
        print("🔍 BUSCANDO COLUMNA QUE CONTIENE 'FAMILIA'")
        print("="*80)
        
        for col in columnas_candidatas:
            print(f"\n📊 Columna: {col}")
            print("-"*80)
            
            # Obtener valores únicos
            cursor.execute(f"""
                SELECT DISTINCT `{col}` 
                FROM maximo 
                WHERE `{col}` IS NOT NULL 
                ORDER BY `{col}` 
                LIMIT 15
            """)
            valores = cursor.fetchall()
            
            if valores:
                print(f"Valores únicos encontrados ({len(valores)}):")
                for idx, (val,) in enumerate(valores, 1):
                    val_str = str(val)[:80]  # Limitar a 80 caracteres
                    print(f"  {idx:2}. {val_str}")
                    
                    # Buscar palabras clave
                    val_lower = val_str.lower()
                    if any(palabra in val_lower for palabra in ['degradacion', 'degradación', 'reclamacion', 'reclamación', 'notificacion', 'notificación']):
                        print(f"      🎯 ¡POSIBLE COINCIDENCIA!")
            else:
                print("  (Sin valores)")
        
        # Buscar directamente por palabras clave
        print("\n" + "="*80)
        print("🎯 BÚSQUEDA DIRECTA POR PALABRAS CLAVE")
        print("="*80)
        
        palabras_clave = ['degradacion', 'degradación', 'reclamacion', 'reclamación', 'notificacion', 'notificación']
        
        for palabra in palabras_clave:
            print(f"\n🔎 Buscando '{palabra}'...")
            for col in columnas_candidatas:
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM maximo 
                    WHERE LOWER(`{col}`) LIKE %s
                """, (f'%{palabra.lower()}%',))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    print(f"  ✅ Encontrado en '{col}': {count} registros")
                    
                    # Mostrar ejemplos
                    cursor.execute(f"""
                        SELECT `{col}` 
                        FROM maximo 
                        WHERE LOWER(`{col}`) LIKE %s 
                        LIMIT 3
                    """, (f'%{palabra.lower()}%',))
                    ejemplos = cursor.fetchall()
                    for ejemplo in ejemplos:
                        print(f"     Ejemplo: {str(ejemplo[0])[:100]}")
        
        cursor.close()
        connection.close()
        tunnel.stop()
        
        print("\n✅ Búsqueda completada")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if connection:
            connection.close()
        if tunnel:
            tunnel.stop()
        raise

if __name__ == "__main__":
    buscar_familia()
