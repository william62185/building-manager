# Building Manager Pro - Manifiesto del Proyecto

Este documento describe la estructura crítica del proyecto y sus dependencias.

## 📁 Estructura de Directorios Crítica

```
building_manager_cursor/
├── manager/
│   ├── app/
│   │   ├── services/          # Servicios de negocio (CRUD, lógica)
│   │   ├── ui/
│   │   │   ├── components/    # Componentes reutilizables
│   │   │   └── views/         # Vistas principales
│   │   └── main.py            # Punto de entrada
│   └── data/                  # Archivos JSON de datos (desarrollo)
├── run.py                     # Lanzador principal
├── build_installer.py         # Script de empaquetado (PyInstaller)
└── pyi_rth_manager_paths.py   # Runtime hook PyInstaller (paths_config)
```

## 🔧 Servicios Críticos

### Servicios Core (Deben existir siempre)

1. **app_config_service.py**
   - Gestión de configuración general
   - Tema, moneda, formato de fecha, backups
   - **Instancia global:** `app_config_service`
   - **Métodos críticos:** `get_theme()`, `get_currency_config()`, `get_backup_config()`

2. **backup_service.py**
   - Backups automáticos del sistema
   - **Instancia global:** `backup_service`
   - **Métodos críticos:** `create_backup()`, `start_auto_backup()`

3. **tenant_service.py**
   - Gestión de inquilinos
   - **Instancia global:** `tenant_service`
   - **Métodos críticos:** `get_all_tenants()`, `update_payment_status()`

4. **payment_service.py**
   - Gestión de pagos
   - **Instancia global:** `payment_service`
   - **Métodos críticos:** `get_all_payments()`, `add_payment()`

5. **email_service.py**
   - Envío de emails SMTP
   - **Instancia global:** `email_service`
   - **Métodos críticos:** `get_config()`, `is_configured()`

6. **building_service.py**
   - Gestión de edificios
   - **Instancia global:** `building_service`

7. **apartment_service.py**
   - Gestión de apartamentos
   - **Instancia global:** `apartment_service`

## 🎨 Componentes UI Críticos

1. **theme_manager.py**
   - Gestión de temas (light/dark)
   - **Clase:** `ThemeManager`
   - **Instancia global:** `theme_manager`
   - **Constantes:** `Spacing`, `Colors`

2. **modern_widgets.py**
   - Widgets reutilizables
   - **Clases:** `ModernButton`, `ModernCard`, `ModernSeparator`

3. **icons.py**
   - Iconos del sistema
   - **Clase:** `Icons`

## 📱 Vistas Principales

1. **main_window.py**
   - Ventana principal y navegación
   - **Clase:** `MainWindow`
   - **Dependencias:** Todas las vistas

2. **settings_view.py**
   - Configuración del sistema
   - **Clase:** `SettingsView`
   - **Variables críticas en __init__:**
     - `theme_var`
     - `currency_symbol_var`, `currency_code_var`
     - `thousands_sep_var`, `decimal_sep_var`
     - `date_format_var`
     - `auto_backup_var`, `backup_interval_var`, `max_backups_var`
   - **Dependencias:** `app_config_service`, `backup_service`, `email_service`

3. **reports_view.py**
   - Generación de reportes
   - **Clase:** `ReportsView`

4. **tenants_view.py**
   - Gestión de inquilinos
   - **Clase:** `TenantsView`

5. **payments_view.py**
   - Gestión de pagos
   - **Clase:** `PaymentsView`

## 🔗 Dependencias Críticas

### SettingsView requiere:
- ✅ `app_config_service` (para tema, moneda, fecha, backups)
- ✅ `backup_service` (para configuración de backups)
- ✅ `email_service` (para configuración SMTP)

### MainWindow requiere:
- ✅ Todas las vistas
- ✅ Todos los servicios
- ✅ `theme_manager`

## 📝 Archivos de Configuración

- `data/app_config.json` - Configuración general
- `data/email_config.json` - Configuración SMTP
- `data/tenants.json` - Datos de inquilinos
- `data/payments.json` - Datos de pagos
- `data/building_structure.json` - Estructura del edificio

## ⚠️ Problemas Comunes

### Error: "ModuleNotFoundError: No module named 'manager.app.services.backup_service'"
**Solución:** Verificar que exista `manager/app/services/backup_service.py`.

### Error: "AttributeError: 'SettingsView' object has no attribute 'theme_var'"
**Solución:** Faltan variables en `__init__` de `SettingsView`. Verificar que todas las variables estén inicializadas.

### Error: "Colors.GRAY_600 no existe"
**Solución:** Usar `theme.get("text_secondary")` en lugar de `Colors.GRAY_600`.

---

**Última actualización:** 2025-03-04
