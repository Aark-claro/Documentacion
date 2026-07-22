"""
Script final: verificar formato de orden_de_trabajo en dth/pymes vs maximo,
y explorar Region_Occidente (mayúscula) + source_name como campo de segmento.
"""
from sshtunnel import SSHTunnelForwarder
import mysql.connector

SSH_CONFIG = {"host": "186.147.60.119", "user": "ccot", "password": "Siesconmigo*"}
DB_CONFIG  = {"user": "otc_app", "password": "22122012Elf@", "database": "contingencia", "host": "127.0.0.1", "port": 3307}

def main():
    tunnel = SSHTunnelForwarder(
        (SSH_CONFIG["host"], 22),
        ssh_username=SSH_CONFIG["user"],
        ssh_password=SSH_CONFIG["password"],
        remote_bind_address=(DB_CONFIG["host"], DB_CONFIG["port"])
    )
    tunnel.start()
    conn = mysql.connector.connect(
        host='127.0.0.1', port=tunnel.local_bind_port,
        user=DB_CONFIG["user"], password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )
    c = conn.cursor()
    print("✅ Conectado\n")

    # ── 1. Muestra de orden_de_trabajo en dth y pymes ─────────────────────
    print("=" * 60)
    print("FORMATO de orden_de_trabajo en dth (primeras 5)")
    print("=" * 60)
    c.execute("SELECT orden_de_trabajo FROM dth WHERE orden_de_trabajo IS NOT NULL LIMIT 5")
    for r in c.fetchall():
        print(f"  '{r[0]}'")

    print("\n" + "=" * 60)
    print("FORMATO de orden_de_trabajo en pymes (primeras 5)")
    print("=" * 60)
    c.execute("SELECT orden_de_trabajo FROM pymes WHERE orden_de_trabajo IS NOT NULL LIMIT 5")
    for r in c.fetchall():
        print(f"  '{r[0]}'")

    print("\n" + "=" * 60)
    print("FORMATO de orden_de_trabajo en maximo (primeras 5)")
    print("=" * 60)
    c.execute("SELECT orden_de_trabajo FROM maximo WHERE orden_de_trabajo IS NOT NULL LIMIT 5")
    for r in c.fetchall():
        print(f"  '{r[0]}'")

    # ── 2. Intentar cruce con CAST o TRIM ─────────────────────────────────
    print("\n" + "=" * 60)
    print("CRUCE con conversión: CAST(dth.orden_de_trabajo AS CHAR) vs maximo")
    print("=" * 60)
    c.execute("""
        SELECT COUNT(DISTINCT m.orden_de_trabajo)
        FROM maximo m
        INNER JOIN dth d ON m.orden_de_trabajo = CAST(d.orden_de_trabajo AS CHAR)
    """)
    print(f"  maximo ↔ dth (cast): {c.fetchone()[0]:,} coincidencias")

    c.execute("""
        SELECT COUNT(DISTINCT m.orden_de_trabajo)
        FROM maximo m
        INNER JOIN pymes p ON m.orden_de_trabajo = CAST(p.orden_de_trabajo AS CHAR)
    """)
    print(f"  maximo ↔ pymes (cast): {c.fetchone()[0]:,} coincidencias")

    # ── 3. Region_Occidente (mayúscula) - columnas y source_name ─────────
    print("\n" + "=" * 60)
    print("COLUMNAS DE 'Region_Occidente' (mayúscula)")
    print("=" * 60)
    c.execute("DESCRIBE `Region_Occidente`")
    for r in c.fetchall():
        print(f"  {r[0]:<40} {r[1]}")

    print("\n" + "=" * 60)
    print("Valores únicos en source_name (Region_Occidente)")
    print("=" * 60)
    c.execute("SELECT DISTINCT source_name FROM `Region_Occidente` WHERE source_name IS NOT NULL LIMIT 20")
    for r in c.fetchall():
        print(f"  '{r[0]}'")

    print("\n" + "=" * 60)
    print("Columnas con 'orden' en Region_Occidente")
    print("=" * 60)
    c.execute("DESCRIBE `Region_Occidente`")
    cols = [r[0] for r in c.fetchall()]
    ot_cols = [c2 for c2 in cols if 'orden' in c2.lower()]
    print(f"  {ot_cols}")

    # ── 4. Cruce Region_Occidente con maximo via orden_de_trabajo_1 ───────
    if 'orden_de_trabajo_1' in cols or 'orden_de_trabajo' in cols:
        ot_col = 'orden_de_trabajo' if 'orden_de_trabajo' in cols else 'orden_de_trabajo_1'
        print(f"\n" + "=" * 60)
        print(f"CRUCE Region_Occidente (via {ot_col}) con maximo")
        print("=" * 60)
        c.execute(f"""
            SELECT COUNT(DISTINCT m.orden_de_trabajo)
            FROM maximo m
            INNER JOIN `Region_Occidente` ro ON m.orden_de_trabajo = CAST(ro.`{ot_col}` AS CHAR)
        """)
        print(f"  maximo ↔ Region_Occidente (cast): {c.fetchone()[0]:,} coincidencias")

        # Muestra con source_name
        c.execute(f"""
            SELECT m.orden_de_trabajo, ro.source_name
            FROM maximo m
            INNER JOIN `Region_Occidente` ro ON m.orden_de_trabajo = CAST(ro.`{ot_col}` AS CHAR)
            LIMIT 5
        """)
        print("\n  Muestra OT → source_name:")
        for r in c.fetchall():
            print(f"    OT {r[0]} → '{r[1]}'")

    # ── 5. Explorar ots_abiertas ───────────────────────────────────────────
    print("\n" + "=" * 60)
    print("COLUMNAS y muestra de 'ots_abiertas'")
    print("=" * 60)
    c.execute("DESCRIBE ots_abiertas")
    desc_ots = c.fetchall()
    for r in desc_ots:
        print(f"  {r[0]:<40} {r[1]}")

    c.execute("SELECT * FROM ots_abiertas LIMIT 3")
    cols_ots = [d[0] for d in c.description]
    for row in c.fetchall():
        print(f"  {dict(zip(cols_ots, [str(v)[:35] for v in row]))}")

    # ── 6. Explorar mto_abiertos ───────────────────────────────────────────
    print("\n" + "=" * 60)
    print("COLUMNAS y muestra de 'mto_abiertos'")
    print("=" * 60)
    c.execute("DESCRIBE mto_abiertos")
    for r in c.fetchall():
        print(f"  {r[0]:<40} {r[1]}")

    c.execute("SELECT * FROM mto_abiertos LIMIT 3")
    cols_mto = [d[0] for d in c.description]
    for row in c.fetchall():
        print(f"  {dict(zip(cols_mto, [str(v)[:35] for v in row]))}")

    c.close()
    conn.close()
    tunnel.stop()
    print("\n✅ Listo")

if __name__ == "__main__":
    main()
