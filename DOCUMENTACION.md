# Documentación Técnica - Image Decomposer

## Índice

1. [Visión General](#visión-general)
2. [Tecnologías y Arquitectura](#tecnologías-y-arquitectura)
3. [config.py - Configuración](#configpy---configuración)
4. [database.py - Capa de Datos](#databasepy---capa-de-datos)
5. [image_processor.py - Procesamiento de Imágenes](#image_processorpy---procesamiento-de-imágenes)
6. [gui_upload.py - Interfaz de Carga](#gui_uploadpy---interfaz-de-carga)
7. [gui_viewer.py - Interfaz de Visualización](#gui_viewerpy---interfaz-de-visualización)
8. [main.py - Punto de Entrada](#mainpy---punto-de-entrada)
9. [Conceptos Avanzados de OpenCV](#conceptos-avanzados-de-opencv)

---

## Visión General

**Image Decomposer** es una aplicación de escritorio que permite:
- Capturar imágenes desde la cámara web con OpenCV
- Descomponer imágenes en sus valores RGB individuales
- Almacenar estos valores en una base de datos en la nube (Supabase)
- Reconstruir imágenes desde sus valores RGB almacenados

El proyecto utiliza **OpenCV (cv2)** como biblioteca principal de procesamiento de imágenes, siguiendo las técnicas enseñadas en el curso de procesamiento digital de imágenes.

### Separación de Responsabilidades

El proyecto sigue el patrón de **separación de responsabilidades** y arquitectura modular:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   config    │────▶│  database   │────▶│  Supabase   │
└─────────────┘     └─────────────┘     │  (Cloud DB) │
                          ▲              └─────────────┘
                          │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  gui_upload │────▶│   image     │────▶│   OpenCV    │
│  gui_viewer │     │  processor  │     │  + NumPy    │
└─────────────┘     └─────────────┘     └─────────────┘
        ▲                   │
        │                   ▼
┌─────────────┐     ┌─────────────┐
│    main     │     │     PIL     │ (solo para Tkinter)
│  (Tkinter)  │     │  (ImageTk)  │
└─────────────┘     └─────────────┘
```

### Flujo de Datos

**Captura de Imagen:**
```
Cámara → cv2.VideoCapture(0) → Frame BGR → cvtColor(BGR→RGB) → Array NumPy RGB → Flatten → String → Supabase
```

**Reconstrucción:**
```
Supabase → String → Array NumPy → Reshape → Imagen RGB → PIL → Tkinter
```

---

## Tecnologías y Arquitectura

### Stack Tecnológico

| Tecnología | Propósito | Dónde se Usa |
|------------|-----------|--------------|
| **OpenCV (cv2)** | Lectura y procesamiento principal de imágenes | `image_processor.py` - Todas las operaciones de imagen |
| **NumPy** | Manipulación de matrices y arrays | `image_processor.py` - flatten, reshape, indexing |
| **PIL/Pillow** | Conversión de NumPy a formato Tkinter **únicamente** | GUIs - Solo para método `ImageTk.PhotoImage()` |
| **Tkinter** | Interfaz gráfica de usuario | `main.py`, `gui_upload.py`, `gui_viewer.py` |
| **Supabase** | Base de datos PostgreSQL en la nube | `database.py` |
| **python-dotenv** | Manejo de variables de entorno | `config.py` |

### ¿Por qué OpenCV y no PIL?

**OpenCV es superior para procesamiento digital de imágenes porque:**

1. **Formato de arrays NumPy nativo**: OpenCV trabaja directamente con arrays NumPy, mientras que PIL usa su propio formato Image
2. **BGR vs RGB**: OpenCV lee en BGR (estándar de visión por computadora), permitiendo control total
3. **Rendimiento**: OpenCV está optimizado en C/C++ para operaciones matriciales
4. **Funcionalidades avanzadas**: Filtros, transformaciones, detección, etc.

**PIL solo se usa para una cosa:**
```python
# OpenCV procesa la imagen
imagen_cv = cv2.imread("foto.jpg")  # Array NumPy
procesar_con_opencv(imagen_cv)

# PIL solo para mostrar en Tkinter (incompatibilidad)
img_pil = Image.fromarray(imagen_cv)
photo = ImageTk.PhotoImage(img_pil)  # Requerido por Tkinter
canvas.create_image(x, y, image=photo)
```

### Conceptos de OpenCV Utilizados

| Concepto | Descripción | Código |
|----------|-------------|--------|
| **Lectura BGR** | OpenCV lee imágenes en formato BGR por defecto | `cv2.imread(path)` |
| **Conversión BGR→RGB** | Convertir a RGB para visualización correcta | `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)` |
| **Shape** | Dimensiones del array: (alto, ancho, canales) | `imagen.shape` → `(480, 640, 3)` |
| **Indexing** | Acceso a píxeles y canales | `imagen[y, x, canal]` |
| **Slicing de canales** | Extraer canal individual | `r = imagen[:, :, 0]` |
| **dtype uint8** | Tipo de dato: enteros sin signo 0-255 | `imagen.dtype` → `uint8` |

---

## config.py - Configuración

### Propósito
Centraliza la configuración del proyecto, cargando las credenciales de Supabase desde variables de entorno.

### Imports

```python
import os
from dotenv import load_dotenv
```

| Import | Uso |
|--------|-----|
| `os` | Acceder a variables de entorno del sistema |
| `load_dotenv` | Cargar variables desde archivo `.env` |

### Sección 1: Carga de Variables

```python
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
```

**Explicación:**
- `load_dotenv()` lee el archivo `.env` y carga sus valores como variables de entorno
- `os.getenv("NOMBRE")` obtiene el valor de una variable de entorno
- Si la variable no existe, retorna `None`

### Sección 2: Validación

```python
def validate_config():
    ### Verifica que las credenciales de Supabase esten configuradas
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL no esta configurado en el archivo .env")
    if not SUPABASE_KEY:
        raise ValueError("SUPABASE_KEY no esta configurado en el archivo .env")
```

**Explicación:**
- Verifica que las variables no estén vacías (`not SUPABASE_URL`)
- `raise ValueError` lanza un error descriptivo si algo falla
- Se usa antes de conectar a Supabase para dar errores claros

---

## database.py - Capa de Datos

### Propósito
Maneja toda la comunicación con la base de datos Supabase. Aísla la lógica de persistencia del resto de la aplicación.

### Imports

```python
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY, validate_config
```

| Import | Uso |
|--------|-----|
| `create_client` | Función para crear conexión a Supabase |
| `config.*` | Credenciales y validación |

### Sección 1: Cliente Singleton

```python
cliente = None

def init_client():
    ### Inicializa y retorna el cliente de Supabase
    global cliente
    if cliente is None:
        validate_config()
        cliente = create_client(SUPABASE_URL, SUPABASE_KEY)
    return cliente
```

**Explicación:**
- `cliente` es una variable global
- **Patrón Singleton**: Solo se crea UNA conexión, sin importar cuántas veces se llame
- `global cliente` permite modificar la variable global dentro de la función
- Si ya existe conexión (`cliente is not None`), la reutiliza

**¿Por qué Singleton?**
```python
# Sin singleton: Crea conexión cada vez (ineficiente)
cliente1 = create_client(url, key)  # Nueva conexión
cliente2 = create_client(url, key)  # Otra conexión

# Con singleton: Reutiliza la misma conexión
cliente1 = init_client()  # Crea conexión
cliente2 = init_client()  # Retorna la misma conexión
```

### Sección 2: Guardar Imagen

```python
def save_image(width, height, rgb_data):
    ### Guarda los datos de una imagen en Supabase, retorna el ID
    client = init_client()

    data = {
        "width": width,
        "height": height,
        "rgb_data": rgb_data
    }

    response = client.table("images").insert(data).execute()

    if response.data:
        return response.data[0]["id"]
    else:
        raise Exception("Error al guardar la imagen en la base de datos")
```

**Explicación línea por línea:**

| Línea | Qué hace |
|-------|----------|
| `client = init_client()` | Obtiene la conexión a Supabase |
| `data = {...}` | Crea diccionario con los campos a insertar |
| `client.table("images")` | Selecciona la tabla "images" |
| `.insert(data)` | Prepara la operación INSERT |
| `.execute()` | Ejecuta la query |
| `response.data[0]["id"]` | Extrae el ID del registro creado |

**Equivalente SQL:**
```sql
INSERT INTO images (width, height, rgb_data)
VALUES (100, 100, "255,0,0,...")
RETURNING id;
```

### Sección 3: Obtener Imagen

```python
def get_image(image_id):
    ### Recupera los datos de una imagen por su ID
    client = init_client()

    response = client.table("images").select("*").eq("id", image_id).execute()

    if response.data:
        return response.data[0]
    else:
        raise Exception(f"No se encontro imagen con ID: {image_id}")
```

**Explicación:**

| Método | Qué hace |
|--------|----------|
| `.select("*")` | Selecciona todas las columnas |
| `.eq("id", image_id)` | Filtro WHERE id = image_id |
| `.execute()` | Ejecuta la query |

**Equivalente SQL:**
```sql
SELECT * FROM images WHERE id = 1;
```

**Retorna un diccionario:**
```python
{
    "id": 1,
    "width": 100,
    "height": 100,
    "rgb_data": "255,0,0,255,0,0,...",
    "created_at": "2024-01-15T10:30:00Z"
}
```

---

## image_processor.py - Procesamiento de Imágenes

### Propósito
Contiene la lógica de conversión de imágenes a string RGB y viceversa, usando **NumPy**. Solo tiene 2 funciones: `imagen_a_string_rgb` y `string_rgb_a_imagen`.

### Imports

```python
import numpy as np
```

| Import | Uso | Detalles |
|--------|-----|----------|
| `numpy` | Operaciones matemáticas con matrices | flatten, reshape, array |

### Sección 1: Descomposición - Imagen a String RGB

```python
def imagen_a_string_rgb(imagen):
    ### Descompone imagen en valores RGB y convierte a string
    ### Proceso: obtener dimensiones -> aplanar 3D a 1D -> string con comas
    alto, ancho, canales = imagen.shape
    flat = imagen.flatten()
    rgb_string = ",".join(map(str, flat))
    return rgb_string, ancho, alto
```

**Explicación paso a paso:**

#### 1. Extraer dimensiones del shape

```python
alto, ancho, canales = imagen.shape
# Ejemplo: alto=480, ancho=640, canales=3
```

**Shape en OpenCV vs PIL:**
```python
# OpenCV (NumPy array)
imagen.shape = (alto, ancho, canales)  # (480, 640, 3)
               (filas, columnas, depth)

# PIL/Pillow
imagen.size = (ancho, alto)  # (640, 480)
              (width, height)

# ⚠️ Orden diferente! Por eso usamos OpenCV
```

#### 2. Separar canales RGB con slicing

```python
r = imagen[:, :, 0]  # Canal Rojo
g = imagen[:, :, 1]  # Canal Verde
b = imagen[:, :, 2]  # Canal Azul
```

**Sintaxis de indexing NumPy:**
```python
imagen[filas, columnas, canal]
       [:, :, 0]
        ↑   ↑  ↑
        │   │  └─ Canal 0 (Rojo)
        │   └──── Todas las columnas
        └──────── Todas las filas
```

**Visualización de la separación:**
```
Imagen original RGB:          Canales separados:
┌──────────────────┐         ┌────┐  ┌────┐  ┌────┐
│ [255, 128, 0  ]  │   →     │255 │  │128 │  │ 0  │  
│ [ 0,  255, 128]  │         │ 0  │  │255 │  │128 │
│ [128,   0, 255]  │         │128 │  │ 0  │  │255 │
└──────────────────┘         └────┘  └────┘  └────┘
   Imagen 2D con RGB          R       G       B
                           (2D)    (2D)    (2D)
```

**Cada canal es una matriz 2D:**
```python
r.shape = (480, 640)  # Solo valores rojos
g.shape = (480, 640)  # Solo valores verdes
b.shape = (480, 640)  # Solo valores azules
```

#### 3. Aplanar (flatten) - De 3D a 1D

```python
flat = imagen.flatten()
```

**¿Qué hace flatten()?**

Convierte una matriz multidimensional en un vector 1D, leyendo los datos en orden **row-major** (por filas).

**Ejemplo visual con imagen pequeña (3x2):**

```python
# Imagen original 3D: shape (2, 3, 3)
imagen = [
    [[255,0,0], [0,255,0], [0,0,255]],    # Fila 0: Rojo, Verde, Azul
    [[255,255,0], [255,0,255], [0,255,255]]  # Fila 1: Amarillo, Magenta, Cian
]

# Después de flatten(): shape (18,)
flat = [255,0,0,  0,255,0,  0,0,255,  255,255,0,  255,0,255,  0,255,255]
       └──┬──┘   └──┬──┘   └──┬──┘   └───┬──┘   └───┬───┘   └───┬──┘
       Píxel 0   Píxel 1   Píxel 2   Píxel 3    Píxel 4    Píxel 5
```

**Orden de lectura:**
```
  Columna 0    Columna 1    Columna 2
    ┌─────┐     ┌─────┐     ┌─────┐
F0  │ RGB │ →   │ RGB │ →   │ RGB │ ┐
    └─────┘     └─────┘     └─────┘ │
    ┌─────┐     ┌─────┐     ┌─────┐ │ Flatten
F1  │ RGB │ →   │ RGB │ →   │ RGB │ │ lee en
    └─────┘     └─────┘     └─────┘ ┘ este orden
    
Resultado: [R0,G0,B0, R1,G1,B1, R2,G2,B2, R3,G3,B3, R4,G4,B4, R5,G5,B5]
```

**Tamaño del vector aplanado:**
```python
len(flat) = alto × ancho × canales
          = 480 × 640 × 3
          = 921,600 valores
```

#### 4. Convertir a string separado por comas

```python
rgb_string = ",".join(map(str, flat))
```

**Desglose de esta línea:**

```python
# 1. map(str, flat): Convierte cada número a string
flat = [255, 0, 0, 128, 255, 0]
map(str, flat)  →  ["255", "0", "0", "128", "255", "0"]

# 2. ",".join(): Une con comas
",".join(["255", "0", "0", "128", "255", "0"])
→  "255,0,0,128,255,0"
```

**Resultado final:**
```python
rgb_string = "255,0,0,0,255,0,0,0,255,255,255,0,255,0,255,0,255,255"
             └──────────────────── 921,600 valores ──────────────────┘
             
# Este string se guardará en la base de datos
```

### Sección 2: Reconstrucción - String RGB a Imagen

```python
def string_rgb_a_imagen(rgb_string, ancho, alto):
    ### Reconstruye imagen desde string de valores RGB
    ### Proceso: parsear string -> array numpy uint8 -> reshape (alto, ancho, 3)
    valores = list(map(int, rgb_string.split(",")))
    arr = np.array(valores, dtype=np.uint8)
    imagen = arr.reshape((alto, ancho, 3))
    return imagen
```

**Explicación del proceso inverso:**

#### 1. Parsear string a lista de enteros

```python
valores = list(map(int, rgb_string.split(",")))
```

```python
# String original
"255,0,0,128,255,0"

# .split(",") → separa por comas
["255", "0", "0", "128", "255", "0"]

# map(int, ...) → convierte cada string a int
[255, 0, 0, 128, 255, 0]
```

#### 2. Crear array NumPy con tipo correcto

```python
arr = np.array(valores, dtype=np.uint8)
```

**¿Por qué `dtype=np.uint8` es crucial?**

```python
# Sin especificar dtype (por defecto usa int64)
arr_default = np.array([255, 128, 0])
arr_default.dtype  # int64 (8 bytes por valor)
arr_default.nbytes  # 24 bytes

# Con dtype=np.uint8
arr_uint8 = np.array([255, 128, 0], dtype=np.uint8)
arr_uint8.dtype  # uint8 (1 byte por valor)
arr_uint8.nbytes  # 3 bytes

# ¡8 veces menos memoria! Y es el formato que espera OpenCV
```

**Rango de valores:**
```python
uint8: 0 a 255 (valores válidos para RGB)
int64: -9,223,372,036,854,775,808 a 9,223,372,036,854,775,807 (desperdicio)
```

#### 3. Reshape - De 1D a 3D

```python
imagen = arr.reshape((alto, ancho, 3))
```

**¿Qué hace reshape()?**

Reorganiza el vector 1D en una matriz 3D sin cambiar los datos, solo su "forma".

**Ejemplo con imagen 3x2:**

```python
# Vector 1D (shape: 18,)
arr = [255,0,0, 0,255,0, 0,0,255, 255,255,0, 255,0,255, 0,255,255]

# Reshape a (alto=2, ancho=3, canales=3)
imagen = arr.reshape((2, 3, 3))

# Resultado:
[
  [ [255,0,0],   [0,255,0],   [0,0,255]   ],  # Fila 0
  [ [255,255,0], [255,0,255], [0,255,255] ]   # Fila 1
]
```

**Visualización:**
```
Vector 1D:
[255,0,0,0,255,0,0,0,255,255,255,0,255,0,255,0,255,255]
 └──┬──┘ └──┬──┘ └──┬──┘ └───┬──┘ └───┬───┘ └───┬──┘
   P0      P1      P2       P3       P4       P5

Reshape (2, 3, 3):
        Columna 0     Columna 1     Columna 2
Fila 0  [255,0,0]    [0,255,0]    [0,0,255]
Fila 1  [255,255,0]  [255,0,255]  [0,255,255]

Imagen resultante:
┌─────┬──────┬─────┐
│ 🔴  │  🟢  │ 🔵  │
├─────┼──────┼─────┤
│ 🟡  │  🟣  │ 🔵  │
└─────┴──────┴─────┘
```

**Condición para reshape:**
```python
producto_de_dimensiones = alto × ancho × canales

len(arr) debe ser igual a producto_de_dimensiones

Ejemplo:
len(arr) = 18
alto × ancho × canales = 2 × 3 × 3 = 18 ✅

Si fueran diferentes:
reshape((3, 3, 3)) → 3 × 3 × 3 = 27 ❌
# ValueError: cannot reshape array of size 18 into shape (3,3,3)
```

### Sección 3: Obtener Canales Separados

```python
def obtener_canales(imagen):
    ### Separa los canales RGB de una imagen
    ### Similar a canales_naturales.py del profesor
    r = imagen[:, :, 0]
    g = imagen[:, :, 1]
    b = imagen[:, :, 2]

    ### Crear imagenes de cada canal
    R = np.zeros_like(imagen)
    R[:, :, 0] = r

    G = np.zeros_like(imagen)
    G[:, :, 1] = g

    B = np.zeros_like(imagen)
    B[:, :, 2] = b

    return R, G, B
```

**¿Qué hace esto?**

Crea tres imágenes RGB donde cada una muestra solo un canal:

```python
Imagen original:           Canal R:              Canal G:              Canal B:
┌──────────┐              ┌──────────┐          ┌──────────┐          ┌──────────┐
│ [255,128,64] │          │ [255, 0, 0] │       │ [ 0,128, 0] │       │ [ 0, 0,64] │
│ [ 0, 255, 0] │    →     │ [  0, 0, 0] │       │ [ 0,255, 0] │       │ [ 0, 0, 0] │
│ [ 0,  0,255] │          │ [  0, 0, 0] │       │ [ 0,  0, 0] │       │ [ 0, 0,255] │
└──────────────┘          └────────────┘        └────────────┘        └────────────┘
   Color normal              Solo rojo            Solo verde            Solo azul
```

### Sección 4: Calcular Tamaño en Memoria

```python
def calcular_tamano_imagen(imagen):
    ### Calcula el tamano de una imagen en memoria
    alto, ancho, canales = imagen.shape
    tamano_bytes = alto * ancho * canales
    tamano_kb = tamano_bytes / 1024
    tamano_mb = tamano_kb / 1024

    print(f"Dimensiones: {ancho}x{alto}")
    print(f"Canales: {canales}")
    print(f"Total pixeles: {alto * ancho}")
    print(f"Tamano en memoria: {tamano_kb:.2f} KB ({tamano_mb:.4f} MB)")
```

**Cálculo de memoria:**

```
Imagen de 1920x1080 (Full HD):

Píxeles = 1920 × 1080 = 2,073,600 píxeles
Valores RGB = 2,073,600 × 3 canales = 6,220,800 valores
Bytes = 6,220,800 × 1 byte (uint8) = 6,220,800 bytes
                                    = 6,075 KB
                                    ≈ 5.93 MB sin comprimir
```

---

## gui_upload.py - Interfaz de Captura

### Propósito
Ventana gráfica para capturar imágenes desde la cámara web, mostrar feed en vivo, y guardarlas en la base de datos. Usa **OpenCV para captura de cámara y procesamiento** y PIL solo para la conversión final a ImageTk.

### Imports

```python
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from image_processor import imagen_a_string_rgb, calcular_tamano_imagen
from database import save_image
```

| Import | Uso | Cuándo se usa |
|--------|-----|---------------|
| `tkinter` | Biblioteca GUI estándar de Python | Ventanas, botones, canvas |
| `messagebox` | Ventanas de alerta/información | Errores, confirmaciones |
| `cv2` | OpenCV - Captura de cámara y procesamiento | **Cámara y procesamiento** |
| `ImageTk` | Convertir array NumPy a formato Tkinter | **Solo para mostrar en canvas** |

**Flujo de datos:**
```
Cámara → cv2.VideoCapture(0) → frame BGR → cvtColor → NumPy array RGB → PIL → ImageTk → Canvas
         └──────────── Captura y Procesamiento ────────────┘   └─ Solo conversión ─┘
```

### Arquitectura de la Clase

```python
class UploadWindow:
    def __init__(self, parent=None):
        # Variables de instancia
        self.imagen_actual = None      # Array NumPy de OpenCV (foto capturada)
        self.photo_image = None        # ImageTk para Tkinter

        # Variables de cámara
        self.cap = None                # cv2.VideoCapture
        self.camara_activa = False     # Flag para el loop de feed
```

**Tipos de datos:**
```python
self.imagen_actual: np.ndarray         # Array NumPy (alto, ancho, 3) uint8
self.cap: cv2.VideoCapture             # Objeto de captura de cámara
self.camara_activa: bool               # True cuando el feed está activo
self.photo_image: ImageTk.PhotoImage   # Objeto para Tkinter
```

### Sección 1: Abrir Cámara y Feed en Vivo

```python
def _abrir_camara(self):
    """Inicializa cv2.VideoCapture(0) y arranca el loop de feed."""
    self.cap = cv2.VideoCapture(0)

    if not self.cap.isOpened():
        messagebox.showerror("Error", "No se pudo acceder a la cámara")
        return

    self.camara_activa = True
    self._actualizar_feed()

def _actualizar_feed(self):
    """Lee frame, convierte BGR→RGB, muestra en canvas, se llama con after(30)."""
    if not self.camara_activa or self.cap is None:
        return

    ret, frame = self.cap.read()
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Redimensionar y mostrar en canvas...
        pil_image = Image.fromarray(preview)
        self.photo_image = ImageTk.PhotoImage(pil_image)
        self.canvas.create_image(...)

    self.window.after(30, self._actualizar_feed)  # ~33 FPS
```

**Explicación detallada:**

#### 1. Abrir la cámara con OpenCV

```python
self.cap = cv2.VideoCapture(0)
```

- `cv2.VideoCapture(0)` abre la cámara por defecto del sistema (índice 0)
- Similar al estilo del profesor en scripts `video.py` y `*_live.py`
- Retorna un objeto de captura que permite leer frames

#### 2. Loop de actualización (Tkinter-friendly)

```python
def _actualizar_feed(self):
    if self.camara_activa and self.cap.isOpened():
        ret, frame = self.cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # mostrar en canvas...
        self.window.after(30, self._actualizar_feed)
```

- **No usa `while True`** (bloquearía la GUI de Tkinter)
- Usa `self.window.after(30, ...)` para programar la siguiente actualización
- Cada 30ms (~33 FPS) lee un nuevo frame de la cámara
- Convierte BGR→RGB antes de mostrar

#### 3. Tomar foto y detener cámara

```python
def _tomar_foto(self):
    ret, frame = self.cap.read()
    self.imagen_actual = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    self._detener_camara()  # cap.release()
```

- Captura el frame actual como numpy array RGB
- Detiene la cámara liberando el recurso
- Muestra preview estática de la foto capturada

### Sección 2: Mostrar Preview

```python
def _mostrar_preview(self):
    """Muestra la imagen en el canvas usando OpenCV → PIL → ImageTk."""
    if self.imagen_actual is None:
        return

    # Obtener tamaño del canvas
    canvas_width = self.canvas.winfo_width()
    canvas_height = self.canvas.winfo_height()

    # Calcular tamaño manteniendo proporción
    alto, ancho = self.imagen_actual.shape[:2]
    ratio = min(canvas_width / ancho, canvas_height / alto)

    nuevo_ancho = int(ancho * ratio * 0.9)
    nuevo_alto = int(alto * ratio * 0.9)

    # Redimensionar con OpenCV
    imagen_preview = cv2.resize(
        self.imagen_actual, 
        (nuevo_ancho, nuevo_alto),
        interpolation=cv2.INTER_LANCZOS4
    )

    # Convertir NumPy array a PIL Image para Tkinter
    img_pil = Image.fromarray(imagen_preview)
    self.photo_image = ImageTk.PhotoImage(img_pil)

    # Mostrar en canvas
    self.canvas.delete("all")
    self.canvas.create_image(
        canvas_width // 2,
        canvas_height // 2,
        image=self.photo_image,
        anchor=tk.CENTER
    )
```

**Explicación paso a paso:**

#### 1. Calcular ratio para mantener proporción

```python
ratio = min(canvas_width / ancho, canvas_height / alto)
```

**Ejemplo:**
```
Canvas: 400x300 píxeles
Imagen: 1920x1080 píxeles

ratio_ancho = 400 / 1920 = 0.208
ratio_alto  = 300 / 1080 = 0.278

ratio = min(0.208, 0.278) = 0.208

Nueva imagen: 1920 × 0.208 = 399 píxeles ancho
             1080 × 0.208 = 224 píxeles alto

Resultado: 399x224 cabe perfectamente en 400x300 ✅
```

**Si no usáramos `min()`, la imagen se saldría:**
```
Con ratio_alto = 0.278:
Nueva imagen: 1920 × 0.278 = 533 píxeles ancho ❌ (se sale de 400)
             1080 × 0.278 = 300 píxeles alto
```

#### 2. Multiplicar por 0.9 para márgenes

```python
nuevo_ancho = int(ancho * ratio * 0.9)
nuevo_alto = int(alto * ratio * 0.9)
```

El `* 0.9` deja un 10% de margen para que no quede pegada a los bordes.

#### 3. Redimensionar con OpenCV

```python
imagen_preview = cv2.resize(
    self.imagen_actual, 
    (nuevo_ancho, nuevo_alto),
    interpolation=cv2.INTER_LANCZOS4
)
```

**Métodos de interpolación en OpenCV:**

| Método | Calidad | Velocidad | Uso |
|--------|---------|-----------|-----|
| `INTER_NEAREST` | Baja | Muy rápida | Píxel art, imágenes pequeñas |
| `INTER_LINEAR` | Media | Rápida | Uso general |
| `INTER_CUBIC` | Alta | Media | Reducir tamaño |
| `INTER_LANCZOS4` | Muy alta | Lenta | **Calidad máxima (lo que usamos)** |
| `INTER_AREA` | Alta | Rápida | Reducir tamaño (alternativa) |

**¿Qué hace la interpolación?**

Cuando redimensionas una imagen, debes "inventar" o "promediar" píxeles:

```
Original (4x4):          Redimensionada (2x2):
┌─┬─┬─┬─┐               ┌───┬───┐
│1│2│3│4│               │ ? │ ? │
├─┼─┼─┼─┤     →         ├───┼───┤
│5│6│7│8│               │ ? │ ? │
├─┼─┼─┼─┤               └───┴───┘
│9│A│B│C│               
├─┼─┼─┼─┤               ¿Qué valores poner?
│D│E│F│G│
└─┴─┴─┴─┘

INTER_NEAREST: Toma el píxel más cercano
  [1, 3]
  [9, B]

INTER_LANCZOS4: Promedio ponderado de 4x4 vecinos
  [promedio(1,2,5,6), promedio(3,4,7,8)]
  [promedio(9,A,D,E), promedio(B,C,F,G)]
  → Bordes más suaves
```

#### 4. Convertir a PIL para Tkinter (única razón de usar PIL)

```python
img_pil = Image.fromarray(imagen_preview)
self.photo_image = ImageTk.PhotoImage(img_pil)
```

**¿Por qué este paso?**

```python
# Tkinter NO puede mostrar arrays NumPy directamente
canvas.create_image(x, y, image=imagen_preview)  # ❌ TypeError

# Tkinter SÍ puede mostrar ImageTk.PhotoImage
img_pil = Image.fromarray(imagen_preview)  # NumPy → PIL
photo = ImageTk.PhotoImage(img_pil)         # PIL → ImageTk
canvas.create_image(x, y, image=photo)      # ✅ Funciona
```

**Es una limitación de Tkinter, no una elección de diseño.**

**Alternativas que NO funcionan:**
```python
# Intentar usar NumPy directamente
canvas.create_image(x, y, image=imagen_preview)  # ❌

# Intentar usar OpenCV directamente
cv2.imshow("Ventana", imagen_preview)  # ✅ Funciona pero...
# → Abre ventana SEPARADA de OpenCV, no integra con Tkinter
```

#### 5. Mostrar en canvas

```python
self.canvas.delete("all")  # Borrar contenido anterior
self.canvas.create_image(
    canvas_width // 2,      # x: Centro horizontal
    canvas_height // 2,     # y: Centro vertical
    image=self.photo_image,
    anchor=tk.CENTER        # Anclar desde el centro
)
```

**Anchors en Tkinter:**
```
anchor=tk.NW (noroeste)    anchor=tk.N     anchor=tk.NE
        ┌────────┐              ┌────────┐      ┌────────┐
        │█       │              │   █    │      │       █│
        
anchor=tk.W                anchor=tk.CENTER    anchor=tk.E
        ┌────────┐              ┌────────┐      ┌────────┐
        │█       │              │   █    │      │       █│
        
anchor=tk.SW               anchor=tk.S         anchor=tk.SE
        ┌────────┐              ┌────────┐      ┌────────┐
        │       █│              │   █    │      │       █│

█ = Punto de referencia
```

### Sección 3: Guardar en Base de Datos

```python
def _guardar_en_bd(self):
    """Descompone la imagen con OpenCV y guarda en Supabase."""
    if self.imagen_actual is None:
        return

    try:
        # Deshabilitar botón mientras procesa
        self.btn_save.config(state=tk.DISABLED, text="Procesando...")
        self.window.update()  # Forzar actualización de UI

        # Descomponer imagen (OpenCV/NumPy)
        rgb_string, ancho, alto = imagen_a_string_rgb(self.imagen_actual)

        # Guardar en base de datos
        image_id = save_image(ancho, alto, rgb_string)

        # Mostrar ID generado
        self.lbl_id.config(text=f"Imagen guardada con ID: {image_id}")

        messagebox.showinfo("Éxito", f"Imagen guardada con ID: {image_id}")

    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")

    finally:
        self.btn_save.config(state=tk.NORMAL, text="Guardar en Base de Datos")
```

**Flujo completo:**

```
self.imagen_actual (NumPy array RGB)
        │
        ▼
imagen_a_string_rgb()  [OpenCV/NumPy]
        │
        ├─→ imagen.flatten()
        ├─→ ",".join(map(str, flat))
        │
        ▼
(rgb_string, ancho, alto)
        │
        ▼
save_image(ancho, alto, rgb_string)  [Supabase]
        │
        ▼
ID generado
```

**¿Por qué `self.window.update()`?**

```python
self.btn_save.config(text="Procesando...")
self.window.update()  # Sin esto, el texto no cambia hasta que termine
```

Tkinter es de un solo hilo. Si no llamas a `.update()`, los cambios visuales se quedan "pendientes" hasta que termine la función:

```python
# Sin update()
self.btn_save.config(text="Procesando...")  # Se queda pendiente
time.sleep(5)  # Usuario ve el botón sin cambiar
# Al terminar, cambia por un instante y vuelve a "Guardar..."

# Con update()
self.btn_save.config(text="Procesando...")
self.window.update()  # ✅ Cambia inmediatamente
time.sleep(5)  # Usuario VE "Procesando..."
```

---

## gui_viewer.py - Interfaz de Visualización

### Propósito
Ventana para consultar imágenes por ID, reconstruirlas desde la base de datos usando **OpenCV/NumPy**, y mostrarlas. PIL solo se usa para la conversión a ImageTk.

### Sección Principal: Consultar y Reconstruir Imagen

```python
def _consultar_imagen(self):
    """Consulta la imagen por ID, la reconstruye con OpenCV y la muestra."""
    id_text = self.entry_id.get().strip()

    if not id_text:
        messagebox.showwarning("Advertencia", "Ingresa un ID de imagen")
        return

    try:
        image_id = int(id_text)
    except ValueError:
        messagebox.showerror("Error", "El ID debe ser un número entero")
        return

    try:
        # Consultar base de datos
        image_data = get_image(image_id)

        # Extraer datos
        ancho = image_data["width"]
        alto = image_data["height"]
        rgb_string = image_data["rgb_data"]

        # Reconstruir imagen con OpenCV/NumPy
        self.imagen_actual = string_rgb_a_imagen(rgb_string, ancho, alto)

        # Mostrar información
        self.lbl_info.config(
            text=f"Dimensiones: {ancho}x{alto} | "
                 f"Valores RGB: {len(rgb_string.split(','))}"
        )

        # Mostrar imagen
        self._mostrar_imagen()

    except Exception as e:
        messagebox.showerror("Error", f"Error al consultar:\n{str(e)}")
```

**Flujo de reconstrucción completo:**

```
ID ingresado por usuario (texto)
        │
        ├─→ Validar que sea entero
        │
        ▼
get_image(id)  [Consulta Supabase]
        │
        ▼
{
  "id": 1,
  "width": 640,
  "height": 480,
  "rgb_data": "255,0,0,0,255,0,...",
  "created_at": "2024-..."
}
        │
        ▼
string_rgb_a_imagen(rgb_data, width, height)  [OpenCV/NumPy]
        │
        ├─→ rgb_string.split(",")          # String → Lista
        ├─→ np.array(valores, dtype=uint8) # Lista → Array NumPy
        ├─→ arr.reshape((alto, ancho, 3))  # 1D → 3D
        │
        ▼
Array NumPy RGB (alto, ancho, 3) uint8
        │
        ├─→ cv2.resize() si es necesario
        ├─→ Image.fromarray()  # NumPy → PIL
        ├─→ ImageTk.PhotoImage()  # PIL → ImageTk
        │
        ▼
Mostrar en Tkinter Canvas
```

### Detalle de cada paso:

#### 1. Validación del ID

```python
id_text = self.entry_id.get().strip()

if not id_text:
    messagebox.showwarning("Advertencia", "Ingresa un ID de imagen")
    return

try:
    image_id = int(id_text)
except ValueError:
    messagebox.showerror("Error", "El ID debe ser un número entero")
    return
```

**Casos que maneja:**

| Input | Resultado |
|-------|-----------|
| `"  123  "` | `image_id = 123` ✅ (strip elimina espacios) |
| `"abc"` | ValueError → Mensaje de error ❌ |
| `""` | Warning "Ingresa un ID" ❌ |
| `"12.5"` | ValueError (no es entero) ❌ |
| `"0"` | `image_id = 0` ✅ (válido aunque probablemente no exista) |

#### 2. Consultar base de datos

```python
image_data = get_image(image_id)
```

**Internamente ejecuta:**
```python
response = client.table("images")\
    .select("*")\
    .eq("id", image_id)\
    .execute()
```

**Retorna un diccionario:**
```python
{
    "id": 1,
    "width": 640,
    "height": 480,
    "rgb_data": "255,0,0,0,255,0,0,0,255,...",  # String MUY largo
    "created_at": "2024-01-15T10:30:00.000Z"
}
```

**Tamaño del string:**
```python
# Imagen 640x480
valores = 640 × 480 × 3 = 921,600 valores
string = "255,0,0,..." con comas = ~3.5 MB de texto

# PostgreSQL puede almacenar hasta 1 GB por campo TEXT
# → No hay problema de capacidad
```

#### 3. Reconstruir imagen

```python
self.imagen_actual = string_rgb_a_imagen(rgb_string, ancho, alto)
```

**Internamente:**

```python
def string_rgb_a_imagen(rgb_string: str, ancho: int, alto: int):
    # 1. Parsear string
    valores = list(map(int, rgb_string.split(",")))
    # "255,0,0" → [255, 0, 0]
    
    # 2. Crear array NumPy
    arr = np.array(valores, dtype=np.uint8)
    # [255, 0, 0, ...] shape: (921600,)
    
    # 3. Reshape a imagen 3D
    imagen = arr.reshape((alto, ancho, 3))
    # shape: (480, 640, 3)
    
    return imagen  # Array NumPy RGB
```

**Proceso visual:**

```
String en BD:
"255,0,0,0,255,0,0,0,255,255,255,0,0,255,255,255,0,255"

    ↓ split(",")

Lista de strings:
["255", "0", "0", "0", "255", "0", ...]

    ↓ map(int, ...)

Lista de enteros:
[255, 0, 0, 0, 255, 0, ...]

    ↓ np.array(..., dtype=np.uint8)

Array 1D:
[255 0 0 0 255 0 ...] shape: (18,)

    ↓ reshape((2, 3, 3))

Array 3D (imagen):
[
  [[255,0,0], [0,255,0], [0,0,255]],     # Fila 0
  [[255,255,0], [0,255,255], [255,0,255]] # Fila 1
]
shape: (2, 3, 3)
```

#### 4. Mostrar información

```python
self.lbl_info.config(
    text=f"Dimensiones: {ancho}x{alto} | "
         f"Valores RGB: {len(rgb_string.split(','))}"
)
```

**Ejemplo de salida:**
```
Dimensiones: 640x480 | Valores RGB: 921,600
```

### Mostrar Imagen Reconstruida

```python
def _mostrar_imagen(self):
    """Muestra la imagen reconstruida en el canvas."""
    if self.imagen_actual is None:
        return

    # Obtener tamaño del canvas
    canvas_width = self.canvas.winfo_width()
    canvas_height = self.canvas.winfo_height()

    # Calcular redimensionamiento
    alto, ancho = self.imagen_actual.shape[:2]
    ratio = min(canvas_width / ancho, canvas_height / alto)

    nuevo_ancho = int(ancho * ratio * 0.9)
    nuevo_alto = int(alto * ratio * 0.9)

    # Redimensionar con OpenCV
    imagen_preview = cv2.resize(
        self.imagen_actual,
        (nuevo_ancho, nuevo_alto),
        interpolation=cv2.INTER_LANCZOS4
    )

    # Convertir NumPy → PIL → ImageTk (solo para Tkinter)
    img_pil = Image.fromarray(imagen_preview)
    self.photo_image = ImageTk.PhotoImage(img_pil)

    # Mostrar en canvas
    self.canvas.delete("all")
    self.canvas.create_image(
        canvas_width // 2,
        canvas_height // 2,
        image=self.photo_image,
        anchor=tk.CENTER
    )
```

**Comparación: Imagen Original vs Reconstruida**

```
Imagen Original (archivo JPG/PNG):
  - Puede tener compresión con pérdida (JPG)
  - Puede tener metadatos EXIF
  - Tamaño: ~100 KB - 2 MB

        ↓ Cargar con cv2.imread()
        ↓ Convertir BGR → RGB
        ↓ Descomponer a string RGB
        ↓ Guardar en BD

String en BD:
  - Sin compresión
  - Sin metadatos
  - Valores RGB puros
  - Tamaño: ~3.5 MB (texto)

        ↓ Consultar de BD
        ↓ Reconstruir con NumPy
        ↓ Reshape a imagen

Imagen Reconstruida (NumPy array):
  - Idéntica píxel por píxel a la cargada
  - Sin pérdida de calidad
  - Lista para procesar o guardar
```

**¿Se pierde calidad?**

```python
# NO, si guardas y reconstruyes en el mismo formato

Imagen original → cv2.imread() → Array NumPy → flatten() → String
                                      ↓
                                 [255, 0, 0, ...]
                                      ↑
String → split() → Array NumPy → reshape() → Imagen reconstruida

Comparación:
np.array_equal(imagen_original, imagen_reconstruida)  # True ✅
```

---

## main.py - Punto de Entrada

### Propósito
Ventana principal que permite abrir las otras dos interfaces.

### Estructura

```python
class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Decomposer")
        self._setup_ui()

    def _open_upload(self):
        """Abre la ventana de carga de imágenes."""
        from gui_upload import UploadWindow
        UploadWindow(self.root)

    def _open_viewer(self):
        """Abre la ventana de visualización de imágenes."""
        from gui_viewer import ViewerWindow
        ViewerWindow(self.root)

    def run(self):
        self.root.mainloop()


def main():
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
```

**Explicación de `if __name__ == "__main__"`:**

```python
if __name__ == "__main__":
    main()
```

- `__name__` es una variable especial de Python
- Vale `"__main__"` solo cuando ejecutas el archivo directamente
- Si importas el archivo desde otro módulo, `__name__` será el nombre del módulo

```python
# Si ejecutas: python main.py
__name__ == "__main__"  # True, ejecuta main()

# Si importas: from main import MainWindow
__name__ == "main"  # False, no ejecuta main()
```

---

---

## Conceptos Avanzados de OpenCV

### 1. BGR vs RGB - ¿Por qué OpenCV es diferente?

**Historia:**
OpenCV fue creado a finales de los 90. Las cámaras de video analógicas de esa época usaban señales BGR (Blue-Green-Red) por razones de compatibilidad con televisores antiguos.

**Implicaciones:**

```python
# Leer imagen
imagen = cv2.imread("foto.jpg")  # Lee en BGR

# Ver el color de un píxel rojo puro
print(imagen[0, 0])  # [0, 0, 255] ← [B, G, R]

# Sin conversión, se vería azul
plt.imshow(imagen)  # ❌ Colores invertidos

# Conversión correcta
imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
plt.imshow(imagen_rgb)  # ✅ Colores correctos
```

**Tabla de conversiones comunes:**

| Desde | Hacia | Código OpenCV |
|-------|-------|---------------|
| BGR | RGB | `cv2.COLOR_BGR2RGB` |
| RGB | BGR | `cv2.COLOR_RGB2BGR` |
| BGR | Grises | `cv2.COLOR_BGR2GRAY` |
| RGB | HSV | `cv2.COLOR_RGB2HSV` |
| Grises | BGR | `cv2.COLOR_GRAY2BGR` |

### 2. Shape, Dtype y Size en NumPy

#### Shape - Dimensiones del array

```python
imagen.shape  # (alto, ancho, canales)
```

**Diferentes tipos de imágenes:**

```python
# Imagen a color
imagen_rgb.shape = (480, 640, 3)
                   alto  ancho  RGB

# Imagen en escala de grises
imagen_gray.shape = (480, 640)
                    alto  ancho (sin canal)

# Imagen con transparencia
imagen_rgba.shape = (480, 640, 4)
                    alto  ancho  RGBA

# Video frame (mismo que imagen)
frame.shape = (1080, 1920, 3)
              alto   ancho  RGB
```

#### Dtype - Tipo de datos

```python
imagen.dtype  # uint8, uint16, float32, etc.
```

**Tipos comunes:**

| Tipo | Rango | Bytes | Uso |
|------|-------|-------|-----|
| `uint8` | 0 - 255 | 1 | **Imágenes estándar RGB** |
| `uint16` | 0 - 65,535 | 2 | Imágenes médicas, RAW |
| `float32` | 0.0 - 1.0 | 4 | Procesamiento intermedio |
| `float64` | 0.0 - 1.0 | 8 | Alta precisión (raro) |

**Conversiones:**

```python
# uint8 (0-255) a float32 (0.0-1.0)
imagen_float = imagen.astype(np.float32) / 255.0

# float32 (0.0-1.0) a uint8 (0-255)
imagen_uint8 = (imagen_float * 255).astype(np.uint8)
```

#### Size - Total de elementos

```python
imagen.size = alto × ancho × canales
```

**Cálculo de memoria:**

```python
imagen.shape = (1080, 1920, 3)
imagen.dtype = uint8

Total elementos = 1080 × 1920 × 3 = 6,220,800
Bytes por elemento = 1 byte (uint8)
Memoria total = 6,220,800 bytes = 6.22 MB

# Verificar
imagen.nbytes  # 6220800
```

### 3. Indexing y Slicing - Acceso a píxeles

#### Sintaxis básica

```python
imagen[fila, columna, canal]
```

**Ejemplos:**

```python
# Acceder a un píxel específico (fila 100, columna 200)
pixel = imagen[100, 200]  # [R, G, B]

# Acceder al valor rojo de ese píxel
rojo = imagen[100, 200, 0]

# Cambiar un píxel a blanco
imagen[100, 200] = [255, 255, 255]

# Región rectangular (ROI - Region of Interest)
region = imagen[100:200, 300:400]  # Filas 100-199, Columnas 300-399

# Primer canal (rojo) completo
canal_rojo = imagen[:, :, 0]

# Invertir imagen verticalmente
imagen_invertida = imagen[::-1, :, :]

# Invertir imagen horizontalmente (espejo)
imagen_espejo = imagen[:, ::-1, :]
```

**Visualización de slicing:**

```
Imagen completa:         Región [100:200, 300:400]:
  0  100 200 300 400        300      400
0 ┌───────────────────┐   ┌──────────┐
  │                   │   │          │
100 │     ┌────────┐  │   │ Extraída │
  │     │▓▓▓▓▓▓▓▓│  │   │          │
200 │     └────────┘  │   └──────────┘
  │                   │
  └───────────────────┘
```

### 4. Flatten y Reshape - Transformaciones

#### Flatten - 3D a 1D

```python
flat = imagen.flatten()
```

**Visualización:**

```python
imagen.shape = (2, 3, 3)  # 2 filas, 3 columnas, 3 canales

Imagen 3D:
Fila 0: [[255,0,0], [0,255,0], [0,0,255]]
Fila 1: [[255,255,0], [0,255,255], [255,0,255]]

flat.shape = (18,)  # Vector 1D

[255, 0, 0, 0, 255, 0, 0, 0, 255, 255, 255, 0, 0, 255, 255, 255, 0, 255]
 └─ P0 ─┘  └─ P1 ─┘  └─ P2 ─┘  └─  P3  ─┘  └─  P4  ─┘  └─  P5  ─┘
```

**Orden de lectura (row-major / C order):**
```
1. Lee fila 0, columna 0, todos los canales: [255, 0, 0]
2. Lee fila 0, columna 1, todos los canales: [0, 255, 0]
3. Lee fila 0, columna 2, todos los canales: [0, 0, 255]
4. Lee fila 1, columna 0, todos los canales: [255, 255, 0]
... y así sucesivamente
```

#### Reshape - Cambiar forma sin copiar datos

```python
nueva_forma = arr.reshape((nuevo_alto, nuevo_ancho, 3))
```

**Ejemplo práctico:**

```python
# Vector 1D de 18 elementos
arr = np.array([255,0,0, 0,255,0, 0,0,255, 255,255,0, 0,255,255, 255,0,255])

# Reshape a diferentes formas (todas válidas)
img_2x3 = arr.reshape((2, 3, 3))  # 2×3×3 = 18 ✅
img_3x2 = arr.reshape((3, 2, 3))  # 3×2×3 = 18 ✅
img_1x6 = arr.reshape((1, 6, 3))  # 1×6×3 = 18 ✅

# Reshape inválido
img_4x4 = arr.reshape((4, 4, 3))  # 4×4×3 = 48 ❌ ValueError
```

**Reshape no copia datos (eficiente):**

```python
original = np.array([1, 2, 3, 4, 5, 6])
reshaped = original.reshape((2, 3))

reshaped[0, 0] = 99
print(original)  # [99, 2, 3, 4, 5, 6] ← ¡También cambió!

# Son dos "vistas" del mismo bloque de memoria
```

### 5. Interpolación en resize()

Cuando redimensionas una imagen, necesitas "inventar" píxeles nuevos (aumentar tamaño) o "combinar" píxeles existentes (reducir tamaño).

#### Métodos disponibles

```python
cv2.resize(imagen, (nuevo_ancho, nuevo_alto), interpolation=METODO)
```

| Método | Calidad | Velocidad | Mejor para |
|--------|---------|-----------|------------|
| `INTER_NEAREST` | ⭐ | ⚡⚡⚡⚡⚡ | Píxel art, imágenes pequeñas, aumentar tamaño conservando píxeles |
| `INTER_LINEAR` | ⭐⭐⭐ | ⚡⚡⚡⚡ | Uso general, buen balance |
| `INTER_CUBIC` | ⭐⭐⭐⭐ | ⚡⚡⚡ | Reducir tamaño, alta calidad |
| `INTER_LANCZOS4` | ⭐⭐⭐⭐⭐ | ⚡⚡ | **Máxima calidad, previews, impresión** |
| `INTER_AREA` | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ | Reducir tamaño rápidamente |

#### Ejemplos visuales

**Aumentar tamaño (upscaling) 2x2 → 4x4:**

```
Original:           INTER_NEAREST:      INTER_LANCZOS4:
┌──┬──┐            ┌──┬──┬──┬──┐       ┌──┬──┬──┬──┐
│■ │  │            │■ │■ │  │  │       │■ │▓ │░ │  │
├──┼──┤     →      │■ │■ │  │  │       │▓ │▒ │░ │░ │
│  │▓ │            │  │  │▓ │▓ │       │░ │░ │▒ │▓ │
└──┴──┘            │  │  │▓ │▓ │       │  │░ │▓ │▓ │
                   └──┴──┴──┴──┘       └──┴──┴──┴──┘
                   Pixelado            Suave
```

**Reducir tamaño (downscaling) 4x4 → 2x2:**

```
Original:           INTER_AREA:         INTER_NEAREST:
┌──┬──┬──┬──┐      ┌──┬──┐            ┌──┬──┐
│■ │▓ │░ │  │      │▒ │░ │            │■ │░ │
│▓ │▒ │░ │░ │  →   │░ │▒ │            │  │▓ │
│░ │░ │▒ │▓ │      └──┴──┘            └──┴──┘
│  │░ │▓ │▓ │      Promediado         Píxeles saltados
└──┴──┴──┴──┘
```

#### ¿Cuál usar?

```python
# Máxima calidad (previews, interfaz usuario)
cv2.resize(img, (ancho, alto), interpolation=cv2.INTER_LANCZOS4)

# Balance calidad/velocidad (procesamiento en tiempo real)
cv2.resize(img, (ancho, alto), interpolation=cv2.INTER_LINEAR)

# Reducir tamaño rápido (miniaturas, batch processing)
cv2.resize(img, (ancho, alto), interpolation=cv2.INTER_AREA)

# Píxel art / imágenes de juegos retro
cv2.resize(img, (ancho, alto), interpolation=cv2.INTER_NEAREST)
```

### 6. Operaciones matemáticas con arrays

#### Operaciones elemento por elemento

```python
# Dividir por 2 (oscurecer imagen)
imagen_oscura = imagen // 2

# Multiplicar por 1.5 (aclarar)
imagen_clara = np.clip(imagen * 1.5, 0, 255).astype(np.uint8)

# Invertir colores (negativo)
imagen_negativa = 255 - imagen

# Binarizar (blanco o negro)
imagen_binaria = np.where(imagen > 127, 255, 0).astype(np.uint8)
```

#### Operaciones entre imágenes

```python
# Promedio de dos imágenes (blend 50/50)
blend = cv2.addWeighted(img1, 0.5, img2, 0.5, 0)

# Diferencia absoluta
diferencia = cv2.absdiff(img1, img2)

# Máscara (mostrar solo donde mask > 0)
resultado = cv2.bitwise_and(imagen, imagen, mask=mascara)
```

#### Estadísticas

```python
# Valor mínimo, máximo, promedio
min_val = np.min(imagen)
max_val = np.max(imagen)
promedio = np.mean(imagen)

# Por canal
promedio_r = np.mean(imagen[:, :, 0])
promedio_g = np.mean(imagen[:, :, 1])
promedio_b = np.mean(imagen[:, :, 2])

# Desviación estándar (contraste)
std = np.std(imagen)
```

### 7. Espacios de color

OpenCV puede convertir entre múltiples espacios de color:

#### RGB vs HSV

```python
# RGB: Red, Green, Blue (colores luz)
rgb = [255, 0, 0]  # Rojo puro

# HSV: Hue, Saturation, Value (tono, saturación, brillo)
hsv = cv2.cvtColor(imagen_rgb, cv2.COLOR_RGB2HSV)
```

**¿Cuándo usar HSV?**

HSV es mejor para:
- Detección de objetos por color (range de colores)
- Ajustar brillo sin cambiar el color
- Segmentación por color

```python
# Ejemplo: Detectar objetos rojos
hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
rojo_bajo = np.array([0, 100, 100])
rojo_alto = np.array([10, 255, 255])
mascara = cv2.inRange(hsv, rojo_bajo, rojo_alto)
```

#### Escala de grises

```python
# Conversión a grises
gris = cv2.cvtColor(imagen_rgb, cv2.COLOR_RGB2GRAY)

# Fórmula: Gris = 0.299*R + 0.587*G + 0.114*B
# (Pondera más el verde porque el ojo humano es más sensible)
```

---

## Resumen de Flujos Completos

### Flujo de Captura (con OpenCV)

```
1. Usuario: main.py → Click "Cargar Imagen"
2. GUI: gui_upload.py → Abre ventana
3. Usuario: Click "Abrir Cámara"
4. GUI: cv2.VideoCapture(0) → Feed en vivo en canvas (loop con after(30))
5. Usuario: Click "Tomar Foto"
6. GUI: cap.read() → frame BGR → cv2.cvtColor(BGR → RGB) → Array NumPy RGB
7. GUI: cap.release() → Cámara liberada
8. GUI: Mostrar dimensiones, calcular tamaño
9. GUI: cv2.resize() + Image.fromarray() + ImageTk → Mostrar preview
10. Usuario: Click "Guardar"
11. Procesador: imagen.flatten() → Vector 1D
12. Procesador: ",".join() → String RGB
13. Database: INSERT en Supabase
14. Database: Retorna ID
15. GUI: Mostrar ID generado
```

### Flujo de Consulta (con OpenCV)

```
1. Usuario: main.py → Click "Ver Imagen"
2. GUI: gui_viewer.py → Abre ventana
3. Usuario: Ingresa ID → Click "Consultar"
4. GUI: Validar ID (int)
5. Database: SELECT de Supabase
6. Database: Retorna {width, height, rgb_data}
7. Procesador: rgb_data.split(",") → Lista
8. Procesador: np.array(..., uint8) → Array 1D
9. Procesador: arr.reshape(alto, ancho, 3) → Array 3D
10. GUI: cv2.resize() + Image.fromarray() + ImageTk → Mostrar
11. Usuario: Ve imagen reconstruida (idéntica al original)
```

---

## Comparación: OpenCV vs PIL

| Aspecto | OpenCV (cv2) | PIL/Pillow |
|---------|--------------|------------|
| **Formato de datos** | NumPy array (alto, ancho, 3) | Objeto Image |
| **Orden de canales** | BGR por defecto | RGB |
| **Rendimiento** | ⚡⚡⚡⚡⚡ C/C++ optimizado | ⚡⚡⚡ Python |
| **Operaciones** | Miles (filtros, detección, etc.) | Básicas (abrir, guardar, redimensionar) |
| **Integración NumPy** | Nativa | Requiere conversión |
| **Lectura de archivos** | `cv2.imread()` | `Image.open()` |
| **Redimensionar** | `cv2.resize()` | `img.thumbnail()` / `img.resize()` |
| **Conversión de color** | `cv2.cvtColor()` | `img.convert()` |
| **Mostrar en Tkinter** | ❌ Necesita conversión a PIL | ✅ Via ImageTk |

**Decisión de arquitectura:**
```
Procesamiento pesado → OpenCV (rápido, potente)
Mostrar en Tkinter → PIL/ImageTk (único compatible)
```

---

## Conceptos Clave de Python Usados

| Concepto | Dónde se usa | Explicación |
|----------|--------------|-------------|
| **Singleton** | `database.py` | Una sola instancia de conexión a BD |
| **Type hints** | `def func() -> int:` | Documenta tipos de entrada/salida |
| **Docstrings** | `"""texto"""` | Documentación de funciones |
| **Try/except** | Todos los handlers de GUI | Manejo de errores robusto |
| **Global** | `global _client` | Modificar variable global (singleton) |
| **f-strings** | `f"ID: {id}"` | Interpolación de strings |
| **List comprehension** | `[x for x in list]` | Crear listas compactas |
| **map()** | `map(str, flat)` | Aplicar función a iterable |
| **Lambda** | Tkinter callbacks | Funciones anónimas |
| **Context managers** | (no usado pero útil) | `with open() as f:` |

---

## Conceptos Clave de OpenCV/NumPy Usados

| Concepto | Código | Explicación |
|----------|--------|-------------|
| **Shape** | `imagen.shape` | Dimensiones: (alto, ancho, canales) |
| **Dtype** | `dtype=np.uint8` | Tipo de datos: 0-255 |
| **Slicing** | `imagen[:, :, 0]` | Extraer canal rojo |
| **Flatten** | `imagen.flatten()` | 3D → 1D |
| **Reshape** | `arr.reshape((h,w,3))` | 1D → 3D |
| **cvtColor** | `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)` | Conversión BGR→RGB |
| **resize** | `cv2.resize(img, (w,h), interpolation)` | Cambiar tamaño |
| **imread** | `cv2.imread(path)` | Leer imagen (BGR) |

---

## Apéndice: Tamaños de Imágenes Comunes

| Resolución | Dimensiones | Píxeles | Memoria sin comprimir (RGB) |
|------------|-------------|---------|------------------------------|
| HD Ready | 1280 × 720 | 921,600 | 2.64 MB |
| Full HD | 1920 × 1080 | 2,073,600 | 5.93 MB |
| 2K | 2560 × 1440 | 3,686,400 | 10.55 MB |
| 4K UHD | 3840 × 2160 | 8,294,400 | 23.73 MB |
| 8K UHD | 7680 × 4320 | 33,177,600 | 94.92 MB |

**Nota:** Archivos PNG/JPG son mucho más pequeños debido a compresión (3x - 20x).

---
