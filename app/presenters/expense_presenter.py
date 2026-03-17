"""
Presenter del módulo de gastos (MVP).
Centraliza callbacks y datos para la vista de gastos.
"""

from typing import Callable, List, Dict, Any, Optional

from manager.app.services.expense_service import ExpenseService
from manager.app.logger import logger


class ExpensePresenter:
    """Lógica de presentación para el módulo de gastos."""

    def __init__(self, on_back: Optional[Callable[[], None]] = None):
        self._on_back = on_back
        self._expense_service = ExpenseService()

    def load_expenses(self) -> List[Dict[str, Any]]:
        """Carga la lista de gastos desde el servicio."""
        try:
            self._expense_service._load_data()
            return self._expense_service.get_all_expenses()
        except Exception as e:
            logger.warning("Error al cargar gastos: %s", e)
            return []

    def go_back(self) -> None:
        """Navega al dashboard (o pantalla anterior)."""
        if self._on_back:
            self._on_back()
