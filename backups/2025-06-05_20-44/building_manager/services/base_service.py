from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic, Dict, Any
from .database_service import DatabaseService

T = TypeVar('T')

class BaseService(DatabaseService, Generic[T], ABC):
    """
    Servicio base abstracto que proporciona operaciones CRUD comunes.
    """
    def __init__(self, db_path: str = 'edificio.db'):
        super().__init__(db_path)
        self.table_name = self._get_table_name()
        self._ensure_table_exists()

    @abstractmethod
    def _get_table_name(self) -> str:
        """Retorna el nombre de la tabla para este servicio."""
        pass

    @abstractmethod
    def _get_create_table_sql(self) -> str:
        """Retorna el SQL para crear la tabla."""
        pass

    @abstractmethod
    def _to_model(self, row: Dict[str, Any]) -> T:
        """Convierte una fila de la base de datos al modelo correspondiente."""
        pass

    def _ensure_table_exists(self) -> None:
        """Asegura que la tabla existe en la base de datos."""
        if not self.table_exists(self.table_name):
            self.execute_query(self._get_create_table_sql(), fetch=False)
            self.logger.info(f"Tabla {self.table_name} creada exitosamente")

    def get_all(self) -> List[T]:
        """Obtiene todos los registros."""
        query = f"SELECT * FROM {self.table_name}"
        rows = self.execute_query(query)
        return [self._to_model(dict(zip(row.keys(), row))) for row in rows]

    def get_by_id(self, id: int) -> Optional[T]:
        """Obtiene un registro por su ID."""
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        rows = self.execute_query(query, (id,))
        return self._to_model(dict(zip(rows[0].keys(), rows[0]))) if rows else None

    def create(self, model: T) -> T:
        """Crea un nuevo registro."""
        data = model.to_dict()
        if 'id' in data:
            del data['id']  # La base de datos asignará el ID

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            model.id = cursor.lastrowid
            conn.commit()
        
        return model

    def update(self, id: int, model: T) -> Optional[T]:
        """Actualiza un registro existente."""
        data = model.to_dict()
        if 'id' in data:
            del data['id']

        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?"
        
        values = tuple(data.values()) + (id,)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            if cursor.rowcount == 0:
                return None
        
        model.id = id
        return model

    def delete(self, id: int) -> bool:
        """Elimina un registro por su ID."""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id,))
            conn.commit()
            return cursor.rowcount > 0

    def count(self) -> int:
        """Cuenta el número total de registros."""
        query = f"SELECT COUNT(*) as count FROM {self.table_name}"
        result = self.execute_query(query)
        return result[0]['count'] if result else 0 