"""
Verificar union_back_completo como fuente del segmento vía tipo_de_red,
y también Region_Occidente (mayúscula) con orden_de_trabajo text.
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

    # ── 1. Formato de OT en union_back_completo ────────────────────────────
    print("=" * 60)
    print("Formato orden_de_trabajo en union_back_completo (5 filas)")
    print("=" * 60)
    c.execute("SELECT orden_de_trabajo, tipo_de_red FROM union_back_completo WHERE orden_de_trabajo IS NOT NULL LIMIT 10")
    for r in c.fetchall():
        print(f"  OT='{r[0]}'  tipo_de_red='{r[1]}'")

    # ── 2. Cruce maximo ↔ union_back_completo ─────────────────────────────
    print("\n" + "=" * 60)
    print("CRUCE maximo ↔ union_back_completo")
    print("=" * 60)
    c.execute("""
        SELECT COUNT(DISTINCT m.orden_de_trabajo)
        FROM maximo m
        INNER JOIN union_back_completo u ON m.orden_de_trabajo = u.orden_de_trabajo
    """)
    print(f"  Coincidencias directas: {c.fetchone()[0]:,}")

    # ── 3. Muestra del cruce con tipo_de_red como segmento ────────────────
    print("\n" + "=" * 60)
    print("MUESTRA: maximo + segmento desde union_back_completo")
    print("=" * 60)
    c.execute("""
        SELECT m.orden_de_trabajo, m.estado, u.tipo_de_red AS segmento
        FROM maximo m
        INNER JOIN union_back_completo u ON m.orden_de_trabajo = u.orden_de_trabajo
        LIMIT 10
    """)
    for r in c.fetchall():
        print(f"  OT={r[0]}  estado={r[1]}  segmento={r[2]}")

    # ── 4. ¿Duplicados en union_back_completo por OT? ─────────────────────
    print("\n" + "=" * 60)
    print("¿Hay duplicados en union_back_completo por orden_de_trabajo?")
    print("=" * 60)
    c.execute("""
        SELECT orden_de_trabajo, COUNT(*) as cnt
        FROM union_back_completo
        WHERE orden_de_trabajo IS NOT NULL
        GROUP BY orden_de_trabajo
        HAVING cnt > 1
        ORDER BY cnt DESC
        LIMIT 10
    """)
    dups = c.fetchall()
    if dups:
        print(f"  Hay duplicados. Ejemplos:")
        for r in dups:
            print(f"    OT='{r[0]}'  aparece {r[1]} veces")
        # Si hay dups, ver si tipo_de_red varía
        ot_dup = dups[0][0]
        c.execute("SELECT tipo_de_red FROM union_back_completo WHERE orden_de_trabajo = %s", (ot_dup,))
        print(f"  tipo_de_red para OT duplicada '{ot_dup}': {[r[0] for r in c.fetchall()]}")
    else:
        print("  Sin duplicados ✅")

    # ── 5. Cobertura: ¿qué % de maximo tiene segmento en union_back? ──────
    print("\n" + "=" * 60)
    print("COBERTURA del segmento")
    print("=" * 60)
    c.execute("SELECT COUNT(*) FROM maximo")
    total_maximo = c.fetchone()[0]
    c.execute("""
        SELECT COUNT(DISTINCT m.orden_de_trabajo)
        FROM maximo m
        INNER JOIN union_back_completo u ON m.orden_de_trabajo = u.orden_de_trabajo
    """)
    con_segmento = c.fetchone()[0]
    pct = (con_segmento / total_maximo * 100) if total_maximo else 0
    print(f"  Total OTs en maximo: {total_maximo:,}")
    print(f"  Con segmento en union_back_completo: {con_segmento:,}  ({pct:.1f}%)")

    # ── 6. Distribución de segmentos ──────────────────────────────────────
    print("\n" + "=" * 60)
    print("DISTRIBUCIÓN de tipo_de_red (segmento) en union_back_completo")
    print("cruzado con maximo")
    print("=" * 60)
    c.execute("""
        SELECT u.tipo_de_red, COUNT(DISTINCT m.orden_de_trabajo) as total
        FROM maximo m
        INNER JOIN union_back_completo u ON m.orden_de_trabajo = u.orden_de_trabajo
        GROUP BY u.tipo_de_red
        ORDER BY total DESC
    """)
    for r in c.fetchall():
        print(f"  {str(r[0]):<25} → {r[1]:,} OTs")

    # ── 7. Region_Occidente (mayúscula) como alternativa ──────────────────
    print("\n" + "=" * 60)
    print("Formato OT en Region_Occidente (mayúscula)")
    print("=" * 60)
    c.execute("SELECT orden_de_trabajo FROM `Region_Occidente` WHERE orden_de_trabajo IS NOT NULL LIMIT 5")
    for r in c.fetchall():
        print(f"  '{r[0]}'")

    c.execute("""
        SELECT COUNT(DISTINCT m.orden_de_trabajo)
        FROM maximo m
        INNER JOIN `Region_Occidente` ro ON m.orden_de_trabajo = ro.orden_de_trabajo
    """)
    print(f"  Cruce maximo ↔ Region_Occidente: {c.fetchone()[0]:,}")

    c.close()
    conn.close()
    tunnel.stop()
    print("\n✅ Listo")

if __name__ == "__main__":
    main()
