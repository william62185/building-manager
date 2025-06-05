from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date, datetime
import os

from ..models import Tenant
from .database_service import DatabaseService

class TenantService:
    """Servicio para gestionar inquilinos."""
    def __init__(self):
        self.db = DatabaseService()
        self.files_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "files")
        # Crear directorio de archivos si no existe
        if not os.path.exists(self.files_dir):
            os.makedirs(self.files_dir)
        self._setup_table()

    def _setup_table(self):
        """Configura la tabla de inquilinos."""
        query = """
        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            identification TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            profession TEXT,
            apartment TEXT NOT NULL,
            rent DECIMAL(10,2) NOT NULL,
            deposit DECIMAL(10,2) NOT NULL,
            entry_date DATE NOT NULL,
            status TEXT NOT NULL,
            emergency_contact_name TEXT,
            emergency_contact_phone TEXT,
            emergency_contact_relation TEXT,
            notes TEXT,
            id_file_path TEXT,
            contract_file_path TEXT
        )
        """
        self.db.execute(query)

    def _save_file(self, file_path: str, tenant_id: int, file_type: str) -> str:
        """Guarda un archivo en el sistema de archivos."""
        if not file_path or not os.path.exists(file_path):
            return ""
            
        # Crear directorio para el inquilino si no existe
        tenant_dir = os.path.join(self.files_dir, str(tenant_id))
        if not os.path.exists(tenant_dir):
            os.makedirs(tenant_dir)
        
        # Obtener extensión del archivo
        _, ext = os.path.splitext(file_path)
        
        # Crear nombre de archivo
        new_filename = f"{file_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        new_file_path = os.path.join(tenant_dir, new_filename)
        
        # Copiar archivo
        try:
            with open(file_path, 'rb') as src, open(new_file_path, 'wb') as dst:
                dst.write(src.read())
            return new_file_path
        except Exception as e:
            print(f"Error al guardar archivo: {e}")
            return ""

    def create(self, tenant: Tenant) -> Tenant:
        """Crea un nuevo inquilino."""
        # Guardar archivos primero para obtener las rutas
        id_file = tenant.id_file_path
        contract_file = tenant.contract_file_path
        tenant.id_file_path = ""
        tenant.contract_file_path = ""

        # Insertar inquilino en la base de datos
        query = """
            INSERT INTO tenants (
                name, identification, email, phone, profession,
                apartment, rent, deposit, entry_date, status,
                emergency_contact_name, emergency_contact_phone,
                emergency_contact_relation, notes, id_file_path,
                contract_file_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            tenant.name, tenant.identification, tenant.email,
            tenant.phone, tenant.profession, tenant.apartment,
            float(tenant.rent), float(tenant.deposit), tenant.entry_date,
            tenant.status, tenant.emergency_contact_name,
            tenant.emergency_contact_phone, tenant.emergency_contact_relation,
            tenant.notes, "", ""
        )
        
        cursor = self.db.execute(query, params)
        tenant_id = cursor.lastrowid

        # Guardar archivos y actualizar rutas
        if id_file:
            id_file_path = self._save_file(id_file, tenant_id, "id")
            if id_file_path:
                self.db.execute(
                    "UPDATE tenants SET id_file_path = ? WHERE id = ?",
                    (id_file_path, tenant_id)
                )

        if contract_file:
            contract_file_path = self._save_file(contract_file, tenant_id, "contract")
            if contract_file_path:
                self.db.execute(
                    "UPDATE tenants SET contract_file_path = ? WHERE id = ?",
                    (contract_file_path, tenant_id)
                )
        
        return self.get_by_id(tenant_id)

    def get_all(self) -> List[Tenant]:
        """Obtiene todos los inquilinos."""
        query = "SELECT * FROM tenants"
        results = self.db.fetch_all(query)
        tenants = []
        for row in results:
            # Convertir valores monetarios de float a Decimal
            row['rent'] = Decimal(str(row['rent']))
            row['deposit'] = Decimal(str(row['deposit']))
            tenants.append(Tenant(**row))
        return tenants

    def get_by_id(self, tenant_id: int) -> Optional[Tenant]:
        """Obtiene un inquilino por su ID."""
        query = "SELECT * FROM tenants WHERE id = ?"
        result = self.db.fetch_one(query, (tenant_id,))
        if result:
            # Convertir valores monetarios de float a Decimal
            result['rent'] = Decimal(str(result['rent']))
            result['deposit'] = Decimal(str(result['deposit']))
            return Tenant(**result)
        return None

    def get_active_tenants(self) -> List[Tenant]:
        """
        Obtiene los inquilinos activos.
        
        Returns:
            Lista de inquilinos activos
        """
        query = "SELECT * FROM tenants WHERE status = 'Activo' ORDER BY apartment"
        results = self.db.fetch_all(query)
        tenants = []
        for row in results:
            # Convertir valores monetarios de float a Decimal
            row['rent'] = Decimal(str(row['rent']))
            row['deposit'] = Decimal(str(row['deposit']))
            tenants.append(Tenant(**row))
        return tenants

    def update(self, tenant_id_or_tenant, tenant: Optional[Tenant] = None) -> Optional[Tenant]:
        """Actualiza un inquilino existente."""
        # Manejar diferentes tipos de llamada
        if isinstance(tenant_id_or_tenant, Tenant):
            # Llamada con objeto Tenant directo
            tenant = tenant_id_or_tenant
            tenant_id = tenant.id
            if not tenant_id:
                raise ValueError("El inquilino debe tener un ID para poder actualizarlo")
        else:
            # Llamada tradicional con ID y objeto separados
            tenant_id = tenant_id_or_tenant
            if not tenant:
                raise ValueError("Se debe proporcionar un objeto Tenant")
        
        # Actualizar datos básicos
        query = """
            UPDATE tenants SET
                name = ?, identification = ?, email = ?,
                phone = ?, profession = ?, apartment = ?,
                rent = ?, deposit = ?, entry_date = ?,
                status = ?, emergency_contact_name = ?,
                emergency_contact_phone = ?, emergency_contact_relation = ?,
                notes = ?
            WHERE id = ?
        """
        params = (
            tenant.name, tenant.identification, tenant.email,
            tenant.phone, tenant.profession, tenant.apartment,
            float(tenant.rent), float(tenant.deposit), tenant.entry_date,
            tenant.status, tenant.emergency_contact_name,
            tenant.emergency_contact_phone, tenant.emergency_contact_relation,
            tenant.notes, tenant_id
        )
        self.db.execute(query, params)
        
        # Actualizar archivos si se proporcionaron nuevos
        if hasattr(tenant, 'id_file_path') and tenant.id_file_path:
            id_file_path = self._save_file(tenant.id_file_path, tenant_id, "id")
            if id_file_path:
                self.db.execute(
                    "UPDATE tenants SET id_file_path = ? WHERE id = ?",
                    (id_file_path, tenant_id)
                )
            
        if hasattr(tenant, 'contract_file_path') and tenant.contract_file_path:
            contract_file_path = self._save_file(tenant.contract_file_path, tenant_id, "contract")
            if contract_file_path:
                self.db.execute(
                    "UPDATE tenants SET contract_file_path = ? WHERE id = ?",
                    (contract_file_path, tenant_id)
                )
        
        return self.get_by_id(tenant_id)

    def delete(self, tenant_id: int) -> bool:
        """Elimina un inquilino."""
        query = "DELETE FROM tenants WHERE id = ?"
        self.db.execute(query, (tenant_id,))
        return True

    def apartment_exists(self, apartment: str, exclude_tenant_id: Optional[int] = None) -> bool:
        """
        Verifica si un apartamento ya está ocupado.
        
        Args:
            apartment: Número de apartamento a verificar
            exclude_tenant_id: ID de inquilino a excluir de la búsqueda (para ediciones)
            
        Returns:
            True si el apartamento está ocupado, False en caso contrario
        """
        if exclude_tenant_id:
            query = "SELECT COUNT(*) as count FROM tenants WHERE apartment = ? AND id != ?"
            result = self.db.fetch_one(query, (apartment, exclude_tenant_id))
        else:
            query = "SELECT COUNT(*) as count FROM tenants WHERE apartment = ?"
            result = self.db.fetch_one(query, (apartment,))
        
        return result and result['count'] > 0

    def save(self, tenant: Tenant) -> Tenant:
        """Guarda un inquilino (alias para create)."""
        return self.create(tenant)

    def get_tenant_metrics(self) -> Dict[str, int]:
        """
        Obtiene métricas de los inquilinos.
        
        Returns:
            Diccionario con las métricas:
            - total_tenants: Total de inquilinos
            - active_tenants: Inquilinos al día con sus pagos
        """
        # Total de inquilinos
        query = "SELECT COUNT(*) as total FROM tenants"
        result = self.db.execute_query(query)
        total_tenants = result[0]["total"] if result else 0

        # Inquilinos al día (sin pagos pendientes)
        query = """
        SELECT COUNT(DISTINCT t.id) as active
        FROM tenants t
        LEFT JOIN payments p ON t.id = p.tenant_id
        WHERE p.status = 'Pendiente' OR p.status IS NULL
        """
        result = self.db.execute_query(query)
        active_tenants = total_tenants - (result[0]["active"] if result else 0)

        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants
        } 