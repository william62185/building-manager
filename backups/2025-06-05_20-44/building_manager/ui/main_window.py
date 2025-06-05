import tkinter as tk
from ttkbootstrap import Window as TtkWindow
from ttkbootstrap import ttk

from .views import (
    DashboardView,
    TenantsView,
    TenantsDashboard,
    TenantFormView
)

class MainWindow(TtkWindow):
    """Ventana principal de la aplicación."""
    def __init__(self):
        super().__init__(themename="litera")
        
        # Configurar ventana
        self.title("Building Manager")
        self.geometry("1024x768")
        
        # Contenedor principal
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Diccionario de vistas
        self.views = {
            'dashboard': DashboardView,
            'tenants_dashboard': TenantsDashboard,
            'tenants': TenantsView,
            'tenant_form': TenantFormView
        }
        
        # Vista actual
        self.current_view = None
        
        # Mostrar dashboard inicial
        self._show_view('dashboard')
        
        # Configurar estilo de las tarjetas
        self.style.configure(
            "Card.TFrame",
            background="white",
            relief="solid",
            borderwidth=1
        )

    def _show_view(self, view_name: str, **kwargs):
        """
        Muestra una vista específica.
        
        Args:
            view_name: Nombre de la vista a mostrar
            **kwargs: Argumentos adicionales para la vista
        """
        # Destruir vista actual si existe
        if self.current_view:
            self.current_view.destroy()
        
        # Crear nueva vista
        ViewClass = self.views.get(view_name)
        if ViewClass:
            self.current_view = ViewClass(self.main_container, **kwargs)
            self.current_view.pack(fill=tk.BOTH, expand=True)
        else:
            print(f"Error: Vista '{view_name}' no encontrada")

def main():
    """Función principal para iniciar la aplicación."""
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main() 