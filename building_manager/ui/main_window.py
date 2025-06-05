import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
from .views.dashboard_view import DashboardView

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Building Manager")
        
        # Inicializar estilo básico
        self.style = Style(theme='flatly')
        
        # Configurar ventana
        self.root.state('zoomed')  # Maximizar ventana
        self.setup_ui()

    def setup_ui(self):
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame superior para título
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Contenedor para centrar el título
        self.title_container = ttk.Frame(self.header_frame)
        self.title_container.pack(expand=True)
        
        # Logo y título
        self.title_label = ttk.Label(
            self.title_container,
            text="📈 Dashboard Manager",
            font=("Segoe UI", 32, "bold"),
            foreground="#1a73e8"
        )
        self.title_label.pack()
        
        self.subtitle_label = ttk.Label(
            self.title_container,
            text="Panel de Control y Gestión Integral",
            font=("Segoe UI", 14),
            foreground="#5f6368"
        )
        self.subtitle_label.pack()
        
        # Vista del dashboard
        self.dashboard = DashboardView(self.main_frame)
        self.dashboard.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def run(self):
        self.root.mainloop()

def main():
    """Función principal para iniciar la aplicación."""
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main() 