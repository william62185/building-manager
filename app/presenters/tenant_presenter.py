"""
Presenter del módulo de inquilinos (MVP).
Responsable de: carga de datos, filtrado y coordinación con el servicio.
La vista solo muestra datos y delega acciones aquí.
"""

from datetime import datetime, timedelta
from typing import Callable, Dict, Any, List, Optional

from manager.app.services.tenant_service import tenant_service
from manager.app.services.apartment_service import apartment_service
from manager.app.logger import logger


class TenantPresenter:
    """Lógica de presentación para el módulo de inquilinos."""

    def __init__(
        self,
        on_navigate: Optional[Callable[[str], None]] = None,
        on_data_change: Optional[Callable[[], None]] = None,
        on_register_payment: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self._on_navigate = on_navigate
        self._on_data_change = on_data_change
        self._on_register_payment = on_register_payment

    def load_tenants(self) -> List[Dict[str, Any]]:
        """Carga inquilinos desde el servicio (recarga, recalcula estados y devuelve lista)."""
        try:
            tenant_service._load_data()
            tenant_service.recalculate_all_payment_statuses()
            tenant_service._load_data()
            return tenant_service.get_all_tenants()
        except Exception as e:
            logger.warning("Error al cargar inquilinos: %s", e)
            return []

    def get_filtered_tenants(
        self,
        all_tenants: List[Dict[str, Any]],
        filter_state: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Aplica filtros a la lista de inquilinos. filter_state: search_text, apartment, status, date_from, date_to, rent_min, rent_max."""
        filtered = list(all_tenants)

        search_text = (filter_state.get("search_text") or "").strip().lower()
        if search_text:
            def matches_apartment_number(tenant: Dict[str, Any]) -> bool:
                apt_id = tenant.get("apartamento")
                if apt_id is None:
                    return False
                apt = apartment_service.get_apartment_by_id(apt_id) if hasattr(apartment_service, "get_apartment_by_id") else None
                if not apt:
                    all_apts = apartment_service.get_all_apartments()
                    apt = next((a for a in all_apts if a.get("id") == apt_id), None)
                if apt:
                    return search_text in str(apt.get("number", "")).lower()
                return False

            filtered = [
                t for t in filtered
                if search_text in str(t.get("nombre", "")).lower()
                or search_text in str(t.get("numero_documento", "")).lower()
                or matches_apartment_number(t)
                or search_text in str(t.get("email", "")).lower()
                or search_text in str(t.get("telefono", "")).lower()
            ]

        apartment = filter_state.get("apartment", "Todos")
        if apartment and apartment != "Todos":
            def matches_apartment(tenant: Dict[str, Any]) -> bool:
                apt_id = tenant.get("apartamento")
                if apt_id is None:
                    return False
                apt = apartment_service.get_apartment_by_id(apt_id) if hasattr(apartment_service, "get_apartment_by_id") else None
                if not apt:
                    all_apts = apartment_service.get_all_apartments()
                    apt = next((a for a in all_apts if a.get("id") == apt_id), None)
                if not apt:
                    return False
                apt_number = apt.get("number", "")
                apt_type = apt.get("unit_type", "Apartamento Estándar")
                apt_display = apt_number if apt_type == "Apartamento Estándar" else f"{apt_type} {apt_number}"
                return apt_display == apartment
            filtered = [t for t in filtered if matches_apartment(t)]

        status = filter_state.get("status", "Todos")
        if status and status != "Todos":
            status_mapping = {
                "Al Día": "al_dia",
                "Pendiente Registro": "pendiente_registro",
                "En Mora": "moroso",
                "Inactivo": "inactivo",
            }
            target = status_mapping.get(status, (status or "").lower())
            filtered = [t for t in filtered if t.get("estado_pago") == target]
        else:
            filtered = [t for t in filtered if t.get("estado_pago") != "inactivo"]

        date_from_str = filter_state.get("date_from") or ""
        date_to_str = filter_state.get("date_to") or ""
        if date_from_str or date_to_str:
            def parse_date(s: str):
                try:
                    return datetime.strptime(s.strip(), "%d/%m/%Y").date()
                except (ValueError, AttributeError):
                    return None
            d_from = parse_date(date_from_str) if date_from_str else None
            d_to = parse_date(date_to_str) if date_to_str else None

            def in_range(tenant: Dict[str, Any]) -> bool:
                fi = tenant.get("fecha_ingreso") or ""
                if not fi:
                    return False
                d = parse_date(fi)
                if d is None:
                    return False
                if d_from is not None and d < d_from:
                    return False
                if d_to is not None and d > d_to:
                    return False
                return True
            filtered = [t for t in filtered if in_range(t)]

        rent_min_str = (filter_state.get("rent_min") or "").strip()
        rent_max_str = (filter_state.get("rent_max") or "").strip()
        if rent_min_str or rent_max_str:
            def parse_rent(s: str) -> Optional[float]:
                try:
                    s = str(s).strip().replace(",", "")
                    if not s:
                        return None
                    if "." in s:
                        parts = s.split(".")
                        if len(parts) == 2 and len(parts[1]) <= 2 and parts[1].isdigit():
                            return float(s)
                        return float(s.replace(".", ""))
                    return float(s)
                except (ValueError, TypeError):
                    return None
            r_min = parse_rent(rent_min_str) if rent_min_str else None
            r_max = parse_rent(rent_max_str) if rent_max_str else None

            def in_rent_range(tenant: Dict[str, Any]) -> bool:
                val = tenant.get("valor_arriendo")
                if val is None or val == "":
                    return False
                rent = parse_rent(str(val))
                if rent is None:
                    return False
                if r_min is not None and rent < r_min:
                    return False
                if r_max is not None and rent > r_max:
                    return False
                return True
            filtered = [t for t in filtered if in_rent_range(t)]

        return filtered

    def get_apartment_options(self) -> List[str]:
        """Opciones para el combo de apartamentos (Todos + lista de apartamentos)."""
        options = ["Todos"]
        try:
            for apt in apartment_service.get_all_apartments():
                num = apt.get("number", "")
                ut = apt.get("unit_type", "Apartamento Estándar")
                if ut == "Apartamento Estándar":
                    options.append(num)
                else:
                    options.append(f"{ut} {num}")
        except Exception as e:
            logger.warning("Error al cargar apartamentos para filtro: %s", e)
        return options

    def navigate_to_reports(self) -> None:
        """Navega al módulo de reportes."""
        if self._on_navigate:
            self._on_navigate("reports")

    def notify_data_change(self) -> None:
        """Notifica que los datos han cambiado (p. ej. tras guardar inquilino)."""
        if self._on_data_change:
            self._on_data_change()

    def register_payment_for(self, tenant: Dict[str, Any]) -> None:
        """Solicita registrar pago para un inquilino (navegación o callback)."""
        if self._on_register_payment:
            self._on_register_payment(tenant)
