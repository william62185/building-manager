import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

APARTMENTS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/apartments.json'))

def _natural_sort_key(s):
    """Clave de ordenamiento natural para cadenas como '101', '201', 'Penthouse'."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'([0-9]+)', str(s))]

class ApartmentService:
    """Servicio para gestionar los datos de los apartamentos."""

    def __init__(self):
        self.apartments_file = APARTMENTS_FILE
        apartments, self._next_id, cleanup_needed = self._load_data()
        self.apartments = apartments
        
        # Si se realizó una limpieza durante la carga, guardar el resultado para hacerlo permanente.
        if cleanup_needed:
            print("INFO: Guardando la lista de apartamentos depurada para eliminar registros obsoletos permanentemente.")
            self._save_data()

    def _load_data(self) -> (List[Dict[str, Any]], int, bool):
        """Carga, limpia y ordena los apartamentos desde el archivo JSON."""
        cleanup_needed = False
        if not os.path.exists(self.apartments_file):
            return [], 1, False
        try:
            with open(self.apartments_file, 'r', encoding='utf-8') as f:
                apartments_from_file = json.load(f)

            if not isinstance(apartments_from_file, list):
                print(f"ADVERTENCIA: El archivo de apartamentos no contenía una lista. Se ha reiniciado.")
                return [], 1, False

            # Limpieza: solo cargar apartamentos que pertenecen a un edificio.
            valid_apartments = [apt for apt in apartments_from_file if apt.get('building_id') is not None]

            if len(valid_apartments) < len(apartments_from_file):
                print(f"INFO: Se han filtrado {len(apartments_from_file) - len(valid_apartments)} apartamentos obsoletos (sin ID de edificio).")
                cleanup_needed = True

            if not valid_apartments:
                return [], 1, cleanup_needed
            
            # Ordenar apartamentos por clave natural de su 'número'
            sorted_apartments = self._natural_sort_apartments(valid_apartments)
            next_id = max(apt.get('id', 0) for apt in sorted_apartments) + 1 if sorted_apartments else 1
            
            return sorted_apartments, next_id, cleanup_needed
        except (IOError, json.JSONDecodeError):
            return [], 1, False

    def _save_data(self):
        """Guarda la lista de apartamentos en el archivo JSON, manteniendo el orden."""
        try:
            sorted_apartments = self._natural_sort_apartments(self.apartments)
            with open(self.apartments_file, 'w', encoding='utf-8') as f:
                json.dump(sorted_apartments, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error al guardar datos de apartamentos: {e}")
    
    def _natural_sort_apartments(self, apartment_list: List[Dict[str, Any]]):
        """Ordena una lista de apartamentos usando ordenamiento natural por el campo 'number'."""
        return sorted(apartment_list, key=lambda x: _natural_sort_key(x.get('number', '')))

    def get_all_apartments(self) -> List[Dict[str, Any]]:
        """Devuelve todos los apartamentos, ordenados."""
        return self._natural_sort_apartments(self.apartments)

    def get_apartment_by_id(self, apartment_id: int) -> Optional[Dict[str, Any]]:
        """Busca un apartamento por su ID."""
        for apt in self.apartments:
            if apt.get('id') == apartment_id:
                return apt
        return None

    def create_apartment(self, apartment_data: Dict[str, Any], building_id: int) -> Dict[str, Any]:
        """Crea un nuevo apartamento asociado a un edificio."""
        new_apartment = {
            "id": self._next_id,
            "building_id": building_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **apartment_data
        }
        self.apartments.append(new_apartment)
        self._next_id += 1
        self._save_data()
        return new_apartment

    def update_apartment(self, apartment_id: int, apartment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza un apartamento existente."""
        for apt in self.apartments:
            if apt.get('id') == apartment_id:
                apt.update(apartment_data)
                apt['updated_at'] = datetime.now().isoformat()
                self._save_data()
                return apt
        return None

    def delete_apartment(self, apartment_id: int) -> bool:
        """Elimina un apartamento por su ID."""
        initial_count = len(self.apartments)
        self.apartments = [apt for apt in self.apartments if apt.get('id') != apartment_id]
        if len(self.apartments) < initial_count:
            self._save_data()
            return True
        return False

    def delete_apartments_by_building_id(self, building_id: int) -> bool:
        """Elimina todos los apartamentos asociados a un ID de edificio."""
        initial_count = len(self.apartments)
        self.apartments = [apt for apt in self.apartments if apt.get('building_id') != building_id]
        if len(self.apartments) < initial_count:
            self._save_data()
            return True
        return False

    def reload_data(self):
        """Recarga los datos de apartamentos desde el archivo JSON."""
        apartments, self._next_id, _ = self._load_data()
        self.apartments = apartments

apartment_service = ApartmentService()