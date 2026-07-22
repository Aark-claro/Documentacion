"""
Analizar los datos reales de maximo para determinar cómo inferir el segmento.
Mostrar valores únicos de todos los campos de texto relevantes.
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

    # Campos candidatos para inferir segmento en maximo
    campos = [
        'tipo_de_trabajo',
        'descripcion_grupo',
        'clasificacion',
        'ruta_de_clasificacion',
        'aliado',
        'descripcion',
        'grupo_site_owner',
        'smu',
        'propietario',
        'descripcion_estado',
        'ot_wfm',
    ]

    for campo in campos:
        print(f"\n{'=' * 60}")
        print(f"VALORES ÚNICOS EN '{campo}'")
        print("=" * 60)
        try:
            c.execute(f"SELECT DISTINCT `{campo}` FROM maximo WHERE `{campo}` IS NOT NULL ORDER BY `{campo}` LIMIT 30")
            vals = c.fetchall()
            if vals:
                for v in vals:
                    print(f"  '{v[0]}'")
            else:
                print("  (sin valores)")
        except Exception as e:
            print(f"  ❌ {e}")

    # Mostrar todos los campos de 5 registros de muestra
    print(f"\n{'=' * 60}")
    print("MUESTRA COMPLETA: 5 registros de maximo")
    print("=" * 60)
    c.execute("SELECT * FROM maximo LIMIT 5")
    cols = [d[0] for d in c.description]
    rows = c.fetchall()
    for row in rows:
        print(f"\n  --- Registro ---")
        for col, val in zip(cols, row):
            if val is not None and str(val).strip():
                print(f"    {col:<35}: {str(val)[:80]}")

    # Relación ot_wfm con tablas de segmento
    print(f"\n{'=' * 60}")
    print("¿ot_wfm de maximo coincide con alguna tabla de segmento?")
    print("=" * 60)
    c.execute("SELECT ot_wfm FROM maximo WHERE ot_wfm IS NOT NULL LIMIT 10")
    ot_wfm_vals = [str(r[0]) for r in c.fetchall()]
    print(f"  Valores ot_wfm: {ot_wfm_vals}")

    # Intentar cruce via ot_wfm
    for tabla in ['dth', 'pymes', 'Region_Occidente']:
        try:
            col_ot = 'orden_de_trabajo'
            c.execute(f"""
                SELECT COUNT(DISTINCT m.id)
                FROM maximo m
                INNER JOIN `{tabla}` t ON CAST(m.ot_wfm AS CHAR) = CAST(t.`{col_ot}` AS CHAR)
                WHERE m.ot_wfm IS NOT NULL
            """)
            print(f"  maximo.ot_wfm ↔ {tabla}.orden_de_trabajo: {c.fetchone()[0]} coincidencias")
        except Exception as e:
            print(f"  {tabla}: ❌ {e}")

    c.close()
    conn.close()
    tunnel.stop()
    print("\n✅ Listo")

if __name__ == "__main__":
    main()
