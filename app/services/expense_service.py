"""
Servicio para gestionar los gastos del edificio
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from manager.app.paths_config import DATA_DIR, ensure_dirs


class ExpenseService:
    """Servicio para gestionar los gastos del edificio"""
    
    DATA_FILE = DATA_DIR / "gastos.json"
    
    def __init__(self):
        self._ensure_data_file()
        self._load_data()
    
    def _ensure_data_file(self):
        """Asegura que el archivo de datos existe"""
        ensure_dirs()
        if not self.DATA_FILE.exists():
            self.DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_data(self):
        """Carga los datos de gastos desde el archivo JSON"""
        try:
            with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                self.expenses = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.expenses = []
    
    def _save_data(self):
        """Guarda los datos de gastos en el archivo JSON"""
        with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)
    
    def get_all_expenses(self) -> List[Dict[str, Any]]:
        """Obtiene todos los gastos"""
        return self.expenses.copy()
    
    def filter_expenses(self, year: Optional[int] = None, month: Optional[int] = None, 
                       category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Filtra los gastos por año, mes y/o categoría
        
        Args:
            year: Año a filtrar (opcional)
            month: Mes a filtrar (opcional, 1-12)
            category: Categoría a filtrar (opcional)
        
        Returns:
            Lista de gastos que cumplen con los filtros
        """
        filtered = self.expenses.copy()
        
        if year is not None or month is not None:
            filtered = [e for e in filtered if self._matches_date(e, year, month)]
        
        if category is not None:
            filtered = [e for e in filtered if e.get("categoria") == category]
        
        return filtered
    
    def _matches_date(self, expense: Dict[str, Any], year: Optional[int], month: Optional[int]) -> bool:
        """Verifica si un gasto coincide con el año y mes especificados"""
        fecha_str = expense.get("fecha", "")
        if not fecha_str:
            return False
        
        try:
            # La fecha está en formato "YYYY-MM-DD"
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
            
            if year is not None and fecha.year != year:
                return False
            
            if month is not None and fecha.month != month:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    def get_expense_by_id(self, expense_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un gasto por su ID"""
        for expense in self.expenses:
            if expense.get("id") == expense_id:
                return expense.copy()
        return None
    
    def add_expense(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agrega un nuevo gasto"""
        new_id = max([e.get("id", 0) for e in self.expenses], default=0) + 1
        expense = {
            "id": new_id,
            "fecha": expense_data.get("fecha", datetime.now().strftime("%Y-%m-%d")),
            "categoria": expense_data.get("categoria", ""),
            "subtipo": expense_data.get("subtipo", ""),
            "apartamento": expense_data.get("apartamento", "---"),
            "monto": float(expense_data.get("monto", 0)),
            "descripcion": expense_data.get("descripcion", ""),
            "documento": expense_data.get("documento")
        }
        self.expenses.append(expense)
        self._save_data()
        return expense.copy()
    
    def update_expense(self, expense_id: int, expense_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza un gasto existente"""
        for i, expense in enumerate(self.expenses):
            if expense.get("id") == expense_id:
                for key, value in expense_data.items():
                    self.expenses[i][key] = value
                self._save_data()
                return self.expenses[i].copy()
        return None
    
    def delete_expense(self, expense_id: int) -> bool:
        """Elimina un gasto"""
        initial_count = len(self.expenses)
        self.expenses = [e for e in self.expenses if e.get("id") != expense_id]
        
        if len(self.expenses) < initial_count:
            self._save_data()
            return True
        
        return False

# Instancia global del servicio
expense_service = ExpenseService()