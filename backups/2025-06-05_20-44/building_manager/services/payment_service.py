from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date

from ..models import Payment
from .database_service import DatabaseService

class PaymentService:
    """Servicio para gestionar pagos."""
    def __init__(self):
        self.db = DatabaseService()
        self._setup_table()

    def _setup_table(self):
        """Configura la tabla de pagos."""
        query = """
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            date DATE NOT NULL,
            payment_type TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            due_date DATE,
            FOREIGN KEY (tenant_id) REFERENCES tenants (id)
        )
        """
        self.db.execute(query)

        # Verificar si la columna due_date existe
        check_column = """
        SELECT COUNT(*) as count
        FROM pragma_table_info('payments')
        WHERE name = 'due_date'
        """
        result = self.db.execute_query(check_column)
        
        # Si la columna no existe, agregarla
        if result and result[0]['count'] == 0:
            alter_query = "ALTER TABLE payments ADD COLUMN due_date DATE"
            self.db.execute(alter_query)

    def register_payment(self, payment: Payment) -> int:
        """
        Registra un nuevo pago.
        
        Args:
            payment: Datos del pago
            
        Returns:
            ID del pago registrado
        """
        query = """
        INSERT INTO payments (
            tenant_id, amount, date, payment_type,
            description, status, due_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            payment.tenant_id,
            payment.amount,
            payment.date,
            payment.payment_type,
            payment.description,
            payment.status,
            payment.due_date
        )
        cursor = self.db.execute(query, params)
        return cursor.lastrowid

    def get_by_id(self, payment_id: int) -> Optional[Payment]:
        """
        Obtiene un pago por su ID.
        
        Args:
            payment_id: ID del pago
            
        Returns:
            Pago encontrado o None
        """
        query = "SELECT * FROM payments WHERE id = ?"
        result = self.db.fetch_one(query, (payment_id,))
        return Payment(**result) if result else None

    def get_all(self) -> List[Payment]:
        """
        Obtiene todos los pagos.
        
        Returns:
            Lista de pagos
        """
        query = "SELECT * FROM payments ORDER BY date DESC"
        results = self.db.fetch_all(query)
        return [Payment(**row) for row in results]

    def get_payments_by_tenant(self, tenant_id: int) -> List[Payment]:
        """
        Obtiene los pagos de un inquilino.
        
        Args:
            tenant_id: ID del inquilino
            
        Returns:
            Lista de pagos del inquilino
        """
        query = "SELECT * FROM payments WHERE tenant_id = ? ORDER BY date DESC"
        results = self.db.fetch_all(query, (tenant_id,))
        return [Payment(**row) for row in results]

    def get_payments_by_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[Payment]:
        """
        Obtiene los pagos en un rango de fechas.
        
        Args:
            start_date: Fecha inicial
            end_date: Fecha final
            
        Returns:
            Lista de pagos en el rango
        """
        query = """
        SELECT * FROM payments 
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC
        """
        results = self.db.fetch_all(query, (start_date, end_date))
        return [Payment(**row) for row in results]

    def update(self, payment_id: int, payment: Payment) -> bool:
        """
        Actualiza un pago.
        
        Args:
            payment_id: ID del pago
            payment: Nuevos datos del pago
            
        Returns:
            True si se actualizó correctamente
        """
        query = """
        UPDATE payments SET
            tenant_id = ?, amount = ?, date = ?,
            payment_type = ?, description = ?, status = ?,
            due_date = ?
        WHERE id = ?
        """
        params = (
            payment.tenant_id,
            payment.amount,
            payment.date,
            payment.payment_type,
            payment.description,
            payment.status,
            payment.due_date,
            payment_id
        )
        cursor = self.db.execute(query, params)
        return cursor.rowcount > 0

    def delete(self, payment_id: int) -> bool:
        """
        Elimina un pago.
        
        Args:
            payment_id: ID del pago
            
        Returns:
            True si se eliminó correctamente
        """
        query = "DELETE FROM payments WHERE id = ?"
        cursor = self.db.execute(query, (payment_id,))
        return cursor.rowcount > 0

    def get_payment_metrics(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de pagos en un rango de fechas.
        
        Args:
            start_date: Fecha inicial
            end_date: Fecha final
            
        Returns:
            Diccionario con métricas:
            - total_payments: Total de pagos
            - total_amount: Monto total
            - pending_amount: Monto pendiente
            - completed_payments: Pagos completados
        """
        query = """
        SELECT 
            COUNT(*) as total_payments,
            SUM(CASE WHEN status = 'Completado' THEN amount ELSE 0 END) as total_amount,
            SUM(CASE WHEN status = 'Pendiente' THEN amount ELSE 0 END) as pending_amount,
            COUNT(CASE WHEN status = 'Completado' THEN 1 END) as completed_payments
        FROM payments
        WHERE date BETWEEN ? AND ?
        """
        result = self.db.fetch_one(query, (start_date, end_date))
        
        return {
            "total_payments": result["total_payments"] if result else 0,
            "total_amount": Decimal(str(result["total_amount"])) if result and result["total_amount"] else Decimal("0"),
            "pending_amount": Decimal(str(result["pending_amount"])) if result and result["pending_amount"] else Decimal("0"),
            "completed_payments": result["completed_payments"] if result else 0
        }

    def get_pending_payments(self) -> List[Payment]:
        """
        Obtiene los pagos pendientes.
        
        Returns:
            Lista de pagos pendientes ordenados por fecha de vencimiento
        """
        query = """
        SELECT * FROM payments 
        WHERE status = 'Pendiente'
        ORDER BY due_date ASC
        """
        results = self.db.fetch_all(query)
        return [Payment(**row) for row in results] 