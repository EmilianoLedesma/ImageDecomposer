### GUI 1: Captura de camara y descomposicion de imagenes
### Usa OpenCV para captura y procesamiento, PIL solo para mostrar en Tkinter
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
from datetime import datetime
from image_processor import imagen_a_string_rgb, calcular_tamano_imagen, mostrar_en_canvas
from database import guardar_imagen


def abrir_ventana_captura(parent=None):
    ### Crea y muestra la ventana de captura de imagenes con camara

    ### Crear ventana
    if parent:
        ventana = tk.Toplevel(parent)
    else:
        ventana = tk.Tk()

    ventana.title("Capturar Imagen - Image Decomposer")
    ventana.geometry("700x550")
    ventana.resizable(True, True)

    ### Variables
    captura = [None]        ### cv2.VideoCapture
    camara_activa = [False] ### flag para el loop
    imagen_actual = [None]  ### numpy array RGB de la foto capturada
    foto_tk = [None]        ### referencia a ImageTk para que no se borre

    ### --- Funciones ---

    def abrir_camara():
        ### Inicializa la camara y arranca el feed en vivo
        if camara_activa[0]:
            return

        captura[0] = cv2.VideoCapture(0)  ### 0 para la camara por defecto

        if not captura[0].isOpened():
            messagebox.showerror("Error", "No se pudo acceder a la camara")
            captura[0] = None
            return

        camara_activa[0] = True
        imagen_actual[0] = None
        print("Camara abierta")

        ### Actualizar botones y labels
        btn_camara.config(state=tk.DISABLED)
        btn_foto.config(state=tk.NORMAL)
        btn_guardar.config(state=tk.DISABLED)
        lbl_estado.config(text="Camara activa - Feed en vivo", fg="green")
        lbl_info.config(text="")
        lbl_id.config(text="")

        ### Iniciar loop de feed
        actualizar_feed()

    def actualizar_feed():
        ### Lee un frame de la camara y lo muestra en el canvas
        if not camara_activa[0] or captura[0] is None or not captura[0].isOpened():
            return

        ret, frame = captura[0].read()  ### lee un frame de la camara
        if ret:
            imagen_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  ### convierte BGR a RGB
            mostrar_en_canvas(canvas, ventana, imagen_rgb, foto_tk, 0.95)

        ventana.after(30, actualizar_feed)  ### ~33 FPS

    def tomar_foto():
        ### Captura el frame actual, detiene la camara y muestra la foto
        if not camara_activa[0] or captura[0] is None or not captura[0].isOpened():
            return

        ret, frame = captura[0].read()
        if not ret:
            messagebox.showerror("Error", "No se pudo capturar el frame")
            return

        ### Guardar foto como numpy array RGB
        imagen_actual[0] = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        ### Detener camara
        detener_camara()

        ### Guardar foto en img/
        carpeta_img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
        marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_foto = os.path.join(carpeta_img, f"foto_{marca_tiempo}.png")
        imagen_bgr = cv2.cvtColor(imagen_actual[0], cv2.COLOR_RGB2BGR)
        cv2.imwrite(ruta_foto, imagen_bgr)
        print(f"Foto guardada en: {ruta_foto}")

        ### Mostrar info
        alto, ancho, canales = imagen_actual[0].shape
        calcular_tamano_imagen(imagen_actual[0])
        print(f"Foto capturada - Shape: {imagen_actual[0].shape}")

        lbl_estado.config(text="Foto capturada", fg="blue")
        lbl_info.config(text=f"Dimensiones: {ancho} x {alto} px | Canales: {canales}\nGuardada en: {ruta_foto}")
        lbl_id.config(text="")

        ### Mostrar preview
        mostrar_en_canvas(canvas, ventana, imagen_actual[0], foto_tk)

        ### Habilitar boton guardar
        btn_guardar.config(state=tk.NORMAL)

    def detener_camara():
        ### Libera la camara y limpia variables
        camara_activa[0] = False
        if captura[0] is not None:
            captura[0].release()
            captura[0] = None
            print("Camara liberada")

        btn_camara.config(state=tk.NORMAL)
        btn_foto.config(state=tk.DISABLED)

    def guardar_en_bd():
        ### Descompone la imagen en RGB y la guarda en Supabase
        if imagen_actual[0] is None:
            messagebox.showwarning("Advertencia", "No hay imagen para guardar")
            return

        try:
            btn_guardar.config(state=tk.DISABLED, text="Procesando...")
            ventana.update()

            cadena_rgb, ancho, alto = imagen_a_string_rgb(imagen_actual[0])
            id_imagen = guardar_imagen(ancho, alto, cadena_rgb)

            lbl_id.config(text=f"Imagen guardada con ID: {id_imagen}", fg="green")
            messagebox.showinfo(
                "Exito",
                f"Imagen guardada correctamente.\nID: {id_imagen}\n\nUsa este ID para recuperar la imagen."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
            lbl_id.config(text="Error al guardar", fg="red")

        finally:
            btn_guardar.config(state=tk.NORMAL, text="Guardar en Base de Datos")

    def cerrar_ventana(event=None):
        ### Libera la camara y cierra la ventana
        detener_camara()
        ventana.destroy()

    ### --- Construir UI ---

    ### Frame superior
    frame_superior = tk.Frame(ventana, padx=20, pady=10)
    frame_superior.pack(fill=tk.X)

    tk.Label(
        frame_superior,
        text="Capturar y Descomponer Imagen",
        font=("Arial", 16, "bold")
    ).pack(pady=(0, 10))

    ### Frame de botones de camara
    frame_botones = tk.Frame(frame_superior)
    frame_botones.pack(pady=5)

    btn_camara = tk.Button(
        frame_botones,
        text="Abrir Camara",
        command=abrir_camara,
        font=("Arial", 11),
        width=15,
        height=2
    )
    btn_camara.pack(side=tk.LEFT, padx=5)

    btn_foto = tk.Button(
        frame_botones,
        text="Tomar Foto",
        command=tomar_foto,
        font=("Arial", 11),
        width=15,
        height=2,
        state=tk.DISABLED
    )
    btn_foto.pack(side=tk.LEFT, padx=5)

    ### Label de estado
    lbl_estado = tk.Label(
        frame_superior,
        text="Presiona 'Abrir Camara' para comenzar",
        font=("Arial", 9),
        fg="gray"
    )
    lbl_estado.pack(pady=5)

    ### Frame inferior
    frame_inferior = tk.Frame(ventana, padx=20, pady=10)
    frame_inferior.pack(fill=tk.X, side=tk.BOTTOM)

    lbl_id = tk.Label(frame_inferior, text="", font=("Arial", 12, "bold"), fg="green")
    lbl_id.pack(pady=5)

    btn_guardar = tk.Button(
        frame_inferior,
        text="Guardar en Base de Datos",
        command=guardar_en_bd,
        font=("Arial", 11),
        width=25,
        height=2,
        state=tk.DISABLED
    )
    btn_guardar.pack(pady=5)

    lbl_info = tk.Label(frame_inferior, text="", font=("Arial", 10))
    lbl_info.pack(pady=5)

    ### Frame central - preview
    frame_central = tk.Frame(ventana, padx=20)
    frame_central.pack(fill=tk.BOTH, expand=True)

    frame_preview = tk.LabelFrame(frame_central, text="Camara / Vista Previa", padx=10, pady=10)
    frame_preview.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame_preview, width=640, height=480, bg="lightgray")
    canvas.pack(fill=tk.BOTH, expand=True)

    ### Presionar 'q' para cerrar la ventana y liberar la camara
    ventana.bind('<q>', cerrar_ventana)
    ventana.protocol("WM_DELETE_WINDOW", cerrar_ventana)

    return ventana


### Para pruebas directas
if __name__ == "__main__":
    ventana = abrir_ventana_captura()
    ventana.mainloop()
