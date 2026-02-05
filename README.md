<div align="center">

<!-- Header Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=180&section=header&text=Image%20Decomposer&fontSize=42&fontColor=fff&animation=twinkling&fontAlignY=32&desc=Sistema%20de%20Descomposicion%20y%20Reconstruccion%20de%20Imagenes%20RGB&descAlignY=52&descSize=18"/>

<!-- Badges -->
<p>
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/OpenCV-cv2-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV"/>
  <img src="https://img.shields.io/badge/Supabase-Database-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" alt="Supabase"/>
  <img src="https://img.shields.io/badge/Tkinter-GUI-FF6F00?style=for-the-badge&logo=python&logoColor=white" alt="Tkinter"/>
  <img src="https://img.shields.io/badge/License-MIT-F7DF1E?style=for-the-badge" alt="License"/>
</p>

<p>
  <img src="https://img.shields.io/badge/Estado-Activo-success?style=flat-square" alt="Estado"/>
  <img src="https://img.shields.io/badge/Version-1.0.0-blue?style=flat-square" alt="Version"/>
  <img src="https://img.shields.io/badge/PRs-Bienvenidos-brightgreen?style=flat-square" alt="PRs"/>
</p>

</div>

---

## Tabla de Contenidos

- [Descripcion](#descripcion)
- [Caracteristicas](#caracteristicas)
- [Arquitectura](#arquitectura)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalacion](#instalacion)
- [Uso](#uso)
- [Tecnologias](#tecnologias)
- [Formato de Datos](#formato-de-datos)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

---

## Descripcion

**Image Decomposer** es una aplicacion de escritorio que demuestra como las imagenes digitales se componen de matrices de valores RGB. Utiliza **OpenCV (cv2)** y **NumPy** para la captura de camara y procesamiento de imagenes, siguiendo los conceptos del curso de Sistemas Inteligentes.

```python
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
print(frame.shape)  # (alto, ancho, canales)
print(frame.dtype)  # uint8
cap.release()
```

<div align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1000&color=3ECF8E&center=true&vCenter=true&random=false&width=600&lines=Carga+cualquier+imagen;Descompone+pixel+por+pixel;Almacena+en+la+nube;Reconstruye+cuando+quieras" alt="Typing SVG" />
</div>

---

## Caracteristicas

<table>
<tr>
<td width="50%">

### Captura de Imagenes
- Captura en vivo desde **camara web** con OpenCV
- Feed en tiempo real (~33 FPS)
- Captura de foto con un click

</td>
<td width="50%">

### Procesamiento RGB
- Extraccion pixel por pixel
- Operaciones matriciales con NumPy
- Algoritmo optimizado

</td>
</tr>
<tr>
<td width="50%">

### Almacenamiento Cloud
- Base de datos Supabase
- ID unico por imagen
- Acceso desde cualquier lugar

</td>
<td width="50%">

### Reconstruccion
- Recuperacion por ID
- Regeneracion perfecta
- Visualizacion inmediata

</td>
</tr>
</table>

---

## Arquitectura

```
                        ╔══════════════════════════════════════════════════╗
                        ║            IMAGE DECOMPOSER SYSTEM               ║
                        ╚══════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                FLUJO DE CARGA                                   │
└─────────────────────────────────────────────────────────────────────────────────┘

      ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
      │              │          │              │          │              │
      │    Upload    │  ─────▶  │   Process    │  ─────▶  │    Cloud     │
      │     GUI      │          │    Engine    │          │   Storage    │
      │              │          │              │          │              │
      └──────────────┘          └──────────────┘          └──────┬───────┘
                                                                 │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FLUJO DE CONSULTA                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                                                 │
      ┌──────────────┐          ┌──────────────┐                 │
      │              │          │              │                 │
      │    Viewer    │  ◀─────  │   Process    │  ◀──────────────┘
      │     GUI      │          │    Engine    │
      │              │          │              │
      └──────────────┘          └──────────────┘
```

---

## Estructura del Proyecto

```
ImageDecomposer/
│
├── main.py               # Punto de entrada principal
├── gui_upload.py         # Interfaz para capturar imagenes
├── gui_viewer.py         # Interfaz para visualizar imagenes
├── database.py           # Operaciones con Supabase
├── image_processor.py    # Logica de procesamiento RGB y preview
├── config.py             # Configuracion y variables
├── img/                  # Fotos capturadas desde la camara
├── requirements.txt      # Dependencias del proyecto
├── DOCUMENTACION.md      # Documentacion tecnica detallada
├── .env                  # Variables de entorno (no incluido)
├── .gitignore            # Archivos ignorados por Git
└── README.md             # Este archivo
```

---

## Instalacion

### Prerequisitos

- Python 3.10 o superior
- Cuenta en [Supabase](https://supabase.com) (gratuita)
- Git instalado

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/ImageDecomposer.git
cd ImageDecomposer
```

### Paso 2: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Configurar Supabase

<details>
<summary><b>3.1 Crear proyecto en Supabase</b></summary>

1. Ve a [supabase.com](https://supabase.com) y crea una cuenta
2. Crea un nuevo proyecto
3. Espera a que se inicialice (~2 minutos)

</details>

<details>
<summary><b>3.2 Crear la tabla</b></summary>

Ejecuta en el **SQL Editor** de Supabase:

```sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    rgb_data TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habilitar acceso publico (RLS)
ALTER TABLE images ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Permitir insertar imagenes"
ON images FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Permitir leer imagenes"
ON images FOR SELECT TO anon USING (true);
```

</details>

<details>
<summary><b>3.3 Obtener credenciales</b></summary>

- Ve a **Settings** → **API**
- Copia `Project URL` y `anon public key`

</details>

### Paso 4: Configurar variables de entorno

Crea un archivo `.env` en la raiz del proyecto:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_anon_key_aqui
```

---

## Uso

### Ejecutar la aplicacion

```bash
python main.py
```

### Capturar Imagen

1. Click en **"Cargar Imagen"**
2. Click en **"Abrir Camara"** para ver el feed en vivo
3. Click en **"Tomar Foto"** para capturar
4. Click en **"Guardar en Base de Datos"**
5. Anota el **ID** generado

### Ver Imagen

1. Click en **"Ver Imagen"**
2. Ingresa el **ID** de la imagen
3. Click en **"Consultar"**
4. Visualiza la imagen reconstruida

---

## Tecnologias

<div align="center">

| Tecnologia | Descripcion | Badge |
|:----------:|:-----------:|:-----:|
| **Python** | Lenguaje principal | ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white) |
| **OpenCV** | Lectura y procesamiento de imagenes | ![OpenCV](https://img.shields.io/badge/-OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white) |
| **NumPy** | Operaciones matriciales (flatten, reshape) | ![NumPy](https://img.shields.io/badge/-NumPy-013243?style=flat-square&logo=numpy&logoColor=white) |
| **Pillow (PIL)** | Conversion NumPy → ImageTk (solo para Tkinter) | ![Pillow](https://img.shields.io/badge/-Pillow-3776AB?style=flat-square&logo=python&logoColor=white) |
| **Supabase** | Base de datos PostgreSQL en la nube | ![Supabase](https://img.shields.io/badge/-Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white) |
| **Tkinter** | Interfaz grafica | ![Tkinter](https://img.shields.io/badge/-Tkinter-FF6F00?style=flat-square&logo=python&logoColor=white) |

</div>

---

## Formato de Datos

La imagen se almacena como una cadena de valores RGB:

```
"R,G,B,R,G,B,R,G,B,..."
```

<div align="center">

| Campo | Tipo | Descripcion |
|:-----:|:----:|:-----------:|
| `id` | INTEGER | Identificador unico |
| `width` | INTEGER | Ancho en pixeles |
| `height` | INTEGER | Alto en pixeles |
| `rgb_data` | TEXT | Valores RGB separados por coma |
| `created_at` | TIMESTAMP | Fecha de creacion |

</div>

---

## Licencia

<div align="center">

Este proyecto esta bajo la **Licencia MIT**.

</div>

<!-- Footer -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer"/>
