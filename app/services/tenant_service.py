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
        self.data_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/tenants.json'))
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
        try:
            # Generar nuevo ID
            new_id = max([t.get("id", 0) for t in self.tenants], default=0) + 1
            
            # Preparar archivos
            archivos = tenant_data.get("archivos", {})
            
            # Preparar datos del inquilino con valores por defecto
            apto_val = tenant_data.get("apartamento", "")
            if isinstance(apto_val, str):
                apto_val = apto_val.strip()
            tenant = {
                "id": new_id,
                "nombre": tenant_data.get("nombre", "").strip(),
                "numero_documento": tenant_data.get("numero_documento", "").strip(),
                "telefono": tenant_data.get("telefono", "").strip(),
                "email": tenant_data.get("email", "").strip(),
                "apartamento": apto_val,
                "valor_arriendo": float(tenant_data.get("valor_arriendo", 0)),
                "fecha_ingreso": tenant_data.get("fecha_ingreso", "").strip(),
                "estado_pago": tenant_data.get("estado_pago", "al_dia"),
                "direccion": tenant_data.get("direccion", "").strip(),
                "contacto_emergencia_nombre": tenant_data.get("contacto_emergencia_nombre", "").strip(),
                "contacto_emergencia_telefono": tenant_data.get("contacto_emergencia_telefono", "").strip(),
                "archivos": archivos,
                "has_documents": bool(archivos.get("id") or archivos.get("contract")),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "deposito": tenant_data.get("deposito", ""),
                "deposito_devuelto": 0  # Valor por defecto
            }
            
            # Agregar a la lista
            self.tenants.append(tenant)
            
            # Guardar cambios
            self._save_data()
            
            return tenant.copy()
            
        except Exception as e:
            print(f"Error al crear inquilino: {str(e)}")
            return None
    
    def update_tenant(self, tenant_id: int, tenant_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza un inquilino existente"""
        try:
            for i, tenant in enumerate(self.tenants):
                if tenant.get("id") == tenant_id:
                    # Actualizar todos los campos del diccionario tenant_data
                    for key, value in tenant_data.items():
                        self.tenants[i][key] = value
                    self.tenants[i]["updated_at"] = datetime.now().isoformat()
                    self._save_data()
                    return self.tenants[i].copy()
            return None
        except Exception as e:
            print(f"Error al actualizar inquilino: {str(e)}")
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
            if (
                query_lower in str(tenant.get("nombre") or "").lower() or
                query_lower in str(tenant.get("apartamento") or "").lower() or
                query_lower in str(tenant.get("telefono") or "").lower() or
                query_lower in str(tenant.get("email") or "").lower()
            ):
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
    
    def calculate_payment_status(self, tenant_id: int) -> str:
        """Calcula automáticamente el estado de pago basado en el historial real"""
        try:
            from manager.app.services.payment_service import payment_service
            from datetime import datetime, timedelta
            
            # Recargar datos de pagos para asegurar que estén actualizados
            payment_service._load_data()
            
            # Obtener el inquilino
            tenant = self.get_tenant_by_id(tenant_id)
            if not tenant:
                return "inactivo"
            
            # Obtener todos los pagos del inquilino (después de recargar datos)
            payments = payment_service.get_payments_by_tenant(tenant_id)
            
            if not payments:
                # Si no hay pagos, verificar si es un inquilino nuevo
                fecha_ingreso = tenant.get("fecha_ingreso", "")
                if fecha_ingreso:
                    try:
                        # Convertir fecha de ingreso a datetime
                        fecha_ingreso_dt = datetime.strptime(fecha_ingreso, "%d/%m/%Y")
                        dias_desde_ingreso = (datetime.now() - fecha_ingreso_dt).days
                        
                        if dias_desde_ingreso <= 5:
                            return "pendiente_registro"  # Alerta: pendiente registro pago inicial
                        else:
                            return "moroso"  # Sin pagos y más de 5 días
                    except:
                        return "moroso"  # Error en fecha, considerar moroso
                else:
                    return "moroso"  # Sin fecha de ingreso, considerar moroso
            
            # Ordenar pagos por fecha (más reciente primero)
            payments.sort(key=lambda x: datetime.strptime(x.get("fecha_pago", "01/01/1900"), "%d/%m/%Y"), reverse=True)
            
            # Obtener el pago más reciente
            ultimo_pago = payments[0]
            fecha_ultimo_pago = datetime.strptime(ultimo_pago.get("fecha_pago", "01/01/1900"), "%d/%m/%Y")
            
            # Calcular días desde el último pago
            dias_desde_ultimo_pago = (datetime.now() - fecha_ultimo_pago).days
            
            # Lógica para determinar estado:
            # - Si el último pago fue hace menos de 30 días: al_dia
            # - Si fue hace más de 30 días pero menos de 90: moroso
            # - Si fue hace más de 90 días: inactivo (muy moroso)
            
            if dias_desde_ultimo_pago <= 30:
                return "al_dia"
            elif dias_desde_ultimo_pago <= 90:
                return "moroso"
            else:
                return "inactivo"
                
        except Exception as e:
            print(f"Error al calcular estado de pago: {str(e)}")
            return "moroso"  # En caso de error, considerar moroso
    
    def update_payment_status(self, tenant_id: int) -> bool:
        """Actualiza el estado de pago de un inquilino basado en el cálculo automático"""
        try:
            new_status = self.calculate_payment_status(tenant_id)
            
            # Buscar y actualizar el inquilino en la lista original
            for i, tenant in enumerate(self.tenants):
                if tenant.get("id") == tenant_id:
                    self.tenants[i]["estado_pago"] = new_status
                    self.tenants[i]["updated_at"] = datetime.now().isoformat()
                    self._save_data()
                    print(f"✅ Estado actualizado para {tenant.get('nombre')}: {new_status}")
                    return True
            
            return False
        except Exception as e:
            print(f"Error al actualizar estado de pago: {str(e)}")
            return False
    
    def recalculate_all_payment_statuses(self) -> Dict[str, int]:
        """Recalcula el estado de pago de todos los inquilinos"""
        try:
            # Recargar datos de pagos antes de recalcular estados
            from manager.app.services.payment_service import payment_service
            payment_service._load_data()
            
            # Recargar datos de inquilinos también
            self._load_data()
            
            updated_count = 0
            status_changes = {
                'al_dia': 0,
                'pendiente_registro': 0,
                'moroso': 0,
                'inactivo': 0
            }
            
            for tenant in self.tenants:
                old_status = tenant.get('estado_pago', 'al_dia')
                new_status = self.calculate_payment_status(tenant.get('id'))
                
                if old_status != new_status:
                    tenant['estado_pago'] = new_status
                    tenant['updated_at'] = datetime.now().isoformat()
                    updated_count += 1
                    print(f"Inquilino {tenant.get('nombre')}: {old_status} → {new_status}")
                
                status_changes[new_status] += 1
            
            if updated_count > 0:
                self._save_data()
                print(f"✅ Estados actualizados: {updated_count} inquilinos")
            
            return status_changes
            
        except Exception as e:
            print(f"Error al recalcular estados: {str(e)}")
            return {}

# Instancia global del servicio
tenant_service = TenantService() 