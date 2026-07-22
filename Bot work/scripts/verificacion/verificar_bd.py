from sshtunnel import SSHTunnelForwarder
import mysql.connector

SSH_CONFIG = {"host": "186.147.60.119", "user": "ccot", "password": "Siesconmigo*"}
DB_CONFIG  = {"user": "otc_app", "password": "22122012Elf@", "database": "contingencia", "host": "127.0.0.1", "port": 3307}

try:
    print("Conectando SSH...")
    tunnel = SSHTunnelForwarder(
        (SSH_CONFIG["host"], 22),
        ssh_username=SSH_CONFIG["user"],
        ssh_password=SSH_CONFIG["password"],
        remote_bind_address=(DB_CONFIG["host"], DB_CONFIG["port"])
    )
    tunnel.start()
    print("✅ Túnel SSH OK")

    conn = mysql.connector.connect(
        host='127.0.0.1', port=tunnel.local_bind_port,
        user=DB_CONFIG["user"], password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )
    print("✅ MySQL OK")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM maximo")
    total = cursor.fetchone()[0]
    print(f"\n📊 Registros en maximo: {total}")

    cursor.execute("SELECT COUNT(*) FROM oym_fijo")
    total_oym = cursor.fetchone()[0]
    print(f"📊 Registros en oym_fijo: {total_oym}")

    # Probar el JOIN exacto que usa el backend
    cursor.execute("""
        SELECT COUNT(*) 
        FROM maximo m
        LEFT JOIN oym_fijo o ON m.orden_de_trabajo = o.orden_de_trabajo
            AND o.fin = (
                SELECT MAX(o2.fin) FROM oym_fijo o2
                WHERE o2.orden_de_trabajo = m.orden_de_trabajo
            )
    """)
    total_join = cursor.fetchone()[0]
    print(f"📊 Resultado del JOIN (debe coincidir con maximo): {total_join}")

    # Ver un registro de ejemplo
    cursor.execute("""
        SELECT m.orden_de_trabajo, m.estado, o.estado AS estado_oym
        FROM maximo m
        LEFT JOIN oym_fijo o ON m.orden_de_trabajo = o.orden_de_trabajo
            AND o.fin = (
                SELECT MAX(o2.fin) FROM oym_fijo o2
                WHERE o2.orden_de_trabajo = m.orden_de_trabajo
            )
        LIMIT 3
    """)
    print("\n🔍 Muestra de 3 registros del JOIN:")
    for row in cursor.fetchall():
        print(f"   OT: {row[0]} | estado_maximo: {row[1]} | estado_oym: {row[2]}")

    cursor.close()
    conn.close()
    tunnel.stop()
    print("\n✅ Todo OK")

except Exception as e:
    print(f"\n❌ Error: {e}")
