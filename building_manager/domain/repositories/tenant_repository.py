from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.tenant import Tenant

class TenantRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Tenant]:
        pass

    @abstractmethod
    def get_by_id(self, tenant_id: int) -> Optional[Tenant]:
        pass

    @abstractmethod
    def create(self, tenant: Tenant) -> Tenant:
        pass

    @abstractmethod
    def update(self, tenant: Tenant) -> Tenant:
        pass

    @abstractmethod
    def delete(self, tenant_id: int) -> bool:
        pass

    @abstractmethod
    def get_active_count(self) -> int:
        pass

    @abstractmethod
    def get_pending_count(self) -> int:
        pass

    @abstractmethod
    def search(self, query: str, status: Optional[str] = None) -> List[Tenant]:
        pass 