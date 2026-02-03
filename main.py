"""
Image Decomposer - Sistema de Descomposición y Reconstrucción de Imágenes
Punto de entrada principal con selector de GUI
"""
import tkinter as tk
from tkinter import messagebox
import sys


class MainWindow:
    def __init__(self):
        """Inicializa la ventana principal."""
        self.root = tk.Tk()
        self.root.title("Image Decomposer")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Centrar ventana
        self._center_window()

        self._setup_ui()

    def _center_window(self):
        """Centra la ventana en la pantalla."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _setup_ui(self):
        """Configura los componentes de la interfaz."""
        # Frame principal
        main_frame = tk.Frame(self.root, padx=40, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = tk.Label(
            main_frame,
            text="Image Decomposer",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Subtítulo
        subtitle_label = tk.Label(
            main_frame,
            text="Sistema de Descomposición y\nReconstrucción de Imágenes RGB",
            font=("Arial", 10),
            fg="gray"
        )
        subtitle_label.pack(pady=(0, 30))

        # Botón Cargar Imagen
        btn_upload = tk.Button(
            main_frame,
            text="Cargar Imagen",
            command=self._open_upload,
            font=("Arial", 12),
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white",
            cursor="hand2"
        )
        btn_upload.pack(pady=10)

        # Botón Ver Imagen
        btn_viewer = tk.Button(
            main_frame,
            text="Ver Imagen",
            command=self._open_viewer,
            font=("Arial", 12),
            width=20,
            height=2,
            bg="#2196F3",
            fg="white",
            cursor="hand2"
        )
        btn_viewer.pack(pady=10)

        # Botón Salir
        btn_exit = tk.Button(
            main_frame,
            text="Salir",
            command=self.root.quit,
            font=("Arial", 10),
            width=10
        )
        btn_exit.pack(pady=(20, 0))

    def _open_upload(self):
        """Abre la ventana de carga de imágenes."""
        try:
            from gui_upload import UploadWindow
            UploadWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana:\n{str(e)}")

    def _open_viewer(self):
        """Abre la ventana de visualización de imágenes."""
        try:
            from gui_viewer import ViewerWindow
            ViewerWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana:\n{str(e)}")

    def run(self):
        """Inicia el loop principal de la aplicación."""
        self.root.mainloop()


def main():
    """Función principal."""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
