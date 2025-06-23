import json
import os
from pathlib import Path
from typing import List, Dict, Optional

class ExpenseService:
    """Servicio para gestionar gastos generales y particulares"""
    DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "gastos.json"

    def __init__(self):
        self._ensure_data_file()

    def _ensure_data_file(self):
        if not self.DATA_FILE.exists():
            self.DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

    def get_all_expenses(self) -> List[Dict]:
        with open(self.DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def add_expense(self, data: Dict) -> None:
        expenses = self.get_all_expenses()
        data["id"] = self._generate_id(expenses)
        expenses.append(data)
        self._save(expenses)

    def update_expense(self, expense_id: int, new_data: Dict) -> bool:
        expenses = self.get_all_expenses()
        for idx, exp in enumerate(expenses):
            if exp["id"] == expense_id:
                new_data["id"] = expense_id
                expenses[idx] = new_data
                self._save(expenses)
                return True
        return False

    def delete_expense(self, expense_id: int) -> bool:
        expenses = self.get_all_expenses()
        new_expenses = [e for e in expenses if e["id"] != expense_id]
        if len(new_expenses) == len(expenses):
            return False
        self._save(new_expenses)
        return True

    def _save(self, expenses: List[Dict]):
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(expenses, f, ensure_ascii=False, indent=2)

    def _generate_id(self, expenses: List[Dict]) -> int:
        if not expenses:
            return 1
        return max(e["id"] for e in expenses) + 1

    def filter_expenses(self, year=None, month=None, building=None, apartment=None) -> List[Dict]:
        expenses = self.get_all_expenses()
        result = expenses
        if year:
            result = [e for e in result if str(e.get("fecha", "")).startswith(str(year))]
        if month:
            result = [e for e in result if e.get("fecha", "")[5:7] == str(month).zfill(2)]
        if building:
            result = [e for e in result if e.get("edificio", "") == building]
        if apartment:
            result = [e for e in result if e.get("apartamento", "") == apartment]
        return result 