"""
Script focalizado: verificar que dth, pymes, region_occidente tienen orden_de_trabajo
y cuántas OTs de maximo aparecen en cada una (para determinar el segmento).
"""
from sshtunnel import SSHTunnelForwarder
import mysql.connector

SSH_CONFIG = {"host": "186.147.60.119", "user": "ccot", "password": "Siesconmigo*"}
DB_CONFIG  = {"user": "otc_app", "password": "22122012Elf@", "database": "contingencia", "host": "127.0.0.1", "port": 3307}

def q(cursor, sql, params=None):
    cursor.execute(sql, params or [])
    return cursor.fetchall()

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

    # ── Cuántos registros en cada tabla segmento ───────────────────────────
    tablas_segmento = ['dth', 'pymes', 'region_occidente', 'Region_Occidente',
                       'ots_abiertas', 'mto_abiertos', 'recursos', 'oym']
    print("CONTEO POR TABLA")
    print("-" * 50)
    for t in tablas_segmento:
        try:
            rows = q(c, f"SELECT COUNT(*) FROM `{t}`")
            print(f"  {t:<25} → {rows[0][0]:,} filas")
        except Exception as e:
            print(f"  {t:<25} → ❌ {e}")

    # ── Columnas de dth y pymes ────────────────────────────────────────────
    for t in ['dth', 'pymes', 'region_occidente']:
        print(f"\n{'=' * 60}")
        print(f"COLUMNAS DE '{t}'")
        print("=" * 60)
        try:
            rows = q(c, f"DESCRIBE `{t}`")
            for r in rows:
                print(f"  {r[0]:<35} {r[1]}")
        except Exception as e:
            print(f"  ❌ {e}")

    # ── Cruce maximo ↔ dth / pymes ─────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("CRUCE maximo ↔ tablas por orden_de_trabajo")
    print("=" * 60)
    for t in ['dth', 'pymes', 'region_occidente']:
        try:
            rows = q(c, f"""
                SELECT COUNT(DISTINCT m.orden_de_trabajo)
                FROM maximo m
                INNER JOIN `{t}` x ON m.orden_de_trabajo = x.orden_de_trabajo
            """)
            print(f"  maximo ↔ {t}: {rows[0][0]:,} OTs en común")
        except Exception as e:
            print(f"  {t}: ❌ {e}")

    # ── ¿Están las mismas OTs en varias tablas? (solapamiento) ────────────
    print(f"\n{'=' * 60}")
    print("SOLAPAMIENTO entre tablas de segmento")
    print("=" * 60)
    try:
        rows = q(c, """
            SELECT COUNT(*) FROM dth d
            INNER JOIN pymes p ON d.orden_de_trabajo = p.orden_de_trabajo
        """)
        print(f"  dth ∩ pymes: {rows[0][0]:,} OTs en ambas")
    except Exception as e:
        print(f"  ❌ {e}")

    # ── Muestra de OTs en maximo y cuál tabla las contiene ────────────────
    print(f"\n{'=' * 60}")
    print("MUESTRA: 5 OTs de maximo con su segmento inferido")
    print("=" * 60)
    try:
        rows = q(c, "SELECT orden_de_trabajo FROM maximo WHERE orden_de_trabajo IS NOT NULL LIMIT 10")
        ots = [r[0] for r in rows]
        for ot in ots[:5]:
            segmento = "Sin segmento"
            for t in ['dth', 'pymes', 'region_occidente']:
                try:
                    res = q(c, f"SELECT COUNT(*) FROM `{t}` WHERE orden_de_trabajo = %s", (ot,))
                    if res[0][0] > 0:
                        segmento = t
                        break
                except:
                    pass
            print(f"  OT {ot} → {segmento}")
    except Exception as e:
        print(f"  ❌ {e}")

    # ── Verificar si union_back_completo tiene columna de segmento ─────────
    print(f"\n{'=' * 60}")
    print("¿union_back_completo tiene campo que indique segmento?")
    print("=" * 60)
    try:
        rows = q(c, "DESCRIBE union_back_completo")
        for r in rows:
            print(f"  {r[0]:<35} {r[1]}")
        # Muestra de tipo_de_red (parece clave)
        rows2 = q(c, "SELECT DISTINCT tipo_de_red FROM union_back_completo WHERE tipo_de_red IS NOT NULL LIMIT 20")
        print(f"\n  Valores únicos en tipo_de_red: {[r[0] for r in rows2]}")
    except Exception as e:
        print(f"  ❌ {e}")

    c.close()
    conn.close()
    tunnel.stop()
    print("\n✅ Listo")

if __name__ == "__main__":
    main()
