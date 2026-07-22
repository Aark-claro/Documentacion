"""
Verifica si las OTs activas de maximo ya tienen SLA en las tablas WFM.
"""
from sshtunnel import SSHTunnelForwarder
import mysql.connector, warnings
warnings.filterwarnings('ignore')

SSH = {"host": "186.147.60.119", "user": "ccot", "password": "Siesconmigo*"}
DB  = {"user": "otc_app", "password": "22122012Elf@", "database": "contingencia", "host": "127.0.0.1", "port": 3307}

tunnel = SSHTunnelForwarder((SSH["host"], 22), ssh_username=SSH["user"], ssh_password=SSH["password"], remote_bind_address=(DB["host"], DB["port"]))
tunnel.start()
conn = mysql.connector.connect(host='127.0.0.1', port=tunnel.local_bind_port, user=DB["user"], password=DB["password"], database=DB["database"])
c = conn.cursor()
print("✅ Conectado\n")

# OTs activas de maximo
c.execute("SELECT orden_de_trabajo FROM maximo WHERE orden_de_trabajo IS NOT NULL")
ots_maximo = [r[0] for r in c.fetchall()]
print(f"OTs activas en maximo: {len(ots_maximo)}\n")

# Verificar en cada tabla candidata
tablas = ['Region_Occidente', 'wfm_completo', 'oym_fijo', 'pymes', 'dth']
for t in tablas:
    try:
        placeholders = ','.join(['%s'] * len(ots_maximo))
        c.execute(f"""
            SELECT COUNT(DISTINCT orden_de_trabajo)
            FROM `{t}`
            WHERE orden_de_trabajo IN ({placeholders})
        """, ots_maximo)
        cnt = c.fetchone()[0]
        print(f"  {t:<30} → {cnt}/{len(ots_maximo)} OTs encontradas")

        if cnt > 0:
            # Muestra con SLA
            c.execute(f"""
                SELECT m.orden_de_trabajo, w.estado_sla, w.sla_suscriptor, w.sla_cumplimiento
                FROM maximo m
                INNER JOIN `{t}` w ON m.orden_de_trabajo = w.orden_de_trabajo
                LIMIT 5
            """)
            for r in c.fetchall():
                print(f"    OT={r[0]}  estado_sla={r[1]}  sla_sus={r[2]}h  sla_cum={r[3]}h")
    except Exception as e:
        print(f"  {t:<30} → ❌ {e}")

conn.close()
tunnel.stop()
print("\n✅ Listo")
