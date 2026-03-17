"""
Servicio para gestión de inquilinos
Maneja operaciones CRUD con persistencia en JSON.
Incluye lógica de mora integral: períodos mensuales desde fecha_ingreso (día de pago),
aplicación de pagos a períodos y cálculo de días/meses en mora por montos.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from dateutil.relativedelta import relativedelta

from manager.app.paths_config import DATA_DIR, ensure_dirs
from manager.app.logger import logger
from manager.app.persistence import save_json_atomic

# Formato de fecha usado en la app (ingreso, pagos)
DATE_FMT = "%d/%m/%Y"


class TenantService:
    """Servicio para gestión de inquilinos"""
    
    def __init__(self):
        self.data_file = str(DATA_DIR / "tenants.json")
        self._ensure_data_directory()
        self._load_data()
    
    def _ensure_data_directory(self):
        """Asegura que el directorio de datos exista"""
        ensure_dirs()
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Crear archivo vacío si no existe
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_data(self):
        """Carga datos desde el archivo JSON. Si está corrupto, renombra a .bak y arranca con lista vacía."""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.tenants = json.load(f)
            if not isinstance(self.tenants, list):
                self.tenants = []
        except FileNotFoundError:
            self.tenants = []
        except json.JSONDecodeError:
            logger.warning("Archivo de inquilinos corrupto, respaldo como .bak y reinicio con lista vacía: %s", self.data_file)
            try:
                bak = Path(self.data_file).with_suffix(".json.bak")
                os.replace(self.data_file, bak)
            except Exception as e:
                logger.warning("No se pudo renombrar archivo corrupto: %s", e)
            self.tenants = []
    
    def _save_data(self):
        """Guarda datos al archivo JSON (escritura atómica)."""
        if not save_json_atomic(self.data_file, self.tenants, ensure_ascii=False, indent=2):
            raise IOError("No se pudo guardar tenants.json")
    
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
            logger.exception("Error al crear inquilino: %s", e)
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
            logger.exception("Error al actualizar inquilino: %s", e)
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

    @staticmethod
    def _parse_fecha(fecha_str: str) -> Optional[datetime]:
        """Parsea fecha en formato DD/MM/YYYY. Retorna datetime a las 00:00:00 o None."""
        if not fecha_str or not isinstance(fecha_str, str):
            return None
        s = fecha_str.strip()
        try:
            return datetime.strptime(s, DATE_FMT)
        except ValueError:
            try:
                return datetime.fromisoformat(s.replace("Z", "+00:00"))
            except Exception:
                return None

    def _get_arrears_info(self, tenant: Dict[str, Any], payments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula mora integral: períodos mensuales desde fecha_ingreso (día de pago),
        aplicación de pagos por monto y estado/días en mora.
        - Día de pago = día del mes de fecha_ingreso.
        - Pago por anticipado: el período 0 (primer mes de ocupación) vence en fecha_ingreso.
        - Período n vence en fecha_ingreso + n meses (n=0,1,2,...).
        - Pagos se aplican a períodos más antiguos primero (por monto total).
        - Al día solo cuando total_pagado >= total esperado de períodos vencidos.
        """
        hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_ingreso = self._parse_fecha(tenant.get("fecha_ingreso", "") or "")
        valor_arriendo = float(tenant.get("valor_arriendo") or 0)

        result = {
            "estado_pago": "al_dia",
            "dias_mora": 0,
            "dias_del_periodo_actual": 0,
            "meses_mora": 0,
            "periods_due": 0,
            "periods_covered": 0,
            "total_expected": 0.0,
            "total_paid": 0.0,
            "amount_pending": 0.0,  # total_expected + mes actual si ya estamos en ese período (pago por mes completo)
            "first_unpaid_due_date": None,
        }

        if not fecha_ingreso:
            result["estado_pago"] = "moroso"
            return result

        # Períodos vencidos: período 0 vence en fecha_ingreso (pago por anticipado), luego +1 mes cada uno
        # Contamos todo período con due_n <= hoy
        n = 0
        periods_due = 0
        while True:
            due_n = fecha_ingreso + relativedelta(months=n)
            if due_n > hoy:
                break
            periods_due += 1
            n += 1
        result["periods_due"] = periods_due
        result["total_expected"] = round(periods_due * valor_arriendo, 2)

        total_paid = sum(float(p.get("monto") or 0) for p in payments)
        result["total_paid"] = round(total_paid, 2)

        if valor_arriendo <= 0:
            result["periods_covered"] = periods_due if total_paid >= result["total_expected"] else 0
        else:
            result["periods_covered"] = min(periods_due, int(total_paid / valor_arriendo))
        periods_in_arrears = max(0, periods_due - result["periods_covered"])
        result["meses_mora"] = periods_in_arrears

        # Fecha de vencimiento del primer período impago (índice 0-based = periods_covered)
        first_unpaid_period = result["periods_covered"]
        first_unpaid_due = fecha_ingreso + relativedelta(months=first_unpaid_period)
        result["first_unpaid_due_date"] = first_unpaid_due

        if first_unpaid_due < hoy:
            result["dias_mora"] = (hoy - first_unpaid_due).days

        # Días del período actual (para formato "X meses y Y días"): días desde el inicio del
        # último período vencido (el "mes actual" en mora), no desde el primer período impago.
        if periods_in_arrears > 0:
            # Inicio del período actual = vencimiento del último período que ya venció (periods_due - 1)
            inicio_periodo_actual = fecha_ingreso + relativedelta(months=periods_due - 1)
            if hoy >= inicio_periodo_actual:
                result["dias_del_periodo_actual"] = (hoy - inicio_periodo_actual).days

        # Monto pendiente: total esperado de los períodos ya vencidos (total_expected ya incluye
        # el período actual si hoy >= su fecha de vencimiento; no sumar mes extra).
        result["amount_pending"] = result["total_expected"]

        # Estado: al día solo si lo pagado cubre todos los períodos vencidos.
        # Gracia de 5 días: si solo hay 1 período impago y estamos dentro de 5 días
        # desde su vencimiento, mostrar "pendiente_pago" (no "moroso") como apoyo visual.
        if periods_due == 0:
            dias_desde_ingreso = (hoy - fecha_ingreso).days
            result["estado_pago"] = "pendiente_registro" if dias_desde_ingreso <= 5 else "al_dia"
        elif total_paid >= result["total_expected"]:
            result["estado_pago"] = "al_dia"
        elif periods_in_arrears > 0:
            dias_desde_vencimiento = (hoy - first_unpaid_due).days
            if (
                periods_in_arrears == 1
                and hoy >= first_unpaid_due
                and 0 <= dias_desde_vencimiento <= 5
            ):
                result["estado_pago"] = "pendiente_pago"
                result["dias_mora"] = 0
                result["dias_del_periodo_actual"] = 0
            else:
                result["estado_pago"] = "moroso"
        else:
            result["estado_pago"] = "al_dia"

        return result

    def get_arrears_info(self, tenant_id: int) -> Optional[Dict[str, Any]]:
        """
        Retorna información de mora integral para el inquilino (para UI y reportes).
        Incluye estado_pago, dias_mora, meses_mora, total_expected, total_paid.
        """
        try:
            from manager.app.services.payment_service import payment_service
            payment_service._load_data()
            tenant = self.get_tenant_by_id(tenant_id)
            if not tenant:
                return None
            payments = payment_service.get_payments_by_tenant(tenant_id)
            return self._get_arrears_info(tenant, payments)
        except Exception as e:
            logger.warning("Error al obtener información de mora: %s", e)
            return None

    def get_dias_mora(self, tenant_id: int) -> int:
        """Retorna los días en mora (integral) para el inquilino. 0 si no aplica o error."""
        info = self.get_arrears_info(tenant_id)
        return (info or {}).get("dias_mora", 0)

    def calculate_payment_status(self, tenant_id: int) -> str:
        """Calcula el estado de pago con lógica de mora integral (períodos y montos)."""
        try:
            from manager.app.services.payment_service import payment_service
            payment_service._load_data()
            tenant = self.get_tenant_by_id(tenant_id)
            if not tenant:
                return "inactivo"
            payments = payment_service.get_payments_by_tenant(tenant_id)
            info = self._get_arrears_info(tenant, payments)
            return info["estado_pago"]
        except Exception as e:
            logger.warning("Error al calcular estado de pago: %s", e)
            return "moroso"
    
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
                    return True
            
            return False
        except Exception as e:
            logger.warning("Error al actualizar estado de pago: %s", e)
            return False
    
    def recalculate_all_payment_statuses(self) -> Dict[str, int]:
        """Recalcula el estado de pago de todos los inquilinos, excepto los desactivados manualmente"""
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
                'pendiente_pago': 0,
                'moroso': 0,
                'inactivo': 0
            }
            
            for tenant in self.tenants:
                old_status = tenant.get('estado_pago', 'al_dia')
                
                # NO recalcular estado si el inquilino fue desactivado manualmente
                # (tiene fecha_desactivacion o motivo_desactivacion)
                if tenant.get('fecha_desactivacion') or tenant.get('motivo_desactivacion'):
                    # Mantener el estado inactivo y no recalcular
                    if old_status == 'inactivo':
                        status_changes['inactivo'] += 1
                        continue
                
                # Recalcular estado solo para inquilinos no desactivados manualmente
                new_status = self.calculate_payment_status(tenant.get('id'))
                
                if old_status != new_status:
                    tenant['estado_pago'] = new_status
                    tenant['updated_at'] = datetime.now().isoformat()
                    updated_count += 1
                
                status_changes[new_status] += 1
            
            if updated_count > 0:
                self._save_data()
            
            return status_changes
            
        except Exception as e:
            logger.warning("Error al recalcular estados: %s", e)
            return {}

# Instancia global del servicio
tenant_service = TenantService() 