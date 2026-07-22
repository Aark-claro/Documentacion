# 🛠️ Guía de Fallas y Soluciones

**Proyecto:** Bot Work — Panel de Órdenes de Trabajo  
**Última actualización:** Julio 2026

---

## Índice

1. [Fallas de Conexión](#1-fallas-de-conexión)
2. [Fallas del Backend (FastAPI)](#2-fallas-del-backend-fastapi)
3. [Fallas del Frontend (React)](#3-fallas-del-frontend-react)
4. [Fallas del Script de Descarga (Selenium)](#4-fallas-del-script-de-descarga-selenium)
5. [Fallas de la Base de Datos](#5-fallas-de-la-base-de-datos)
6. [Fallas de Datos / Lógica de Negocio](#6-fallas-de-datos--lógica-de-negocio)
7. [Fallas de Entorno y Dependencias](#7-fallas-de-entorno-y-dependencias)

---

## 1. Fallas de Conexión

### 1.1 Error: `SSH tunnel failed to start` / `Connection refused`

**Síntoma:**  
El backend arranca pero al llamar `/api/ordenes` responde 500 con `Error al consultar BD: ...` y en consola aparece algo como:
```
Could not connect to server at 186.147.60.119:22
```

**Causas posibles:**
- El servidor SSH está caído o no accesible desde la red actual
- Se está conectando desde una red sin acceso a la VPN corporativa
- Las credenciales SSH cambiaron

**Solución:**
1. Verificar conectividad: `ping 186.147.60.119`
2. Si se está fuera de la red corporativa, conectar a la VPN antes de levantar el backend
3. Probar conexión SSH manual: `ssh ccot@186.147.60.119`
4. Si las credenciales cambiaron, actualizar `SSH_CONFIG` en `backend/main.py` (o en `.env` si ya se migró)

---

### 1.2 Error: `mysql.connector.errors.InterfaceError: 2003`

**Síntoma:**  
El túnel SSH se establece pero la conexión a MySQL falla.

**Causas posibles:**
- El puerto 3307 no está abierto en el servidor remoto
- El usuario MySQL no tiene permisos desde `127.0.0.1`
- El túnel apunta al puerto equivocado

**Solución:**
1. Ejecutar `scripts/verificacion/verificar_bd.py` para aislar el problema
2. Confirmar que `remote_bind_address=('127.0.0.1', 3307)` coincide con la configuración del servidor
3. Verificar que `tunnel.local_bind_port` se pasa correctamente a `mysql.connector.connect()`

---

### 1.3 Error: `SSHTunnelForwarder` tarda demasiado o se queda colgado

**Síntoma:**  
El backend no responde y el proceso de Python queda bloqueado indefinidamente.

**Causa:**  
`sshtunnel` no tiene timeout configurado por defecto.

**Solución:**
Agregar timeout explícito en `get_db_connection()`:

```python
tunnel = SSHTunnelForwarder(
    (SSH_CONFIG["host"], 22),
    ssh_username=SSH_CONFIG["user"],
    ssh_password=SSH_CONFIG["password"],
    remote_bind_address=(DB_CONFIG["host"], DB_CONFIG["port"]),
    set_keepalive=10.0,      # keepalive cada 10 segundos
    ssh_timeout=15.0         # timeout de conexión 15 segundos
)
```

---

## 2. Fallas del Backend (FastAPI)

### 2.1 Error: `ImportError: No module named 'sshtunnel'` (u otro módulo)

**Síntoma:**  
Al ejecutar `python main.py` aparece `ImportError` o `ModuleNotFoundError`.

**Solución:**
```bash
cd backend
pip install -r requirements.txt
```

Si el error persiste, verificar que se está usando el Python del entorno correcto:
```bash
python --version
pip --version
# Si son distintos entornos, usar:
python -m pip install -r requirements.txt
```

---

### 2.2 Error: `422 Unprocessable Entity` en `/api/ordenes`

**Síntoma:**  
La API devuelve 422 con un mensaje sobre validación de campos.

**Causa:**  
El modelo Pydantic `Orden` tiene un campo que no coincide con lo que devuelve la BD (por ejemplo, un campo `int` con un valor `None` o un `str` con tipo inesperado).

**Solución:**
1. Ejecutar `scripts/verificacion/verificar_alineacion.py` para ver discrepancias
2. Asegurarse de que todos los campos del modelo usen `Optional[tipo] = None`
3. Para fechas, verificar que se están convirtiendo a `str` antes de enviar (el backend ya hace esto con `isinstance(valor, datetime)`)

---

### 2.3 El endpoint responde pero la lista viene vacía

**Síntoma:**  
`GET /api/ordenes` devuelve `{"total": 0, "ordenes": []}` sin errores.

**Causas posibles:**
- Se pasó un filtro con un valor que no existe en la BD (ej: `estado=ASIGNADO` en lugar de `ASIGNADO`)
- La tabla `maximo` está vacía o no sincronizada
- El JOIN con `oym_fijo` tiene un problema que descarta todas las filas (poco probable con LEFT JOIN)

**Solución:**
1. Llamar sin filtros: `GET /api/ordenes`
2. Verificar que la tabla tiene datos: `scripts/verificacion/verificar_bd.py`
3. Revisar los valores exactos de los campos con los scripts de exploración

---

### 2.4 Error: `OSError: [Errno 98] Address already in use`

**Síntoma:**  
Al iniciar el backend: `ERROR: [Errno 98] Address already in use`.

**Causa:**  
El puerto 8000 ya está ocupado por otra instancia del servidor.

**Solución en Windows:**
```powershell
# Encontrar el proceso usando el puerto 8000
netstat -ano | findstr :8000
# Terminar el proceso (reemplazar PID)
taskkill /PID <PID> /F
```

O cambiar el puerto en `backend/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

### 2.5 El backend se cae después de varias consultas

**Síntoma:**  
El backend funciona las primeras veces pero después de un rato empieza a devolver errores 500.

**Causa:**  
Cada petición abre un túnel SSH y una conexión MySQL nuevos, y si alguno no se cierra correctamente (por una excepción no manejada), se van acumulando conexiones abiertas hasta agotar los recursos.

**Solución:**  
Verificar que los bloques `try/except` en el backend siempre cierran el túnel y la conexión en el bloque `finally`. La estructura correcta es:

```python
tunnel = None
connection = None
try:
    tunnel, connection = get_db_connection()
    # ... lógica
finally:
    if connection:
        connection.close()
    if tunnel:
        tunnel.stop()
```

---

## 3. Fallas del Frontend (React)

### 3.1 Error: `Network Error` o `Failed to fetch` en el dashboard

**Síntoma:**  
El dashboard carga pero no muestra datos y en la consola del navegador (F12) aparece un error CORS o de red.

**Causas posibles:**
- El backend no está corriendo
- La URL de la API en `App.jsx` es incorrecta
- Error de CORS

**Solución:**
1. Verificar que el backend está corriendo en `http://localhost:8000`
2. Abrir `http://localhost:8000/api/ordenes` directamente en el navegador para confirmar
3. Si el backend está en otro puerto, actualizar en `App.jsx`:
   ```javascript
   const API_URL = 'http://localhost:PUERTO/api'
   ```
4. Si es CORS, verificar que el backend tiene el middleware configurado (ya lo tiene por defecto)

---

### 3.2 Error: `npm install` falla por dependencias

**Síntoma:**  
Al ejecutar `npm install` en la carpeta `frontend` aparecen errores de versiones incompatibles.

**Solución:**
```bash
# Limpiar caché de npm y reinstalar
cd frontend
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm cache clean --force
npm install
```

---

### 3.3 Los filtros no funcionan / No filtra correctamente

**Síntoma:**  
Se selecciona un filtro en el dropdown pero la tabla no cambia.

**Causas posibles:**
- El valor del filtro tiene mayúsculas/minúsculas distintas a los datos de la BD
- El campo `familia` o `segmento` se filtra en frontend (no se envía al backend como parámetro)

**Solución:**
- Verificar los valores exactos que devuelve la BD usando los scripts de exploración
- El filtro de `familia` y `segmento` se aplica en el frontend porque son campos calculados — si el cálculo no funciona, revisar la lógica en `backend/main.py` (`calcular_familia` y `calcular_segmento`)

---

### 3.4 La tabla muestra columnas vacías o con `null`

**Síntoma:**  
Algunas columnas aparecen en blanco para todas las filas.

**Causa:**  
El nombre de la columna en el frontend no coincide con la clave que devuelve el backend.

**Solución:**
1. Ejecutar `scripts/verificacion/verificar_alineacion.py`
2. Comparar el campo problemático en `TODAS_LAS_COLUMNAS` (frontend) con el modelo `Orden` (backend)
3. Verificar que el nombre de la columna en la BD sea exactamente igual (incluyendo mayúsculas)

---

### 3.5 `npm run dev` arranca pero el navegador no abre

**Síntoma:**  
Vite muestra en consola `Local: http://localhost:5173/` pero el navegador no abre automáticamente.

**Solución:**  
Simplemente abrir `http://localhost:5173` manualmente en el navegador. El auto-open no siempre funciona en Windows.

---

## 4. Fallas del Script de Descarga (Selenium)

### 4.1 Error: `WebDriverException: Message: 'msedgedriver' executable needs to be in PATH`

**Síntoma:**  
Al ejecutar `descarga_bds_oracle.py` aparece un error relacionado con EdgeDriver.

**Solución:**  
Con Selenium 4.x el driver se descarga automáticamente. Si falla:
```bash
pip install --upgrade selenium
```

Si el error persiste, verificar que Microsoft Edge esté instalado y actualizado (versión 149+).

---

### 4.2 Error: No se encuentra el botón SSO en Oracle

**Síntoma:**  
El script imprime `✗ No se encontró el botón SSO` y lanza excepción.

**Causas posibles:**
- La página de Oracle cambió su estructura HTML
- El portal tarda más de 5 segundos en cargar

**Solución:**
1. Reducir la dependencia en tiempos fijos (`time.sleep(5)`) y usar `WebDriverWait` con condiciones explícitas
2. Ejecutar el script en modo visible (sin `--headless`) para inspeccionar qué aparece en pantalla
3. Inspeccionar el HTML del botón SSO con las DevTools del navegador y actualizar el selector XPath en el script

---

### 4.3 La autenticación de dos factores expira antes de completarse

**Síntoma:**  
Al completar el 2FA y presionar ENTER, la sesión ya expiró y Oracle muestra pantalla de login nuevamente.

**Solución:**
- Completar el 2FA lo más rápido posible después de que el script pause
- Si el timeout del 2FA es muy corto, solicitar al área de TI extender el tiempo de espera de autenticación

---

### 4.4 Los archivos no se mueven a la carpeta correcta

**Síntoma:**  
Los `.xlsx` descargados quedan en `BDS_work/` en lugar de en sus subcarpetas.

**Causas posibles:**
- La función `move_downloaded_files()` no encuentra los archivos porque la descarga no terminó
- El nombre del archivo no termina en `.xlsx` (Oracle a veces descarga como `.xlsx (1)` si ya existe)

**Solución:**
1. Aumentar el `time.sleep(5)` en `move_downloaded_files()` a 10-15 segundos
2. Agregar manejo de archivos con nombres duplicados:
   ```python
   import glob
   archivos = glob.glob(os.path.join(source_folder, '*.xlsx*'))
   ```

---

### 4.5 El script de descarga pierde la sesión a mitad del proceso

**Síntoma:**  
Después de descargar 2-3 bases de datos, Oracle pide autenticación nuevamente.

**Causa:**  
La sesión de Oracle expira por inactividad. El keep-alive JavaScript (`console.log`) no es suficiente para mantener la sesión de OFS activa.

**Solución:**
- Agregar una acción real en el keep-alive, como hacer scroll o navegar a una página de inicio:
  ```python
  self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.F5)
  ```
- Reducir el intervalo del loop a menos de 15 minutos si Oracle expira antes

---

### 4.6 El calendario de fechas no selecciona el día correcto

**Síntoma:**  
El script exporta siempre el mismo día o salta fechas.

**Causa:**  
El selector XPath del día puede coincidir con un día de un mes diferente cuando el calendario muestra dos meses.

**Solución:**  
Usar el `aria-label` completo del día para evitar ambigüedad:
```python
f"//a[@role='checkbox'][contains(@aria-label, '{day} {target_month} {target_year}')]"
```

---

## 5. Fallas de la Base de Datos

### 5.1 La tabla `maximo` no tiene datos recientes

**Síntoma:**  
Las OTs del dashboard son antiguas o la fecha de actualización no corresponde al día actual.

**Causa:**  
El proceso ETL que sincroniza Maximo con la BD de contingencia no se ejecutó.

**Solución:**  
Contactar al equipo de integración/ETL para verificar el proceso de sincronización de Maximo. Este proyecto no controla ese proceso — solo consume los datos.

---

### 5.2 El JOIN con `oym_fijo` multiplica registros (duplicados)

**Síntoma:**  
El endpoint `/api/ordenes` devuelve más OTs de las que existen en `maximo`, o la misma OT aparece varias veces.

**Causa:**  
`oym_fijo` tiene múltiples registros para la misma `orden_de_trabajo` y el JOIN sin el subquery de `MAX(fin)` los multiplica.

**Diagnóstico:**  
```bash
python scripts/verificacion/verificar_oym_duplicados.py
```

**Solución:**  
Verificar que el query en `main.py` usa el subquery de deduplicación:
```sql
AND o.fin = (
    SELECT MAX(o2.fin) FROM oym_fijo o2
    WHERE o2.orden_de_trabajo = m.orden_de_trabajo
)
```

---

### 5.3 Las fechas llegan como `None` o con formato incorrecto

**Síntoma:**  
Los campos `dias` y `horas` en el dashboard siempre muestran 0, o la fecha de creación aparece como `None`.

**Diagnóstico:**  
```bash
python scripts/verificacion/verificar_fechas.py
```

**Solución:**  
Si las fechas vienen como `datetime` de Python (no como string), el backend ya las convierte:
```python
if isinstance(valor, datetime):
    valor = valor.strftime('%Y-%m-%d %H:%M:%S')
```

Si vienen como `str` con formato diferente (ej: `DD/MM/YYYY`), actualizar el `strptime` en el cálculo de días:
```python
fecha_creacion = datetime.strptime(fecha_creacion_str, '%d/%m/%Y %H:%M:%S')
```

---

### 5.4 Columnas de SLA vacías en el dashboard

**Síntoma:**  
Los campos `estado_sla`, `sla_suscriptor`, etc. siempre vienen vacíos.

**Causa:**  
Las tablas WFM (`Region_Occidente`, `pymes`, `dth`) no tienen OTs que coincidan con las de `maximo`, posiblemente porque los archivos de Oracle no han sido cargados a la BD o son de un rango de fechas diferente.

**Diagnóstico:**  
```bash
python scripts/verificacion/verificar_sla_activo.py
```

---

## 6. Fallas de Datos / Lógica de Negocio

### 6.1 El `segmento` de muchas OTs aparece como `"Sin clasificar"`

**Síntoma:**  
La mayoría de OTs tienen `segmento = "Sin clasificar"` en lugar de "Residencial", "Empresas y Negocios", etc.

**Causa:**  
El campo `ruta_de_clasificacion` está vacío o nulo para esas OTs, o el primer nivel de la ruta no coincide con los patrones definidos.

**Diagnóstico:**  
```bash
python scripts/busqueda/check_segmento.py
```

**Solución:**  
Revisar la distribución que imprime el script y agregar los patrones que faltan en `calcular_segmento()` en `backend/main.py`. Por ejemplo:

```python
if 'NUEVO_SEGMENTO' in primer_nivel:
    return 'Nombre del segmento'
```

---

### 6.2 La `familia` siempre es `"Sin clasificar"`

**Síntoma:**  
Todas las OTs tienen `familia = "Sin clasificar"`.

**Causa:**  
La columna `ruta_de_clasificacion` no contiene los términos "DEGRADACION", "RECLAMACION", etc., o los términos están con ortografía diferente.

**Diagnóstico:**  
```bash
python scripts/busqueda/buscar_familia.py
```

**Solución:**  
Ejecutar el script para ver los valores reales en la BD y actualizar los patrones en `calcular_familia()`.

---

### 6.3 Los días calculados son negativos

**Síntoma:**  
La columna "Días" muestra valores negativos.

**Causa:**  
La fecha de creación de la OT en la BD tiene una zona horaria diferente a la del servidor donde corre el backend.

**Solución:**  
Usar fechas con zona horaria explícita:
```python
from datetime import timezone
diff = datetime.now(timezone.utc) - fecha_creacion.replace(tzinfo=timezone.utc)
```

---

## 7. Fallas de Entorno y Dependencias

### 7.1 `paramiko` incompatible con `sshtunnel`

**Síntoma:**  
Error como `TypeError: object NoneType can't be used in 'await' expression` o errores de handshake SSH.

**Causa:**  
`paramiko` versión 3.x no es totalmente compatible con `sshtunnel`. El `requirements.txt` ya restringe `paramiko<3.0`.

**Solución:**
```bash
pip install "paramiko<3.0" --force-reinstall
```

---

### 7.2 Versión de Python incompatible

**Síntoma:**  
Errores de sintaxis o de tipo al ejecutar scripts.

**Requisito mínimo:** Python 3.8+

**Verificar:**
```bash
python --version
```

Si la versión es menor a 3.8, instalar una versión compatible desde [python.org](https://www.python.org/downloads/).

---

### 7.3 Node.js / npm muy antiguo

**Síntoma:**  
`npm install` falla con errores de peer dependencies o sintaxis.

**Requisito mínimo:** Node.js 16+ / npm 8+

**Verificar:**
```bash
node --version
npm --version
```

**Solución:** Descargar la versión LTS desde [nodejs.org](https://nodejs.org/).

---

### 7.4 `pip install` instala en el Python equivocado

**Síntoma:**  
Se instalan las dependencias sin error pero al correr el script sigue diciendo `ModuleNotFoundError`.

**Causa:**  
Hay múltiples versiones de Python instaladas y el `pip` y el `python` no apuntan al mismo intérprete.

**Solución:**
```bash
# Usar siempre el mismo intérprete
python -m pip install -r requirements.txt
python main.py
```

O usar un entorno virtual:
```bash
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
python main.py
```

---

## Checklist de Diagnóstico Rápido

Cuando algo no funciona, seguir este orden:

```
1. ¿El backend responde?       → http://localhost:8000/
2. ¿La BD es accesible?        → python scripts/verificacion/verificar_bd.py
3. ¿Los datos existen?         → python scripts/exploracion/explorar_bd.py
4. ¿Backend y frontend alinean?→ python scripts/verificacion/verificar_alineacion.py
5. ¿Error de CORS?             → Abrir F12 en el navegador y revisar consola
6. ¿Error de módulo?           → pip install -r requirements.txt
```
