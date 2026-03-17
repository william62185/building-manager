"""
Presenter del módulo de reportes (MVP).
Centraliza la recarga de datos y callbacks para la vista de reportes.
"""

from datetime import datetime, timedelta
from typing import Callable, Optional

from dateutil.relativedelta import relativedelta

from manager.app.services.tenant_service import tenant_service
from manager.app.services.payment_service import payment_service
from manager.app.services.apartment_service import apartment_service
from manager.app.services.building_service import building_service
from manager.app.services.expense_service import expense_service
from manager.app.logger import logger


class ReportPresenter:
    """Lógica de presentación para el módulo de reportes."""

    def __init__(
        self,
        on_back: Optional[Callable[[], None]] = None,
        on_show_occupancy_report: Optional[Callable[[], None]] = None,
        on_show_pending_payments_report: Optional[Callable[[], None]] = None,
    ):
        self._on_back = on_back
        self._on_show_occupancy_report = on_show_occupancy_report
        self._on_show_pending_payments_report = on_show_pending_payments_report

    def reload_all_data(self) -> None:
        """Recarga todos los datos necesarios para los reportes."""
        try:
            tenant_service._load_data()
            payment_service._load_data()
            apartment_service._load_data()
            building_service._load_buildings()
            expense_service._load_data()
        except Exception as e:
            logger.warning("Error al recargar datos para reportes: %s", e)

    def get_pending_payments_report_text(self) -> str:
        """
        Recarga datos, recalcula estados de pago y genera el texto del reporte
        de pagos pendientes con lógica de mora integral (igual que módulo Pagos).
        Retorna cadena vacía si no hay inquilinos pendientes.
        """
        tenant_service._load_data()
        payment_service._load_data()
        apartment_service._load_data()
        tenant_service.recalculate_all_payment_statuses()
        tenant_service._load_data()

        tenants = tenant_service.get_all_tenants()
        pending_tenants = [
            t for t in tenants
            if t.get("estado_pago") in ("pendiente_registro", "pendiente_pago", "moroso")
        ]
        if not pending_tenants:
            return ""

        report = []
        report.append("=" * 60)
        report.append("REPORTE DE PAGOS PENDIENTES")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append("RESUMEN:")
        report.append(f"  • Inquilinos con pagos pendientes: {len(pending_tenants)}")
        report.append("")
        report.append("DETALLE DE INQUILINOS:")
        report.append("-" * 60)

        for tenant in pending_tenants:
            estado = tenant.get("estado_pago", "N/A")
            if estado == "moroso":
                estado_text = "En Mora"
            elif estado == "pendiente_pago":
                estado_text = "Pendiente de pago"
            else:
                estado_text = "Pendiente Registro"

            apt_id = tenant.get("apartamento", None)
            apt_number = "N/A"
            if apt_id is not None:
                try:
                    apt = apartment_service.get_apartment_by_id(int(apt_id))
                    if apt and "number" in apt:
                        apt_number = apt.get("number", "N/A")
                except Exception:
                    apt_number = str(apt_id) if apt_id else "N/A"

            report.append(f"Inquilino: {tenant.get('nombre', 'N/A')}")
            report.append(f"  • Apartamento: {apt_number}")
            report.append(f"  • Documento: {tenant.get('numero_documento', 'N/A')}")
            report.append(f"  • Teléfono: {tenant.get('telefono', 'N/A')}")
            report.append(f"  • Estado: {estado_text}")
            report.append(f"  • Valor de arriendo: ${float(tenant.get('valor_arriendo', 0)):,.2f}")

            raw_id = tenant.get("id")
            tenant_id = int(raw_id) if raw_id is not None else None
            if tenant_id is not None:
                arrears = tenant_service.get_arrears_info(tenant_id)
                if arrears and arrears.get("estado_pago") in ("moroso", "pendiente_pago", "pendiente_registro"):
                    meses_mora = int(arrears.get("meses_mora", 0) or 0)
                    dias_del_periodo = int(arrears.get("dias_del_periodo_actual", 0) or 0)
                    first_unpaid = arrears.get("first_unpaid_due_date")
                    if first_unpaid and meses_mora >= 1:
                        current_period_due = first_unpaid + relativedelta(months=meses_mora - 1)
                        report.append(f"  • Fecha de pago (vencimiento): {current_period_due.strftime('%d/%m/%Y')}")
                    if meses_mora >= 1 or dias_del_periodo > 0:
                        if meses_mora == 1:
                            mora_texto = f"{dias_del_periodo} día{'s' if dias_del_periodo != 1 else ''}"
                        else:
                            meses_completos = meses_mora - 1
                            partes = []
                            if meses_completos > 0:
                                partes.append(f"{meses_completos} mes{'es' if meses_completos != 1 else ''}")
                            if dias_del_periodo > 0:
                                partes.append(f"{dias_del_periodo} día{'s' if dias_del_periodo != 1 else ''}")
                            mora_texto = " y ".join(partes) if partes else "0"
                        report.append(f"  • Días en mora: {mora_texto}")
                    pending_amount = float(arrears.get("amount_pending", arrears.get("total_expected", 0)) or 0)
                    paid = float(arrears.get("total_paid", 0) or 0)
                    report.append(f"  • Monto total en mora: ${max(0.0, pending_amount - paid):,.2f}")

            report.append("")

        return "\n".join(report)

    def go_back(self) -> None:
        """Navega al dashboard."""
        if self._on_back:
            self._on_back()

    def show_occupancy_report(self) -> None:
        """Abre el reporte de ocupación y vacancia."""
        if self._on_show_occupancy_report:
            self._on_show_occupancy_report()

    def show_pending_payments_report(self) -> None:
        """Abre el reporte de pagos pendientes."""
        if self._on_show_pending_payments_report:
            self._on_show_pending_payments_report()
