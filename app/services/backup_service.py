"""
Servicio para gestión de backups completos del sistema
Incluye todos los datos, documentos y metadatos para restauración completa.
Soporta cifrado AES con contraseña (manual o guardada para automáticos) y copia a carpeta en la nube.
"""

import os
import shutil
import json
import platform
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from threading import Timer
import zipfile

try:
    import pyzipper
    _HAS_PYZIPPER = True
except ImportError:
    _HAS_PYZIPPER = False

from manager.app.paths_config import (
    BASE_PATH as _BASE_PATH,
    DATA_DIR as _DATA_DIR,
    BACKUPS_DIR as _BACKUPS_DIR,
    DOCUMENTOS_INQUILINOS_DIR,
    GASTOS_DOCS_DIR,
    EXPORTS_DIR,
    ensure_dirs,
)
from manager.app.logger import logger


class BackupService:
    """Servicio para gestión de backups completos del sistema"""
    
    BACKUP_DIR = _BACKUPS_DIR
    BASE_DIR = _BASE_PATH
    DATA_DIR = _DATA_DIR
    
    # (nombre_en_backup, Path del directorio)
    DOCUMENT_DIRS = [
        ("documentos_inquilinos", DOCUMENTOS_INQUILINOS_DIR),
        ("gastos_docs", GASTOS_DOCS_DIR),
        ("exports", EXPORTS_DIR),
    ]
    
    VERSION = "1.0.0"  # Versión del formato de backup
    
    def __init__(self):
        self._ensure_backup_directory()
        self._auto_backup_enabled = False
        self._backup_timer: Optional[Timer] = None
        self._max_backups = 5
        self._backup_interval_hours = 6
        # Activar backups automáticos cada 6 horas (crear el primero inmediatamente)
        self.start_auto_backup(create_immediately=True)
    
    def _ensure_backup_directory(self):
        """Asegura que el directorio de backups existe"""
        ensure_dirs()
        self.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    def create_full_backup(
        self,
        output_path: Optional[str] = None,
        password: Optional[str] = None,
        is_auto: bool = False,
    ) -> Optional[str]:
        """
        Crea un backup completo del sistema incluyendo:
        - Todos los archivos JSON de datos
        - Todos los documentos (PDFs, etc.)
        - Metadatos del sistema
        - Información de trazabilidad

        Si se indica contraseña (o is_auto y hay contraseña en configuración), el ZIP se cifra con AES.

        Args:
            output_path: Ruta donde guardar el backup. Si es None, se guarda en el directorio de backups.
            password: Contraseña para cifrar el backup. Si None y is_auto, se usa la de configuración.
            is_auto: Si True, se usa la contraseña de backups automáticos de app_config si no se pasa password.

        Returns:
            Ruta del archivo de backup creado o None si hay error
        """
        try:
            if is_auto and password is None:
                try:
                    from manager.app.services.app_config_service import app_config_service
                    backup_config = app_config_service.get_backup_config()
                    password = (backup_config.get("auto_backup_password") or "").strip() or None
                except Exception as e:
                    logger.debug("No se pudo obtener contraseña de auto-backup: %s", e)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_completo_{timestamp}.zip"

            if output_path:
                backup_path = Path(output_path)
                if backup_path.is_dir():
                    backup_path = backup_path / backup_filename
                else:
                    # Ruta escrita a mano: asumir que es directorio y crear si no existe
                    backup_path.mkdir(parents=True, exist_ok=True)
                    backup_path = backup_path / backup_filename
            else:
                backup_path = self.BACKUP_DIR / backup_filename

            backup_path.parent.mkdir(parents=True, exist_ok=True)
            use_encryption = bool(password and _HAS_PYZIPPER)

            if use_encryption:
                with pyzipper.AESZipFile(
                    backup_path,
                    "w",
                    compression=pyzipper.ZIP_DEFLATED,
                    encryption=pyzipper.WZ_AES,
                ) as zipf:
                    zipf.setpassword(password.encode("utf-8"))
                    self._write_backup_contents(zipf)
            else:
                with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    self._write_backup_contents(zipf)

            # Copiar a carpeta en la nube si está configurada
            self._copy_to_cloud_folder(backup_path)

            # Limpiar backups antiguos (solo si se guardó en el directorio de backups)
            if not output_path or Path(output_path).is_dir():
                self._cleanup_old_backups()

            return str(backup_path)
        except Exception as e:
            logger.exception("Error al crear backup completo: %s", e)
            return None

    def _write_backup_contents(self, zipf) -> None:
        """Escribe el contenido del backup en el ZipFile ya abierto (estándar o pyzipper)."""
        if self.DATA_DIR.exists():
            for file_path in self.DATA_DIR.glob("*.json"):
                zipf.write(file_path, f"data/{file_path.name}")
        for dir_name, dir_path in self.DOCUMENT_DIRS:
            if dir_path.exists() and dir_path.is_dir():
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file():
                        arcname = f"{dir_name}/{file_path.relative_to(dir_path)}"
                        zipf.write(file_path, arcname)
        metadata = self._create_metadata()
        metadata_json = json.dumps(metadata, indent=2, ensure_ascii=False)
        zipf.writestr("backup_metadata.json", metadata_json)

    def _copy_to_cloud_folder(self, backup_path: Path) -> None:
        """Si hay carpeta en la nube configurada, copia el backup allí."""
        try:
            from manager.app.services.app_config_service import app_config_service
            backup_config = app_config_service.get_backup_config()
            cloud_folder = (backup_config.get("cloud_folder") or "").strip()
            if not cloud_folder:
                return
            dest_dir = Path(cloud_folder)
            if not dest_dir.is_dir():
                dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir / backup_path.name
            shutil.copy2(backup_path, dest_file)
            logger.info("Backup copiado a carpeta en la nube: %s", dest_file)
        except Exception as e:
            logger.warning("No se pudo copiar el backup a la carpeta en la nube: %s", e)
    
    def _create_metadata(self) -> Dict[str, Any]:
        """Crea metadatos del backup para trazabilidad"""
        return {
            "version": self.VERSION,
            "created_at": datetime.now().isoformat(),
            "created_by": "Building Manager Pro",
            "system_info": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.machine(),
                "python_version": platform.python_version()
            },
            "backup_contents": {
                "data_files": [f.name for f in self.DATA_DIR.glob("*.json")] if self.DATA_DIR.exists() else [],
                "document_dirs": self._get_document_dirs_info()
            },
            "statistics": self._get_system_statistics()
        }
    
    def _get_document_dirs_info(self) -> List[Dict[str, Any]]:
        """Obtiene información sobre los directorios de documentos respaldados"""
        dirs_info = []
        for dir_name, dir_path in self.DOCUMENT_DIRS:
            if dir_path.exists() and dir_path.is_dir():
                files = list(dir_path.rglob("*"))
                file_count = len([f for f in files if f.is_file()])
                dirs_info.append({
                    "name": dir_name,
                    "path": dir_name,
                    "file_count": file_count
                })
        return dirs_info
    
    def _get_system_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema para el backup"""
        stats = {}
        
        try:
            # Contar inquilinos
            tenants_file = self.DATA_DIR / "tenants.json"
            if tenants_file.exists():
                with open(tenants_file, 'r', encoding='utf-8') as f:
                    tenants = json.load(f)
                    stats["total_tenants"] = len(tenants) if isinstance(tenants, list) else 0
                    # Contar activos e inactivos
                    if isinstance(tenants, list):
                        stats["active_tenants"] = len([t for t in tenants if t.get('estado_pago') != 'inactivo'])
                        stats["inactive_tenants"] = len([t for t in tenants if t.get('estado_pago') == 'inactivo'])
            
            # Contar pagos
            payments_file = self.DATA_DIR / "payments.json"
            if payments_file.exists():
                with open(payments_file, 'r', encoding='utf-8') as f:
                    payments = json.load(f)
                    stats["total_payments"] = len(payments) if isinstance(payments, list) else 0
            
            # Contar apartamentos
            apartments_file = self.DATA_DIR / "apartments.json"
            if apartments_file.exists():
                with open(apartments_file, 'r', encoding='utf-8') as f:
                    apartments = json.load(f)
                    stats["total_apartments"] = len(apartments) if isinstance(apartments, list) else 0
                    # Contar por estado
                    if isinstance(apartments, list):
                        stats["available_apartments"] = len([a for a in apartments if a.get('status') == 'Disponible'])
                        stats["occupied_apartments"] = len([a for a in apartments if a.get('status') == 'Ocupado'])
            
            # Contar gastos
            expenses_file = self.DATA_DIR / "gastos.json"
            if expenses_file.exists():
                with open(expenses_file, 'r', encoding='utf-8') as f:
                    expenses = json.load(f)
                    stats["total_expenses"] = len(expenses) if isinstance(expenses, list) else 0
            
            # Contar documentos por directorio
            total_docs = 0
            docs_by_dir = {}
            for dir_name, dir_path in self.DOCUMENT_DIRS:
                if dir_path.exists():
                    files = [f for f in dir_path.rglob("*") if f.is_file()]
                    file_count = len(files)
                    total_docs += file_count
                    docs_by_dir[dir_name] = file_count
            stats["total_documents"] = total_docs
            stats["documents_by_directory"] = docs_by_dir
            
        except Exception as e:
            logger.warning("Error al obtener estadísticas: %s", e)
        
        return stats
    
    def _open_backup_zip(self, backup_file: Path, password: Optional[str] = None):
        """Abre un archivo de backup (ZIP normal o cifrado). Retorna un context manager."""
        if password and _HAS_PYZIPPER:
            zf = pyzipper.AESZipFile(backup_file, "r")
            zf.setpassword(password.encode("utf-8"))
            return zf
        try:
            return zipfile.ZipFile(backup_file, "r")
        except Exception:
            if password and _HAS_PYZIPPER:
                zf = pyzipper.AESZipFile(backup_file, "r")
                zf.setpassword(password.encode("utf-8"))
                return zf
            raise

    def restore_from_backup(
        self,
        backup_path: str,
        confirm_callback: Optional[Callable] = None,
        password: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Restaura el sistema desde un archivo de backup.

        Args:
            backup_path: Ruta al archivo de backup
            confirm_callback: Función callback para confirmar antes de restaurar
            password: Contraseña si el backup está cifrado

        Returns:
            Dict con resultado de la restauración
        """
        result = {
            "success": False,
            "message": "",
            "errors": [],
            "restored_files": [],
        }

        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                result["message"] = f"El archivo de backup no existe: {backup_path}"
                return result

            if backup_file.suffix != ".zip":
                result["message"] = "El archivo no es un backup válido (debe ser .zip)"
                return result

            metadata = self._extract_metadata(backup_file, password=password)
            if not metadata:
                result["message"] = "El archivo no contiene metadatos válidos de backup. Si está cifrado, use la contraseña correcta."
                return result

            if confirm_callback and not confirm_callback(metadata):
                result["message"] = "Restauración cancelada por el usuario"
                return result

            safety_backup = self.create_full_backup()
            if safety_backup:
                result["safety_backup"] = safety_backup

            with self._open_backup_zip(backup_file, password=password) as zipf:
                for member in zipf.namelist():
                    if member == "backup_metadata.json":
                        continue
                    if member.startswith("data/"):
                        file_name = member.replace("data/", "")
                        target_path = self.DATA_DIR / file_name
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with zipf.open(member) as source:
                            with open(target_path, "wb") as target:
                                target.write(source.read())
                        result["restored_files"].append(str(target_path))
                    elif any(member.startswith(f"{d[0]}/") for d in self.DOCUMENT_DIRS):
                        target_path = self.BASE_DIR / member
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        with zipf.open(member) as source:
                            with open(target_path, "wb") as target:
                                target.write(source.read())
                        result["restored_files"].append(str(target_path))

            result["success"] = True
            result["message"] = f"Restauración completada exitosamente. {len(result['restored_files'])} archivos restaurados."
            result["metadata"] = metadata
            self._reload_services()

        except Exception as e:
            result["message"] = f"Error durante la restauración: {str(e)}"
            result["errors"].append(str(e))

        return result
    
    def _reload_services(self):
        """Recarga los servicios después de una restauración para que los datos actualizados se reflejen"""
        try:
            # Importar servicios globales
            from manager.app.services.tenant_service import tenant_service
            from manager.app.services.payment_service import payment_service
            from manager.app.services.apartment_service import apartment_service
            from manager.app.services.expense_service import expense_service
            from manager.app.services.building_service import building_service
            
            # Recargar datos de cada servicio
            if hasattr(tenant_service, '_load_data'):
                tenant_service._load_data()
            if hasattr(payment_service, '_load_data'):
                payment_service._load_data()
            if hasattr(apartment_service, '_load_data'):
                apartment_service._load_data()
            if hasattr(expense_service, '_load_data'):
                expense_service._load_data()
            if hasattr(building_service, '_load_buildings'):
                building_service._load_buildings()
                
        except Exception as e:
            logger.warning("No se pudieron recargar todos los servicios: %s. Se recomienda reiniciar la aplicación.", e)
    
    def _extract_metadata(self, backup_file: Path, password: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Extrae metadatos de un archivo de backup. Si está cifrado, se debe pasar password."""
        try:
            with self._open_backup_zip(backup_file, password=password) as zipf:
                if "backup_metadata.json" in zipf.namelist():
                    metadata_json = zipf.read("backup_metadata.json").decode("utf-8")
                    return json.loads(metadata_json)
        except Exception as e:
            logger.debug("Error al extraer metadatos (puede ser backup cifrado): %s", e)
        return None
    
    def validate_backup(self, backup_path: str, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Valida que un archivo de backup sea válido. Si está cifrado, indicar password.

        Returns:
            Dict con información de validación
        """
        result = {"valid": False, "message": "", "metadata": None, "files_count": 0}
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                result["message"] = "El archivo no existe"
                return result
            if backup_file.suffix != ".zip":
                result["message"] = "El archivo no es un ZIP válido"
                return result
            with self._open_backup_zip(backup_file, password=password) as zipf:
                result["files_count"] = len(zipf.namelist())
            metadata = self._extract_metadata(backup_file, password=password)
            if metadata:
                result["valid"] = True
                result["metadata"] = metadata
                result["message"] = f"Backup válido creado el {metadata.get('created_at', 'desconocido')}"
            else:
                result["message"] = "El backup no contiene metadatos válidos o requiere contraseña."
        except Exception as e:
            result["message"] = f"Error al validar backup: {str(e)}"
        return result
    
    def _cleanup_old_backups(self):
        """Elimina backups antiguos según la configuración de retención"""
        try:
            backups = list(self.BACKUP_DIR.glob("backup_completo_*.zip"))
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Mantener solo los más recientes según max_backups
            if len(backups) > self._max_backups:
                for old_backup in backups[self._max_backups:]:
                    try:
                        old_backup.unlink()
                    except Exception as e:
                        logger.warning("Error al eliminar backup antiguo: %s", e)
        except Exception as e:
            logger.warning("Error al limpiar backups antiguos: %s", e)
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual de los backups"""
        backups = list(self.BACKUP_DIR.glob("backup_completo_*.zip"))
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        next_backup = None
        if self._auto_backup_enabled and self._backup_timer:
            next_backup_time = datetime.now() + timedelta(hours=self._backup_interval_hours)
            next_backup = next_backup_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return {
            "enabled": self._auto_backup_enabled,
            "interval_hours": self._backup_interval_hours,
            "max_backups": self._max_backups,
            "total_backups": len(backups),
            "next_backup": next_backup,
            "last_backup": backups[0].name if backups else None
        }
    
    def set_max_backups(self, max_backups: int):
        """Establece el número máximo de backups a mantener"""
        self._max_backups = max_backups
        self._cleanup_old_backups()
    
    def set_backup_interval(self, interval_hours: int):
        """Establece el intervalo entre backups en horas"""
        self._backup_interval_hours = interval_hours
        if self._auto_backup_enabled:
            self.stop_auto_backup()
            self.start_auto_backup(interval_hours)
    
    def start_auto_backup(self, interval_hours: int = None, create_immediately: bool = False):
        """Inicia los backups automáticos"""
        if interval_hours:
            self._backup_interval_hours = interval_hours
        
        if self._auto_backup_enabled:
            self.stop_auto_backup()
        
        self._auto_backup_enabled = True
        self._schedule_next_backup(create_now=create_immediately)
    
    def stop_auto_backup(self):
        """Detiene los backups automáticos"""
        self._auto_backup_enabled = False
        if self._backup_timer:
            self._backup_timer.cancel()
            self._backup_timer = None
    
    def _schedule_next_backup(self, create_now: bool = True):
        """Programa el próximo backup"""
        if not self._auto_backup_enabled:
            return
        
        # Crear backup ahora si se indica (is_auto=True para usar contraseña de configuración)
        if create_now:
            try:
                self.create_full_backup(is_auto=True)
            except Exception as e:
                logger.warning("Error al crear backup automático: %s", e)
        
        # Programar próximo backup
        interval_seconds = self._backup_interval_hours * 3600
        self._backup_timer = Timer(interval_seconds, lambda: self._schedule_next_backup(create_now=True))
        self._backup_timer.daemon = True
        self._backup_timer.start()
    
    def get_backup_list(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de backups disponibles"""
        backups = list(self.BACKUP_DIR.glob("backup_completo_*.zip"))
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        backup_list = []
        for backup_file in backups:
            stat = backup_file.stat()
            metadata = self._extract_metadata(backup_file)
            
            backup_info = {
                "filename": backup_file.name,
                "path": str(backup_file),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size_mb": round(stat.st_size / (1024 * 1024), 2)
            }
            
            if metadata:
                backup_info["metadata"] = metadata
                backup_info["statistics"] = metadata.get("statistics", {})
            
            backup_list.append(backup_info)
        
        return backup_list
    
    # Método legacy para compatibilidad
    def create_backup(self) -> Optional[str]:
        """Método legacy - usa create_full_backup"""
        return self.create_full_backup()


# Instancia global del servicio
backup_service = BackupService()
