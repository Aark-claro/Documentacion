from sshtunnel import SSHTunnelForwarder
import mysql.connector

tunnel = SSHTunnelForwarder(
    ('186.147.60.119', 22),
    ssh_username='ccot',
    ssh_password='Siesconmigo*',
    remote_bind_address=('127.0.0.1', 3307)
)
tunnel.start()

conn = mysql.connector.connect(
    host='127.0.0.1',
    port=tunnel.local_bind_port,
    user='otc_app',
    password='22122012Elf@',
    database='contingencia'
)
cursor = conn.cursor()

print('=== COLUMNAS de oym_fijo ===')
cursor.execute('DESCRIBE oym_fijo')
for col in cursor.fetchall():
    print(col[0], '-', col[1])

print()
print('=== 1 REGISTRO de ejemplo ===')
cursor.execute('SELECT * FROM oym_fijo LIMIT 1')
cols = [d[0] for d in cursor.description]
row = cursor.fetchone()
if row:
    for c, v in zip(cols, row):
        print(f'{c}: {str(v)[:60]}')

cursor.close()
conn.close()
tunnel.stop()
print('done')
