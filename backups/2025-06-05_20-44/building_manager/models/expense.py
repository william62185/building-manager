from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

@dataclass
class Expense:
    """
    Modelo que representa un gasto del edificio.
    """
    id: Optional[int]
    amount: Decimal
    date: date
    category: str
    description: str
    provider: Optional[str]
    invoice_number: Optional[str]
    payment_method: str
    is_recurring: bool = False
    recurrence_period: Optional[str] = None  # Mensual, Trimestral, Anual
    status: str = "Pagado"  # Pagado, Pendiente, Anulado

    def __post_init__(self):
        """Validaciones y conversiones después de la inicialización."""
        # Convertir monto a Decimal si es str o float
        if isinstance(self.amount, (str, float)):
            self.amount = Decimal(str(self.amount))

        # Convertir fecha si es string
        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, '%Y-%m-%d').date()

        # Validaciones básicas
        self._validate()

    def _validate(self):
        """Realiza validaciones de los datos del gasto."""
        if self.amount <= 0:
            raise ValueError("El monto del gasto debe ser mayor a cero")
        if not self.description:
            raise ValueError("La descripción es requerida")
        if self.category not in [
            "Mantenimiento", "Servicios", "Reparaciones",
            "Impuestos", "Seguros", "Limpieza", "Otro"
        ]:
            raise ValueError("Categoría de gasto no válida")
        if self.payment_method not in ["Efectivo", "Transferencia", "Tarjeta", "Otro"]:
            raise ValueError("Método de pago no válido")
        if self.status not in ["Pagado", "Pendiente", "Anulado"]:
            raise ValueError("Estado de gasto no válido")
        if self.is_recurring and self.recurrence_period not in [
            "Mensual", "Trimestral", "Anual", None
        ]:
            raise ValueError("Período de recurrencia no válido")

    @property
    def is_paid(self) -> bool:
        """Indica si el gasto está pagado."""
        return self.status == "Pagado"

    @property
    def is_maintenance(self) -> bool:
        """Indica si el gasto es de mantenimiento."""
        return self.category == "Mantenimiento"

    def to_dict(self) -> dict:
        """Convierte el gasto a un diccionario para almacenamiento/API."""
        return {
            "id": self.id,
            "amount": str(self.amount),
            "date": self.date.isoformat(),
            "category": self.category,
            "description": self.description,
            "provider": self.provider,
            "invoice_number": self.invoice_number,
            "payment_method": self.payment_method,
            "is_recurring": self.is_recurring,
            "recurrence_period": self.recurrence_period,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Expense':
        """Crea una instancia de Expense desde un diccionario."""
        return cls(**data)

    def __str__(self) -> str:
        """Representación en string del gasto."""
        return f"{self.category}: ${self.amount} - {self.description[:30]}..."

    def next_recurrence_date(self) -> Optional[date]:
        """Calcula la fecha de la próxima recurrencia si el gasto es recurrente."""
        if not self.is_recurring or not self.recurrence_period:
            return None

        today = date.today()
        if self.recurrence_period == "Mensual":
            next_date = date(today.year, today.month + 1, self.date.day)
        elif self.recurrence_period == "Trimestral":
            next_date = date(today.year, today.month + 3, self.date.day)
        else:  # Anual
            next_date = date(today.year + 1, self.date.month, self.date.day)

        return next_date 