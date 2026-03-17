"""
App Controller: centraliza la navegación entre vistas.
Responsable de orquestar el cambio de vista: título, botones, contenedor y carga.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manager.app.ui.views.main_window import MainWindow

# Títulos por nombre de vista (único punto de verdad para la navegación)
VIEW_TITLES = {
    "dashboard": "Dashboard",
    "tenants": "Gestión de Inquilinos",
    "payments": "Gestión de Pagos",
    "expenses": "Gestión de Gastos",
    "accounting": "Contabilidad",
    "administration": "Administración",
    "reports": "Reportes y Análisis",
    "settings": "Configuración",
}


class AppController:
    """Controlador de aplicación: navegación entre ventanas/vistas."""

    def __init__(self, main_window: "MainWindow"):
        self._main_window = main_window

    def navigate_to(self, view_name: str) -> None:
        """Navega a la vista indicada: actualiza estado, título, limpia contenedor y carga la vista."""
        self._main_window.set_current_view(view_name)
        self._main_window.update_nav_buttons(view_name)
        title = VIEW_TITLES.get(view_name, "Building Manager")
        self._main_window.set_page_title(title)
        self._main_window.clear_views_container()
        self._main_window.load_view(view_name)
