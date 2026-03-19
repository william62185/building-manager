"""
Presenter del dashboard (MVP).
Proporciona métricas para la vista: inquilinos, pagos pendientes, ingresos/gastos del mes.
"""

import datetime
from typing import Dict, Any

from manager.app.services.tenant_service import tenant_service
from manager.app.services.payment_service import payment_service
from manager.app.services.expense_service import expense_service
from manager.app.logger import logger


class DashboardPresenter:
    """Lógica de presentación para el dashboard."""

    def get_tenant_statistics(self) -> Dict[str, int]:
        """Estadísticas de inquilinos (total, al_dia, moroso, inactivo). Recarga y recalcula estados."""
        try:
            tenant_service._load_data()
            payment_service._load_data()
            tenant_service.recalculate_all_payment_statuses()
            tenant_service._load_data()
            return tenant_service.get_statistics()
        except Exception as e:
            logger.warning("Error al obtener estadísticas de inquilinos: %s", e)
            return {"total": 0, "al_dia": 0, "moroso": 0, "inactivo": 0}

    def get_pending_payments_total(self) -> float:
        """Monto total de pagos pendientes = deuda real (total_expected - total_paid) por mora integral."""
        try:
            tenant_service._load_data()
            payment_service._load_data()
            tenant_service.recalculate_all_payment_statuses()
            tenant_service._load_data()
            tenants = tenant_service.get_all_tenants()
            pending = [
                t for t in tenants
                if t.get("estado_pago") != "inactivo"
                and t.get("estado_pago") in ("moroso", "pendiente_registro", "pendiente_pago")
            ]
            total = 0.0
            for t in pending:
                tenant_id = t.get("id")
                if not tenant_id:
                    continue
                info = tenant_service.get_arrears_info(tenant_id)
                if info is not None:
                    # amount_pending incluye el período actual si ya estamos en él (pago por mes completo)
                    pending = float(info.get("amount_pending", info.get("total_expected", 0)) or 0)
                    paid = float(info.get("total_paid", 0) or 0)
                    total += max(0.0, pending - paid)
            return round(total, 2)
        except Exception as e:
            logger.warning("Error al calcular pagos pendientes: %s", e)
            return 0.0

    def get_payments_of_current_month(self) -> float:
        """Total de ingresos del mes actual (pagos registrados)."""
        try:
            payment_service._load_data()
            now = datetime.datetime.now()
            pagos = payment_service.get_all_payments()
            pagos_mes = [p for p in pagos if self._is_payment_in_current_month(p, now)]
            return sum(float(p.get("monto", 0)) for p in pagos_mes)
        except Exception as e:
            logger.warning("Error al calcular ingresos del mes: %s", e)
            return 0.0

    def _is_payment_in_current_month(self, pago: Dict[str, Any], now: datetime.datetime) -> bool:
        """True si el pago pertenece al mes actual (fecha_pago DD/MM/YYYY o fecha ISO)."""
        try:
            fecha = pago.get("fecha_pago", "") or pago.get("fecha", "")
            if not fecha:
                return False
            if "/" in str(fecha):
                parts = str(fecha).strip().split("/")
                if len(parts) == 3:
                    dia, mes, anio = int(parts[0]), int(parts[1]), int(parts[2])
                    return mes == now.month and anio == now.year
            else:
                fecha_dt = datetime.datetime.strptime(str(fecha)[:10], "%Y-%m-%d")
                return fecha_dt.month == now.month and fecha_dt.year == now.year
        except Exception:
            return False

    def get_expenses_of_current_month(self) -> float:
        """Total de gastos del mes actual."""
        try:
            expense_service._load_data()
            now = datetime.datetime.now()
            expenses = expense_service.filter_expenses(year=now.year, month=now.month)
            return sum(float(e.get("monto", 0)) for e in expenses)
        except Exception as e:
            logger.warning("Error al calcular gastos del mes: %s", e)
            return 0.0

    # ── Métricas anuales ──────────────────────────────────────────────────────

    def get_payments_of_current_year(self) -> float:
        """Total de ingresos del año actual."""
        try:
            payment_service._load_data()
            now = datetime.datetime.now()
            pagos = payment_service.get_all_payments()
            return sum(
                float(p.get("monto", 0))
                for p in pagos
                if self._is_payment_in_year(p, now.year)
            )
        except Exception as e:
            logger.warning("Error al calcular ingresos del año: %s", e)
            return 0.0

    def get_expenses_of_current_year(self) -> float:
        """Total de gastos del año actual."""
        try:
            expense_service._load_data()
            now = datetime.datetime.now()
            expenses = expense_service.filter_expenses(year=now.year)
            return sum(float(e.get("monto", 0)) for e in expenses)
        except Exception as e:
            logger.warning("Error al calcular gastos del año: %s", e)
            return 0.0

    def get_monthly_income_average(self) -> float:
        """Promedio mensual de ingresos = ingresos del año / meses transcurridos (mín. 1)."""
        try:
            ingresos_anio = self.get_payments_of_current_year()
            meses = max(1, datetime.datetime.now().month)
            return round(ingresos_anio / meses, 2)
        except Exception as e:
            logger.warning("Error al calcular promedio mensual: %s", e)
            return 0.0

    def get_occupation_rate(self) -> Dict[str, Any]:
        """Tasa de ocupación: ocupados / total apartamentos."""
        try:
            from manager.app.services.apartment_service import apartment_service
            apartment_service.reload_data()
            tenant_service._load_data()
            apartments = apartment_service.get_all_apartments()
            total = len(apartments)
            if total == 0:
                return {"total": 0, "occupied": 0, "rate": 0.0}
            tenants = tenant_service.get_all_tenants()
            occupied_apt_ids = {
                t.get("apartamento")
                for t in tenants
                if t.get("estado_pago") != "inactivo" and t.get("apartamento") is not None
            }
            occupied = len(occupied_apt_ids)
            return {"total": total, "occupied": occupied, "rate": round(occupied / total * 100, 1)}
        except Exception as e:
            logger.warning("Error al calcular tasa de ocupación: %s", e)
            return {"total": 0, "occupied": 0, "rate": 0.0}

    def _is_payment_in_year(self, pago: Dict[str, Any], year: int) -> bool:
        """True si el pago pertenece al año indicado."""
        try:
            fecha = pago.get("fecha_pago", "") or pago.get("fecha", "")
            if not fecha:
                return False
            if "/" in str(fecha):
                parts = str(fecha).strip().split("/")
                if len(parts) == 3:
                    return int(parts[2]) == year
            else:
                return datetime.datetime.strptime(str(fecha)[:10], "%Y-%m-%d").year == year
        except Exception:
            return False
        return False
