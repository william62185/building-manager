#!/usr/bin/env python3
"""
Script de Validación de Integridad
Verifica que todos los archivos críticos y dependencias estén presentes
"""

import sys
from pathlib import Path
from typing import List, Tuple, Dict
import importlib.util

class IntegrityValidator:
    """Validador de integridad del proyecto"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.manager_dir = self.project_root / "manager"
        self.errors = []
        self.warnings = []
    
    def validate_file_exists(self, file_path: Path, description: str = "") -> bool:
        """Valida que un archivo exista"""
        if not file_path.exists():
            self.errors.append(f"❌ Archivo faltante: {file_path.relative_to(self.project_root)} {description}")
            return False
        return True
    
    def validate_import(self, module_path: str, description: str = "") -> bool:
        """Valida que un módulo se pueda importar"""
        try:
            # Intentar importar
            spec = importlib.util.find_spec(module_path)
            if spec is None:
                self.errors.append(f"❌ No se puede importar: {module_path} {description}")
                return False
            
            # Intentar cargar el módulo
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return True
        except Exception as e:
            self.errors.append(f"❌ Error al importar {module_path}: {str(e)} {description}")
            return False
    
    def validate_critical_files(self):
        """Valida archivos críticos del proyecto"""
        print("🔍 Validando archivos críticos...")
        
        critical_files = [
            # Servicios críticos
            (self.manager_dir / "app" / "services" / "app_config_service.py", "Servicio de configuración"),
            (self.manager_dir / "app" / "services" / "backup_service.py", "Servicio de backups"),
            (self.manager_dir / "app" / "services" / "tenant_service.py", "Servicio de inquilinos"),
            (self.manager_dir / "app" / "services" / "payment_service.py", "Servicio de pagos"),
            (self.manager_dir / "app" / "services" / "email_service.py", "Servicio de email"),
            (self.manager_dir / "app" / "services" / "building_service.py", "Servicio de edificios"),
            (self.manager_dir / "app" / "services" / "apartment_service.py", "Servicio de apartamentos"),
            
            # Vistas principales
            (self.manager_dir / "app" / "ui" / "views" / "main_window.py", "Vista principal"),
            (self.manager_dir / "app" / "ui" / "views" / "settings_view.py", "Vista de configuración"),
            (self.manager_dir / "app" / "ui" / "views" / "reports_view.py", "Vista de reportes"),
            (self.manager_dir / "app" / "ui" / "views" / "tenants_view.py", "Vista de inquilinos"),
            (self.manager_dir / "app" / "ui" / "views" / "payments_view.py", "Vista de pagos"),
            
            # Componentes UI
            (self.manager_dir / "app" / "ui" / "components" / "theme_manager.py", "Gestor de temas"),
            (self.manager_dir / "app" / "ui" / "components" / "modern_widgets.py", "Widgets modernos"),
            (self.manager_dir / "app" / "ui" / "components" / "icons.py", "Iconos"),
            
            # Punto de entrada
            (self.project_root / "run.py", "Punto de entrada principal"),
            (self.manager_dir / "app" / "main.py", "Módulo principal"),
        ]
        
        for file_path, description in critical_files:
            self.validate_file_exists(file_path, f"({description})")
    
    def validate_critical_imports(self):
        """Valida imports críticos"""
        print("🔍 Validando imports críticos...")
        
        critical_imports = [
            ("manager.app.services.app_config_service", "app_config_service"),
            ("manager.app.services.backup_service", "backup_service"),
            ("manager.app.services.tenant_service", "tenant_service"),
            ("manager.app.services.payment_service", "payment_service"),
            ("manager.app.ui.components.theme_manager", "theme_manager"),
            ("manager.app.ui.views.main_window", "MainWindow"),
            ("manager.app.ui.views.settings_view", "SettingsView"),
        ]
        
        for module_path, description in critical_imports:
            self.validate_import(module_path, f"({description})")
    
    def validate_service_instances(self):
        """Valida que los servicios tengan instancias globales"""
        print("🔍 Validando instancias de servicios...")
        
        try:
            from manager.app.services.app_config_service import app_config_service
            if not hasattr(app_config_service, 'get_theme'):
                self.errors.append("❌ app_config_service no tiene método get_theme")
        except Exception as e:
            self.errors.append(f"❌ Error al validar app_config_service: {str(e)}")
        
        try:
            from manager.app.services.backup_service import backup_service
            if not hasattr(backup_service, 'create_backup'):
                self.errors.append("❌ backup_service no tiene método create_backup")
        except Exception as e:
            self.errors.append(f"❌ Error al validar backup_service: {str(e)}")
    
    def validate_settings_view_variables(self):
        """Valida que SettingsView tenga todas las variables necesarias"""
        print("🔍 Validando variables de SettingsView...")
        
        try:
            # Intentar importar y verificar que la clase tenga los atributos necesarios
            from manager.app.ui.views.settings_view import SettingsView
            import inspect
            
            # Verificar que __init__ inicialice las variables necesarias
            source = inspect.getsource(SettingsView.__init__)
            required_vars = [
                'theme_var',
                'currency_symbol_var',
                'currency_code_var',
                'thousands_sep_var',
                'decimal_sep_var',
                'date_format_var',
                'auto_backup_var',
                'backup_interval_var',
                'max_backups_var'
            ]
            
            for var in required_vars:
                if f'self.{var}' not in source:
                    self.warnings.append(f"⚠️  SettingsView podría no tener la variable: {var}")
        except Exception as e:
            self.warnings.append(f"⚠️  No se pudo validar SettingsView: {str(e)}")
    
    def validate_directory_structure(self):
        """Valida la estructura de directorios"""
        print("🔍 Validando estructura de directorios...")
        
        required_dirs = [
            self.manager_dir / "app" / "services",
            self.manager_dir / "app" / "ui" / "views",
            self.manager_dir / "app" / "ui" / "components",
            self.project_root / "data",
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                self.errors.append(f"❌ Directorio faltante: {dir_path.relative_to(self.project_root)}")
    
    def run_validation(self) -> bool:
        """Ejecuta todas las validaciones"""
        print("\n" + "=" * 80)
        print("🔍 VALIDACIÓN DE INTEGRIDAD DEL PROYECTO")
        print("=" * 80 + "\n")
        
        self.validate_directory_structure()
        self.validate_critical_files()
        self.validate_critical_imports()
        self.validate_service_instances()
        self.validate_settings_view_variables()
        
        # Mostrar resultados
        print("\n" + "=" * 80)
        print("📊 RESULTADOS DE LA VALIDACIÓN")
        print("=" * 80 + "\n")
        
        if self.errors:
            print(f"❌ Errores encontrados: {len(self.errors)}")
            for error in self.errors:
                print(f"   {error}")
            print()
        else:
            print("✅ No se encontraron errores críticos\n")
        
        if self.warnings:
            print(f"⚠️  Advertencias: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   {warning}")
            print()
        
        if not self.errors:
            print("✅ El proyecto parece estar íntegro y funcional")
            return True
        else:
            print("❌ El proyecto tiene problemas que deben corregirse")
            return False


def main():
    """Función principal"""
    import sys
    
    # Agregar manager al path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root / "manager"))
    
    validator = IntegrityValidator()
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
