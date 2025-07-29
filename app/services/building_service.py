"""
Servicio para gestionar la estructura del edificio.
Guarda y carga la configuración completa del edificio, incluyendo pisos y apartamentos.
"""
import json
import os
from typing import Dict, Any, Optional, List

# Define la ruta al archivo de datos de la estructura del edificio
BUILDING_STRUCTURE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/building_structure.json'))

class BuildingService:
    """Gestiona la carga y guardado de las estructuras de los edificios."""

    def __init__(self):
        self._buildings = self._load_buildings()

    def _load_buildings(self) -> List[Dict[str, Any]]:
        """Carga la lista de estructuras de edificios desde el archivo JSON."""
        if not os.path.exists(BUILDING_STRUCTURE_FILE):
            return []
        try:
            with open(BUILDING_STRUCTURE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error al cargar la estructura de los edificios: {e}")
            return []

    def _save_buildings(self):
        """Guarda la lista de estructuras actual en el archivo JSON."""
        try:
            with open(BUILDING_STRUCTURE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._buildings, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error al guardar la estructura de los edificios: {e}")

    def _get_next_building_id(self) -> int:
        """Calcula el siguiente ID de edificio disponible."""
        if not self._buildings:
            return 1
        return max(b.get('id', 0) for b in self._buildings) + 1

    def get_all_buildings(self) -> List[Dict[str, Any]]:
        """Devuelve todas las estructuras de edificios."""
        return self._buildings

    def has_buildings(self) -> bool:
        """Comprueba si ya existe al menos una estructura de edificio creada."""
        return bool(self._buildings)

    def can_create_new_building(self) -> bool:
        """Para la versión profesional: solo permite crear un edificio."""
        return not self.has_buildings()

    def get_active_building(self) -> Optional[Dict[str, Any]]:
        """Para la versión profesional: obtiene el edificio activo (el único)."""
        buildings = self.get_all_buildings()
        return buildings[0] if buildings else None

    def get_building_count(self) -> int:
        """Obtiene el número total de edificios."""
        return len(self._buildings)

    def update_building_name(self, building_id: int, new_name: str) -> bool:
        """Actualiza el nombre de un edificio específico."""
        for building in self._buildings:
            if building.get('id') == building_id:
                building['name'] = new_name
                self._save_buildings()
                return True
        return False

    def create_building_from_wizard(self, name: str, floors_config: List[Dict[str, Any]], special_units: List[Dict[str, Any]]):
        """
        Crea y guarda la estructura completa de un nuevo edificio y genera sus unidades
        individuales en el ApartmentService.
        """
        # Verificar si ya existe un edificio (versión profesional)
        if not self.can_create_new_building():
            raise ValueError("Ya existe un edificio configurado. La versión profesional solo permite un edificio.")

        from .apartment_service import apartment_service

        building_id = self._get_next_building_id()

        # 1. Crear la estructura del edificio
        new_building = {
            "id": building_id,
            "name": name,
            "floor_count": len(floors_config),
            "apartment_count": sum(f['apartment_count'] for f in floors_config),
            "special_unit_count": len(special_units),
            "floors": floors_config,
            "special_units": special_units
        }
        self._buildings.append(new_building)
        self._save_buildings()

        # 2. Generar los apartamentos para este nuevo edificio en ApartmentService
        apartments_to_create = []
        for floor_info in floors_config:
            floor_number = floor_info['floor_number']
            for i in range(floor_info['apartment_count']):
                apartments_to_create.append({
                    "number": f"{floor_number}{i+1:02d}",
                    "floor": str(floor_number),
                    "unit_type": "Apartamento Estándar",
                    "base_rent": "0", "status": "Disponible", "rooms": "0",
                    "bathrooms": "0", "area": "0",
                    "description": f"Apartamento estándar en el piso {floor_number}"
                })

        for unit in special_units:
             apartments_to_create.append({
                "number": unit['name'],
                "floor": unit['floor'],
                "unit_type": unit['type'],
                "base_rent": "0", "status": "Disponible", "rooms": "0",
                "bathrooms": "0", "area": "0",
                "description": f"Unidad especial: {unit['type']}"
            })
       
        for apt_data in apartments_to_create:
            # Asociar cada apartamento con el ID del nuevo edificio
            apartment_service.create_apartment(apt_data, building_id)

        return True

    def get_building_by_id(self, building_id):
        """Devuelve el edificio con el ID dado, o None si no existe."""
        for b in self.get_all_buildings():
            if b.get('id') == building_id:
                return b
        return None

building_service = BuildingService() 