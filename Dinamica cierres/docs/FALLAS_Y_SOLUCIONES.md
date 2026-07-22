# 🛠️ Guía de Fallas y Soluciones — Dinámica de Cierres Android TV

> Proyecto: Informe Diario de Instalaciones Android TV — Región Occidente  
> Archivos principales: `cierres_android_tv.py`, `cierres_corregido.py`, `macros.py`, `vba_code.bas`

---

## Índice

1. [Fallas de Conexión SSH / MySQL](#1-fallas-de-conexión-ssh--mysql)
2. [Fallas de Datos Vacíos o Incorrectos](#2-fallas-de-datos-vacíos-o-incorrectos)
3. [Fallas al Generar el Archivo Excel](#3-fallas-al-generar-el-archivo-excel)
4. [Fallas de Dependencias / Entorno](#4-fallas-de-dependencias--entorno)
5. [Fallas de la Integración VBA + xlwings](#5-fallas-de-la-integración-vba--xlwings)
6. [Fallas de Nombres de Hojas en Excel](#6-fallas-de-nombres-de-hojas-en-excel)
7. [Fallas en Hipervínculos de Detalle](#7-fallas-en-hipervínculos-de-detalle)
8. [Fallas de Rendimiento](#8-fallas-de-rendimiento)

---

## 1. Fallas de Conexión SSH / MySQL

### ❌ Falla: `SSHException: Error reading SSH protocol banner`

**Causa:** El servidor SSH (`186.147.60.119`) no responde a tiempo, la VPN no está activa, o la red corporativa bloquea el puerto 22.

**Solución:**
1. Verificar que la VPN corporativa esté conectada antes de ejecutar el script.
2. Confirmar que el host y puerto SSH sean accesibles:
   ```cmd
   ping 186.147.60.119
   ```
3. Si el problema persiste, reiniciar la conexión VPN y volver a intentar.

---

### ❌ Falla: `AuthenticationException: Authentication failed`

**Causa:** Credenciales SSH incorrectas o caducadas (`SSH_USER`, `SSH_PASSWORD` en `cierres_android_tv.py`).

**Solución:**
1. Verificar las credenciales con el administrador de infraestructura.
2. Actualizar las variables en la sección de configuración del script:
   ```python
   SSH_USER     = 'ccot'
   SSH_PASSWORD = 'nueva_contraseña'
   ```

---

### ❌ Falla: `pymysql.err.OperationalError: (2003) Can't connect to MySQL server`

**Causa:** El túnel SSH se estableció pero el puerto de MySQL (`3307`) no está disponible en el servidor remoto, o la base de datos `otc_backlog` no existe.

**Solución:**
1. Confirmar con el DBA que el servicio MySQL está activo en el puerto `3307`.
2. Verificar que `DB_NAME = 'otc_backlog'` existe y tiene la tabla `wf_dia`.
3. Comprobar que el usuario `root` tiene permisos sobre esa base de datos.

---

### ❌ Falla: `mysql.connector.errors.InterfaceError` (en `cierres_corregido.py`)

**Causa:** `mysql-connector-python` no puede alcanzar el host `10.108.34.32:33063` (acceso directo sin túnel SSH).

**Solución:**
1. Verificar que la IP `10.108.34.32` sea accesible desde la red actual.
2. Asegurarse de que la VPN otorgue acceso a ese segmento de red.
3. Confirmar usuario y contraseña (`ccot` / `ccot`) con el administrador de BD.

---

## 2. Fallas de Datos Vacíos o Incorrectos

### ❌ Falla: `⚠️ No hay datos para hoy`

**Causa:** La consulta SQL no retorna filas porque:
- La tabla `wf_dia` aún no fue cargada con los datos del día.
- El campo `INSTALACION ANDROID TV` no tiene el valor exacto `'si'` (diferencia de mayúsculas o espacios).
- El campo `Origen` no contiene `'REGION OCCIDENTE'` exacto.

**Solución:**
1. Ejecutar la consulta directamente en la BD para validar:
   ```sql
   SELECT COUNT(*) FROM wf_dia
   WHERE `INSTALACION ANDROID TV` = 'si'
     AND Origen = 'REGION OCCIDENTE'
     AND Fecha >= CURDATE();
   ```
2. Si hay datos pero con variación en el texto, ajustar el filtro en `SQL_QUERY`:
   ```python
   AND LOWER(TRIM(`INSTALACION ANDROID TV`)) = 'si'
   ```
3. Ejecutar el script después de que el proceso ETL de la BD haya cargado los datos del día (normalmente después de las 8:00 a.m.).

---

### ❌ Falla: Columna esperada no encontrada (`KeyError` o `⚠️ Columna 'X' no encontrada`)

**Causa:** El nombre de la columna en la BD cambió o tiene espacios/tildes distintos a los definidos en las constantes `COL_*`.

**Solución:**
1. Imprimir las columnas del DataFrame para verificar los nombres reales:
   ```python
   df = fetch_data()
   print(df.columns.tolist())
   ```
2. Actualizar las constantes en el script según corresponda:
   ```python
   COL_TIPO_TRABAJO = "Tipo de Actividad"   # Verificar nombre exacto
   COL_ALIADO       = "Compañia"
   COL_AREA         = "Ciudad"
   ```

---

### ❌ Falla: `NaT` o fechas en blanco en los pivotes

**Causa:** Registros con `Fecha` nula en la BD. El script los elimina con `dropna`, pero si la mayoría son nulos el informe queda vacío.

**Solución:**
1. Verificar la calidad de los datos de fecha en la BD:
   ```sql
   SELECT COUNT(*) FROM wf_dia WHERE Fecha IS NULL;
   ```
2. Si el problema es recurrente, notificar al equipo de datos para corregir el proceso de carga.

---

## 3. Fallas al Generar el Archivo Excel

### ❌ Falla: `PermissionError: [Errno 13] Permission denied: 'Informe_AndroidTV_Diario.xlsx'`

**Causa:** El archivo Excel de salida ya está abierto en Excel al momento de ejecutar el script.

**Solución:**
1. Cerrar el archivo `Informe_AndroidTV_Diario.xlsx` en Excel antes de ejecutar el script.
2. Si se ejecuta de forma programada (tarea programada), asegurarse de que nadie tenga el archivo abierto en ese horario.

---

### ❌ Falla: `openpyxl.utils.exceptions.InvalidFileException`

**Causa:** El archivo `.xlsx` existente está corrupto o fue guardado en formato `.xls` antiguo.

**Solución:**
1. Eliminar el archivo existente y volver a ejecutar el script para que lo genere desde cero.
2. No renombrar archivos `.xls` a `.xlsx` manualmente; siempre generarlos con openpyxl.

---

### ❌ Falla: Hoja de detalle no creada / hipervínculo roto

**Causa:** El nombre de la hoja de detalle supera los 31 caracteres permitidos por Excel, o contiene caracteres inválidos (`\ / ? * [ ] :`).

**Solución:**
La función `_safe_sheet_name` en `cierres_android_tv.py` ya maneja esto, pero si aparece el error revisar que la función esté siendo llamada en todos los puntos de creación de hojas:
```python
def _safe_sheet_name(raw: str) -> str:
    return re.sub(r'[:\\/?*\[\]]', '_', raw)[:31]
```
Si el nombre sigue fallando, reducir los prefijos (`str(item)[:8]` → `str(item)[:5]`).

---

### ❌ Falla: `ValueError: Sheet 'X' already exists`

**Causa:** Se intenta crear una hoja con un nombre que ya existe en el workbook, sin eliminarla previamente.

**Solución:**
El script ya incluye verificaciones del tipo:
```python
if sheet_name in wb.sheetnames:
    del wb[sheet_name]
```
Si el error aparece, verificar que todos los bloques de creación de hojas incluyan esa validación.

---

## 4. Fallas de Dependencias / Entorno

### ❌ Falla: `ModuleNotFoundError: No module named 'sshtunnel'`

**Causa:** El paquete `sshtunnel` no está instalado en el entorno virtual activo.

**Solución:**
```cmd
cd "d:\OneDrive - Comunicacion Celular S.A.- Comcel S.A\Escritorio\Dinamica cierres"
venv\Scripts\activate
pip install sshtunnel
```
O reinstalar todas las dependencias:
```cmd
pip install -r requirements.txt
```

---

### ❌ Falla: `ModuleNotFoundError: No module named 'pymysql'` o `mysql.connector`

**Causa:** Los drivers de MySQL no están instalados.

**Solución:**
```cmd
pip install PyMySQL mysql-connector-python
```
Nota: `cierres_android_tv.py` usa `pymysql` y `cierres_corregido.py` usa `mysql-connector-python`. Ambos deben estar instalados según el script que se ejecute.

---

### ❌ Falla: `ImportError: DLL load failed` (en Windows)

**Causa:** Conflicto entre versiones de librerías C/C++ nativas (común con `numpy`, `pandas` o `pymysql` en entornos Windows).

**Solución:**
1. Recrear el entorno virtual:
   ```cmd
   rmdir /s /q venv
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Asegurarse de usar la misma arquitectura de Python (32-bit vs 64-bit) que las librerías instaladas.

---

### ❌ Falla: Versión de Python incompatible

**Causa:** El proyecto requiere Python 3.8+ por el uso de f-strings avanzados, `pandas 2.x` y `openpyxl 3.x`.

**Solución:**
Verificar la versión activa:
```cmd
python --version
```
Si es inferior a 3.8, instalar Python 3.10 o 3.11 desde [python.org](https://www.python.org/downloads/).

---

## 5. Fallas de la Integración VBA + xlwings

### ❌ Falla: `Error ejecutando Python: xlwings no está disponible`

**Causa:** `xlwings` no está instalado o el archivo Excel no tiene la referencia al complemento xlwings (`xlwings.xlam`).

**Solución:**
1. Instalar xlwings:
   ```cmd
   pip install xlwings
   xlwings addin install
   ```
2. En Excel, ir a **Archivo → Opciones → Complementos → Complementos de Excel** y activar `xlwings`.

---

### ❌ Falla: `RunPython` no ejecuta el script correcto

**Causa:** El VBA llama funciones que no existen en `macros.py` (ej. `export_detalle`), o la ruta del intérprete de Python en xlwings no apunta al entorno virtual del proyecto.

**Solución:**
1. Verificar en `macros.py` que las funciones llamadas desde VBA estén definidas.
2. En Excel, ir a la hoja `xlwings.conf` o configurar la ruta del intérprete:
   - `INTERPRETER_WIN` → `d:\...\Dinamica cierres\venv\Scripts\pythonw.exe`
3. Ajustar el código VBA para llamar la función correcta:
   ```vb
   result = xlwings.RunPython("from macros import actualizar_datos; actualizar_datos()")
   ```

---

### ❌ Falla: El doble clic en Excel no dispara la macro

**Causa:** El código VBA en `vba_code.bas` está en `Module1`, pero el evento `Worksheet_BeforeDoubleClick` debe estar en el módulo de la hoja específica (`Sheet1`, `Visión Diaria`, etc.), no en un módulo estándar.

**Solución:**
1. En el editor VBA (`Alt + F11`), abrir el módulo de la hoja donde se quiere el doble clic.
2. Pegar el código del evento `Worksheet_BeforeDoubleClick` directamente en ese módulo de hoja.
3. Dejar en `Module1` únicamente las subrutinas auxiliares (`ProcessMacroComment`, `RunPythonExport`, etc.).

---

## 6. Fallas de Nombres de Hojas en Excel

### ❌ Falla: Hoja con nombre truncado o con `_` inesperados

**Causa:** Los nombres de hojas de detalle se generan concatenando el prefijo (`Det_VD_`, `Det_Al_`, etc.) con el nombre del item y la fecha. Si el item contiene caracteres especiales, la función `_safe_sheet_name` los reemplaza por `_`.

**Diagnóstico:** Si el hipervínculo lleva a una hoja inexistente, el nombre esperado difiere del generado.

**Solución:**
Agregar un print de diagnóstico temporal al generar las hojas:
```python
print(f"Creando hoja de detalle: '{sname}'")
```
Esto permite comparar el nombre del hipervínculo con el nombre real de la hoja.

---

### ❌ Falla: Hoja `_Datos` visible en el archivo final

**Causa:** La línea que oculta la hoja de datos crudos no se ejecuta si el proceso termina con error antes de llegar a ese punto.

**Solución:**
Verificar que en `main()` la línea de ocultación esté presente y no comentada:
```python
wb['_Datos'].sheet_state = 'hidden'
```

---

## 7. Fallas en Hipervínculos de Detalle

### ❌ Falla: Hipervínculo lleva a hoja incorrecta o inexistente

**Causa:** Se registran hojas de detalle duplicadas en `detail_registry` con el mismo nombre pero diferentes filtros, y el `set seen` descarta los duplicados sin crear la hoja.

**Solución:**
Asegurarse de que cada combinación `(item, fecha, index_col)` genere un nombre de hoja único. Si hay colisiones, agregar un sufijo numérico:
```python
base = _safe_sheet_name(f"Det_{prefix}_{str(item)[:8]}_{...}")
sname = base
counter = 1
while sname in seen:
    sname = f"{base[:28]}_{counter}"
    counter += 1
```

---

### ❌ Falla: Hipervínculos no funcionan al abrir el archivo en otro equipo

**Causa:** Los hipervínculos internos usan la sintaxis `#'Nombre hoja'!A1`. Si el nombre de la hoja tiene caracteres especiales o el archivo se guarda con una codificación diferente, Excel puede no resolverlos.

**Solución:**
1. Verificar que los nombres de hojas no contengan tildes ni caracteres especiales.
2. Guardar el archivo siempre como `.xlsx` (no `.xlsm` ni `.xls`).
3. Al compartir el archivo, asegurarse de que el destinatario lo abra con Excel (no con LibreOffice u otro visor).

---

## 8. Fallas de Rendimiento

### ❌ Falla: El script tarda demasiado o se congela

**Causa posible A:** La consulta SQL retorna miles de filas sin filtro de fecha eficiente.  
**Causa posible B:** Se generan cientos de hojas de detalle, lo que ralentiza `openpyxl`.  
**Causa posible C:** El cálculo de anchos automáticos de columna (`iter_cols`) en hojas con muchas filas es lento.

**Solución A:** Asegurarse de que la columna `Fecha` en la BD tenga índice. Agregar `LIMIT` en desarrollo para pruebas.

**Solución B:** Limitar la cantidad de hojas de detalle generadas. Considerar generarlas bajo demanda (solo cuando el usuario hace clic) en lugar de generar todas al inicio.

**Solución C:** Reemplazar el cálculo dinámico de anchos por valores fijos para columnas conocidas:
```python
# En lugar de iterar todas las celdas, usar ancho fijo
ws.column_dimensions['A'].width = 30
ws.column_dimensions['B'].width = 20
```

---

### ❌ Falla: `MemoryError` al procesar DataFrames grandes

**Causa:** El DataFrame original se copia múltiples veces en `prepare_data` y en cada llamada a `create_summary_sheet`.

**Solución:**
1. Usar `df.copy()` solo donde sea estrictamente necesario.
2. Liberar DataFrames intermedios con `del df_tmp` después de usarlos.
3. En producción, filtrar la consulta SQL para traer solo las columnas necesarias (evitar `SELECT *`):
   ```sql
   SELECT Fecha, `Tipo de Actividad`, Compañia, Ciudad, `Tipo de Red`, Estado
   FROM wf_dia
   WHERE ...
   ```

---

## Tabla de Referencia Rápida

| # | Error / Síntoma | Archivo | Sección |
|---|---|---|---|
| 1 | No conecta SSH | `cierres_android_tv.py` | `fetch_data()` |
| 2 | No hay datos hoy | `cierres_android_tv.py` | `main()` |
| 3 | PermissionError Excel | `cierres_android_tv.py` | `main()` |
| 4 | ModuleNotFoundError | `requirements.txt` / `venv` | Instalación |
| 5 | Macro VBA no ejecuta | `vba_code.bas` / `macros.py` | xlwings config |
| 6 | Hoja duplicada / rota | `cierres_android_tv.py` | `create_summary_sheet()` |
| 7 | Hipervínculo roto | `cierres_android_tv.py` | `_safe_sheet_name()` |
| 8 | Script lento / colgado | Ambos `.py` | Optimización SQL/Excel |

---

*Documento generado: Julio 2026 — Dinámica Cierres / Región Occidente*
