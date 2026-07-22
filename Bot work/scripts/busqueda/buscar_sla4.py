"""
Verificación final: oym_fijo cruzado con maximo y su estado_sla.
También revisar si alguna tabla tiene las OTs de maximo con SLA.
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

# ── 1. oym_fijo: ¿tiene datos en sus columnas SLA para las OTs de maximo? ─
print("=" * 65)
print("oym_fijo × maximo: estado_sla, sla_suscriptor, sla_cumplimiento")
print("=" * 65)
c.execute("""
    SELECT m.orden_de_trabajo, o.estado AS estado_oym,
           o.estado_sla, o.sla_suscriptor, o.sla_cumplimiento,
           o.inicio_de_sla, o.fin_de_sla
    FROM maximo m
    LEFT JOIN oym_fijo o ON m.orden_de_trabajo = o.orden_de_trabajo
        AND o.fin = (SELECT MAX(o2.fin) FROM oym_fijo o2 WHERE o2.orden_de_trabajo = m.orden_de_trabajo)
    LIMIT 15
""")
for r in c.fetchall():
    print(f"  OT={r[0]}  oym={r[1]}  estado_sla={r[2]}  sla_sus={r[3]}  sla_cum={r[4]}  ini_sla={r[5]}  fin_sla={r[6]}")

# ── 2. ¿Cuántas OTs de maximo tienen estado_sla en oym_fijo? ─────────────
print("\n" + "=" * 65)
print("Cobertura de estado_sla en oym_fijo para OTs de maximo")
print("=" * 65)
c.execute("""
    SELECT
        COUNT(DISTINCT m.id) as total_maximo,
        COUNT(DISTINCT CASE WHEN o.estado_sla IS NOT NULL AND o.estado_sla != 0 THEN m.id END) as con_sla
    FROM maximo m
    LEFT JOIN oym_fijo o ON m.orden_de_trabajo = o.orden_de_trabajo
""")
r = c.fetchone()
print(f"  Total OTs maximo: {r[0]}  |  Con estado_sla en oym_fijo: {r[1]}")

# ── 3. Todas las OTs de maximo — ¿aparecen en alguna tabla WFM? ──────────
print("\n" + "=" * 65)
print("¿Las OTs de maximo existen en ALGUNA tabla WFM?")
print("=" * 65)
c.execute("SELECT orden_de_trabajo FROM maximo WHERE orden_de_trabajo IS NOT NULL")
ots_maximo = [r[0] for r in c.fetchall()]
print(f"  OTs en maximo: {len(ots_maximo)}")

tablas_wfm = ['Region_Occidente', 'wfm_completo', 'pymes', 'dth', 'oym_fijo']
for t in tablas_wfm:
    try:
        placeholders = ','.join(['%s'] * len(ots_maximo))
        c.execute(f"SELECT COUNT(DISTINCT orden_de_trabajo) FROM `{t}` WHERE orden_de_trabajo IN ({placeholders})", ots_maximo)
        cnt = c.fetchone()[0]
        print(f"  {t:<30} → {cnt} de {len(ots_maximo)} OTs encontradas")
    except Exception as e:
        print(f"  {t}: ❌ {e}")

# ── 4. Rango de OTs en cada tabla WFM ────────────────────────────────────
print("\n" + "=" * 65)
print("Rango de OTs (MIN/MAX) en cada tabla WFM con SLA")
print("=" * 65)
for t in ['Region_Occidente', 'wfm_completo', 'pymes']:
    try:
        c.execute(f"""
            SELECT MIN(orden_de_trabajo), MAX(orden_de_trabajo), COUNT(DISTINCT orden_de_trabajo)
            FROM `{t}`
            WHERE orden_de_trabajo IS NOT NULL
              AND orden_de_trabajo NOT LIKE '<NA>%'
              AND orden_de_trabajo LIKE 'OT%'
        """)
        r = c.fetchone()
        print(f"  {t:<30}  min={r[0]}  max={r[1]}  distintas={r[2]}")
    except Exception as e:
        print(f"  {t}: ❌ {e}")

# ── 5. Rango de OTs en maximo ─────────────────────────────────────────────
print("\n" + "=" * 65)
print("Rango de OTs en maximo")
print("=" * 65)
c.execute("SELECT MIN(orden_de_trabajo), MAX(orden_de_trabajo) FROM maximo")
r = c.fetchone()
print(f"  min={r[0]}  max={r[1]}")

# ── 6. inicio_programado y finalizacion_programada en maximo ─────────────
print("\n" + "=" * 65)
print("maximo: cobertura de inicio_programado / finalizacion_programada")
print("(para calcular SLA propio si no hay fuente externa)")
print("=" * 65)
c.execute("""
    SELECT
        COUNT(*) as total,
        COUNT(inicio_programado) as con_ini_prog,
        COUNT(finalizacion_programada) as con_fin_prog,
        COUNT(inicio_real) as con_ini_real,
        COUNT(finalizacion_real) as con_fin_real
    FROM maximo
""")
r = c.fetchone()
print(f"  Total: {r[0]}  inicio_prog={r[1]}  fin_prog={r[2]}  inicio_real={r[3]}  fin_real={r[4]}")

# Muestra de fechas
c.execute("""
    SELECT orden_de_trabajo, fecha_de_creacion, inicio_programado, finalizacion_programada
    FROM maximo
    WHERE inicio_programado IS NOT NULL
    LIMIT 8
""")
print("\n  Muestra con fechas:")
for r in c.fetchall():
    print(f"  OT={r[0]}  creacion={r[1]}  ini_prog={r[2]}  fin_prog={r[3]}")

conn.close()
tunnel.stop()
print("\n✅ Listo")
