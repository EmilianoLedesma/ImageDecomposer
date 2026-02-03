"""
Módulo de procesamiento de imágenes - Conversión y manipulación RGB
Usa OpenCV (cv2) siguiendo el estilo del curso
"""
import cv2
import numpy as np


def cargar_imagen(path: str):
    """
    Carga una imagen desde cualquier formato.
    Retorna la imagen en formato RGB (convertida desde BGR de OpenCV).
    """
    # Leer imagen con OpenCV (lee en BGR)
    imagen = cv2.imread(path)

    if imagen is None:
        raise Exception(f"No se pudo cargar la imagen: {path}")

    # Mostrar info como en clase
    print(f"Shape: {imagen.shape}")  # (alto, ancho, canales)
    print(f"Dtype: {imagen.dtype}")  # uint8
    print(f"Size: {imagen.size}")    # alto * ancho * canales

    # Convertir de BGR a RGB (OpenCV usa BGR por defecto)
    imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

    return imagen_rgb


def imagen_a_string_rgb(imagen) -> tuple:
    """
    Descompone una imagen en sus valores RGB y los convierte a string.

    Proceso:
    1. Obtener dimensiones (alto, ancho, canales)
    2. Aplanar matriz 3D a vector 1D
    3. Convertir a string separado por comas
    """
    # Obtener dimensiones
    alto, ancho, canales = imagen.shape
    print(f"Descomponiendo imagen de {ancho}x{alto} pixeles")
    print(f"Total de valores RGB: {alto * ancho * canales}")

    # Separar canales como en clase
    r = imagen[:, :, 0]  # Canal Rojo
    g = imagen[:, :, 1]  # Canal Verde
    b = imagen[:, :, 2]  # Canal Azul

    print(f"Canal R shape: {r.shape}")
    print(f"Canal G shape: {g.shape}")
    print(f"Canal B shape: {b.shape}")

    # Aplanar la imagen completa a un vector 1D
    flat = imagen.flatten()
    print(f"Vector aplanado: {len(flat)} valores")

    # Convertir a string
    rgb_string = ",".join(map(str, flat))

    return rgb_string, ancho, alto


def string_rgb_a_imagen(rgb_string: str, ancho: int, alto: int):
    """
    Reconstruye una imagen desde un string de valores RGB.

    Proceso:
    1. Parsear string a lista de enteros
    2. Convertir a array numpy uint8
    3. Reshape a (alto, ancho, 3)
    """
    print(f"Reconstruyendo imagen de {ancho}x{alto}")

    # Parsear string a lista de enteros
    valores = list(map(int, rgb_string.split(",")))
    print(f"Valores parseados: {len(valores)}")

    # Crear array numpy con tipo uint8 (0-255)
    arr = np.array(valores, dtype=np.uint8)

    # Reshape a dimensiones originales (alto, ancho, 3)
    imagen = arr.reshape((alto, ancho, 3))
    print(f"Imagen reconstruida shape: {imagen.shape}")

    return imagen


def obtener_canales(imagen):
    """
    Separa los canales RGB de una imagen.
    Similar a canales_naturales.py del profesor.
    """
    r = imagen[:, :, 0]
    g = imagen[:, :, 1]
    b = imagen[:, :, 2]

    # Crear imágenes de cada canal
    R = np.zeros_like(imagen)
    R[:, :, 0] = r

    G = np.zeros_like(imagen)
    G[:, :, 1] = g

    B = np.zeros_like(imagen)
    B[:, :, 2] = b

    return R, G, B


def calcular_tamano_imagen(imagen):
    """
    Calcula el tamaño de una imagen en memoria.
    """
    alto, ancho, canales = imagen.shape
    bytes_por_pixel = canales * 1  # uint8 = 1 byte
    tamano_bytes = alto * ancho * bytes_por_pixel
    tamano_kb = tamano_bytes / 1024
    tamano_mb = tamano_kb / 1024

    print(f"Dimensiones: {ancho}x{alto}")
    print(f"Canales: {canales}")
    print(f"Total pixeles: {alto * ancho}")
    print(f"Tamaño en memoria: {tamano_kb:.2f} KB ({tamano_mb:.4f} MB)")

    return tamano_bytes
