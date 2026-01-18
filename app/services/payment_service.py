import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

class PaymentService:
    DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "payments.json"

    def __init__(self):
        self._ensure_data_file()
        self._load_data()

    def _ensure_data_file(self):
        if not self.DATA_FILE.exists():
            self.DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _load_data(self):
        try:
            with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                self.payments = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.payments = []

    def _save_data(self):
        with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.payments, f, ensure_ascii=False, indent=2)

    def get_all_payments(self) -> List[Dict[str, Any]]:
        return self.payments.copy()

    def get_payments_by_tenant(self, tenant_id: int) -> List[Dict[str, Any]]:
        # Asegurar que los datos estén actualizados
        self._load_data()
        return [p for p in self.payments if p.get("id_inquilino") == tenant_id]

    def add_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        new_id = max([p.get("id", 0) for p in self.payments], default=0) + 1
        payment = {
            "id": new_id,
            "id_inquilino": payment_data.get("id_inquilino"),
            "nombre_inquilino": payment_data.get("nombre_inquilino", ""),
            "fecha_pago": payment_data.get("fecha_pago", datetime.now().strftime("%d/%m/%Y")),
            "monto": float(payment_data.get("monto", 0)),
            "metodo": payment_data.get("metodo", "Efectivo"),
            "observaciones": payment_data.get("observaciones", ""),
            "creado_en": datetime.now().isoformat(),
            "actualizado_en": datetime.now().isoformat()
        }
        self.payments.append(payment)
        self._save_data()
        
        # Actualizar automáticamente el estado del inquilino DESPUÉS de guardar
        tenant_id = payment_data.get("id_inquilino")
        if tenant_id:
            try:
                from manager.app.services.tenant_service import tenant_service
                # Recargar datos de inquilinos para asegurar datos actualizados
                tenant_service._load_data()
                # Recargar datos de pagos en este servicio para asegurar consistencia
                self._load_data()
                # Actualizar el estado del inquilino específico (esto también recarga pagos)
                tenant_service.update_payment_status(tenant_id)
                print(f"✅ Estado de pago actualizado para inquilino ID: {tenant_id}")
            except Exception as e:
                print(f"⚠️ Error al actualizar estado de pago: {str(e)}")
                import traceback
                traceback.print_exc()
        
        return payment.copy()

    def update_payment(self, payment_id: int, payment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for i, payment in enumerate(self.payments):
            if payment.get("id") == payment_id:
                for key, value in payment_data.items():
                    self.payments[i][key] = value
                self.payments[i]["actualizado_en"] = datetime.now().isoformat()
                self._save_data()
                
                # Actualizar automáticamente el estado del inquilino
                tenant_id = payment_data.get("id_inquilino")
                if tenant_id:
                    try:
                        from manager.app.services.tenant_service import tenant_service
                        tenant_service.update_payment_status(tenant_id)
                        print(f"✅ Estado de pago actualizado para inquilino ID: {tenant_id}")
                    except Exception as e:
                        print(f"⚠️ Error al actualizar estado de pago: {str(e)}")
                
                return self.payments[i].copy()
        return None

    def delete_payment(self, payment_id: int) -> bool:
        # Obtener el inquilino antes de eliminar el pago
        tenant_id = None
        for payment in self.payments:
            if payment.get("id") == payment_id:
                tenant_id = payment.get("id_inquilino")
                break
        
        initial_count = len(self.payments)
        self.payments = [p for p in self.payments if p.get("id") != payment_id]
        if len(self.payments) < initial_count:
            self._save_data()
            
            # Actualizar automáticamente el estado del inquilino después de eliminar el pago
            if tenant_id:
                try:
                    from manager.app.services.tenant_service import tenant_service
                    tenant_service.update_payment_status(tenant_id)
                    print(f"✅ Estado de pago actualizado para inquilino ID: {tenant_id} después de eliminar pago")
                except Exception as e:
                    print(f"⚠️ Error al actualizar estado de pago: {str(e)}")
            
            return True
        return False 

# Instancia global del servicio
payment_service = PaymentService() 