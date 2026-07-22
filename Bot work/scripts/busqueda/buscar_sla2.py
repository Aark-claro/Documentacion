"""
Explorar wfm_completo (tabla nueva) y encontrar cómo cruzar SLA con maximo.
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

# ── 1. Estructura de wfm_completo ─────────────────────────────────────────
print("=" * 65)
print("COLUMNAS DE wfm_completo")
print("=" * 65)
c.execute("DESCRIBE wfm_completo")
cols_wfm = c.fetchall()
for r in cols_wfm:
    print(f"  {r[0]:<40} {r[1]}")

c.execute("SELECT COUNT(*) FROM wfm_completo")
print(f"\n  → Total registros: {c.fetchone()[0]:,}")

# ── 2. Muestra de wfm_completo (columnas clave) ───────────────────────────
print("\n" + "=" * 65)
print("MUESTRA wfm_completo (columnas con 'orden', 'sla', 'estado')")
print("=" * 65)
cols_names = [r[0] for r in cols_wfm]
cols_interes = [c2 for c2 in cols_names if any(k in c2.lower() for k in ['orden', 'sla', 'estado', 'fecha'])]
print(f"  Columnas de interés: {cols_interes}")

c.execute(f"SELECT * FROM wfm_completo LIMIT 5")
rows = c.fetchall()
for row in rows:
    d = {cols_names[i]: str(row[i])[:40] for i in range(len(cols_names))}
    # Solo mostrar columnas de interés
    filtrado = {k: v for k, v in d.items() if any(kw in k.lower() for kw in ['orden', 'sla', 'estado', 'fecha'])}
    print(f"\n  {filtrado}")

# ── 3. Formato de orden_de_trabajo en wfm_completo ────────────────────────
print("\n" + "=" * 65)
print("FORMATO de orden_de_trabajo en wfm_completo")
print("=" * 65)
ot_col_wfm = next((r[0] for r in cols_wfm if 'orden' in r[0].lower()), None)
if ot_col_wfm:
    c.execute(f"SELECT DISTINCT `{ot_col_wfm}` FROM wfm_completo WHERE `{ot_col_wfm}` IS NOT NULL LIMIT 10")
    for r in c.fetchall():
        print(f"  '{r[0]}'")
else:
    print("  ❌ No hay columna con 'orden'")
    # Buscar columna que podría ser la OT
    for col_r in cols_wfm[:10]:
        print(f"  Columna disponible: {col_r[0]}")

# ── 4. Cruce directo wfm_completo ↔ maximo ────────────────────────────────
print("\n" + "=" * 65)
print("CRUCE wfm_completo ↔ maximo (varios intentos)")
print("=" * 65)

if ot_col_wfm:
    # Cruce directo
    try:
        c.execute(f"""
            SELECT COUNT(DISTINCT m.id)
            FROM maximo m
            INNER JOIN wfm_completo w ON m.orden_de_trabajo = w.`{ot_col_wfm}`
        """)
        print(f"  maximo.orden_de_trabajo ↔ wfm_completo.{ot_col_wfm} (directo): {c.fetchone()[0]}")
    except Exception as e:
        print(f"  Directo: ❌ {e}")

    # Via ot_wfm
    try:
        c.execute(f"""
            SELECT COUNT(DISTINCT m.id)
            FROM maximo m
            INNER JOIN wfm_completo w ON CAST(m.ot_wfm AS CHAR) = CAST(w.`{ot_col_wfm}` AS CHAR)
            WHERE m.ot_wfm IS NOT NULL
        """)
        print(f"  maximo.ot_wfm ↔ wfm_completo.{ot_col_wfm} (cast): {c.fetchone()[0]}")
    except Exception as e:
        print(f"  Via ot_wfm: ❌ {e}")

# ── 5. Muestra de ot_wfm de maximo vs wfm_completo ────────────────────────
print("\n" + "=" * 65)
print("COMPARACIÓN de formatos")
print("=" * 65)
c.execute("SELECT ot_wfm FROM maximo WHERE ot_wfm IS NOT NULL LIMIT 5")
print("  maximo.ot_wfm (primeros 5):")
for r in c.fetchall():
    print(f"    '{r[0]}'")

if ot_col_wfm:
    c.execute(f"SELECT `{ot_col_wfm}` FROM wfm_completo WHERE `{ot_col_wfm}` IS NOT NULL LIMIT 5")
    print(f"  wfm_completo.{ot_col_wfm} (primeros 5):")
    for r in c.fetchall():
        print(f"    '{r[0]}'")

# ── 6. SLA en wfm_completo con OTs concretas de maximo ───────────────────
print("\n" + "=" * 65)
print("¿Existe alguna OT de maximo en wfm_completo? (búsqueda manual)")
print("=" * 65)
c.execute("SELECT ot_wfm, orden_de_trabajo FROM maximo WHERE ot_wfm IS NOT NULL LIMIT 3")
ots_maximo = c.fetchall()
for ot_wfm, ot_maximo in ots_maximo:
    if ot_col_wfm:
        c.execute(f"SELECT COUNT(*) FROM wfm_completo WHERE `{ot_col_wfm}` = %s", (str(ot_wfm),))
        cnt1 = c.fetchone()[0]
        c.execute(f"SELECT COUNT(*) FROM wfm_completo WHERE `{ot_col_wfm}` = %s", (str(ot_maximo),))
        cnt2 = c.fetchone()[0]
        print(f"  ot_wfm={ot_wfm} → en wfm_completo: {cnt1} | orden_de_trabajo={ot_maximo} → en wfm_completo: {cnt2}")

conn.close()
tunnel.stop()
print("\n✅ Listo")
