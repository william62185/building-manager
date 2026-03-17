# Presenters: lógica de presentación por módulo (MVP).
# Cada presenter orquesta datos (servicios) y estado para su vista.

from manager.app.presenters.tenant_presenter import TenantPresenter
from manager.app.presenters.payment_presenter import PaymentPresenter
from manager.app.presenters.expense_presenter import ExpensePresenter
from manager.app.presenters.report_presenter import ReportPresenter
from manager.app.presenters.dashboard_presenter import DashboardPresenter

__all__ = [
    "TenantPresenter",
    "PaymentPresenter",
    "ExpensePresenter",
    "ReportPresenter",
    "DashboardPresenter",
]
