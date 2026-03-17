"""
Servicio para gestión de configuración general de la aplicación
Maneja tema, moneda, formato de fecha y configuración de backups
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

from manager.app.paths_config import DATA_DIR, ensure_dirs
from manager.app.logger import logger
from manager.app.persistence import save_json_atomic


class AppConfigService:
    """Servicio para gestión de configuración de la aplicación"""
    
    CONFIG_FILE = DATA_DIR / "app_config.json"
    
    def __init__(self):
        self._ensure_config_file()
        self._load_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Configuración por defecto única (evita duplicación)."""
        return {
            "theme": "dark",
            "currency": {
                "symbol": "$",
                "code": "COP",
                "thousands_separator": ".",
                "decimal_separator": ","
            },
            "date_format": "DD/MM/YYYY",
            "backup": {
                "auto_backup_enabled": True,
                "interval_hours": 6,
                "max_backups": 10,
                "auto_backup_password": "",
                "cloud_folder": ""
            },
            "license": {
                "first_run_date": None,
                "demo_ends_at": None,
                "license_key": None,
                "license_status": "unknown",
                "license_expires_at": None,
                "activated_at": None,
                "test_mode": False,
                "demo_days_override": 1,
                "force_expired": False
            }
        }
    
    def _ensure_config_file(self):
        """Asegura que el archivo de configuración existe"""
        try:
            from manager.app.paths_config import ensure_dirs
            ensure_dirs()
        except (NameError, ImportError, AttributeError):
            try:
                DATA_DIR.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
        if not self.CONFIG_FILE.exists():
            self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._default_config(), f, ensure_ascii=False, indent=2)
    
    def _load_config(self):
        """Carga la configuración desde el archivo. Si está corrupto, respaldo .bak y usa valores por defecto."""
        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            if not isinstance(self.config, dict):
                self.config = self._default_config().copy()
                self._save_config()
        except FileNotFoundError:
            self.config = self._default_config().copy()
            self._save_config()
        except json.JSONDecodeError:
            logger.warning("Archivo de configuración corrupto, respaldo como .bak: %s", self.CONFIG_FILE)
            try:
                bak = self.CONFIG_FILE.with_suffix(".json.bak")
                self.CONFIG_FILE.rename(bak)
            except Exception as e:
                logger.warning("No se pudo renombrar archivo corrupto: %s", e)
            self.config = self._default_config().copy()
            self._save_config()
    
    def _save_config(self):
        """Guarda la configuración al archivo (escritura atómica)."""
        return save_json_atomic(self.CONFIG_FILE, self.config, ensure_ascii=False, indent=2)
    
    # Métodos para tema
    def get_theme(self) -> str:
        """Obtiene el tema actual"""
        return self.config.get("theme", "dark")
    
    def set_theme(self, theme: str) -> bool:
        """Establece el tema (light o dark)"""
        if theme not in ["light", "dark"]:
            return False
        self.config["theme"] = theme
        return self._save_config()
    
    # Métodos para moneda
    def get_currency_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de moneda"""
        return self.config.get("currency", {
            "symbol": "$",
            "code": "COP",
            "thousands_separator": ".",
            "decimal_separator": ","
        })
    
    def set_currency_config(self, currency_config: Dict[str, Any]) -> bool:
        """Establece la configuración de moneda"""
        self.config["currency"] = currency_config
        return self._save_config()
    
    # Métodos para formato de fecha
    def get_date_format(self) -> str:
        """Obtiene el formato de fecha actual"""
        return self.config.get("date_format", "DD/MM/YYYY")
    
    def set_date_format(self, date_format: str) -> bool:
        """Establece el formato de fecha"""
        valid_formats = ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"]
        if date_format not in valid_formats:
            return False
        self.config["date_format"] = date_format
        return self._save_config()
    
    # Métodos para backups
    def get_backup_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de backups"""
        return self.config.get("backup", {
            "auto_backup_enabled": True,
            "interval_hours": 6,
            "max_backups": 10,
            "auto_backup_password": "",
            "cloud_folder": ""
        })
    
    def set_backup_config(self, backup_config: Dict[str, Any]) -> bool:
        """Establece la configuración de backups"""
        self.config["backup"] = backup_config
        return self._save_config()

    # Onboarding (primera vez)
    def get_onboarding_completed(self) -> bool:
        """Indica si el usuario ya completó el onboarding inicial."""
        return self.config.get("onboarding_completed", False)

    def set_onboarding_completed(self, completed: bool = True) -> bool:
        """Marca el onboarding como completado."""
        self.config["onboarding_completed"] = completed
        return self._save_config()

    # Licenciamiento
    def _default_license_config(self) -> Dict[str, Any]:
        return {
            "first_run_date": None,
            "demo_ends_at": None,
            "license_key": None,
            "license_status": "unknown",
            "license_expires_at": None,
            "activated_at": None,
            "test_mode": False,
            "demo_days_override": 1,
            "force_expired": False,
        }

    def get_license_config(self) -> Dict[str, Any]:
        """Obtiene la configuración de licencia, garantizando claves por defecto."""
        lic = self.config.get("license")
        base = self._default_license_config()
        if isinstance(lic, dict):
            base.update(lic)
        self.config["license"] = base
        return base

    def set_license_config(self, license_config: Dict[str, Any]) -> bool:
        """Actualiza parcial o totalmente la configuración de licencia."""
        current = self.get_license_config()
        current.update(license_config)
        self.config["license"] = current
        return self._save_config()


# Instancia global del servicio
app_config_service = AppConfigService()
