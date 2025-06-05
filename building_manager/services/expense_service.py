from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import date

from ..models import Expense
from .database_service import DatabaseService

class ExpenseService:
    """Servicio para gestionar gastos."""
    def __init__(self):
        self.db = DatabaseService()
        self._setup_table()

    def _setup_table(self):
        """Configura la tabla de gastos con nuevas funcionalidades."""
        query = """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            date DATE NOT NULL,
            category TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            status TEXT NOT NULL,
            is_recurring BOOLEAN NOT NULL,
            recurrence_period TEXT,
            provider TEXT,
            invoice_number TEXT,
            notes TEXT,
            distribution_type TEXT DEFAULT 'General',
            specific_apartment TEXT,
            attachment_paths TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db.execute(query)
        
        # Agregar nuevas columnas si la tabla ya existe (migración)
        self._migrate_table_if_needed()

    def _migrate_table_if_needed(self):
        """Migra la tabla de gastos agregando nuevas columnas si es necesario."""
        try:
            # Obtener información de la tabla actual
            pragma_query = "PRAGMA table_info(expenses)"
            existing_columns = self.db.fetch_all(pragma_query)
            existing_column_names = [col['name'] for col in existing_columns] if existing_columns else []
            
            # Verificar si existen las nuevas columnas
            columns_to_add = [
                ("recurrence_period", "TEXT"),
                ("distribution_type", "TEXT DEFAULT 'General'"),
                ("specific_apartment", "TEXT"),
                ("attachment_paths", "TEXT"),
                ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
                ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            ]
            
            for column_name, column_type in columns_to_add:
                if column_name not in existing_column_names:
                    try:
                        alter_query = f"ALTER TABLE expenses ADD COLUMN {column_name} {column_type}"
                        self.db.execute(alter_query)
                        print(f"Columna {column_name} agregada exitosamente")
                    except Exception as e:
                        print(f"Error agregando columna {column_name}: {e}")
        except Exception as e:
            print(f"Error en migración de tabla de gastos: {e}")

    def register_expense(self, expense: Expense, attachments: List[str] = None, distribution_info: Dict[str, Any] = None) -> int:
        """
        Registra un nuevo gasto con funcionalidades extendidas.
        
        Args:
            expense: Datos del gasto
            attachments: Lista de rutas de archivos adjuntos
            distribution_info: Información de distribución por apartamentos
            
        Returns:
            ID del gasto registrado
        """
        # Preparar datos de distribución
        distribution_type = distribution_info.get('distribution_type', 'General') if distribution_info else 'General'
        specific_apartment = distribution_info.get('specific_apartment') if distribution_info else None
        
        # Preparar adjuntos
        attachment_paths = ';'.join(attachments) if attachments else None
        
        query = """
        INSERT INTO expenses (
            description, amount, date, category,
            payment_method, status, is_recurring, recurrence_period,
            provider, invoice_number, notes,
            distribution_type, specific_apartment, attachment_paths
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            expense.description,
            float(expense.amount),  # Convertir Decimal a float para SQLite
            expense.date,
            expense.category,
            getattr(expense, 'payment_method', 'Transferencia'),
            expense.status,
            getattr(expense, 'is_recurring', False),
            getattr(expense, 'recurrence_period', None),
            expense.provider,
            expense.invoice_number,
            getattr(expense, 'notes', None),
            distribution_type,
            specific_apartment,
            attachment_paths
        )
        cursor = self.db.execute(query, params)
        return cursor.lastrowid

    def get_by_id(self, expense_id: int) -> Optional[Expense]:
        """
        Obtiene un gasto por su ID.
        
        Args:
            expense_id: ID del gasto
            
        Returns:
            Gasto encontrado o None
        """
        query = "SELECT * FROM expenses WHERE id = ?"
        result = self.db.fetch_one(query, (expense_id,))
        return Expense(**result) if result else None

    def get_all(self) -> List[Expense]:
        """
        Obtiene todos los gastos.
        
        Returns:
            Lista de gastos
        """
        query = "SELECT * FROM expenses ORDER BY date DESC"
        results = self.db.fetch_all(query)
        return [Expense(**row) for row in results]

    def get_expenses_by_category(self, category: str) -> List[Expense]:
        """
        Obtiene los gastos de una categoría.
        
        Args:
            category: Categoría de gastos
            
        Returns:
            Lista de gastos de la categoría
        """
        query = "SELECT * FROM expenses WHERE category = ? ORDER BY date DESC"
        results = self.db.fetch_all(query, (category,))
        return [Expense(**row) for row in results]

    def get_expenses_by_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> List[Expense]:
        """
        Obtiene los gastos en un rango de fechas.
        
        Args:
            start_date: Fecha inicial
            end_date: Fecha final
            
        Returns:
            Lista de gastos en el rango
        """
        query = """
        SELECT * FROM expenses 
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC
        """
        results = self.db.fetch_all(query, (start_date, end_date))
        return [Expense(**row) for row in results]

    def update(self, expense_id: int, expense: Expense) -> bool:
        """
        Actualiza un gasto.
        
        Args:
            expense_id: ID del gasto
            expense: Nuevos datos del gasto
            
        Returns:
            True si se actualizó correctamente
        """
        query = """
        UPDATE expenses SET
            description = ?, amount = ?, date = ?,
            category = ?, payment_type = ?, status = ?,
            is_recurring = ?, provider = ?,
            invoice_number = ?, notes = ?
        WHERE id = ?
        """
        params = (
            expense.description,
            expense.amount,
            expense.date,
            expense.category,
            expense.payment_type,
            expense.status,
            expense.is_recurring,
            expense.provider,
            expense.invoice_number,
            expense.notes,
            expense_id
        )
        cursor = self.db.execute(query, params)
        return cursor.rowcount > 0

    def delete(self, expense_id: int) -> bool:
        """
        Elimina un gasto.
        
        Args:
            expense_id: ID del gasto
            
        Returns:
            True si se eliminó correctamente
        """
        query = "DELETE FROM expenses WHERE id = ?"
        cursor = self.db.execute(query, (expense_id,))
        return cursor.rowcount > 0

    def get_expense_metrics(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de gastos en un rango de fechas.
        
        Args:
            start_date: Fecha inicial
            end_date: Fecha final
            
        Returns:
            Diccionario con métricas:
            - total_expenses: Total de gastos
            - total_amount: Monto total
            - pending_amount: Monto pendiente
            - by_category: Gastos por categoría
        """
        # Métricas generales
        query = """
        SELECT 
            COUNT(*) as total_expenses,
            SUM(CASE WHEN status = 'Pagado' THEN amount ELSE 0 END) as total_amount,
            SUM(CASE WHEN status = 'Pendiente' THEN amount ELSE 0 END) as pending_amount
        FROM expenses
        WHERE date BETWEEN ? AND ?
        """
        result = self.db.fetch_one(query, (start_date, end_date))
        
        # Gastos por categoría
        category_query = """
        SELECT 
            category,
            SUM(amount) as category_amount
        FROM expenses
        WHERE date BETWEEN ? AND ?
        AND status = 'Pagado'
        GROUP BY category
        """
        category_results = self.db.fetch_all(category_query, (start_date, end_date))
        
        return {
            "total_expenses": result["total_expenses"] if result else 0,
            "total_amount": Decimal(str(result["total_amount"])) if result and result["total_amount"] else Decimal("0"),
            "pending_amount": Decimal(str(result["pending_amount"])) if result and result["pending_amount"] else Decimal("0"),
            "by_category": {
                row["category"]: Decimal(str(row["category_amount"]))
                for row in category_results
            } if category_results else {}
        }

    def get_recurring_expenses(self) -> List[Expense]:
        """Obtiene todos los gastos recurrentes."""
        query = "SELECT * FROM expenses WHERE is_recurring = 1 ORDER BY date DESC"
        rows = self.db.fetch_all(query)
        return [Expense(**row) for row in rows]

    def get_expense_summary_by_category(self, start_date: date, end_date: date) -> Dict[str, Decimal]:
        """Obtiene un resumen de gastos por categoría."""
        query = """
        SELECT 
            category,
            SUM(amount) as total_amount
        FROM expenses
        WHERE date BETWEEN ? AND ?
        AND status = 'Pagado'
        GROUP BY category
        """
        rows = self.db.fetch_all(query, (start_date, end_date))
        return {
            row["category"]: Decimal(str(row["total_amount"]))
            for row in rows
        }

    def get_upcoming_recurring_expenses(self, reference_date: date = None) -> List[Expense]:
        """Obtiene los próximos gastos recurrentes."""
        if reference_date is None:
            reference_date = date.today()

        recurring_expenses = self.get_recurring_expenses()
        upcoming_expenses = []

        for expense in recurring_expenses:
            next_date = expense.next_recurrence_date()
            if next_date and next_date > reference_date:
                # Crear una copia del gasto con la nueva fecha
                new_expense = Expense(
                    id=None,  # Nuevo ID cuando se registre
                    amount=expense.amount,
                    date=next_date,
                    category=expense.category,
                    description=expense.description,
                    provider=expense.provider,
                    invoice_number=None,  # Nueva factura cuando se registre
                    payment_method=expense.payment_method,
                    is_recurring=expense.is_recurring,
                    recurrence_period=expense.recurrence_period,
                    status="Pendiente"
                )
                upcoming_expenses.append(new_expense)

        return sorted(upcoming_expenses, key=lambda x: x.date)

    def get_expenses_by_apartment(self, apartment: str = None) -> List[Expense]:
        """
        Obtiene gastos filtrados por apartamento.
        
        Args:
            apartment: Número de apartamento específico. Si es None, obtiene gastos generales.
            
        Returns:
            Lista de gastos del apartamento
        """
        if apartment:
            query = """
            SELECT * FROM expenses 
            WHERE specific_apartment = ? OR distribution_type = 'Dividir entre todos'
            ORDER BY date DESC
            """
            results = self.db.fetch_all(query, (apartment,))
        else:
            query = """
            SELECT * FROM expenses 
            WHERE distribution_type = 'General'
            ORDER BY date DESC
            """
            results = self.db.fetch_all(query)
        
        return [self._create_expense_from_row(row) for row in results]

    def get_expenses_with_attachments(self) -> List[Dict[str, Any]]:
        """
        Obtiene gastos que tienen archivos adjuntos.
        
        Returns:
            Lista de gastos con información de adjuntos
        """
        query = """
        SELECT * FROM expenses 
        WHERE attachment_paths IS NOT NULL AND attachment_paths != ''
        ORDER BY date DESC
        """
        results = self.db.fetch_all(query)
        
        expenses_with_attachments = []
        for row in results:
            expense = self._create_expense_from_row(row)
            attachment_paths = row.get('attachment_paths', '').split(';') if row.get('attachment_paths') else []
            
            expenses_with_attachments.append({
                'expense': expense,
                'attachments': attachment_paths,
                'attachment_count': len(attachment_paths)
            })
        
        return expenses_with_attachments

    def search_expenses(
        self,
        search_text: str = None,
        category: str = None,
        provider: str = None,
        start_date: date = None,
        end_date: date = None,
        min_amount: Decimal = None,
        max_amount: Decimal = None,
        status: str = None,
        distribution_type: str = None
    ) -> List[Expense]:
        """
        Búsqueda avanzada de gastos con múltiples criterios.
        
        Args:
            search_text: Texto a buscar en descripción, proveedor, etc.
            category: Categoría específica
            provider: Proveedor específico
            start_date: Fecha inicial
            end_date: Fecha final
            min_amount: Monto mínimo
            max_amount: Monto máximo
            status: Estado del gasto
            distribution_type: Tipo de distribución
            
        Returns:
            Lista de gastos que coinciden con los criterios
        """
        conditions = []
        params = []
        
        base_query = "SELECT * FROM expenses WHERE 1=1"
        
        if search_text:
            conditions.append("(description LIKE ? OR provider LIKE ? OR invoice_number LIKE ?)")
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        if provider:
            conditions.append("provider LIKE ?")
            params.append(f"%{provider}%")
        
        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)
        
        if min_amount:
            conditions.append("amount >= ?")
            params.append(float(min_amount))
        
        if max_amount:
            conditions.append("amount <= ?")
            params.append(float(max_amount))
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        if distribution_type:
            conditions.append("distribution_type = ?")
            params.append(distribution_type)
        
        if conditions:
            query = base_query + " AND " + " AND ".join(conditions)
        else:
            query = base_query
        
        query += " ORDER BY date DESC"
        
        results = self.db.fetch_all(query, params)
        return [self._create_expense_from_row(row) for row in results]

    def get_category_analysis(
        self,
        start_date: date = None,
        end_date: date = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene análisis detallado por categorías de gastos.
        
        Args:
            start_date: Fecha inicial del análisis
            end_date: Fecha final del análisis
            
        Returns:
            Diccionario con análisis por categoría
        """
        conditions = []
        params = []
        
        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT 
            category,
            COUNT(*) as count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount,
            MIN(amount) as min_amount,
            MAX(amount) as max_amount,
            SUM(CASE WHEN status = 'Pendiente' THEN 1 ELSE 0 END) as pending_count
        FROM expenses
        WHERE {where_clause}
        GROUP BY category
        ORDER BY total_amount DESC
        """
        
        results = self.db.fetch_all(query, params)
        
        analysis = {}
        total_all_categories = sum(row['total_amount'] for row in results)
        
        for row in results:
            category = row['category']
            total_amount = Decimal(str(row['total_amount']))
            percentage = (total_amount / Decimal(str(total_all_categories)) * 100) if total_all_categories > 0 else 0
            
            analysis[category] = {
                'count': row['count'],
                'total_amount': total_amount,
                'avg_amount': Decimal(str(row['avg_amount'])),
                'min_amount': Decimal(str(row['min_amount'])),
                'max_amount': Decimal(str(row['max_amount'])),
                'pending_count': row['pending_count'],
                'percentage': percentage
            }
        
        return analysis

    def get_monthly_summary(self, year: int = None) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene resumen mensual de gastos.
        
        Args:
            year: Año específico. Si es None, usa el año actual.
            
        Returns:
            Diccionario con resumen por mes
        """
        if year is None:
            year = date.today().year
        
        query = """
        SELECT 
            strftime('%m', date) as month,
            COUNT(*) as count,
            SUM(amount) as total_amount,
            AVG(amount) as avg_amount,
            category,
            SUM(CASE WHEN status = 'Pendiente' THEN amount ELSE 0 END) as pending_amount
        FROM expenses
        WHERE strftime('%Y', date) = ?
        GROUP BY strftime('%m', date), category
        ORDER BY month, total_amount DESC
        """
        
        results = self.db.fetch_all(query, (str(year),))
        
        monthly_summary = {}
        for i in range(1, 13):
            month_key = f"{i:02d}"
            monthly_summary[month_key] = {
                'total_amount': Decimal('0'),
                'count': 0,
                'avg_amount': Decimal('0'),
                'pending_amount': Decimal('0'),
                'categories': {}
            }
        
        for row in results:
            month = row['month']
            category = row['category']
            
            if month not in monthly_summary[month]['categories']:
                monthly_summary[month]['categories'][category] = {
                    'count': 0,
                    'total_amount': Decimal('0'),
                    'avg_amount': Decimal('0')
                }
            
            monthly_summary[month]['total_amount'] += Decimal(str(row['total_amount']))
            monthly_summary[month]['count'] += row['count']
            monthly_summary[month]['pending_amount'] += Decimal(str(row['pending_amount']))
            
            monthly_summary[month]['categories'][category]['count'] += row['count']
            monthly_summary[month]['categories'][category]['total_amount'] += Decimal(str(row['total_amount']))
            monthly_summary[month]['categories'][category]['avg_amount'] = Decimal(str(row['avg_amount']))
        
        # Calcular promedios mensuales
        for month_data in monthly_summary.values():
            if month_data['count'] > 0:
                month_data['avg_amount'] = month_data['total_amount'] / month_data['count']
        
        return monthly_summary

    def _create_expense_from_row(self, row: Dict[str, Any]) -> Expense:
        """
        Crea un objeto Expense desde una fila de la base de datos.
        
        Args:
            row: Fila de la base de datos
            
        Returns:
            Objeto Expense
        """
        # Convertir datos de la base de datos
        expense_data = {
            'id': row.get('id'),
            'description': row.get('description'),
            'amount': Decimal(str(row.get('amount', 0))),
            'date': row.get('date'),
            'category': row.get('category'),
            'provider': row.get('provider'),
            'invoice_number': row.get('invoice_number'),
            'payment_method': row.get('payment_method', 'Transferencia'),
            'is_recurring': bool(row.get('is_recurring', False)),
            'recurrence_period': row.get('recurrence_period'),
            'status': row.get('status', 'Pagado')
        }
        
        # Filtrar None values
        expense_data = {k: v for k, v in expense_data.items() if v is not None}
        
        return Expense(**expense_data) 