"""
Exploracion completa BD contingencia - version corregida
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from sshtunnel import SSHTunnelForwarder
import mysql.connector, warnings
warnings.filterwarnings('ignore')

SSH = {"host": "186.147.60.119", "user": "ccot", "password": "Siesconmigo*"}
DB  = {"user": "otc_app", "password": "22122012Elf@", "database": "contingencia", "host": "127.0.0.1", "port": 3307}

tunnel = SSHTunnelForwarder((SSH["host"], 22), ssh_username=SSH["user"], ssh_password=SSH["password"], remote_bind_address=(DB["host"], DB["port"]))
tunnel.start()
conn = mysql.connector.connect(host='127.0.0.1', port=tunnel.local_bind_port, user=DB["user"], password=DB["password"], database=DB["database"])
print("OK Conectado\n")

def q(sql, params=None):
    cur = conn.cursor()
    cur.execute(sql, params or [])
    rows = cur.fetchall()
    cur.close()
    return rows

# OTs activas de maximo
ots_maximo = [r[0] for r in q("SELECT orden_de_trabajo FROM maximo WHERE orden_de_trabajo IS NOT NULL")]
print(f"OTs activas en maximo: {len(ots_maximo)}\n")

# Listar todas las tablas/vistas
tablas = q("""
    SELECT TABLE_NAME, TABLE_TYPE
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'contingencia'
    ORDER BY TABLE_TYPE, TABLE_NAME
""")

print("=" * 70)
print(f"  {'OBJETO':<35} {'TIPO'}")
print("=" * 70)
for t in tablas:
    print(f"  {t[0]:<35} {t[1]}")
print(f"\nTotal: {len(tablas)} objetos\n")

# Explorar cada tabla
for nombre, tipo in tablas:
    print("\n" + "=" * 70)
    print(f"{'[VIEW] ' if tipo == 'VIEW' else '[TABLE] '}{nombre}")
    print("=" * 70)
    try:
        total = q(f"SELECT COUNT(*) FROM `{nombre}`")[0][0]
        print(f"  Registros: {total:,}")

        cols_info = q(f"DESCRIBE `{nombre}`")
        cols = [r[0] for r in cols_info]
        print(f"  Columnas ({len(cols)}): {', '.join(cols[:20])}{'...' if len(cols)>20 else ''}")

        # Columnas SLA
        sla_cols = [c for c in cols if 'sla' in c.lower()]
        if sla_cols:
            print(f"  >>> Columnas SLA: {sla_cols}")
            for sc in sla_cols:
                vals = q(f"SELECT DISTINCT `{sc}` FROM `{nombre}` WHERE `{sc}` IS NOT NULL AND `{sc}` != '' AND `{sc}` != 0 LIMIT 8")
                if vals:
                    print(f"      {sc}: {[str(r[0]) for r in vals]}")

        # Cruce con maximo
        ot_col = next((c for c in cols if c.lower() == 'orden_de_trabajo'), None)
        if ot_col and ots_maximo:
            placeholders = ','.join(['%s'] * len(ots_maximo))
            match = q(f"SELECT COUNT(DISTINCT `{ot_col}`) FROM `{nombre}` WHERE `{ot_col}` IN ({placeholders})", ots_maximo)[0][0]
            print(f"  OTs de maximo: {match}/{len(ots_maximo)}")

            if match > 0 and sla_cols:
                for sc in sla_cols:
                    rows = q(f"""
                        SELECT `{ot_col}`, `{sc}`
                        FROM `{nombre}`
                        WHERE `{ot_col}` IN ({placeholders})
                          AND `{sc}` IS NOT NULL AND `{sc}` != '' AND `{sc}` != 0
                        LIMIT 5
                    """, ots_maximo)
                    if rows:
                        print(f"  >>> OTs con {sc} NO nulo:")
                        for r in rows:
                            print(f"      OT={r[0]}  {sc}={r[1]}")

        # Muestra 2 filas
        rows = q(f"SELECT * FROM `{nombre}` LIMIT 2")
        if rows:
            print(f"  Muestra (primeras 6 cols):")
            for row in rows:
                d = {cols[i]: str(row[i])[:35] for i in range(min(6, len(cols)))}
                print(f"    {d}")

    except Exception as e:
        print(f"  ERROR: {e}")

conn.close()
tunnel.stop()
print("\n\nExploracion completa OK")
