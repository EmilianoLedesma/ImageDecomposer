"""
GUI 1: Captura de cámara y descomposición de imágenes
Usa OpenCV para captura de cámara y procesamiento, PIL solo para mostrar en Tkinter
"""
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from image_processor import imagen_a_string_rgb, calcular_tamano_imagen
from database import save_image


class UploadWindow:
    def __init__(self, parent=None):
        """Inicializa la ventana de captura de cámara."""
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()

        self.window.title("Capturar Imagen - Image Decomposer")
        self.window.geometry("700x550")
        self.window.resizable(True, True)

        # Variables - imagen es array numpy (cv2)
        self.imagen_actual = None
        self.photo_image = None

        # Variables de cámara
        self.cap = None
        self.camara_activa = False

        # Cleanup al cerrar ventana
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        self._setup_ui()

    def _setup_ui(self):
        """Configura los componentes de la interfaz."""
        # Frame superior
        top_frame = tk.Frame(self.window, padx=20, pady=10)
        top_frame.pack(fill=tk.X)

        # Título
        tk.Label(
            top_frame,
            text="Capturar y Descomponer Imagen",
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 10))

        # Frame de botones de cámara
        btn_frame = tk.Frame(top_frame)
        btn_frame.pack(pady=5)

        # Botón abrir cámara
        self.btn_camara = tk.Button(
            btn_frame,
            text="Abrir Cámara",
            command=self._abrir_camara,
            font=("Arial", 11),
            width=15,
            height=2
        )
        self.btn_camara.pack(side=tk.LEFT, padx=5)

        # Botón tomar foto
        self.btn_foto = tk.Button(
            btn_frame,
            text="Tomar Foto",
            command=self._tomar_foto,
            font=("Arial", 11),
            width=15,
            height=2,
            state=tk.DISABLED
        )
        self.btn_foto.pack(side=tk.LEFT, padx=5)

        # Label de estado
        self.lbl_estado = tk.Label(
            top_frame,
            text="Cámara no iniciada",
            font=("Arial", 9),
            fg="gray"
        )
        self.lbl_estado.pack(pady=5)

        # Frame inferior - botones de acción
        bottom_frame = tk.Frame(self.window, padx=20, pady=10)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Label para ID generado
        self.lbl_id = tk.Label(
            bottom_frame,
            text="",
            font=("Arial", 12, "bold"),
            fg="green"
        )
        self.lbl_id.pack(pady=5)

        # Botón guardar en BD
        self.btn_guardar = tk.Button(
            bottom_frame,
            text="Guardar en Base de Datos",
            command=self._guardar_en_bd,
            font=("Arial", 11),
            width=25,
            height=2,
            state=tk.DISABLED
        )
        self.btn_guardar.pack(pady=5)

        # Label para dimensiones
        self.lbl_info = tk.Label(
            bottom_frame,
            text="",
            font=("Arial", 10)
        )
        self.lbl_info.pack(pady=5)

        # Frame central para preview
        center_frame = tk.Frame(self.window, padx=20)
        center_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para preview
        preview_frame = tk.LabelFrame(center_frame, text="Cámara / Vista Previa", padx=10, pady=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas para mostrar imagen
        self.canvas = tk.Canvas(preview_frame, width=640, height=480, bg="lightgray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _abrir_camara(self):
        """Inicializa cv2.VideoCapture(0) y arranca el loop de feed."""
        if self.camara_activa:
            return

        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            messagebox.showerror("Error", "No se pudo acceder a la cámara")
            self.cap = None
            return

        self.camara_activa = True
        self.imagen_actual = None

        # Actualizar UI
        self.btn_camara.config(state=tk.DISABLED)
        self.btn_foto.config(state=tk.NORMAL)
        self.btn_guardar.config(state=tk.DISABLED)
        self.lbl_estado.config(text="Cámara activa - Feed en vivo", fg="green")
        self.lbl_info.config(text="")
        self.lbl_id.config(text="")

        # Iniciar loop de actualización
        self._actualizar_feed()

    def _actualizar_feed(self):
        """Lee frame de la cámara, convierte BGR→RGB, muestra en canvas."""
        if not self.camara_activa or self.cap is None or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if ret:
            # Convertir BGR → RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Obtener tamaño del canvas
            self.window.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if canvas_width < 10:
                canvas_width = 640
                canvas_height = 480

            # Obtener dimensiones del frame
            alto, ancho, _ = frame_rgb.shape

            # Calcular ratio para mantener proporción
            ratio = min(canvas_width / ancho, canvas_height / alto) * 0.95

            nuevo_ancho = int(ancho * ratio)
            nuevo_alto = int(alto * ratio)

            # Redimensionar para preview
            preview = cv2.resize(frame_rgb, (nuevo_ancho, nuevo_alto))

            # Convertir a formato Tkinter
            pil_image = Image.fromarray(preview)
            self.photo_image = ImageTk.PhotoImage(pil_image)

            # Mostrar en canvas
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                image=self.photo_image,
                anchor=tk.CENTER
            )

        # Programar siguiente actualización (~33 FPS)
        self.window.after(30, self._actualizar_feed)

    def _tomar_foto(self):
        """Captura el frame actual, detiene la cámara y muestra preview."""
        if not self.camara_activa or self.cap is None or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            messagebox.showerror("Error", "No se pudo capturar el frame")
            return

        # Convertir BGR → RGB y guardar como imagen actual
        self.imagen_actual = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detener la cámara
        self._detener_camara()

        # Obtener dimensiones
        alto, ancho, canales = self.imagen_actual.shape
        calcular_tamano_imagen(self.imagen_actual)

        # Actualizar UI
        self.lbl_estado.config(text="Foto capturada", fg="blue")
        self.lbl_info.config(
            text=f"Dimensiones: {ancho} x {alto} px | Canales: {canales}"
        )

        # Mostrar preview de la foto capturada
        self._mostrar_preview()

        # Habilitar botón de guardar
        self.btn_guardar.config(state=tk.NORMAL)

        # Limpiar ID anterior
        self.lbl_id.config(text="")

    def _detener_camara(self):
        """Libera la cámara y limpia variables."""
        self.camara_activa = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        # Actualizar botones
        self.btn_camara.config(state=tk.NORMAL)
        self.btn_foto.config(state=tk.DISABLED)

    def _mostrar_preview(self):
        """Muestra la imagen (numpy array) en el canvas de Tkinter."""
        if self.imagen_actual is None:
            return

        # Obtener tamaño del canvas
        self.window.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width < 10:
            canvas_width = 640
            canvas_height = 480

        # Obtener dimensiones de la imagen
        alto, ancho, _ = self.imagen_actual.shape

        # Calcular ratio para mantener proporción
        ratio = min(canvas_width / ancho, canvas_height / alto) * 0.9

        nuevo_ancho = int(ancho * ratio)
        nuevo_alto = int(alto * ratio)

        # Redimensionar con cv2
        preview = cv2.resize(self.imagen_actual, (nuevo_ancho, nuevo_alto))

        # Convertir numpy array a PIL Image para Tkinter
        pil_image = Image.fromarray(preview)
        self.photo_image = ImageTk.PhotoImage(pil_image)

        # Mostrar en canvas
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            image=self.photo_image,
            anchor=tk.CENTER
        )

    def _guardar_en_bd(self):
        """Descompone la imagen en RGB y la guarda en Supabase."""
        if self.imagen_actual is None:
            messagebox.showwarning("Advertencia", "No hay imagen para guardar")
            return

        try:
            # Deshabilitar botón mientras procesa
            self.btn_guardar.config(state=tk.DISABLED, text="Procesando...")
            self.window.update()

            # Convertir imagen a string RGB
            rgb_string, ancho, alto = imagen_a_string_rgb(self.imagen_actual)

            # Guardar en base de datos
            image_id = save_image(ancho, alto, rgb_string)

            # Mostrar ID generado
            self.lbl_id.config(
                text=f"Imagen guardada con ID: {image_id}",
                fg="green"
            )

            messagebox.showinfo(
                "Éxito",
                f"Imagen guardada correctamente.\nID: {image_id}\n\nUsa este ID para recuperar la imagen."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar:\n{str(e)}")
            self.lbl_id.config(text="Error al guardar", fg="red")

        finally:
            self.btn_guardar.config(state=tk.NORMAL, text="Guardar en Base de Datos")

    def _on_close(self):
        """Cleanup al cerrar la ventana: libera la cámara."""
        self._detener_camara()
        self.window.destroy()

    def run(self):
        """Inicia el loop principal de la ventana."""
        self.window.mainloop()


# Para pruebas directas
if __name__ == "__main__":
    app = UploadWindow()
    app.run()
