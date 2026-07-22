"""
Exploración final de SLA: encontrar registros con orden_de_trabajo real en wfm_completo
y probar el cruce con maximo via external_id u otros campos.
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

# ── 1. wfm_completo: registros donde orden_de_trabajo NO es null/NA ───────
print("=" * 65)
print("wfm_completo: registros con orden_de_trabajo real")
print("=" * 65)
c.execute("""
    SELECT COUNT(*) FROM wfm_completo
    WHERE orden_de_trabajo IS NOT NULL
      AND orden_de_trabajo != ''
      AND orden_de_trabajo != '<NA>'
""")
print(f"  Con OT real: {c.fetchone()[0]:,}")

c.execute("""
    SELECT orden_de_trabajo, external_id, estado_sla, sla_suscriptor, sla_cumplimiento, estado
    FROM wfm_completo
    WHERE orden_de_trabajo IS NOT NULL
      AND orden_de_trabajo != ''
      AND orden_de_trabajo != '<NA>'
    LIMIT 10
""")
print("  Muestra:")
for r in c.fetchall():
    print(f"    OT='{r[0]}'  ext_id='{r[1]}'  estado_sla='{r[2]}'  sla_sus={r[3]}  sla_cum={r[4]}  estado='{r[5]}'")

# ── 2. external_id en wfm_completo ────────────────────────────────────────
print("\n" + "=" * 65)
print("external_id en wfm_completo (¿formato WFM numérico?)")
print("=" * 65)
c.execute("""
    SELECT DISTINCT external_id FROM wfm_completo
    WHERE external_id IS NOT NULL AND external_id != '' AND external_id != '<NA>'
    LIMIT 10
""")
for r in c.fetchall():
    print(f"  '{r[0]}'")

# ── 3. Cruce via external_id = maximo.ot_wfm ─────────────────────────────
print("\n" + "=" * 65)
print("CRUCE maximo.ot_wfm ↔ wfm_completo.external_id")
print("=" * 65)
try:
    c.execute("""
        SELECT COUNT(DISTINCT m.id)
        FROM maximo m
        INNER JOIN wfm_completo w ON CAST(m.ot_wfm AS CHAR) = CAST(w.external_id AS CHAR)
        WHERE m.ot_wfm IS NOT NULL
    """)
    cnt = c.fetchone()[0]
    print(f"  Coincidencias: {cnt}")
    if cnt > 0:
        c.execute("""
            SELECT m.orden_de_trabajo, m.ot_wfm, w.estado_sla, w.sla_suscriptor, w.sla_cumplimiento
            FROM maximo m
            INNER JOIN wfm_completo w ON CAST(m.ot_wfm AS CHAR) = CAST(w.external_id AS CHAR)
            WHERE m.ot_wfm IS NOT NULL
            LIMIT 5
        """)
        for r in c.fetchall():
            print(f"    OT={r[0]}  wfm={r[1]}  estado_sla={r[2]}  sla_sus={r[3]}  sla_cum={r[4]}")
except Exception as e:
    print(f"  ❌ {e}")

# ── 4. Cruce via orden_de_trabajo directo ────────────────────────────────
print("\n" + "=" * 65)
print("CRUCE maximo.ot_wfm ↔ wfm_completo.orden_de_trabajo (donde OT es numérica)")
print("=" * 65)
try:
    c.execute("""
        SELECT COUNT(DISTINCT m.id)
        FROM maximo m
        INNER JOIN wfm_completo w
          ON CAST(m.ot_wfm AS CHAR) = CAST(w.orden_de_trabajo AS CHAR)
        WHERE m.ot_wfm IS NOT NULL
          AND w.orden_de_trabajo IS NOT NULL
          AND w.orden_de_trabajo != '<NA>'
    """)
    cnt = c.fetchone()[0]
    print(f"  Coincidencias: {cnt}")
    if cnt > 0:
        c.execute("""
            SELECT m.orden_de_trabajo, m.ot_wfm, w.estado_sla, w.sla_suscriptor, w.sla_cumplimiento
            FROM maximo m
            INNER JOIN wfm_completo w
              ON CAST(m.ot_wfm AS CHAR) = CAST(w.orden_de_trabajo AS CHAR)
            WHERE m.ot_wfm IS NOT NULL
            LIMIT 5
        """)
        for r in c.fetchall():
            print(f"    OT={r[0]}  wfm={r[1]}  estado_sla={r[2]}  sla_sus={r[3]}  sla_cum={r[4]}")
except Exception as e:
    print(f"  ❌ {e}")

# ── 5. origen en wfm_completo (para entender la estructura) ──────────────
print("\n" + "=" * 65)
print("Valores únicos de 'origen' en wfm_completo")
print("=" * 65)
c.execute("SELECT DISTINCT origen, COUNT(*) as cnt FROM wfm_completo GROUP BY origen ORDER BY cnt DESC")
for r in c.fetchall():
    print(f"  origen='{r[0]}'  registros={r[1]:,}")

# ── 6. Buscar OT de maximo manualmente en TODAS las tablas con SLA ────────
print("\n" + "=" * 65)
print("BÚSQUEDA MANUAL: ¿OT4837324 o wfm=137292761 en tablas con SLA?")
print("=" * 65)
tablas_sla = ['Region_Occidente', 'region_occidente', 'pymes', 'wfm_completo', 'union_back_completo']
for t in tablas_sla:
    try:
        # Buscar la OT exacta
        c.execute(f"SELECT COUNT(*) FROM `{t}` WHERE orden_de_trabajo = 'OT4837324'")
        c1 = c.fetchone()[0]
        c.execute(f"SELECT COUNT(*) FROM `{t}` WHERE orden_de_trabajo = '137292761'")
        c2 = c.fetchone()[0]
        print(f"  {t:<30} OT4837324={c1}  137292761={c2}")
    except Exception as e:
        print(f"  {t}: ❌ {e}")

conn.close()
tunnel.stop()
print("\n✅ Listo")
