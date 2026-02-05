### Procesamiento de imagenes - Conversion, manipulacion RGB y preview
import numpy as np
import cv2
from PIL import Image, ImageTk
import tkinter as tk


def imagen_a_string_rgb(imagen):
    ### Descompone imagen en valores RGB y convierte a string
    ### Proceso: obtener dimensiones -> aplanar 3D a 1D -> string con comas
    alto, ancho, canales = imagen.shape
    print(f"Descomponiendo imagen de {ancho}x{alto} pixeles")
    print(f"Total de valores RGB: {alto * ancho * canales}")

    ### Aplanar la imagen completa a un vector 1D
    aplanado = imagen.flatten()
    print(f"Vector aplanado: {len(aplanado)} valores")

    ### Convertir a string
    cadena_rgb = ",".join(map(str, aplanado))

    return cadena_rgb, ancho, alto


def string_rgb_a_imagen(cadena_rgb, ancho, alto):
    ### Reconstruye imagen desde string de valores RGB
    ### Proceso: parsear string -> array numpy uint8 -> reshape (alto, ancho, 3)
    print(f"Reconstruyendo imagen de {ancho}x{alto}")

    ### Parsear string a lista de enteros
    valores = list(map(int, cadena_rgb.split(",")))
    print(f"Valores parseados: {len(valores)}")

    ### Crear array numpy con tipo uint8 (0-255) y reshape
    arr = np.array(valores, dtype=np.uint8)
    imagen = arr.reshape((alto, ancho, 3))
    print(f"Imagen reconstruida shape: {imagen.shape}")

    return imagen


def obtener_canales(imagen):
    ### Separa los canales RGB de una imagen
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


def mostrar_en_canvas(canvas, ventana, imagen_rgb, foto_tk_ref, margen=0.9):
    ### Redimensiona imagen y la muestra centrada en un canvas de Tkinter
    ### foto_tk_ref es una lista [None] para mantener la referencia al ImageTk
    ventana.update()
    ancho_canvas = canvas.winfo_width()
    alto_canvas = canvas.winfo_height()
    if ancho_canvas < 10:
        ancho_canvas, alto_canvas = 640, 480

    alto, ancho, _ = imagen_rgb.shape
    ratio = min(ancho_canvas / ancho, alto_canvas / alto) * margen
    vista_previa = cv2.resize(imagen_rgb, (int(ancho * ratio), int(alto * ratio)))

    foto_tk_ref[0] = ImageTk.PhotoImage(Image.fromarray(vista_previa))
    canvas.delete("all")
    canvas.create_image(ancho_canvas // 2, alto_canvas // 2, image=foto_tk_ref[0], anchor=tk.CENTER)
