from sshtunnel import SSHTunnelForwarder
import mysql.connector

SSH_CONFIG = {"host": "186.147.60.119", "user": "ccot", "password": "Siesconmigo*"}
DB_CONFIG = {"user": "otc_app", "password": "22122012Elf@", "database": "contingencia", "host": "127.0.0.1", "port": 3307}

tunnel = SSHTunnelForwarder(
    (SSH_CONFIG["host"], 22),
    ssh_username=SSH_CONFIG["user"],
    ssh_password=SSH_CONFIG["password"],
    remote_bind_address=(DB_CONFIG["host"], DB_CONFIG["port"])
)
tunnel.start()
conn = mysql.connector.connect(host='127.0.0.1', port=tunnel.local_bind_port,
    user=DB_CONFIG["user"], password=DB_CONFIG["password"], database=DB_CONFIG["database"])
cursor = conn.cursor()

# ¿Hay OTs con más de 1 registro en oym_fijo?
cursor.execute("""
    SELECT orden_de_trabajo, COUNT(*) as total
    FROM oym_fijo
    GROUP BY orden_de_trabajo
    HAVING COUNT(*) > 1
    LIMIT 5
""")
rows = cursor.fetchall()
if rows:
    print("⚠️  OTs con MÚLTIPLES registros en oym_fijo:")
    for r in rows:
        print(f"   OT: {r[0]}  ->  {r[1]} registros")
else:
    print("✅ Cada OT tiene un solo registro en oym_fijo. El JOIN es seguro.")

# ¿Cuántas OTs de maximo NO están en oym_fijo?
cursor.execute("""
    SELECT COUNT(*) FROM maximo m
    LEFT JOIN oym_fijo o ON m.orden_de_trabajo = o.orden_de_trabajo
    WHERE o.orden_de_trabajo IS NULL
""")
sin_oym = cursor.fetchone()[0]
print(f"\n📊 OTs en maximo sin registro en oym_fijo: {sin_oym} (estado_oym = null para estas)")

cursor.close()
conn.close()
tunnel.stop()
