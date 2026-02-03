"""
GUI 2: Consulta y reconstrucción de imágenes
Usa OpenCV/numpy para procesamiento, PIL solo para mostrar en Tkinter
"""
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
from image_processor import string_rgb_a_imagen
from database import get_image


class ViewerWindow:
    def __init__(self, parent=None):
        """Inicializa la ventana de visualización de imágenes."""
        if parent:
            self.window = tk.Toplevel(parent)
        else:
            self.window = tk.Tk()

        self.window.title("Ver Imagen - Image Decomposer")
        self.window.geometry("600x550")
        self.window.resizable(True, True)

        # Variables - imagen es numpy array
        self.imagen_actual = None
        self.photo_image = None

        self._setup_ui()

    def _setup_ui(self):
        """Configura los componentes de la interfaz."""
        # Frame principal
        main_frame = tk.Frame(self.window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        tk.Label(
            main_frame,
            text="Consultar y Reconstruir Imagen",
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 20))

        # Frame para entrada de ID
        input_frame = tk.Frame(main_frame)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="ID de la imagen:", font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 10))

        self.entry_id = tk.Entry(input_frame, font=("Arial", 12), width=15)
        self.entry_id.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_id.bind("<Return>", lambda e: self._consultar_imagen())

        self.btn_consultar = tk.Button(
            input_frame,
            text="Consultar",
            command=self._consultar_imagen,
            font=("Arial", 11),
            width=12
        )
        self.btn_consultar.pack(side=tk.LEFT)

        # Frame para información
        info_frame = tk.Frame(main_frame)
        info_frame.pack(pady=10, fill=tk.X)

        self.lbl_dimensiones = tk.Label(info_frame, text="", font=("Arial", 10))
        self.lbl_dimensiones.pack()

        self.lbl_created = tk.Label(info_frame, text="", font=("Arial", 9), fg="gray")
        self.lbl_created.pack()

        # Frame para la imagen
        image_frame = tk.LabelFrame(main_frame, text="Imagen Reconstruida", padx=10, pady=10)
        image_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.canvas = tk.Canvas(image_frame, width=400, height=300, bg="lightgray")
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # Label de estado
        self.lbl_status = tk.Label(
            main_frame,
            text="Ingresa un ID para consultar",
            font=("Arial", 10),
            fg="gray"
        )
        self.lbl_status.pack(pady=10)

    def _consultar_imagen(self):
        """Consulta la imagen por ID y la reconstruye."""
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
            # Actualizar estado
            self.lbl_status.config(text="Consultando...", fg="blue")
            self.btn_consultar.config(state=tk.DISABLED)
            self.window.update()

            # Consultar base de datos
            datos = get_image(image_id)

            # Extraer datos
            ancho = datos["width"]
            alto = datos["height"]
            rgb_string = datos["rgb_data"]
            created_at = datos.get("created_at", "N/A")

            # Debug info
            print(f"Datos recibidos - Ancho: {ancho}, Alto: {alto}")
            print(f"Longitud rgb_string: {len(rgb_string)}")
            print(f"Valores esperados: {ancho * alto * 3}")

            # Reconstruir imagen (retorna numpy array)
            self.imagen_actual = string_rgb_a_imagen(rgb_string, ancho, alto)

            # Mostrar info
            self.lbl_dimensiones.config(text=f"Dimensiones: {ancho} x {alto} px | Shape: {self.imagen_actual.shape}")
            self.lbl_created.config(text=f"Creado: {created_at}")

            # Mostrar imagen
            self._mostrar_imagen()

            self.lbl_status.config(text=f"Imagen #{image_id} reconstruida correctamente", fg="green")

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al consultar:\n{str(e)}")
            self.lbl_status.config(text="Error en la consulta", fg="red")
            self._limpiar_display()

        finally:
            self.btn_consultar.config(state=tk.NORMAL)

    def _mostrar_imagen(self):
        """Muestra la imagen reconstruida (numpy array) en el canvas."""
        if self.imagen_actual is None:
            return

        self.window.update()

        # Obtener tamaño del canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width < 10:
            canvas_width = 400
            canvas_height = 300

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

    def _limpiar_display(self):
        """Limpia la visualización."""
        self.canvas.delete("all")
        self.lbl_dimensiones.config(text="")
        self.lbl_created.config(text="")
        self.imagen_actual = None
        self.photo_image = None

    def run(self):
        """Inicia el loop principal de la ventana."""
        self.window.mainloop()


# Para pruebas directas
if __name__ == "__main__":
    app = ViewerWindow()
    app.run()
