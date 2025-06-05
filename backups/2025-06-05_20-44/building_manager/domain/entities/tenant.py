from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Tenant:
    id: Optional[int]
    name: str
    apartment: str
    rent: float
    status: str
    identification: str
    email: str
    phone: str
    profession: Optional[str]
    entry_date: date
    deposit: float
    emergency_contact: Optional[str]
    emergency_phone: Optional[str]
    emergency_relation: Optional[str]
    notes: Optional[str]
    id_file: Optional[str]
    contract_file: Optional[str]

    @property
    def is_active(self) -> bool:
        return self.status == "Activo"

    @property
    def has_pending_issues(self) -> bool:
        return self.status in ["Pendiente", "Moroso", "Suspendido"] 