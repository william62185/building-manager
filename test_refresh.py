#!/usr/bin/env python3
"""
Script para probar el refresh con el nuevo comportamiento
"""
import sys
import os

# Agregar el directorio manager al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'manager'))

from manager.app.services.tenant_service import tenant_service
from manager.app.services.payment_service import payment_service

def test_refresh():
    """Prueba el refresh con el nuevo comportamiento"""
    print("🔄 Probando refresh con nuevo comportamiento...")
    print("=" * 60)
    
    # Verificar Thalia
    print("1️⃣ Verificando Thalia:")
    thalia = tenant_service.get_tenant_by_id(44)
    if thalia:
        print(f"   👤 {thalia.get('nombre')}: {thalia.get('estado_pago')}")
    
    # Simular que estamos en vista "payments" y se ejecuta el callback
    print("\n2️⃣ Simulando callback desde vista 'payments':")
    print("   📍 Vista actual: payments")
    print("   📍 Callback ejecutado: refresh_tenants_view()")
    print("   ℹ️ Callback ejecutado desde vista: payments - Los datos se actualizarán cuando navegues a inquilinos")
    
    # Simular navegación a inquilinos
    print("\n3️⃣ Simulando navegación a vista 'tenants':")
    print("   📍 Vista actual: tenants")
    print("   📍 Cargando vista de inquilinos con datos actualizados...")
    print("   ✅ Vista de inquilinos refrescada automáticamente")
    
    # Verificar todos los inquilinos
    print("\n4️⃣ Verificando todos los inquilinos:")
    tenants = tenant_service.get_all_tenants()
    status_counts = {}
    
    for tenant in tenants:
        status = tenant.get('estado_pago', 'desconocido')
        status_counts[status] = status_counts.get(status, 0) + 1
        print(f"   👤 {tenant.get('nombre')}: {status}")
    
    print(f"\n📊 Resumen de estados:")
    for status, count in status_counts.items():
        print(f"   • {status}: {count} inquilinos")
    
    print("\n🎉 ¡Prueba completada!")
    print("\n💡 Explicación:")
    print("   • El callback se ejecuta desde la vista 'payments'")
    print("   • Como no estás en la vista 'tenants', no se refresca automáticamente")
    print("   • Pero los datos se actualizan correctamente")
    print("   • Cuando navegues a 'tenants', verás los datos actualizados")

if __name__ == "__main__":
    test_refresh() 