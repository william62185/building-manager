from typing import List, Optional
from .observable import Observable
from datetime import datetime

class AppState(Observable):
    """
    Estado global de la aplicación.
    Mantiene el estado actual y notifica a los observadores de los cambios.
    """
    def __init__(self):
        super().__init__()
        self.initialize_state()

    def initialize_state(self) -> None:
        """Inicializa el estado con valores por defecto."""
        self.set_state("tenants", [])
        self.set_state("payments", [])
        self.set_state("expenses", [])
        self.set_state("active_tenants_count", 0)
        self.set_state("pending_tenants_count", 0)
        self.set_state("current_month_income", 0.0)
        self.set_state("current_month_expenses", 0.0)
        self.set_state("last_update", datetime.now())
        self.set_state("selected_tenant_id", None)
        self.set_state("is_loading", False)
        self.set_state("error", None)

    def update_dashboard_metrics(self, metrics: dict) -> None:
        """
        Actualiza las métricas del dashboard.
        Args:
            metrics: Diccionario con las métricas actualizadas
        """
        for key, value in metrics.items():
            self.set_state(key, value)
        self.set_state("last_update", datetime.now())

    def set_error(self, error: Optional[str]) -> None:
        """
        Establece un mensaje de error en el estado.
        Args:
            error: Mensaje de error o None para limpiar el error
        """
        self.set_state("error", error)

    def set_loading(self, is_loading: bool) -> None:
        """
        Establece el estado de carga.
        Args:
            is_loading: True si la aplicación está cargando datos
        """
        self.set_state("is_loading", is_loading)

    def select_tenant(self, tenant_id: Optional[int]) -> None:
        """
        Selecciona un inquilino.
        Args:
            tenant_id: ID del inquilino seleccionado o None para deseleccionar
        """
        self.set_state("selected_tenant_id", tenant_id) 