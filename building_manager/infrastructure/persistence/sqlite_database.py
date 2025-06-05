import sqlite3
from typing import List, Optional
from ...domain.entities.tenant import Tenant
from ...domain.repositories.tenant_repository import TenantRepository
from datetime import datetime

class SQLiteTenantRepository(TenantRepository):
    def __init__(self, db_path: str = 'edificio.db'):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_all(self) -> List[Tenant]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, apartamento, renta, estado, identificacion,
                       email, celular, profesion, fecha_ingreso, deposito,
                       contacto_emergencia, telefono_emergencia, relacion_emergencia,
                       notas, archivo_identificacion, archivo_contrato
                FROM inquilinos
                ORDER BY nombre
            """)
            return [self._row_to_tenant(row) for row in cursor.fetchall()]

    def get_by_id(self, tenant_id: int) -> Optional[Tenant]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, apartamento, renta, estado, identificacion,
                       email, celular, profesion, fecha_ingreso, deposito,
                       contacto_emergencia, telefono_emergencia, relacion_emergencia,
                       notas, archivo_identificacion, archivo_contrato
                FROM inquilinos
                WHERE id = ?
            """, (tenant_id,))
            row = cursor.fetchone()
            return self._row_to_tenant(row) if row else None

    def _row_to_tenant(self, row) -> Tenant:
        return Tenant(
            id=row[0],
            name=row[1],
            apartment=row[2],
            rent=float(row[3]),
            status=row[4],
            identification=row[5],
            email=row[6],
            phone=row[7],
            profession=row[8],
            entry_date=datetime.strptime(row[9], '%Y-%m-%d').date(),
            deposit=float(row[10]),
            emergency_contact=row[11],
            emergency_phone=row[12],
            emergency_relation=row[13],
            notes=row[14],
            id_file=row[15],
            contract_file=row[16]
        ) 