### Image Decomposer - Sistema de Descomposicion y Reconstruccion de Imagenes
### Punto de entrada principal
import tkinter as tk
from gui_upload import abrir_ventana_captura
from gui_viewer import abrir_ventana_visor


def main():
    ### Funcion principal - crea la ventana y arranca la aplicacion

    root = tk.Tk()
    root.title("Image Decomposer")
    root.geometry("400x300")
    root.resizable(False, False)

    ### Centrar ventana
    root.update_idletasks()
    ancho = root.winfo_width()
    alto = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (ancho // 2)
    y = (root.winfo_screenheight() // 2) - (alto // 2)
    root.geometry(f"{ancho}x{alto}+{x}+{y}")

    ### --- Construir UI ---

    frame_principal = tk.Frame(root, padx=40, pady=30)
    frame_principal.pack(fill=tk.BOTH, expand=True)

    ### Titulo
    tk.Label(
        frame_principal,
        text="Image Decomposer",
        font=("Arial", 20, "bold")
    ).pack(pady=(0, 10))

    ### Subtitulo
    tk.Label(
        frame_principal,
        text="Sistema de Descomposicion y\nReconstruccion de Imagenes RGB",
        font=("Arial", 10),
        fg="gray"
    ).pack(pady=(0, 30))

    ### Boton Cargar Imagen
    tk.Button(
        frame_principal,
        text="Cargar Imagen",
        command=lambda: abrir_ventana_captura(root),
        font=("Arial", 12),
        width=20,
        height=2,
        bg="#4CAF50",
        fg="white",
        cursor="hand2"
    ).pack(pady=10)

    ### Boton Ver Imagen
    tk.Button(
        frame_principal,
        text="Ver Imagen",
        command=lambda: abrir_ventana_visor(root),
        font=("Arial", 12),
        width=20,
        height=2,
        bg="#2196F3",
        fg="white",
        cursor="hand2"
    ).pack(pady=10)

    ### Boton Salir
    tk.Button(
        frame_principal,
        text="Salir",
        command=root.quit,
        font=("Arial", 10),
        width=10
    ).pack(pady=(20, 0))

    ### Presionar 'q' para salir
    root.bind('<q>', lambda e: root.quit())

    root.mainloop()


if __name__ == "__main__":
    main()
