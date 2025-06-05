import sqlite3
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from decimal import Decimal
import os
from datetime import date, datetime

class DatabaseService:
    """Servicio para gestionar la conexión y operaciones con la base de datos."""
    def __init__(self, db_path: str = "building_manager.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self._create_db_if_not_exists()

    def _create_db_if_not_exists(self):
        """Crea la base de datos si no existe."""
        if not os.path.exists(self.db_path):
            self.connect()

    def connect(self):
        """Establece una conexión con la base de datos."""
        conn = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        conn.row_factory = sqlite3.Row
        return conn

    def execute(
        self,
        query: str,
        params: Optional[Tuple[Any, ...]] = None
    ) -> sqlite3.Cursor:
        """
        Ejecuta una consulta SQL.
        
        Args:
            query: Consulta SQL
            params: Parámetros de la consulta
            
        Returns:
            Cursor con los resultados
        """
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor
        except Exception as e:
            self.logger.error(f"Error ejecutando consulta: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def execute_many(
        self,
        query: str,
        params: List[Tuple[Any, ...]]
    ) -> sqlite3.Cursor:
        """
        Ejecuta una consulta SQL múltiples veces.
        
        Args:
            query: Consulta SQL
            params: Lista de parámetros
            
        Returns:
            Cursor con los resultados
        """
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.executemany(query, params)
            conn.commit()
            return cursor
        except Exception as e:
            self.logger.error(f"Error ejecutando consulta múltiple: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def fetch_one(
        self,
        query: str,
        params: Optional[Tuple[Any, ...]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene un único resultado de una consulta.
        
        Args:
            query: Consulta SQL
            params: Parámetros de la consulta
            
        Returns:
            Diccionario con el resultado o None
        """
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            if conn:
                conn.close()

    def fetch_all(
        self,
        query: str,
        params: Optional[Tuple[Any, ...]] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene todos los resultados de una consulta.
        
        Args:
            query: Consulta SQL
            params: Parámetros de la consulta
            
        Returns:
            Lista de diccionarios con los resultados
        """
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            if conn:
                conn.close()

    def table_exists(self, table_name: str) -> bool:
        """
        Verifica si una tabla existe en la base de datos.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            True si la tabla existe
        """
        query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
        """
        result = self.fetch_one(query, (table_name,))
        return bool(result)

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL y retorna los resultados.
        
        Args:
            query: Consulta SQL
            params: Parámetros para la consulta
            
        Returns:
            Lista de diccionarios con los resultados
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_last_id(self) -> int:
        """
        Obtiene el último ID insertado.
        
        Returns:
            ID del último registro insertado
        """
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_insert_rowid()")
            return cursor.fetchone()[0] 