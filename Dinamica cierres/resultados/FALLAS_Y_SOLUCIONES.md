# 🛠️ Fallas Frecuentes y Soluciones — Proyecto Dinámica Cierres

> Documento de referencia para el mantenimiento del sistema de informes diarios Android TV y Cierres.  
> Aplica a los scripts: `cierres_android_tv.py`, `cierres_corregido.py`, `macros.py` y `vba_code.bas`.

---

## Índice

1. [Fallas de Conexión SSH/MySQL](#1-fallas-de-conexión-sshmysql)
2. [Fallas de Conexión MySQL Directa](#2-fallas-de-conexión-mysql-directa)
3. [Sin Datos en el DataFrame](#3-sin-datos-en-el-dataframe)
4. [Errores al Construir el Pivote](#4-errores-al-construir-el-pivote)
5. [Errores al Generar el Archivo Excel](#5-errores-al-generar-el-archivo-excel)
6. [Errores de Hipervínculos entre Hojas](#6-errores-de-hipervínculos-entre-hojas)
7. [Fallas en la Integración VBA ↔ Python (xlwings)](#7-fallas-en-la-integración-vba--python-xlwings)
8. [Errores de Columnas Faltantes o Mal Nombradas](#8-errores-de-columnas-faltantes-o-mal-nombradas)
9. [Errores de Encoding / Caracteres Especiales](#9-errores-de-encoding--caracteres-especiales)
10. [Fallas en el Entorno Virtual (venv)](#10-fallas-en-el-entorno-virtual-venv)
11. [Fallas de Dependencias / Paquetes](#11-fallas-de-dependencias--paquetes)

---

## 1. Fallas de Conexión SSH/MySQL

**Aplica a:** `cierres_android_tv.py` → función `fetch_data()`

### 1.1 Timeout al abrir el túnel SSH

| Campo | Detalle |
|-------|---------|
| **Síntoma** | El script se cuelga o lanza `socket.timeout` / `paramiko.ssh_exception.NoValidConnectionsError` |
| **Causa** | El host SSH (`186.147.60.119`) no está disponible, la VPN no está activa, o el puerto 22 está bloqueado por firewall |
| **Solución** | 1. Verificar conectividad: `ping 186.147.60.119` en CMD. <br>2. Confirmar que la VPN corporativa está activa. <br>3. Probar manualmente: `ssh ccot@186.147.60.119`. <br>4. Si el firewall bloquea el puerto, solicitar apertura al área de infraestructura. |

### 1.2 Contraseña SSH rechazada

| Campo | Detalle |
|-------|---------|
| **Síntoma** | `paramiko.AuthenticationException: Authentication failed` |
| **Causa** | La contraseña en `SSH_PASSWORD` está vencida o fue cambiada |
| **Solución** | Actualizar la variable `SSH_PASSWORD` en `cierres_android_tv.py` con la nueva credencial. Considerar usar autenticación por llave SSH para evitar rotaciones frecuentes. |

### 1.3 Puerto MySQL remoto incorrecto

| Campo | Detalle |
|-------|---------|
| **Síntoma** | `Can't connect to MySQL server` una vez establecido el túnel |
| **Causa** | El `DB_PORT` (actualmente `3307`) no coincide con el puerto real de MySQL en el servidor remoto |
| **Solución** | Confirmar el puerto real con el DBA. Actualizar `DB_PORT` en el script. |

---

## 2. Fallas de Conexión MySQL Directa

**Aplica a:** `cierres_corregido.py` → función `fetch_data()`

### 2.1 Error de acceso denegado

| Campo | Detalle |
|-------|---------|
| **Síntoma** | `mysql.connector.errors.ProgrammingError: Access denied for user 'ccot'@...` |
| **Causa** | Credenciales incorrectas o el usuario no tiene permisos sobre la base `ccot` |
| **Solución** | Verificar `DB_CONFIG` (host, port, user, password, database). Solicitar al DBA que conceda permisos: `GRANT SELECT ON ccot.* TO 'ccot'@'%';` |

### 2.2 Host inalcanzable

| Campo | Detalle |
|-------|---------|
| **Síntoma** | `mysql.connector.errors.InterfaceError: 2003: Can't connect to MySQL server on '10.108.34.32'` |
| **Causa** | El servidor `10.108.34.32` no es accesible desde la red actual (requiere red interna o VPN) |
| **Solución** | Conectarse a la red interna o activar la VPN antes de ejecutar el script. |

---

## 3. Sin Datos en el DataFrame

**Aplica a:** `cierres_android_tv.py` y `cierres_corregido.py`

### 3.1 DataFrame vacío — no hay registros para hoy

| Campo | Detalle |
|-------|---------|
| **Síntoma** | Mensaje: `⚠️ No hay datos para hoy. Verifica que la tabla wf_dia esté actualizada.` El archivo Excel no se genera. |
| **Causa** | La consulta SQL filtra `Fecha >= CURDATE()` y no hay OT cargadas aún para la fecha actual |
| **Solución** | 1. Verificar directamente en la BD si ya existen registros para el día. <br>2. Ejecutar el script más tarde (luego de que los sistemas operativos carguen los datos). <br>3. Para pruebas, cambiar temporalmente el filtro de fecha a una fecha con datos conocidos. |

### 3.2 Columna de fecha con nulos tras `pd.to_datetime`

| Campo | Detalle |
|-------|---------|
| **Síntoma** | El DataFrame pierde filas inesperadamente después de `dropna(subset=[COL_FECHA])` |
| **Causa** | La columna `Fecha` o `FECHA_AGENDA` contiene cadenas en formato no reconocido (ej. `"15/07/2025"` en lugar de `"2025-07-15"`) |
| **Solución** | Agregar el parámetro `dayfirst=True` en `pd.to_datetime`: `pd.to_datetime(df[COL_FECHA], errors='coerce', dayfirst=True)` |

---

## 4. Errores al Construir el Pivote

**Aplica a:** funciones `build_pivot()` y `build_daily_pivot()`

### 4.1 Columna de agrupación no encontrada

| Campo | Detalle |
|-------|---------|
| **Síntoma** | `⚠️ Columna 'Compañia' no encontrada, saltando 'Resumen por Aliado'` |
| **Causa** | El nombre de la columna en la BD cambió o tiene espacios/tildes distintos a los definidos en las constantes `COL_*` |
| **Solución** | Ejecutar `print(df.columns.tolist())` tras la consulta para ver los nombres exactos. Actualizar las constantes `COL_ALIADO`, `COL_AREA`, etc. para que coincidan. |

### 4.2 Pivote genera solo una columna

| Campo | Detalle |
|-------|---------|
| **Síntoma** | El resumen muestra solo `Total general` sin columnas de fecha |
| **Causa** | Todos los registros tienen la misma fecha o la columna `FECHA_DATE` no se creó correctamente |
| **Solución** | Verificar que `df['FECHA_DATE'] = df[COL_FECHA].dt.date` se ejecuta después de `pd.to_datetime`. Revisar que los datos tienen fechas distintas. |

---

## 5. Errores al Generar el Archivo Excel

**Aplica a:** función `main()` en ambos scripts

### 5.1 Archivo bloqueado por Excel

| Campo | Detalle |
|-------|---------|
| **Síntoma** | `PermissionError: [Errno 13] Permission denied: 'Informe_AndroidTV_Diario.xlsx'` |
| **Causa** | El archivo `Informe_AndroidTV_Diario.xlsx` está abierto en Excel al momento de ejecutar el script |
| **Solución** | Cerrar el archivo en Excel antes de ejecutar el script, o cambiar `OUTPUT_XLSX` a un nombre temporal y luego renombrar. |

### 5.2 Nombre de hoja inválido o duplicado

| Campo | Detalle |
|-------|---------|
| **Síntoma** | `openpyxl.utils.exceptions.InvalidFileException` o hoja no encontrada al navegar hipervínculos |
| **Causa** | Los nombres de hojas de detalle superan 31 caracteres o contienen caracteres especiales no limpiados por `_safe_sheet_name()` |
| **Solución** | La función `_safe_sheet_name()` ya aplica un `[:31]` y limpia `[:\\/?*\[\]]`. Si persiste, agregar limpieza de tildes: `import unicodedata; name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()` antes del `re.sub`. |

### 5.3 Demasiadas hojas generadas (lentitud o crash)

| Campo | Detalle |
|-------|---------|
| **Síntoma** | El script tarda varios minutos o termina con `MemoryError` |
| **Causa** | El `detail_registry` acumula cientos de hojas cuando hay muchos aliados/ciudades con datos en múltiples fechas |
| **Solución** | Limitar el número de hojas de detalle. Por ejemplo, generar detalle solo cuando el conteo supera un umbral: `if val >= 3:` en lugar de `if val > 0:`. |

---

## 6. Errores de Hipervínculos entre Hojas

### 6.1 Hipervínculo lleva a hoja equivocada o da error

| Campo | Detalle |
|-------|---------|
| **Síntoma** | Al hacer clic en un número, Excel muestra _"La referencia no es válida"_ |
| **Causa** | La hoja de detalle registrada en `detail_registry` no coincide exactamente con el nombre de hoja creado (diferencia de espacios, mayúsculas o truncado) |
| **Solución** | Asegurarse de que `sname` se genera con la misma lógica tanto al crear el hipervínculo como al crear la hoja. Usar una función central `_safe_sheet_name()` en ambos puntos. |

### 6.2 Botón "⬅ MENÚ" no regresa al inicio

| Campo | Detalle |
|-------|---------|
| **Síntoma** | El hipervínculo del botón MENÚ no navega o da error |
| **Causa** | El nombre de la hoja del menú tiene tilde: `'MENÚ GERENCIAL'` y en algunos sistemas Excel no la reconoce correctamente |
| **Solución** | Verificar que la hoja se llama exactamente `MENÚ GERENCIAL`. En caso de problemas, renombrar a `MENU GERENCIAL` (sin tilde) y actualizar todas las referencias `hyperlink` en el código. |

---

## 7. Fallas en la Integración VBA ↔ Python (xlwings)

**Aplica a:** `vba_code.bas` y `macros.py`

### 7.1 `xlwings.RunPython` no encontrado en VBA

| Campo | Detalle |
|-------|---------|
| **Síntoma** | Excel muestra _"Sub or Function not defined"_ al ejecutar la macro |
| **Causa** | El complemento xlwings no está instalado o habilitado en Excel |
| **Solución** | 1. En CMD (con venv activo): `xlwings addin install`. <br>2. Reiniciar Excel. <br>3. Verificar en Excel → Archivo → Opciones → Complementos que `xlwings` aparece activo. |

### 7.2 Python no encontrado por xlwings

| Campo | Detalle |
|-------|---------|
| **Síntoma** | Mensaje: _"The Python executable cannot be found"_ al ejecutar desde Excel |
| **Causa** | xlwings no sabe dónde está el intérprete Python del entorno virtual |
| **Solución** | En el archivo `xlwings.conf` (o en Excel → xlwings → Settings), configurar el campo **Interpreter** con la ruta absoluta al Python del venv: `d:\...\Dinamica cierres\venv\Scripts\python.exe` |

### 7.3 Error al importar `cierres_android_tv` desde `macros.py`

| Campo | Detalle |
|-------|---------|
| **Síntoma** | `ModuleNotFoundError: No module named 'cierres_android_tv'` |
| **Causa** | xlwings ejecuta `macros.py` desde un directorio diferente al proyecto |
| **Solución** | El `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))` ya está implementado en `macros.py`. Si falla igualmente, configurar el **PYTHONPATH** en `xlwings.conf` apuntando al directorio del proyecto. |

### 7.4 Macro VBA detecta doble clic pero no ejecuta Python

| Campo | Detalle |
|-------|---------|
| **Síntoma** | La macro entra al `ErrorHandler` con el mensaje _"Error ejecutando Python"_ |
| **Causa** | El método `xlwings.RunPython` retorna un string de error de Python no capturado |
| **Solución** | Ejecutar el script directamente desde CMD para aislar el error: `python macros.py`. Revisar el mensaje detallado antes de volver a Excel. |

---

## 8. Errores de Columnas Faltantes o Mal Nombradas

### 8.1 `KeyError` al acceder a columna del DataFrame

| Campo | Detalle |
|-------|---------|
| **Síntoma** | `KeyError: 'Tipo de Actividad'` (u otro nombre de columna) |
| **Causa** | La tabla `wf_dia` o `back_informe` cambió sus nombres de columna, o hay espacios invisibles al inicio/fin |
| **Solución** | Ejecutar `print(df.columns.tolist())` justo después de `fetch_data()` para inspeccionar los nombres exactos. Actualizar las constantes `COL_*` al inicio de cada script. |

### 8.2 Columna `FECHA_FORMATEADA` faltante en el pivote

| Campo | Detalle |
|-------|---------|
| **Síntoma** | `KeyError: 'FECHA_FORMATEADA'` dentro de `build_pivot()` |
| **Causa** | La función `prepare_data()` no fue llamada antes del pivote, o el DataFrame se pasó sin procesar |
| **Solución** | Asegurarse de llamar `df = prepare_data(df_raw)` antes de cualquier llamada a `build_pivot()`. |

---

## 9. Errores de Encoding / Caracteres Especiales

### 9.1 Nombres con tildes o ñ rompen el nombre de hojas

| Campo | Detalle |
|-------|---------|
| **Síntoma** | Hoja creada con nombre truncado o caracteres extraños; hipervínculo no funciona |
| **Causa** | Los valores de aliado o ciudad contienen tildes (ej. `"BOGOTÁ"`) que aumentan el largo en bytes pero no en la validación de 31 chars de Excel |
| **Solución** | Normalizar el nombre antes de truncar: ```python import unicodedata def _safe_sheet_name(raw): clean = unicodedata.normalize('NFKD', str(raw)).encode('ascii', 'ignore').decode() return re.sub(r'[:\\/?*\[\]]', '_', clean)[:31] ``` |

### 9.2 Datos con caracteres extraños al leer de MySQL

| Campo | Detalle |
|-------|---------|
| **Síntoma** | Los valores de texto aparecen con `â€™` o `Ã©` en el Excel |
| **Causa** | El charset de la conexión MySQL no coincide con `utf8mb4` |
| **Solución** | Verificar que el parámetro `charset='utf8mb4'` está presente en la conexión `pymysql.connect()` y en `mysql.connector.connect()`. En el servidor MySQL, ejecutar: `SHOW VARIABLES LIKE 'character_set%';` |

---

## 10. Fallas en el Entorno Virtual (venv)

### 10.1 El script no encuentra los paquetes instalados

| Campo | Detalle |
|-------|---------|
| **Síntoma** | `ModuleNotFoundError: No module named 'sshtunnel'` (u otro módulo) al ejecutar desde CMD |
| **Causa** | El entorno virtual no está activado y se está usando el Python del sistema que no tiene las dependencias |
| **Solución** | Activar el venv antes de ejecutar: ```cmd d: cd "d:\OneDrive - Comunicacion Celular S.A.- Comcel S.A\Escritorio\Dinamica cierres" venv\Scripts\activate python cierres_android_tv.py ``` |

### 10.2 El venv se creó con una versión de Python incompatible

| Campo | Detalle |
|-------|---------|
| **Síntoma** | Errores de importación raros o mensajes como `RuntimeError: Python version mismatch` |
| **Causa** | El venv fue creado con Python 3.x pero en el sistema hay otra versión activa |
| **Solución** | Recrear el venv con la versión correcta: ```cmd python --version   ← verificar versión python -m venv venv venv\Scripts\activate pip install -r requirements.txt ``` |

---

## 11. Fallas de Dependencias / Paquetes

### 11.1 Versiones de `openpyxl` incompatibles

| Campo | Detalle |
|-------|---------|
| **Síntoma** | `AttributeError: 'Worksheet' object has no attribute 'sheet_view'` o similar |
| **Causa** | La versión instalada de `openpyxl` es anterior a la requerida (`3.1.5` según `requirements.txt`) |
| **Solución** | ```cmd pip install openpyxl==3.1.5 ``` |

### 11.2 `sshtunnel` no instalado

| Campo | Detalle |
|-------|---------|
| **Síntoma** | `ModuleNotFoundError: No module named 'sshtunnel'` |
| **Causa** | El paquete `sshtunnel` no aparece en `requirements.txt` pero es importado en `cierres_android_tv.py` |
| **Solución** | Instalar manualmente: ```cmd pip install sshtunnel ``` Y agregarlo a `requirements.txt`: ``` sshtunnel==0.4.0 ``` |

### 11.3 Conflicto entre `PyMySQL` y `mysql-connector-python`

| Campo | Detalle |
|-------|---------|
| **Síntoma** | Importaciones mixtas causan errores como `InterfaceError: Not connected` |
| **Causa** | `cierres_android_tv.py` usa `pymysql` y `cierres_corregido.py` usa `mysql-connector-python`. Son independientes pero no deben mezclarse en el mismo script |
| **Solución** | Mantener cada script con su propio conector. No mezclar `import pymysql` con `import mysql.connector` en el mismo archivo. |

---

## Tabla Resumen Rápido

| # | Categoría | Error más común | Solución rápida |
|---|-----------|----------------|-----------------|
| 1 | SSH | Timeout / Auth failed | Verificar VPN + credenciales SSH |
| 2 | MySQL directa | Access denied | Verificar `DB_CONFIG` |
| 3 | Datos vacíos | DataFrame vacío | Revisar filtro de fecha en SQL |
| 4 | Pivote | Columna no encontrada | `print(df.columns.tolist())` |
| 5 | Excel | PermissionError | Cerrar el archivo en Excel |
| 6 | Hipervínculos | Referencia no válida | Usar `_safe_sheet_name()` en ambos lados |
| 7 | xlwings/VBA | RunPython no definido | `xlwings addin install` |
| 8 | Columnas | KeyError | Actualizar constantes `COL_*` |
| 9 | Encoding | Caracteres extraños | `charset='utf8mb4'` en conexión |
| 10 | venv | ModuleNotFoundError | Activar venv antes de ejecutar |
| 11 | Paquetes | Versión incorrecta | `pip install -r requirements.txt` |

---

*Documento generado automáticamente — Proyecto Dinámica Cierres*  
*Última revisión: julio 2026*
