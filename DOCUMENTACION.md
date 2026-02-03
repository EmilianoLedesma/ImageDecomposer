# Documentación Técnica - Image Decomposer

## Índice

1. [Visión General](#visión-general)
2. [config.py - Configuración](#configpy---configuración)
3. [database.py - Capa de Datos](#databasepy---capa-de-datos)
4. [image_processor.py - Procesamiento de Imágenes](#image_processorpy---procesamiento-de-imágenes)
5. [gui_upload.py - Interfaz de Carga](#gui_uploadpy---interfaz-de-carga)
6. [gui_viewer.py - Interfaz de Visualización](#gui_viewerpy---interfaz-de-visualización)
7. [main.py - Punto de Entrada](#mainpy---punto-de-entrada)

---

## Visión General

El proyecto sigue el patrón de **separación de responsabilidades**:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   config    │────▶│  database   │────▶│  Supabase   │
└─────────────┘     └─────────────┘     └─────────────┘
                          ▲
                          │
┌─────────────┐     ┌─────────────┐
│  gui_upload │────▶│   image     │
│  gui_viewer │────▶│  processor  │
└─────────────┘     └─────────────┘
        ▲
        │
┌─────────────┐
│    main     │
└─────────────┘
```

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
    """Verifica que las credenciales de Supabase estén configuradas."""
    if not SUPABASE_URL or SUPABASE_URL == "tu_url_aqui":
        raise ValueError("SUPABASE_URL no está configurado en el archivo .env")
    if not SUPABASE_KEY or SUPABASE_KEY == "tu_anon_key_aqui":
        raise ValueError("SUPABASE_KEY no está configurado en el archivo .env")
    return True
```

**Explicación:**
- Verifica que las variables no estén vacías (`not SUPABASE_URL`)
- Verifica que no sean los valores placeholder del template
- `raise ValueError` lanza un error descriptivo si algo falla
- Se usa antes de conectar a Supabase para dar errores claros

---

## database.py - Capa de Datos

### Propósito
Maneja toda la comunicación con la base de datos Supabase. Aísla la lógica de persistencia del resto de la aplicación.

### Imports

```python
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, validate_config
```

| Import | Uso |
|--------|-----|
| `create_client` | Función para crear conexión a Supabase |
| `Client` | Tipo de dato para type hints |
| `config.*` | Credenciales y validación |

### Sección 1: Cliente Singleton

```python
_client: Client = None

def init_client() -> Client:
    """Inicializa y retorna el cliente de Supabase."""
    global _client
    if _client is None:
        validate_config()
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client
```

**Explicación:**
- `_client` es una variable global (el guion bajo indica que es "privada")
- **Patrón Singleton**: Solo se crea UNA conexión, sin importar cuántas veces se llame
- `global _client` permite modificar la variable global dentro de la función
- Si ya existe conexión (`_client is not None`), la reutiliza

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
def save_image(width: int, height: int, rgb_data: str) -> int:
    """Guarda los datos de una imagen en Supabase."""
    client = init_client()

    data = {
        "width": width,
        "height": height,
        "rgb_data": rgb_data
    }

    response = client.table("images").insert(data).execute()

    if response.data and len(response.data) > 0:
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
def get_image(image_id: int) -> dict:
    """Recupera los datos de una imagen por su ID."""
    client = init_client()

    response = client.table("images").select("*").eq("id", image_id).execute()

    if response.data and len(response.data) > 0:
        return response.data[0]
    else:
        raise Exception(f"No se encontró imagen con ID: {image_id}")
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
Contiene toda la lógica de manipulación de imágenes: cargar, descomponer en RGB, y reconstruir.

### Imports

```python
import os
import tempfile
from PIL import Image
import numpy as np
```

| Import | Uso |
|--------|-----|
| `os` | Operaciones con rutas de archivos |
| `tempfile` | Obtener directorio temporal del sistema |
| `PIL.Image` | Biblioteca Pillow para manipular imágenes |
| `numpy` | Operaciones matemáticas con matrices |

### Sección 1: Cargar y Convertir a PNG

```python
def load_and_convert_to_png(path: str) -> tuple[str, Image.Image]:
    """Carga una imagen desde cualquier formato y la convierte a PNG."""

    # Cargar imagen
    image = Image.open(path)

    # Convertir a RGB si es necesario
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Crear nombre para el archivo PNG
    base_name = os.path.splitext(os.path.basename(path))[0]

    # Guardar en carpeta temporal
    temp_dir = tempfile.gettempdir()
    png_path = os.path.join(temp_dir, f"{base_name}_converted.png")

    # Guardar como PNG
    image.save(png_path, "PNG")

    return png_path, image
```

**Explicación paso a paso:**

1. **Cargar imagen:**
   ```python
   image = Image.open(path)  # Abre JPG, PNG, BMP, GIF, etc.
   ```

2. **Convertir a RGB:**
   ```python
   if image.mode != "RGB":
       image = image.convert("RGB")
   ```
   - Las imágenes pueden tener diferentes modos: `RGB`, `RGBA`, `L` (grises), `P` (paleta)
   - Convertimos a `RGB` para tener siempre 3 canales

3. **Extraer nombre base:**
   ```python
   base_name = os.path.splitext(os.path.basename(path))[0]
   # "C:/fotos/mi_imagen.jpg" → "mi_imagen"
   ```

4. **Crear ruta temporal:**
   ```python
   temp_dir = tempfile.gettempdir()  # "C:/Users/X/AppData/Local/Temp"
   png_path = os.path.join(temp_dir, f"{base_name}_converted.png")
   ```

### Sección 2: Imagen a String RGB (Descomposición)

```python
def image_to_rgb_string(image: Image.Image) -> tuple[str, int, int]:
    """Extrae los valores RGB de una imagen y los convierte a string."""

    # Asegurar que esté en modo RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Obtener dimensiones
    width, height = image.size

    # Convertir a array numpy
    img_array = np.array(image)

    # Aplanar el array
    flat_array = img_array.flatten()

    # Convertir a string separado por comas
    rgb_string = ",".join(map(str, flat_array))

    return rgb_string, width, height
```

**Explicación del proceso de descomposición:**

1. **Imagen a Array NumPy:**
   ```python
   img_array = np.array(image)
   ```

   Una imagen de 3x2 píxeles se ve así en memoria:
   ```
   Imagen visual:        Array NumPy (shape: 2, 3, 3):
   ┌───┬───┬───┐         [
   │ R │ G │ B │           [[255,0,0], [0,255,0], [0,0,255]],  ← Fila 0
   ├───┼───┼───┤           [[255,255,0], [0,255,255], [255,0,255]]  ← Fila 1
   │ Y │ C │ M │         ]
   └───┴───┴───┘
   ```

2. **Aplanar (flatten):**
   ```python
   flat_array = img_array.flatten()
   # [255,0,0, 0,255,0, 0,0,255, 255,255,0, 0,255,255, 255,0,255]
   ```

   Convierte la matriz 3D en un vector 1D.

3. **Convertir a String:**
   ```python
   rgb_string = ",".join(map(str, flat_array))
   # "255,0,0,0,255,0,0,0,255,255,255,0,0,255,255,255,0,255"
   ```

**Diagrama del proceso:**
```
┌─────────────────┐
│  PIL Image      │
│  (RGB, 3x2)     │
└────────┬────────┘
         │ np.array()
         ▼
┌─────────────────┐
│  NumPy Array    │
│  shape(2,3,3)   │
└────────┬────────┘
         │ flatten()
         ▼
┌─────────────────┐
│  Vector 1D      │
│  [255,0,0,...]  │
└────────┬────────┘
         │ ",".join()
         ▼
┌─────────────────┐
│  String         │
│  "255,0,0,..."  │
└─────────────────┘
```

### Sección 3: String RGB a Imagen (Reconstrucción)

```python
def rgb_string_to_image(rgb_string: str, width: int, height: int) -> Image.Image:
    """Reconstruye una imagen desde un string de valores RGB."""

    # Parsear string a lista de enteros
    values = list(map(int, rgb_string.split(",")))

    # Convertir a array numpy
    img_array = np.array(values, dtype=np.uint8)

    # Reshape a dimensiones originales
    img_array = img_array.reshape((height, width, 3))

    # Crear imagen PIL
    image = Image.fromarray(img_array, mode="RGB")

    return image
```

**Explicación del proceso de reconstrucción:**

1. **Parsear String:**
   ```python
   values = list(map(int, rgb_string.split(",")))
   # "255,0,0,0,255,0" → [255, 0, 0, 0, 255, 0]
   ```

2. **Crear Array con tipo correcto:**
   ```python
   img_array = np.array(values, dtype=np.uint8)
   ```
   - `dtype=np.uint8` es crucial: valores de 0-255 (unsigned int de 8 bits)

3. **Reshape:**
   ```python
   img_array = img_array.reshape((height, width, 3))
   ```

   ```
   Vector 1D:              Matriz 3D:
   [255,0,0,0,255,0,       [
    0,0,255,255,255,0,  →    [[255,0,0], [0,255,0], [0,0,255]],
    0,255,255,255,0,255]     [[255,255,0], [0,255,255], [255,0,255]]
                           ]
   ```

4. **Crear Imagen:**
   ```python
   image = Image.fromarray(img_array, mode="RGB")
   ```

---

## gui_upload.py - Interfaz de Carga

### Propósito
Ventana gráfica para seleccionar imágenes, mostrar preview, y guardarlas en la base de datos.

### Imports

```python
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from image_processor import load_and_convert_to_png, image_to_rgb_string
from database import save_image
```

| Import | Uso |
|--------|-----|
| `tkinter` | Biblioteca GUI estándar de Python |
| `filedialog` | Diálogo para seleccionar archivos |
| `messagebox` | Ventanas de alerta/información |
| `ImageTk` | Convertir PIL Image a formato Tkinter |

### Sección 1: Inicialización de la Clase

```python
class UploadWindow:
    def __init__(self, parent=None):
        """Inicializa la ventana de carga de imágenes."""
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()

        self.window.title("Cargar Imagen - Image Decomposer")
        self.window.geometry("600x500")

        # Variables de instancia
        self.current_image = None
        self.png_path = None
        self.photo_image = None

        self._setup_ui()
```

**Explicación:**
- `parent` permite abrir como ventana secundaria o principal
- `tk.Toplevel(parent)` → Ventana hija (no bloquea la principal)
- `tk.Tk()` → Ventana principal
- Variables de instancia guardan el estado actual

### Sección 2: Seleccionar Imagen

```python
def _select_image(self):
    """Abre diálogo para seleccionar imagen y la procesa."""
    filetypes = [
        ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp"),
        ("Todos los archivos", "*.*")
    ]

    filepath = filedialog.askopenfilename(
        title="Seleccionar imagen",
        filetypes=filetypes
    )

    if filepath:
        try:
            # Convertir a PNG
            self.png_path, self.current_image = load_and_convert_to_png(filepath)

            # Mostrar dimensiones
            width, height = self.current_image.size
            self.lbl_dimensions.config(text=f"Dimensiones: {width} x {height} píxeles")

            # Mostrar preview
            self._show_preview()

            # Habilitar botón de guardar
            self.btn_save.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar imagen:\n{str(e)}")
```

**Flujo:**
```
Usuario click "Seleccionar"
         │
         ▼
    filedialog.askopenfilename()
         │
         ▼
    ¿Seleccionó archivo?
         │
    Sí   │   No
    ▼    └──────▶ (nada)
load_and_convert_to_png()
         │
         ▼
    Actualizar UI
    - Mostrar preview
    - Habilitar botón guardar
```

### Sección 3: Mostrar Preview

```python
def _show_preview(self):
    """Muestra la imagen en el canvas."""
    if self.current_image is None:
        return

    # Obtener tamaño del canvas
    canvas_width = self.canvas.winfo_width()
    canvas_height = self.canvas.winfo_height()

    # Calcular tamaño manteniendo proporción
    img_width, img_height = self.current_image.size
    ratio = min(canvas_width / img_width, canvas_height / img_height)

    new_width = int(img_width * ratio * 0.9)
    new_height = int(img_height * ratio * 0.9)

    # Redimensionar para preview
    preview_img = self.current_image.copy()
    preview_img.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)

    # Convertir a PhotoImage (formato Tkinter)
    self.photo_image = ImageTk.PhotoImage(preview_img)

    # Mostrar en canvas
    self.canvas.delete("all")
    self.canvas.create_image(
        canvas_width // 2,
        canvas_height // 2,
        image=self.photo_image,
        anchor=tk.CENTER
    )
```

**Explicación del escalado:**
```python
ratio = min(canvas_width / img_width, canvas_height / img_height)
```

Si tenemos:
- Canvas: 300x200
- Imagen: 1000x500

```
ratio_ancho = 300/1000 = 0.3
ratio_alto = 200/500 = 0.4
ratio = min(0.3, 0.4) = 0.3

Nueva imagen: 1000*0.3 x 500*0.3 = 300x150 (cabe en el canvas)
```

### Sección 4: Guardar en Base de Datos

```python
def _save_to_database(self):
    """Procesa la imagen y la guarda en Supabase."""
    if self.current_image is None:
        return

    try:
        # Deshabilitar botón mientras procesa
        self.btn_save.config(state=tk.DISABLED, text="Procesando...")
        self.window.update()

        # Convertir imagen a string RGB
        rgb_string, width, height = image_to_rgb_string(self.current_image)

        # Guardar en base de datos
        image_id = save_image(width, height, rgb_string)

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
current_image (PIL)
       │
       ▼
image_to_rgb_string()
       │
       ▼
(rgb_string, width, height)
       │
       ▼
save_image(width, height, rgb_string)
       │
       ▼
    ID generado
```

---

## gui_viewer.py - Interfaz de Visualización

### Propósito
Ventana para consultar imágenes por ID y mostrar la reconstrucción.

### Sección Principal: Consultar Imagen

```python
def _query_image(self):
    """Consulta la imagen por ID y la muestra."""
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
        width = image_data["width"]
        height = image_data["height"]
        rgb_string = image_data["rgb_data"]

        # Reconstruir imagen
        self.current_image = rgb_string_to_image(rgb_string, width, height)

        # Mostrar imagen
        self._show_image()

    except Exception as e:
        messagebox.showerror("Error", f"Error al consultar:\n{str(e)}")
```

**Flujo de reconstrucción:**
```
ID ingresado por usuario
         │
         ▼
    get_image(id)
         │
         ▼
{width, height, rgb_data}
         │
         ▼
rgb_string_to_image(rgb_data, width, height)
         │
         ▼
    PIL Image
         │
         ▼
  Mostrar en canvas
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

## Resumen de Flujos

### Flujo de Carga Completo

```
1. Usuario abre main.py
2. Click "Cargar Imagen" → Abre gui_upload.py
3. Click "Seleccionar" → filedialog
4. Selecciona archivo → load_and_convert_to_png()
5. Muestra preview
6. Click "Guardar" → image_to_rgb_string() → save_image()
7. Muestra ID generado
```

### Flujo de Consulta Completo

```
1. Usuario abre main.py
2. Click "Ver Imagen" → Abre gui_viewer.py
3. Ingresa ID
4. Click "Consultar" → get_image()
5. Obtiene datos → rgb_string_to_image()
6. Muestra imagen reconstruida
```

---

## Conceptos Clave de Python Usados

| Concepto | Dónde se usa | Explicación |
|----------|--------------|-------------|
| Singleton | `database.py` | Una sola instancia de conexión |
| Type hints | `def func() -> int:` | Indica tipos de retorno |
| Docstrings | `"""texto"""` | Documentación de funciones |
| Try/except | GUI handlers | Manejo de errores |
| Global | `global _client` | Modificar variable global |
| f-strings | `f"ID: {id}"` | Interpolación de strings |
| Ternary | `x if cond else y` | Condicional en una línea |
| List comprehension | `[x for x in list]` | Crear listas compactas |
