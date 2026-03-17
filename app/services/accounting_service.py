"""
Servicio para gestionar los asientos contables del edificio.
Persiste en accounting.json con dos listas: apertura y manual.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from manager.app.paths_config import DATA_DIR, ensure_dirs
from manager.app.persistence import save_json_atomic
from manager.app.logger import logger


class AccountingService:
    """Servicio para gestionar los asientos contables (apertura y manuales)."""

    DATA_FILE = DATA_DIR / "accounting.json"

    def __init__(self):
        self._data: Dict[str, List[Dict[str, Any]]] = {"apertura": [], "manual": []}
        self._ensure_data_file()
        self._load_data()

    # ------------------------------------------------------------------
    # Inicialización y persistencia
    # ------------------------------------------------------------------

    def _ensure_data_file(self):
        """Asegura que el archivo de datos existe con la estructura correcta."""
        ensure_dirs()
        if not self.DATA_FILE.exists():
            self.DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            save_json_atomic(self.DATA_FILE, {"apertura": [], "manual": []})

    def _load_data(self):
        """
        Carga los datos desde el archivo JSON.
        Si el archivo está corrupto, lo renombra a .bak, inicializa vacío y registra advertencia.
        """
        try:
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            bak = self.DATA_FILE.parent / (self.DATA_FILE.name + ".bak")
            try:
                self.DATA_FILE.rename(bak)
            except Exception:
                pass
            self._data = {"apertura": [], "manual": []}
            logger.warning(
                "accounting.json corrupto o no encontrado (%s). "
                "Se renombró a %s y se inicializó vacío.",
                exc,
                bak,
            )

    def _save_data(self):
        """Persiste los datos usando escritura atómica."""
        save_json_atomic(self.DATA_FILE, self._data)

    # ------------------------------------------------------------------
    # Lectura
    # ------------------------------------------------------------------

    def get_all_entries(self) -> List[Dict[str, Any]]:
        """Retorna una copia de todas las entradas (apertura + manual combinadas)."""
        self._load_data()
        return (
            [e.copy() for e in self._data.get("apertura", [])]
            + [e.copy() for e in self._data.get("manual", [])]
        )

    def get_entries_by_type(self, entry_type: str) -> List[Dict[str, Any]]:
        """
        Retorna una copia de la lista correspondiente al tipo indicado.

        Args:
            entry_type: "apertura" o "manual"
        """
        self._load_data()
        return [e.copy() for e in self._data.get(entry_type, [])]

    # ------------------------------------------------------------------
    # Escritura
    # ------------------------------------------------------------------

    def add_entry(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Añade un nuevo asiento contable.

        Infiere la lista destino del campo `tipo` en data ("apertura" o "manual").
        Genera el id como max(ids_en_lista) + 1 (o 1 si la lista está vacía).
        Añade los campos creado_en y actualizado_en en formato ISO 8601.

        Args:
            data: Diccionario con los campos del asiento. Debe incluir "tipo".

        Returns:
            Copia del registro creado.
        """
        self._load_data()
        entry_type = data.get("tipo", "manual")
        lista = self._data.setdefault(entry_type, [])

        ids = [e.get("id", 0) for e in lista if isinstance(e.get("id"), int)]
        new_id = max(ids) + 1 if ids else 1

        now = datetime.now().isoformat(timespec="seconds")
        entry = {**data, "id": new_id, "creado_en": now, "actualizado_en": now}
        lista.append(entry)
        self._save_data()
        return entry.copy()

    def update_entry(self, entry_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Actualiza un asiento existente buscando en ambas listas.

        Args:
            entry_id: ID del asiento a actualizar.
            data: Campos a actualizar.

        Returns:
            Copia del registro actualizado, o None si no se encontró.
        """
        self._load_data()
        for entry_type in ("apertura", "manual"):
            for i, entry in enumerate(self._data.get(entry_type, [])):
                if entry.get("id") == entry_id:
                    self._data[entry_type][i].update(data)
                    self._data[entry_type][i]["actualizado_en"] = datetime.now().isoformat(
                        timespec="seconds"
                    )
                    self._save_data()
                    return self._data[entry_type][i].copy()
        return None

    def delete_entry(self, entry_id: int) -> bool:
        """
        Elimina un asiento buscando en ambas listas.

        Args:
            entry_id: ID del asiento a eliminar.

        Returns:
            True si se encontró y eliminó, False si no se encontró.
        """
        self._load_data()
        for entry_type in ("apertura", "manual"):
            lista = self._data.get(entry_type, [])
            nueva_lista = [e for e in lista if e.get("id") != entry_id]
            if len(nueva_lista) < len(lista):
                self._data[entry_type] = nueva_lista
                self._save_data()
                return True
        return False


# Instancia global del servicio
accounting_service = AccountingService()
