from sshtunnel import SSHTunnelForwarder
import mysql.connector, warnings
warnings.filterwarnings('ignore')

tunnel = SSHTunnelForwarder(('186.147.60.119', 22), ssh_username='ccot', ssh_password='Siesconmigo*', remote_bind_address=('127.0.0.1', 3307))
tunnel.start()
conn = mysql.connector.connect(host='127.0.0.1', port=tunnel.local_bind_port, user='otc_app', password='22122012Elf@', database='contingencia')
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM maximo")
total = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM maximo WHERE ruta_de_clasificacion IS NULL OR TRIM(ruta_de_clasificacion) = ''")
sin_ruta = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM maximo WHERE ruta_de_clasificacion IS NOT NULL AND TRIM(ruta_de_clasificacion) != ''")
con_ruta = c.fetchone()[0]

print(f"Total OTs en maximo: {total}")
print(f"Con ruta_de_clasificacion:    {con_ruta}")
print(f"Sin ruta_de_clasificacion:    {sin_ruta}")
print()

# Ejemplos de OTs sin ruta
c.execute("SELECT orden_de_trabajo, estado, tipo_de_trabajo, ruta_de_clasificacion FROM maximo WHERE ruta_de_clasificacion IS NULL OR TRIM(ruta_de_clasificacion) = '' LIMIT 10")
print("OTs SIN ruta_de_clasificacion:")
for r in c.fetchall():
    print(f"  OT={r[0]}  estado={r[1]}  tipo={r[2]}  ruta={repr(r[3])}")

# Distribución de primer nivel de ruta
print()
c.execute("SELECT ruta_de_clasificacion FROM maximo WHERE ruta_de_clasificacion IS NOT NULL AND TRIM(ruta_de_clasificacion) != ''")
rutas = [r[0] for r in c.fetchall()]
from collections import Counter
primeros = Counter()
for ruta in rutas:
    primer = ruta.split('\\')[0].strip().upper()
    primeros[primer] += 1
print("Distribución por primer nivel de ruta:")
for k, v in primeros.most_common():
    print(f"  {v:3}  '{k}'")

conn.close()
tunnel.stop()
print("\nDone")
