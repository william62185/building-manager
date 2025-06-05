from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

@dataclass
class Tenant:
    """
    Modelo que representa un inquilino en el sistema.
    Incluye toda la información relevante y métodos de utilidad.
    """
    # Campos requeridos
    name: str
    identification: str
    email: str
    phone: str
    apartment: str
    rent: Decimal
    deposit: Decimal
    entry_date: date
    status: str
    
    # Campos opcionales
    id: Optional[int] = None
    profession: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None
    notes: Optional[str] = None
    id_file_path: Optional[str] = None
    contract_file_path: Optional[str] = None

    def __post_init__(self):
        """Validaciones y conversiones después de la inicialización."""
        # Convertir valores monetarios a Decimal si son str o float
        if isinstance(self.rent, (str, float)):
            self.rent = Decimal(str(self.rent))
        if isinstance(self.deposit, (str, float)):
            self.deposit = Decimal(str(self.deposit))

        # Convertir fecha si es string
        if isinstance(self.entry_date, str):
            self.entry_date = datetime.strptime(self.entry_date, '%Y-%m-%d').date()

        # Validaciones básicas
        self._validate()

    def _validate(self):
        """Realiza validaciones de los datos del inquilino."""
        if not self.name:
            raise ValueError("El nombre del inquilino es requerido")
        if not self.apartment:
            raise ValueError("El número de apartamento es requerido")
        if self.rent < 0:
            raise ValueError("La renta no puede ser negativa")
        if self.deposit < 0:
            raise ValueError("El depósito no puede ser negativo")
        if self.status not in ["Activo", "Pendiente", "Moroso", "Suspendido"]:
            raise ValueError("Estado de inquilino no válido")

    @property
    def is_active(self) -> bool:
        """Indica si el inquilino está activo."""
        return self.status == "Activo"

    @property
    def has_pending_issues(self) -> bool:
        """Indica si el inquilino tiene problemas pendientes."""
        return self.status in ["Pendiente", "Moroso", "Suspendido"]

    @property
    def months_as_tenant(self) -> int:
        """Calcula cuántos meses lleva el inquilino en el edificio."""
        today = date.today()
        months = (today.year - self.entry_date.year) * 12
        months += today.month - self.entry_date.month
        return max(0, months)

    def to_dict(self) -> dict:
        """Convierte el inquilino a un diccionario para almacenamiento/API."""
        return {
            "id": self.id,
            "name": self.name,
            "identification": self.identification,
            "email": self.email,
            "phone": self.phone,
            "profession": self.profession,
            "apartment": self.apartment,
            "rent": str(self.rent),
            "status": self.status,
            "entry_date": self.entry_date.isoformat(),
            "deposit": str(self.deposit),
            "emergency_contact_name": self.emergency_contact_name,
            "emergency_contact_phone": self.emergency_contact_phone,
            "emergency_contact_relation": self.emergency_contact_relation,
            "notes": self.notes,
            "id_file_path": self.id_file_path,
            "contract_file_path": self.contract_file_path
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Tenant':
        """Crea una instancia de Tenant desde un diccionario."""
        return cls(**data)

    def __str__(self) -> str:
        """Representación en string del inquilino."""
        return f"{self.name} - Apto {self.apartment} ({self.status})" 