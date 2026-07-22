"""
Script para encontrar la tabla/columna de SEGMENTO en la BD contingencia.
Busca en todas las tablas cualquier referencia a segmento y su relación con maximo.
"""
from sshtunnel import SSHTunnelForwarder
import mysql.connector

SSH_CONFIG = {
    "host": "186.147.60.119",
    "user": "ccot",
    "password": "Siesconmigo*"
}

DB_CONFIG = {
    "user": "otc_app",
    "password": "22122012Elf@",
    "database": "contingencia",
    "host": "127.0.0.1",
    "port": 3307
}

def buscar_segmento():
    tunnel = None
    conn = None

    try:
        print("🔌 Conectando via SSH...")
        tunnel = SSHTunnelForwarder(
            (SSH_CONFIG["host"], 22),
            ssh_username=SSH_CONFIG["user"],
            ssh_password=SSH_CONFIG["password"],
            remote_bind_address=(DB_CONFIG["host"], DB_CONFIG["port"])
        )
        tunnel.start()

        conn = mysql.connector.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        print("✅ Conectado\n")
        cursor = conn.cursor()

        # ── 1. Listar todas las tablas de la BD ──────────────────────────────
        print("=" * 70)
        print("📋 TABLAS EN LA BD 'contingencia'")
        print("=" * 70)
        cursor.execute("SHOW TABLES")
        tablas = [row[0] for row in cursor.fetchall()]
        for t in tablas:
            print(f"  • {t}")

        # ── 2. Buscar en INFORMATION_SCHEMA columnas que contengan "segmento" ─
        print("\n" + "=" * 70)
        print("🔍 COLUMNAS QUE CONTIENEN 'segmento' EN TODA LA BD")
        print("=" * 70)
        db_name = DB_CONFIG["database"]
        cursor.execute(f"""
            SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{db_name}'
              AND LOWER(COLUMN_NAME) LIKE '%segmento%'
            ORDER BY TABLE_NAME, COLUMN_NAME
        """)
        hits = cursor.fetchall()
        if hits:
            for tabla, col, dtype in hits:
                print(f"  ✅ {tabla}.{col}  ({dtype})")
        else:
            print("  ❌ Ninguna columna con nombre 'segmento' encontrada")

        # ── 3. Buscar columnas 'orden_de_trabajo' en todas las tablas ────────
        print("\n" + "=" * 70)
        print("🔗 TABLAS QUE TIENEN COLUMNA 'orden_de_trabajo' (posible FK con maximo)")
        print("=" * 70)
        cursor.execute(f"""
            SELECT TABLE_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = '{db_name}'
              AND LOWER(COLUMN_NAME) LIKE '%orden%'
            ORDER BY TABLE_NAME
        """)
        hits_ot = cursor.fetchall()
        for tabla, col in hits_ot:
            print(f"  • {tabla}.{col}")

        # ── 4. Para cada tabla con 'orden_de_trabajo', mostrar estructura ─────
        tablas_con_ot = list({row[0] for row in hits_ot if row[0] != 'maximo'})
        for tabla in tablas_con_ot:
            print(f"\n{'=' * 70}")
            print(f"📊 ESTRUCTURA DE '{tabla}'")
            print("=" * 70)
            cursor.execute(f"DESCRIBE `{tabla}`")
            for col in cursor.fetchall():
                print(f"  {col[0]:<35} {col[1]:<20} null={col[2]}")

            cursor.execute(f"SELECT COUNT(*) FROM `{tabla}`")
            total = cursor.fetchone()[0]
            print(f"  → Total registros: {total}")

            # Mostrar valores únicos de columnas candidatas a 'segmento'
            cursor.execute(f"DESCRIBE `{tabla}`")
            cols_tabla = [c[0] for c in cursor.fetchall()]
            candidatas = [c for c in cols_tabla if any(
                kw in c.lower() for kw in ['segment', 'negocio', 'linea', 'tipo', 'categoria']
            )]
            for col_c in candidatas[:5]:  # máximo 5
                try:
                    cursor.execute(f"SELECT DISTINCT `{col_c}` FROM `{tabla}` WHERE `{col_c}` IS NOT NULL LIMIT 15")
                    vals = [str(r[0]) for r in cursor.fetchall()]
                    print(f"\n  Valores únicos en '{col_c}': {', '.join(vals)}")
                except Exception:
                    pass

        # ── 5. Buscar el valor 'Residencial', 'Pymes', 'DTH' en todas las tablas ─
        print("\n" + "=" * 70)
        print("🎯 BÚSQUEDA DE VALORES 'Residencial' / 'Pymes' / 'DTH' EN TODAS LAS TABLAS")
        print("=" * 70)
        keywords = ['residencial', 'pymes', 'dth', 'empresas', 'corporativo']
        for tabla in tablas:
            cursor.execute(f"DESCRIBE `{tabla}`")
            cols_str = [c[0] for c in cursor.fetchall() if 'char' in c[1].lower() or 'text' in c[1].lower() or 'enum' in c[1].lower()]
            for col in cols_str[:10]:  # limitar búsqueda
                for kw in keywords:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM `{tabla}` WHERE LOWER(`{col}`) = %s", (kw,))
                        cnt = cursor.fetchone()[0]
                        if cnt > 0:
                            print(f"  ✅ {tabla}.{col} → '{kw}' aparece {cnt} veces")
                    except Exception:
                        pass

        # ── 6. Muestra 2 filas de cada tabla pequeña ─────────────────────────
        print("\n" + "=" * 70)
        print("🗃️  MUESTRA (2 filas) DE CADA TABLA DISTINTA A 'maximo'")
        print("=" * 70)
        for tabla in tablas:
            if tabla == 'maximo':
                continue
            try:
                cursor.execute(f"SELECT * FROM `{tabla}` LIMIT 2")
                cols_t = [d[0] for d in cursor.description]
                rows = cursor.fetchall()
                print(f"\n  ── {tabla} ──")
                print(f"  Columnas: {', '.join(cols_t)}")
                for row in rows:
                    print(f"  {dict(zip(cols_t, [str(v)[:40] for v in row]))}")
            except Exception as e:
                print(f"  {tabla}: no se pudo leer ({e})")

        cursor.close()
        conn.close()
        tunnel.stop()
        print("\n✅ Búsqueda completada")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if conn:
            conn.close()
        if tunnel:
            tunnel.stop()
        raise

if __name__ == "__main__":
    buscar_segmento()
