"""
Servicio para gestión de usuarios del sistema
Maneja operaciones CRUD con persistencia en JSON, roles, permisos y trazabilidad
"""

import json
import os
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from manager.app.paths_config import DATA_DIR, ensure_dirs
from manager.app.logger import logger
from manager.app.persistence import save_json_atomic


class UserService:
    """Servicio para gestión de usuarios del sistema"""
    
    # Roles disponibles
    ROLES = {
        "admin": "Administrador",
        "manager": "Gestor",
        "viewer": "Visualizador"
    }
    
    def __init__(self):
        self.data_file = DATA_DIR / "users.json"
        self.activity_file = DATA_DIR / "user_activity.json"
        self._ensure_data_directory()
        self._load_data()
        self._load_activity()
    
    def _ensure_data_directory(self):
        """Asegura que el directorio de datos exista"""
        ensure_dirs()
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Crear archivo de usuarios vacío si no existe
        if not self.data_file.exists():
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        
        # Crear archivo de actividad vacío si no existe
        if not self.activity_file.exists():
            with open(self.activity_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_data(self):
        """Carga datos de usuarios desde el archivo JSON.
        Si está corrupto, renombra a .bak y arranca con lista vacía.
        """
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
            if not isinstance(self.users, list):
                self.users = []
        except FileNotFoundError:
            self.users = []
        except json.JSONDecodeError:
            logger.warning("Archivo de usuarios corrupto, respaldo como .bak: %s", self.data_file)
            try:
                bak = self.data_file.with_suffix(".json.bak")
                self.data_file.rename(bak)
            except Exception as e:
                logger.warning("No se pudo renombrar archivo corrupto: %s", e)
            self.users = []
    
    def _load_activity(self):
        """Carga el historial de actividad"""
        try:
            with open(self.activity_file, 'r', encoding='utf-8') as f:
                self.activity_log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.activity_log = []
    
    def _create_default_admin(self):
        """Crea un usuario administrador por defecto"""
        default_password = self._hash_password("admin123")
        admin_user = {
            "id": 1,
            "username": "admin",
            "email": "admin@buildingmanager.com",
            "full_name": "Administrador",
            "password_hash": default_password,
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "created_by": "system",
            "last_login": None,
            "notes": "Usuario administrador por defecto"
        }
        self.users.append(admin_user)
        self._save_data()
        self._log_activity("system", "user_created", f"Usuario administrador por defecto creado: {admin_user['username']}")
    
    def _hash_password(self, password: str) -> str:
        """Genera un hash SHA-256 de la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _save_data(self):
        """Guarda datos de usuarios al archivo JSON (escritura atómica)."""
        if not save_json_atomic(self.data_file, self.users, ensure_ascii=False, indent=2):
            raise IOError("No se pudo guardar users.json")

    def _save_activity(self):
        """Guarda el historial de actividad (escritura atómica)."""
        if len(self.activity_log) > 1000:
            self.activity_log = self.activity_log[-1000:]
        if not save_json_atomic(self.activity_file, self.activity_log, ensure_ascii=False, indent=2):
            logger.warning("No se pudo guardar user_activity.json")
    
    def _log_activity(self, username: str, action: str, details: str, target_user: Optional[str] = None):
        """Registra una actividad en el historial"""
        activity = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "action": action,
            "details": details,
            "target_user": target_user
        }
        self.activity_log.append(activity)
        self._save_activity()
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios (sin contraseñas)"""
        users_copy = []
        for user in self.users:
            user_copy = user.copy()
            user_copy.pop("password_hash", None)  # No exponer hash de contraseña
            users_copy.append(user_copy)
        return users_copy
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por ID (sin contraseña)"""
        for user in self.users:
            if user.get("id") == user_id:
                user_copy = user.copy()
                user_copy.pop("password_hash", None)
                return user_copy
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por nombre de usuario"""
        for user in self.users:
            if user.get("username") == username:
                return user.copy()
        return None
    
    def create_user(self, user_data: Dict[str, Any], created_by: str = "admin") -> Dict[str, Any]:
        """Crea un nuevo usuario"""
        try:
            # Validar que el username no exista
            if self.get_user_by_username(user_data.get("username", "")):
                raise ValueError("El nombre de usuario ya existe")
            
            # Validar que el email no exista
            email = user_data.get("email", "").strip()
            if email and any(u.get("email") == email for u in self.users):
                raise ValueError("El email ya está registrado")
            
            # Generar nuevo ID
            new_id = max([u.get("id", 0) for u in self.users], default=0) + 1
            
            # Hash de contraseña
            password = user_data.get("password", "")
            password_hash = self._hash_password(password) if password else None
            
            # Crear usuario
            user = {
                "id": new_id,
                "username": user_data.get("username", "").strip(),
                "email": user_data.get("email", "").strip(),
                "full_name": user_data.get("full_name", "").strip(),
                "password_hash": password_hash,
                "role": user_data.get("role", "viewer"),
                "is_active": user_data.get("is_active", True),
                "created_at": datetime.now().isoformat(),
                "created_by": created_by,
                "last_login": None,
                "notes": user_data.get("notes", "").strip()
            }
            
            self.users.append(user)
            self._save_data()
            
            # Registrar actividad
            self._log_activity(
                created_by,
                "user_created",
                f"Usuario creado: {user['username']} (Rol: {self.ROLES.get(user['role'], user['role'])})",
                user['username']
            )
            
            # Retornar sin contraseña
            user_copy = user.copy()
            user_copy.pop("password_hash", None)
            return user_copy
            
        except Exception as e:
            raise ValueError(f"Error al crear usuario: {str(e)}")
    
    def update_user(self, user_id: int, user_data: Dict[str, Any], updated_by: str = "admin") -> Dict[str, Any]:
        """Actualiza un usuario existente"""
        try:
            user = None
            for u in self.users:
                if u.get("id") == user_id:
                    user = u
                    break
            
            if not user:
                raise ValueError("Usuario no encontrado")
            
            old_username = user.get("username")
            
            # Validar username único (si cambió)
            new_username = user_data.get("username", "").strip()
            if new_username and new_username != user.get("username"):
                if self.get_user_by_username(new_username):
                    raise ValueError("El nombre de usuario ya existe")
            
            # Validar email único (si cambió)
            new_email = user_data.get("email", "").strip()
            if new_email and new_email != user.get("email"):
                if any(u.get("email") == new_email for u in self.users if u.get("id") != user_id):
                    raise ValueError("El email ya está registrado")
            
            # Actualizar campos
            if "username" in user_data:
                user["username"] = new_username
            if "email" in user_data:
                user["email"] = new_email
            if "full_name" in user_data:
                user["full_name"] = user_data.get("full_name", "").strip()
            if "role" in user_data:
                user["role"] = user_data.get("role")
            if "is_active" in user_data:
                user["is_active"] = user_data.get("is_active")
            if "notes" in user_data:
                user["notes"] = user_data.get("notes", "").strip()
            
            user["updated_at"] = datetime.now().isoformat()
            user["updated_by"] = updated_by
            
            self._save_data()
            
            # Registrar actividad
            changes = []
            if "role" in user_data:
                changes.append(f"Rol: {self.ROLES.get(user['role'], user['role'])}")
            if "is_active" in user_data:
                changes.append(f"Estado: {'Activo' if user['is_active'] else 'Inactivo'}")
            
            self._log_activity(
                updated_by,
                "user_updated",
                f"Usuario actualizado: {user['username']}" + (f" ({', '.join(changes)})" if changes else ""),
                user['username']
            )
            
            # Retornar sin contraseña
            user_copy = user.copy()
            user_copy.pop("password_hash", None)
            return user_copy
            
        except Exception as e:
            raise ValueError(f"Error al actualizar usuario: {str(e)}")
    
    def change_password(self, user_id: int, new_password: str, changed_by: str = "admin") -> bool:
        """Cambia la contraseña de un usuario"""
        try:
            user = None
            for u in self.users:
                if u.get("id") == user_id:
                    user = u
                    break
            
            if not user:
                raise ValueError("Usuario no encontrado")
            
            # Hash de nueva contraseña
            user["password_hash"] = self._hash_password(new_password)
            user["password_changed_at"] = datetime.now().isoformat()
            user["password_changed_by"] = changed_by
            
            self._save_data()
            
            # Registrar actividad
            self._log_activity(
                changed_by,
                "password_changed",
                f"Contraseña cambiada para usuario: {user['username']}",
                user['username']
            )
            
            return True
            
        except Exception as e:
            raise ValueError(f"Error al cambiar contraseña: {str(e)}")
    
    def delete_user(self, user_id: int, deleted_by: str = "admin") -> bool:
        """Elimina un usuario (soft delete - marca como inactivo)"""
        try:
            user = None
            for u in self.users:
                if u.get("id") == user_id:
                    user = u
                    break
            
            if not user:
                raise ValueError("Usuario no encontrado")
            
            # No permitir eliminar el último admin activo
            if user.get("role") == "admin" and user.get("is_active"):
                admin_count = sum(1 for u in self.users if u.get("role") == "admin" and u.get("is_active"))
                if admin_count <= 1:
                    raise ValueError("No se puede eliminar el último administrador activo")
            
            # Soft delete - marcar como inactivo
            user["is_active"] = False
            user["deleted_at"] = datetime.now().isoformat()
            user["deleted_by"] = deleted_by
            
            self._save_data()
            
            # Registrar actividad
            self._log_activity(
                deleted_by,
                "user_deleted",
                f"Usuario eliminado (desactivado): {user['username']}",
                user['username']
            )
            
            return True
            
        except Exception as e:
            raise ValueError(f"Error al eliminar usuario: {str(e)}")
    
    def generate_reset_code(self, username: str) -> Optional[str]:
        """Genera un código temporal de 6 dígitos para recuperación de contraseña.
        Válido por 15 minutos. Retorna el código o None si el usuario no existe/no tiene email."""
        import random
        import time
        user = None
        for u in self.users:
            if u.get("username") == username and u.get("is_active"):
                user = u
                break
        if not user or not user.get("email"):
            return None
        code = f"{random.randint(0, 999999):06d}"
        user["_reset_code"] = code
        user["_reset_code_expires"] = time.time() + 900  # 15 minutos
        self._save_data()
        return code

    def verify_reset_code(self, username: str, code: str) -> bool:
        """Verifica si el código de recuperación es válido y no ha expirado."""
        import time
        user = None
        for u in self.users:
            if u.get("username") == username:
                user = u
                break
        if not user:
            return False
        stored = user.get("_reset_code")
        expires = user.get("_reset_code_expires", 0)
        return stored == code and time.time() < expires

    def reset_password_with_code(self, username: str, code: str, new_password: str) -> bool:
        """Cambia la contraseña si el código es válido. Limpia el código tras usarlo."""
        if not self.verify_reset_code(username, code):
            return False
        user = None
        for u in self.users:
            if u.get("username") == username:
                user = u
                break
        if not user:
            return False
        user["password_hash"] = self._hash_password(new_password)
        user.pop("_reset_code", None)
        user.pop("_reset_code_expires", None)
        self._save_data()
        self._log_activity(username, "password_reset", f"Contraseña restablecida por código para: {username}", username)
        return True


        """Obtiene el historial de actividad"""
        log = self.activity_log.copy()
        
        # Filtrar por usuario si se especifica
        if username:
            log = [a for a in log if a.get("username") == username or a.get("target_user") == username]
        
        # Ordenar por timestamp (más reciente primero)
        log.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Limitar resultados
        return log[:limit]
    
    def verify_password(self, username: str, password: str) -> bool:
        """Verifica si la contraseña es correcta para un usuario"""
        user = self.get_user_by_username(username)
        if not user or not user.get("is_active"):
            return False
        
        password_hash = self._hash_password(password)
        return user.get("password_hash") == password_hash
    
    def get_user_count(self) -> Dict[str, int]:
        """Obtiene estadísticas de usuarios"""
        total = len(self.users)
        active = sum(1 for u in self.users if u.get("is_active"))
        inactive = total - active
        
        by_role = {}
        for role in self.ROLES.keys():
            by_role[role] = sum(1 for u in self.users if u.get("role") == role and u.get("is_active"))
        
        return {
            "total": total,
            "active": active,
            "inactive": inactive,
            "by_role": by_role
        }


# Instancia global del servicio
user_service = UserService()
