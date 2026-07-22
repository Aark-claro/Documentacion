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

# Ver los registros duplicados para entender cuál tomar
for ot in ['OT5212072', 'OT5211377']:
    print(f"\n=== {ot} ===")
    cursor.execute("""
        SELECT orden_de_trabajo, estado, fecha, inicio, fin
        FROM oym_fijo
        WHERE orden_de_trabajo = %s
        ORDER BY fecha DESC
    """, (ot,))
    for row in cursor.fetchall():
        print(f"  estado: {row[1]}  |  fecha: {row[2]}  |  inicio: {row[3]}  |  fin: {row[4]}")

cursor.close()
conn.close()
tunnel.stop()
