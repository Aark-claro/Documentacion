# 🚀 Panel de Órdenes de Trabajo - Instrucciones de Instalación

## 📁 Estructura del Proyecto

```
Bot work/
├── backend/              # Backend FastAPI
│   ├── main.py          # API principal
│   └── requirements.txt # Dependencias Python
│
└── frontend/            # Frontend React + Vite
    ├── src/
    │   ├── App.jsx      # Componente principal
    │   └── App.css      # Estilos
    └── package.json
```

---

## ⚙️ Instalación y Ejecución

### **1. Backend (FastAPI)**

#### Instalar dependencias:

```bash
cd backend
pip install -r requirements.txt
```

#### Ejecutar el servidor:

```bash
python main.py
```

✅ **El backend estará corriendo en:** `http://localhost:8000`

#### Endpoints disponibles:

- `GET http://localhost:8000/` - Info de la API
- `GET http://localhost:8000/api/ordenes` - Todas las órdenes
- `GET http://localhost:8000/api/ordenes?estado=ASIGNADO` - Filtrar por estado
- `GET http://localhost:8000/api/ordenes?prioridad=Alto` - Filtrar por prioridad
- `GET http://localhost:8000/api/ordenes/{id}` - Orden específica por ID

**Documentación automática:** `http://localhost:8000/docs`

---

### **2. Frontend (React + Vite)**

El frontend ya fue creado con Vite. Si necesitas instalarlo de nuevo:

```bash
cd frontend
npm install
```

#### Ejecutar el servidor de desarrollo:

```bash
npm run dev
```

✅ **El frontend estará corriendo en:** `http://localhost:5173`

---

## 🎯 Uso del Sistema

### **1. Iniciar Backend:**

```bash
# Terminal 1
cd backend
python main.py
```

### **2. Iniciar Frontend:**

```bash
# Terminal 2
cd frontend
npm run dev
```

### **3. Abrir en el navegador:**

Ir a: `http://localhost:5173`

---

## 🔍 Características del Panel

### **KPIs en el Dashboard:**

- ✅ Total de órdenes
- ✅ Órdenes de alta prioridad
- ✅ Órdenes en progreso
- ✅ Días promedio desde creación

### **Filtros disponibles:**

- 🔹 **Estado:** Asignado, Iniciado, En espera, Suspendido
- 🔹 **Prioridad:** Alto, Medio, Bajo
- 🔹 **Aliado:** CONECTAR, CICSA, ATP
- 🔹 **Departamento:** Valle del Cauca, Tolima, Huila, etc.

### **Tabla de órdenes:**

Muestra todas las órdenes con:
- Número de OT
- Descripción
- Prioridad (con colores)
- Estado
- Aliado responsable
- Ciudad
- Clasificación
- Días desde creación (con colores según urgencia)
- Fecha de creación

### **Colores de prioridad:**

- 🔴 **Alto** - Rojo
- 🟠 **Medio** - Naranja
- 🟢 **Bajo** - Verde

### **Colores de antigüedad:**

- 🟢 **0-1 días** - Verde (Reciente)
- 🟡 **2-3 días** - Amarillo (En proceso)
- 🟠 **4-7 días** - Naranja (Atrasada)
- 🔴 **>7 días** - Rojo (Crítica)

---

## 🛠️ Personalización

### **Cambiar puerto del backend:**

En `backend/main.py`, línea final:

```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Cambiar 8000 por el puerto deseado
```

### **Cambiar URL del backend en el frontend:**

En `frontend/src/App.jsx`, línea 3:

```javascript
const API_URL = 'http://localhost:8000/api'  // Cambiar URL si es necesario
```

### **Agregar más filtros:**

1. En el backend (`main.py`), agregar parámetro en la función `get_ordenes()`
2. En el frontend (`App.jsx`), agregar select en la sección de filtros

---

## 📊 Ejemplo de Uso

### **Consultar todas las órdenes:**

```bash
curl http://localhost:8000/api/ordenes
```

### **Filtrar por estado y prioridad:**

```bash
curl "http://localhost:8000/api/ordenes?estado=ASIGNADO&prioridad=Alto"
```

### **Obtener una orden específica:**

```bash
curl http://localhost:8000/api/ordenes/93
```

---

## ❗ Solución de Problemas

### **Error de conexión a la BD:**

Verificar que:
- ✅ Las credenciales SSH y MySQL sean correctas
- ✅ El servidor SSH esté accesible
- ✅ El puerto 3307 esté abierto

### **CORS Error en el frontend:**

El backend ya tiene CORS habilitado para todos los orígenes. Si necesitas restringirlo:

```python
# En backend/main.py
allow_origins=["http://localhost:5173"]  # Solo permitir el frontend
```

### **Frontend no carga datos:**

1. Verificar que el backend esté corriendo en `http://localhost:8000`
2. Abrir consola del navegador (F12) y revisar errores
3. Verificar que la URL de la API en `App.jsx` sea correcta

---

## 🔒 Seguridad

⚠️ **IMPORTANTE:** Este código es para desarrollo. Para producción:

1. ✅ Usar variables de entorno para credenciales (`.env`)
2. ✅ Restringir CORS a dominios específicos
3. ✅ Agregar autenticación (JWT)
4. ✅ Usar HTTPS
5. ✅ Validar y sanitizar entradas

---

## 📦 Dependencias

### Backend:
- FastAPI
- Uvicorn
- sshtunnel
- paramiko
- mysql-connector-python
- pydantic

### Frontend:
- React 18
- Vite
- CSS vanilla (sin librerías adicionales)

---

## 🎉 ¡Listo!

Ahora tienes:
- ✅ Backend que consulta la BD y expone una API REST
- ✅ Frontend que consume la API y pinta los datos
- ✅ Filtros funcionales
- ✅ KPIs calculados
- ✅ Tabla responsive con colores según prioridad y antigüedad

**¡Disfruta tu panel! 🚀**
