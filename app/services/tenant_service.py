"""
Servicio para gestión de inquilinos
Maneja operaciones CRUD con persistencia en JSON
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

class TenantService:
    """Servicio para gestión de inquilinos"""
    
    def __init__(self):
        self.data_file = "data/tenants.json"
        self._ensure_data_directory()
        self._load_data()
    
    def _ensure_data_directory(self):
        """Asegura que el directorio de datos exista"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Crear archivo vacío si no existe
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_data(self):
        """Carga datos desde el archivo JSON"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.tenants = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.tenants = []
    
    def _save_data(self):
        """Guarda datos al archivo JSON"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.tenants, f, ensure_ascii=False, indent=2)
    
    def get_all_tenants(self) -> List[Dict[str, Any]]:
        """Obtiene todos los inquilinos"""
        return self.tenants.copy()
    
    def get_tenant_by_id(self, tenant_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un inquilino por ID"""
        for tenant in self.tenants:
            if tenant.get("id") == tenant_id:
                return tenant.copy()
        return None
    
    def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo inquilino"""
        # Generar nuevo ID
        new_id = max([t.get("id", 0) for t in self.tenants], default=0) + 1
        
        # Preparar archivos
        archivos = tenant_data.get("archivos", {})
        
        # Preparar datos del inquilino
        tenant = {
            "id": new_id,
            "nombre": tenant_data.get("nombre", "").strip(),
            "numero_documento": tenant_data.get("numero_documento", "").strip(),
            "telefono": tenant_data.get("telefono", "").strip(),
            "email": tenant_data.get("email", "").strip(),
            "apartamento": tenant_data.get("apartamento", "").strip(),
            "valor_arriendo": float(tenant_data.get("valor_arriendo", 0)),
            "fecha_ingreso": tenant_data.get("fecha_ingreso", "").strip(),
            "estado_pago": tenant_data.get("estado_pago", "al_dia"),
            "direccion": tenant_data.get("direccion", "").strip(),
            "contacto_emergencia_nombre": tenant_data.get("contacto_emergencia_nombre", "").strip(),
            "contacto_emergencia_telefono": tenant_data.get("contacto_emergencia_telefono", "").strip(),
            "archivos": archivos,
            "has_documents": bool(archivos.get("id") or archivos.get("contract")),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Agregar a la lista
        self.tenants.append(tenant)
        self._save_data()
        
        return tenant.copy()
    
    def update_tenant(self, tenant_id: int, tenant_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza un inquilino existente"""
        for i, tenant in enumerate(self.tenants):
            if tenant.get("id") == tenant_id:
                # Preparar archivos
                archivos = tenant_data.get("archivos", tenant.get("archivos", {}))
                
                # Actualizar campos
                self.tenants[i].update({
                    "nombre": tenant_data.get("nombre", tenant.get("nombre", "")).strip(),
                    "numero_documento": tenant_data.get("numero_documento", tenant.get("numero_documento", "")).strip(),
                    "telefono": tenant_data.get("telefono", tenant.get("telefono", "")).strip(),
                    "email": tenant_data.get("email", tenant.get("email", "")).strip(),
                    "apartamento": tenant_data.get("apartamento", tenant.get("apartamento", "")).strip(),
                    "valor_arriendo": float(tenant_data.get("valor_arriendo", tenant.get("valor_arriendo", 0))),
                    "fecha_ingreso": tenant_data.get("fecha_ingreso", tenant.get("fecha_ingreso", "")).strip(),
                    "estado_pago": tenant_data.get("estado_pago", tenant.get("estado_pago", "al_dia")),
                    "direccion": tenant_data.get("direccion", tenant.get("direccion", "")).strip(),
                    "contacto_emergencia_nombre": tenant_data.get("contacto_emergencia_nombre", tenant.get("contacto_emergencia_nombre", "")).strip(),
                    "contacto_emergencia_telefono": tenant_data.get("contacto_emergencia_telefono", tenant.get("contacto_emergencia_telefono", "")).strip(),
                    "archivos": archivos,
                    "has_documents": bool(archivos.get("id") or archivos.get("contract")),
                    "updated_at": datetime.now().isoformat()
                })
                
                self._save_data()
                return self.tenants[i].copy()
        
        return None
    
    def delete_tenant(self, tenant_id: int) -> bool:
        """Elimina un inquilino"""
        initial_count = len(self.tenants)
        self.tenants = [t for t in self.tenants if t.get("id") != tenant_id]
        
        if len(self.tenants) < initial_count:
            self._save_data()
            return True
        
        return False
    
    def get_tenants_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Obtiene inquilinos por estado de pago"""
        return [t for t in self.tenants if t.get("estado_pago") == status]
    
    def search_tenants(self, query: str) -> List[Dict[str, Any]]:
        """Busca inquilinos por nombre, apartamento, teléfono o email"""
        query_lower = query.lower().strip()
        if not query_lower:
            return self.tenants.copy()
        
        results = []
        for tenant in self.tenants:
            if (query_lower in tenant.get("nombre", "").lower() or
                query_lower in tenant.get("apartamento", "").lower() or
                query_lower in tenant.get("telefono", "").lower() or
                query_lower in tenant.get("email", "").lower()):
                results.append(tenant.copy())
        
        return results
    
    def get_statistics(self) -> Dict[str, int]:
        """Obtiene estadísticas de inquilinos"""
        total = len(self.tenants)
        al_dia = len([t for t in self.tenants if t.get("estado_pago") == "al_dia"])
        moroso = len([t for t in self.tenants if t.get("estado_pago") == "moroso"])
        inactivo = len([t for t in self.tenants if t.get("estado_pago") == "inactivo"])
        
        return {
            "total": total,
            "al_dia": al_dia,
            "moroso": moroso,
            "inactivo": inactivo
        }

# Instancia global del servicio
tenant_service = TenantService() 