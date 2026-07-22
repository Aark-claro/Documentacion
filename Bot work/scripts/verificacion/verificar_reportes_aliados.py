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

def q(sql, params=None):
    cur = conn.cursor()
    cur.execute(sql, params or [])
    rows = cur.fetchall()
    cur.close()
    return rows

ots_maximo = [r[0] for r in q("SELECT orden_de_trabajo FROM maximo WHERE orden_de_trabajo IS NOT NULL")]
print(f"OTs en maximo: {len(ots_maximo)}\n")

# Estructura completa de reportes_tecnicos_aliados
print("=" * 60)
print("ESTRUCTURA de reportes_tecnicos_aliados")
print("=" * 60)
cols_info = q("DESCRIBE reportes_tecnicos_aliados")
for r in cols_info:
    print(f"  {r[0]:<30} {r[1]}")

total = q("SELECT COUNT(*) FROM reportes_tecnicos_aliados")[0][0]
print(f"\n  Total registros: {total:,}")

# Valores unicos por columna
print("\n  Valores unicos por columna:")
for r in cols_info:
    col = r[0]
    vals = q(f"SELECT DISTINCT `{col}` FROM reportes_tecnicos_aliados WHERE `{col}` IS NOT NULL AND `{col}` != '' AND `{col}` != '<NA>' LIMIT 10")
    if vals:
        print(f"    {col}: {[str(v[0]) for v in vals]}")

# Cruce con maximo
print("\n" + "=" * 60)
print("CRUCE con maximo via columna 'ot'")
print("=" * 60)
placeholders = ','.join(['%s'] * len(ots_maximo))
match = q(f"SELECT COUNT(DISTINCT ot) FROM reportes_tecnicos_aliados WHERE ot IN ({placeholders})", ots_maximo)[0][0]
print(f"  OTs de maximo encontradas: {match}/{len(ots_maximo)}")

if match > 0:
    rows = q(f"""
        SELECT r.ot, r.estado, r.segmento, r.clasificacion, r.xca_cause, r.causa_2
        FROM reportes_tecnicos_aliados r
        WHERE r.ot IN ({placeholders})
        LIMIT 10
    """, ots_maximo)
    print(f"\n  Muestra:")
    for r in rows:
        print(f"    OT={r[0]}  estado={r[1]}  segmento={r[2]}  clasif={str(r[3])[:40]}")

# Rango de OTs en reportes_tecnicos_aliados
print("\n" + "=" * 60)
print("Rango de OTs en reportes_tecnicos_aliados")
print("=" * 60)
r = q("SELECT MIN(ot), MAX(ot), COUNT(DISTINCT ot) FROM reportes_tecnicos_aliados WHERE ot LIKE 'OT%'")[0]
print(f"  min={r[0]}  max={r[1]}  distintas={r[2]:,}")

conn.close()
tunnel.stop()
print("\nOK")
