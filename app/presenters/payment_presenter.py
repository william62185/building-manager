"""
Presenter del módulo de pagos (MVP).
Centraliza callbacks y datos compartidos para la vista de pagos.
"""

from typing import Callable, Dict, Any, List, Optional

from manager.app.services.payment_service import payment_service
from manager.app.services.tenant_service import tenant_service
from manager.app.logger import logger


class PaymentPresenter:
    """Lógica de presentación para el módulo de pagos."""

    def __init__(
        self,
        on_back: Optional[Callable[[], None]] = None,
        on_payment_saved: Optional[Callable[[], None]] = None,
    ):
        self._on_back = on_back
        self._on_payment_saved = on_payment_saved

    def get_active_tenants(self) -> List[Dict[str, Any]]:
        """Devuelve inquilinos activos para listados/combos."""
        try:
            return [t for t in tenant_service.get_all_tenants() if t.get("estado_pago") != "inactivo"]
        except Exception as e:
            logger.warning("Error al cargar inquilinos activos: %s", e)
            return []

    def go_back(self) -> None:
        """Navega al dashboard (o pantalla anterior)."""
        if self._on_back:
            self._on_back()

    def notify_payment_saved(self) -> None:
        """Notifica que se registró un pago (para refrescar otras vistas)."""
        if self._on_payment_saved:
            self._on_payment_saved()
