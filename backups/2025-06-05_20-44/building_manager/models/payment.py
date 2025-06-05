from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

@dataclass
class Payment:
    """
    Modelo que representa un pago realizado por un inquilino.
    """
    id: Optional[int]
    tenant_id: int
    amount: Decimal
    date: date
    payment_type: str
    description: Optional[str]
    receipt_number: Optional[str]
    status: str = "Completado"  # Completado, Pendiente, Anulado
    due_date: Optional[date] = None

    def __post_init__(self):
        """Validaciones y conversiones después de la inicialización."""
        # Convertir monto a Decimal si es str o float
        if isinstance(self.amount, (str, float)):
            self.amount = Decimal(str(self.amount))

        # Convertir fechas si son string
        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, '%Y-%m-%d').date()
        if isinstance(self.due_date, str):
            self.due_date = datetime.strptime(self.due_date, '%Y-%m-%d').date()

        # Si no hay fecha de vencimiento, usar la fecha del pago
        if self.due_date is None:
            self.due_date = self.date

        # Validaciones básicas
        self._validate()

    def _validate(self):
        """Realiza validaciones de los datos del pago."""
        if self.tenant_id <= 0:
            raise ValueError("ID de inquilino inválido")
        if self.amount <= 0:
            raise ValueError("El monto del pago debe ser mayor a cero")
        if self.payment_type not in ["Efectivo", "Transferencia", "Tarjeta", "Otro"]:
            raise ValueError("Tipo de pago no válido")
        if self.status not in ["Completado", "Pendiente", "Anulado"]:
            raise ValueError("Estado de pago no válido")
        if self.due_date < self.date:
            raise ValueError("La fecha de vencimiento no puede ser anterior a la fecha del pago")

    @property
    def is_completed(self) -> bool:
        """Indica si el pago está completado."""
        return self.status == "Completado"

    @property
    def is_cancelled(self) -> bool:
        """Indica si el pago está anulado."""
        return self.status == "Anulado"

    @property
    def is_overdue(self) -> bool:
        """Indica si el pago está vencido."""
        return self.status == "Pendiente" and self.due_date < date.today()

    @property
    def days_overdue(self) -> int:
        """Retorna el número de días de retraso del pago."""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days

    def to_dict(self) -> dict:
        """Convierte el pago a un diccionario para almacenamiento/API."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "amount": str(self.amount),
            "date": self.date.isoformat(),
            "payment_type": self.payment_type,
            "description": self.description,
            "receipt_number": self.receipt_number,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Payment':
        """Crea una instancia de Payment desde un diccionario."""
        return cls(**data)

    def __str__(self) -> str:
        """Representación en string del pago."""
        status_text = " (VENCIDO)" if self.is_overdue else ""
        return f"Pago {self.id} - ${self.amount} ({self.date}){status_text}"

    def generate_receipt_number(self) -> str:
        """Genera un número de recibo único."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"REC-{self.tenant_id}-{timestamp}" 