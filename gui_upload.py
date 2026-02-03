"""
GUI 1: Carga y descomposición de imágenes
Usa OpenCV para procesamiento, PIL solo para mostrar en Tkinter
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
from image_processor import cargar_imagen, imagen_a_string_rgb, calcular_tamano_imagen
from database import save_image


class UploadWindow:
    def __init__(self, parent=None):
        """Inicializa la ventana de carga de imágenes."""
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()

        self.window.title("Cargar Imagen - Image Decomposer")
        self.window.geometry("600x500")
        self.window.resizable(True, True)

        # Variables - imagen es array numpy (cv2)
        self.imagen_actual = None
        self.ruta_imagen = None
        self.photo_image = None

        self._setup_ui()

    def _setup_ui(self):
        """Configura los componentes de la interfaz."""
        # Frame superior
        top_frame = tk.Frame(self.window, padx=20, pady=10)
        top_frame.pack(fill=tk.X)

        # Título
        tk.Label(
            top_frame,
            text="Cargar y Descomponer Imagen",
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 10))

        # Botón seleccionar imagen
        self.btn_select = tk.Button(
            top_frame,
            text="Seleccionar Imagen",
            command=self._seleccionar_imagen,
            font=("Arial", 11),
            width=20,
            height=2
        )
        self.btn_select.pack(pady=5)

        # Label para ruta
        self.lbl_ruta = tk.Label(
            top_frame,
            text="No hay imagen seleccionada",
            font=("Arial", 9),
            fg="gray",
            wraplength=500
        )
        self.lbl_ruta.pack(pady=5)

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
        preview_frame = tk.LabelFrame(center_frame, text="Vista Previa", padx=10, pady=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas para mostrar imagen
        self.canvas = tk.Canvas(preview_frame, width=300, height=150, bg="lightgray")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _seleccionar_imagen(self):
        """Abre diálogo para seleccionar imagen y la procesa con cv2."""
        filetypes = [
            ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("Todos los archivos", "*.*")
        ]

        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=filetypes
        )

        if ruta:
            try:
                self.ruta_imagen = ruta

                # Cargar imagen con cv2 (retorna numpy array RGB)
                self.imagen_actual = cargar_imagen(ruta)

                # Obtener dimensiones (alto, ancho, canales)
                alto, ancho, canales = self.imagen_actual.shape

                # Calcular tamaño
                calcular_tamano_imagen(self.imagen_actual)

                # Actualizar labels
                self.lbl_ruta.config(text=f"Archivo: {ruta}", fg="black")
                self.lbl_info.config(
                    text=f"Dimensiones: {ancho} x {alto} px | Canales: {canales}"
                )

                # Mostrar preview
                self._mostrar_preview()

                # Habilitar botón de guardar
                self.btn_guardar.config(state=tk.NORMAL)

                # Limpiar ID anterior
                self.lbl_id.config(text="")

            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar imagen:\n{str(e)}")

    def _mostrar_preview(self):
        """Muestra la imagen (numpy array) en el canvas de Tkinter."""
        if self.imagen_actual is None:
            return

        # Obtener tamaño del canvas
        self.window.update()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width < 10:
            canvas_width = 300
            canvas_height = 150

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

    def run(self):
        """Inicia el loop principal de la ventana."""
        self.window.mainloop()


# Para pruebas directas
if __name__ == "__main__":
    app = UploadWindow()
    app.run()
