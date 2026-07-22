"""
Script enfocado: explorar tablas dth, pymes, oym, ots_abiertas y mto_abiertos
para encontrar cómo se relacionan con maximo y qué campo da el segmento.
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
    print("✅ Conectado\n")
    cursor = conn.cursor()

    # ── 1. Ver si dth / pymes / oym son vistas ─────────────────────────────
    print("=" * 65)
    print("¿Son vistas o tablas?")
    print("=" * 65)
    cursor.execute("""
        SELECT TABLE_NAME, TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'contingencia'
        ORDER BY TABLE_TYPE, TABLE_NAME
    """)
    for row in cursor.fetchall():
        print(f"  {row[1]:<12}  {row[0]}")

    # ── 2. Columnas de cada tabla/vista de interés ─────────────────────────
    targets = ['dth', 'pymes', 'oym', 'ots_abiertas', 'mto_abiertos',
               'back_contingencia', 'Region_Occidente', 'region_occidente']

    for t in targets:
        print(f"\n{'=' * 65}")
        print(f"COLUMNAS DE '{t}'")
        print("=" * 65)
        try:
            cursor.execute(f"SELECT * FROM `{t}` LIMIT 0")
            cols = [d[0] for d in cursor.description]
            print(f"  {', '.join(cols)}")

            # Conteo
            cursor.execute(f"SELECT COUNT(*) FROM `{t}`")
            print(f"  → {cursor.fetchone()[0]} registros")

            # ¿Tiene orden_de_trabajo?
            ot_cols = [c for c in cols if 'orden' in c.lower()]
            if ot_cols:
                print(f"  → Columnas con 'orden': {ot_cols}")

            # Valores únicos de columnas tipo texto cortas (candidatas a segmento)
            candidatas = [c for c in cols if any(
                kw in c.lower() for kw in ['segment', 'tipo_red', 'compan', 'negocio', 'linea', 'mercado']
            )]
            for col_c in candidatas[:5]:
                cursor.execute(f"SELECT DISTINCT `{col_c}` FROM `{t}` WHERE `{col_c}` IS NOT NULL LIMIT 15")
                vals = [str(r[0]) for r in cursor.fetchall()]
                print(f"  Valores en '{col_c}': {vals}")

            # Muestra 3 filas
            cursor.execute(f"SELECT * FROM `{t}` LIMIT 3")
            rows = cursor.fetchall()
            print(f"\n  --- Muestra 3 filas ---")
            for row in rows:
                d = {cols[i]: str(row[i])[:35] for i in range(min(len(cols), 12))}
                print(f"  {d}")

        except Exception as e:
            print(f"  ❌ {e}")

    # ── 3. ¿La tabla maximo tiene campo tipo_red o compania? ───────────────
    print(f"\n{'=' * 65}")
    print("COLUMNAS DE 'maximo' que puedan indicar segmento")
    print("=" * 65)
    cursor.execute("SELECT * FROM maximo LIMIT 0")
    maximo_cols = [d[0] for d in cursor.description]
    candidatas_m = [c for c in maximo_cols if any(
        kw in c.lower() for kw in ['segm', 'tipo_red', 'compan', 'negocio', 'linea', 'mercado', 'servicio']
    )]
    print(f"  Candidatas: {candidatas_m}")
    for col_c in candidatas_m:
        cursor.execute(f"SELECT DISTINCT `{col_c}` FROM maximo WHERE `{col_c}` IS NOT NULL LIMIT 15")
        vals = [str(r[0]) for r in cursor.fetchall()]
        print(f"  Valores en '{col_c}': {vals}")

    # ── 4. Cruzar maximo con dth / pymes por orden_de_trabajo ──────────────
    print(f"\n{'=' * 65}")
    print("CRUCE maximo vs dth/pymes (¿cuántas OTs coinciden?)")
    print("=" * 65)
    for t in ['dth', 'pymes', 'oym']:
        try:
            # Verificar qué columna tiene la OT en esa tabla
            cursor.execute(f"SELECT * FROM `{t}` LIMIT 0")
            cols_t = [d[0] for d in cursor.description]
            ot_col = next((c for c in cols_t if 'orden' in c.lower()), None)
            if not ot_col:
                print(f"  {t}: sin columna 'orden_de_trabajo'")
                continue

            cursor.execute(f"""
                SELECT COUNT(*)
                FROM maximo m
                INNER JOIN `{t}` x ON m.orden_de_trabajo = x.`{ot_col}`
            """)
            cnt = cursor.fetchone()[0]
            print(f"  maximo ↔ {t} (via {ot_col}): {cnt} coincidencias")

            # Muestra un par de filas del cruce
            cursor.execute(f"""
                SELECT m.orden_de_trabajo, m.estado, x.*
                FROM maximo m
                INNER JOIN `{t}` x ON m.orden_de_trabajo = x.`{ot_col}`
                LIMIT 2
            """)
            for row in cursor.fetchall():
                print(f"    {[str(v)[:30] for v in row[:8]]}")
        except Exception as e:
            print(f"  {t}: ❌ {e}")

    cursor.close()
    conn.close()
    tunnel.stop()
    print("\n✅ Listo")

if __name__ == "__main__":
    main()
