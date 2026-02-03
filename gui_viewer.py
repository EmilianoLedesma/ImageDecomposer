"""
GUI 2: Consulta y reconstruccion de imagenes
Usa OpenCV/numpy para procesamiento, PIL solo para mostrar en Tkinter
"""
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from image_processor import string_rgb_a_imagen
from database import get_image


def abrir_ventana_visor(parent=None):
    """Crea y muestra la ventana de consulta y reconstruccion de imagenes."""

    ### Crear ventana
    if parent:
        ventana = tk.Toplevel(parent)
    else:
        ventana = tk.Tk()

    ventana.title("Ver Imagen - Image Decomposer")
    ventana.geometry("600x550")
    ventana.resizable(True, True)

    ### Variables
    imagen_actual = [None]
    foto_tk = [None]

    ### --- Funciones ---

    def consultar_imagen():
        """Consulta la imagen por ID y la reconstruye."""
        id_texto = entrada_id.get().strip()

        if not id_texto:
            messagebox.showwarning("Advertencia", "Ingresa un ID de imagen")
            return

        try:
            image_id = int(id_texto)
        except ValueError:
            messagebox.showerror("Error", "El ID debe ser un numero entero")
            return

        try:
            lbl_estado.config(text="Consultando...", fg="blue")
            btn_consultar.config(state=tk.DISABLED)
            ventana.update()

            ### Consultar base de datos
            datos = get_image(image_id)

            ### Extraer datos
            ancho = datos["width"]
            alto = datos["height"]
            rgb_string = datos["rgb_data"]
            created_at = datos.get("created_at", "N/A")

            print(f"Datos recibidos - Ancho: {ancho}, Alto: {alto}")
            print(f"Longitud rgb_string: {len(rgb_string)}")
            print(f"Valores esperados: {ancho * alto * 3}")

            ### Reconstruir imagen (retorna numpy array RGB)
            imagen_actual[0] = string_rgb_a_imagen(rgb_string, ancho, alto)

            ### Mostrar info
            lbl_dimensiones.config(
                text=f"Dimensiones: {ancho} x {alto} px | Shape: {imagen_actual[0].shape}"
            )
            lbl_creado.config(text=f"Creado: {created_at}")

            ### Mostrar imagen reconstruida
            mostrar_imagen()

            lbl_estado.config(text=f"Imagen #{image_id} reconstruida correctamente", fg="green")

        except Exception as e:
            messagebox.showerror("Error", f"Error al consultar:\n{str(e)}")
            lbl_estado.config(text="Error en la consulta", fg="red")
            limpiar_display()

        finally:
            btn_consultar.config(state=tk.NORMAL)

    def mostrar_imagen():
        """Muestra la imagen reconstruida en el canvas."""
        if imagen_actual[0] is None:
            return

        ventana.update()
        ancho_canvas = canvas.winfo_width()
        alto_canvas = canvas.winfo_height()

        if ancho_canvas < 10:
            ancho_canvas = 400
            alto_canvas = 300

        alto, ancho, _ = imagen_actual[0].shape
        ratio = min(ancho_canvas / ancho, alto_canvas / alto) * 0.9
        nuevo_ancho = int(ancho * ratio)
        nuevo_alto = int(alto * ratio)

        ### Redimensionar con cv2
        preview = cv2.resize(imagen_actual[0], (nuevo_ancho, nuevo_alto))

        ### Convertir numpy array a PIL Image para Tkinter
        imagen_pil = Image.fromarray(preview)
        foto_tk[0] = ImageTk.PhotoImage(imagen_pil)

        canvas.delete("all")
        canvas.create_image(
            ancho_canvas // 2,
            alto_canvas // 2,
            image=foto_tk[0],
            anchor=tk.CENTER
        )

    def limpiar_display():
        """Limpia la visualizacion."""
        canvas.delete("all")
        lbl_dimensiones.config(text="")
        lbl_creado.config(text="")
        imagen_actual[0] = None
        foto_tk[0] = None

    ### --- Construir UI ---

    ### Frame principal
    frame_principal = tk.Frame(ventana, padx=20, pady=20)
    frame_principal.pack(fill=tk.BOTH, expand=True)

    ### Titulo
    tk.Label(
        frame_principal,
        text="Consultar y Reconstruir Imagen",
        font=("Arial", 16, "bold")
    ).pack(pady=(0, 20))

    ### Frame para entrada de ID
    frame_entrada = tk.Frame(frame_principal)
    frame_entrada.pack(pady=10)

    tk.Label(frame_entrada, text="ID de la imagen:", font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 10))

    entrada_id = tk.Entry(frame_entrada, font=("Arial", 12), width=15)
    entrada_id.pack(side=tk.LEFT, padx=(0, 10))
    entrada_id.bind("<Return>", lambda e: consultar_imagen())

    btn_consultar = tk.Button(
        frame_entrada,
        text="Consultar",
        command=consultar_imagen,
        font=("Arial", 11),
        width=12
    )
    btn_consultar.pack(side=tk.LEFT)

    ### Frame para informacion
    frame_info = tk.Frame(frame_principal)
    frame_info.pack(pady=10, fill=tk.X)

    lbl_dimensiones = tk.Label(frame_info, text="", font=("Arial", 10))
    lbl_dimensiones.pack()

    lbl_creado = tk.Label(frame_info, text="", font=("Arial", 9), fg="gray")
    lbl_creado.pack()

    ### Frame para la imagen
    frame_imagen = tk.LabelFrame(frame_principal, text="Imagen Reconstruida", padx=10, pady=10)
    frame_imagen.pack(fill=tk.BOTH, expand=True, pady=10)

    canvas = tk.Canvas(frame_imagen, width=400, height=300, bg="lightgray")
    canvas.pack(expand=True, fill=tk.BOTH)

    ### Label de estado
    lbl_estado = tk.Label(
        frame_principal,
        text="Ingresa un ID para consultar",
        font=("Arial", 10),
        fg="gray"
    )
    lbl_estado.pack(pady=10)

    return ventana


### Para pruebas directas
if __name__ == "__main__":
    ventana = abrir_ventana_visor()
    ventana.mainloop()
