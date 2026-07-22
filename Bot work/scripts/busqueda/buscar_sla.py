"""
Busca columnas relacionadas con SLA en toda la BD contingencia,
y cómo se relacionan con maximo.
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

# ── 1. Todas las columnas que contengan 'sla' en toda la BD ──────────────
print("=" * 65)
print("COLUMNAS CON 'sla' EN TODA LA BD")
print("=" * 65)
db = DB["database"]
c.execute(f"""
    SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = '{db}'
      AND LOWER(COLUMN_NAME) LIKE '%sla%'
    ORDER BY TABLE_NAME, COLUMN_NAME
""")
hits = c.fetchall()
for tabla, col, dtype in hits:
    print(f"  {tabla:<35} {col:<30} {dtype}")

# ── 2. Valores únicos de cada columna sla encontrada ─────────────────────
print("\n" + "=" * 65)
print("VALORES ÚNICOS POR COLUMNA SLA")
print("=" * 65)
for tabla, col, dtype in hits:
    try:
        c.execute(f"SELECT DISTINCT `{col}` FROM `{tabla}` WHERE `{col}` IS NOT NULL ORDER BY `{col}` LIMIT 20")
        vals = [str(r[0]) for r in c.fetchall()]
        print(f"\n  {tabla}.{col}:")
        for v in vals:
            print(f"    '{v}'")
    except Exception as e:
        print(f"  {tabla}.{col}: ❌ {e}")

# ── 3. ¿maximo tiene alguna columna sla directamente? ────────────────────
print("\n" + "=" * 65)
print("COLUMNAS DE maximo QUE CONTENGAN 'sla', 'fecha', 'plazo', 'vencimiento'")
print("=" * 65)
c.execute("DESCRIBE maximo")
maximo_cols = c.fetchall()
candidatas = [r for r in maximo_cols if any(
    kw in r[0].lower() for kw in ['sla', 'plazo', 'vencim', 'limite', 'compromis', 'target']
)]
if candidatas:
    for r in candidatas:
        print(f"  {r[0]:<40} {r[1]}")
        c.execute(f"SELECT DISTINCT `{r[0]}` FROM maximo WHERE `{r[0]}` IS NOT NULL LIMIT 10")
        vals = [str(v[0]) for v in c.fetchall()]
        print(f"    Valores: {vals}")
else:
    print("  ❌ Ninguna columna con esos términos en maximo")

# ── 4. Revisar oym_fijo por si tiene campos sla ───────────────────────────
print("\n" + "=" * 65)
print("COLUMNAS SLA EN oym_fijo (tabla ya conocida)")
print("=" * 65)
c.execute("DESCRIBE oym_fijo")
oym_cols = c.fetchall()
sla_oym = [r for r in oym_cols if 'sla' in r[0].lower()]
if sla_oym:
    for r in sla_oym:
        print(f"  {r[0]:<40} {r[1]}")
        c.execute(f"SELECT DISTINCT `{r[0]}` FROM oym_fijo WHERE `{r[0]}` IS NOT NULL LIMIT 10")
        vals = [str(v[0]) for v in c.fetchall()]
        print(f"    Valores: {vals}")
else:
    print("  No hay columnas SLA en oym_fijo")

# ── 5. Revisar Region_Occidente (tabla más completa) ─────────────────────
print("\n" + "=" * 65)
print("COLUMNAS SLA EN Region_Occidente")
print("=" * 65)
c.execute("DESCRIBE `Region_Occidente`")
ro_cols = c.fetchall()
sla_ro = [r for r in ro_cols if 'sla' in r[0].lower()]
if sla_ro:
    for r in sla_ro:
        print(f"  {r[0]:<40} {r[1]}")
        c.execute(f"SELECT DISTINCT `{r[0]}` FROM `Region_Occidente` WHERE `{r[0]}` IS NOT NULL LIMIT 15")
        vals = [str(v[0]) for v in c.fetchall()]
        print(f"    Valores: {vals}")
else:
    print("  No hay columnas SLA en Region_Occidente")

# ── 6. Cruce: ¿Region_Occidente tiene OTs de maximo? (via ot_wfm) ────────
print("\n" + "=" * 65)
print("CRUCE maximo.ot_wfm ↔ Region_Occidente.orden_de_trabajo")
print("=" * 65)
try:
    c.execute("""
        SELECT COUNT(DISTINCT m.id)
        FROM maximo m
        INNER JOIN `Region_Occidente` ro ON CAST(m.ot_wfm AS CHAR) = ro.orden_de_trabajo
        WHERE m.ot_wfm IS NOT NULL
    """)
    cnt = c.fetchone()[0]
    print(f"  Coincidencias via ot_wfm: {cnt}")
    if cnt > 0:
        c.execute("""
            SELECT m.orden_de_trabajo, m.ot_wfm, ro.sla_suscriptor, ro.sla_cumplimiento, ro.estado_sla
            FROM maximo m
            INNER JOIN `Region_Occidente` ro ON CAST(m.ot_wfm AS CHAR) = ro.orden_de_trabajo
            WHERE m.ot_wfm IS NOT NULL
            LIMIT 5
        """)
        for r in c.fetchall():
            print(f"  OT={r[0]}  wfm={r[1]}  sla_sus={r[2]}  sla_cum={r[3]}  estado_sla={r[4]}")
except Exception as e:
    print(f"  ❌ {e}")

conn.close()
tunnel.stop()
print("\n✅ Listo")
