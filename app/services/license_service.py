import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import urllib.request
import urllib.error
import os

from manager.app.services.app_config_service import app_config_service


class LicenseService:
    """Gestión de demo y licencia anual."""

    # Slug de tu cuenta en Keygen (account slug).
    # Para pruebas me indicaste: william62185
    KEYGEN_ACCOUNT = "william62185"

    DEMO_DAYS = 30
    DEV_ENV_FLAG = "BM_DEV_MODE"

    def _parse_iso(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            # Soporta formatos con o sin sufijo Z.
            if value.endswith("Z"):
                value = value[:-1]
            return datetime.fromisoformat(value)
        except Exception:
            return None

    def _format_iso(self, dt: Optional[datetime]) -> Optional[str]:
        if not dt:
            return None
        return dt.isoformat()

    def _ensure_first_run(self) -> Dict[str, Any]:
        lic = app_config_service.get_license_config()
        now = datetime.now()
        changed = False
        if not lic.get("first_run_date"):
            lic["first_run_date"] = self._format_iso(now)
            changed = True
        if not lic.get("demo_ends_at"):
            demo_end = now + timedelta(days=self.DEMO_DAYS)
            lic["demo_ends_at"] = self._format_iso(demo_end)
            changed = True
        if changed:
            app_config_service.set_license_config(lic)
        return lic

    def _is_dev_mode(self) -> bool:
        """Habilita funciones de prueba solo en entorno de desarrollo."""
        return os.environ.get(self.DEV_ENV_FLAG, "").strip() == "1"

    def enable_test_mode(self, demo_days: int = 1) -> bool:
        """Activa modo prueba (solo dev): ajusta demo_ends_at a now + demo_days."""
        if not self._is_dev_mode():
            return False
        demo_days = max(0, int(demo_days))
        lic = app_config_service.get_license_config()
        now = datetime.now()
        lic["test_mode"] = True
        lic["demo_days_override"] = demo_days
        lic["force_expired"] = False
        lic["first_run_date"] = self._format_iso(now)
        lic["demo_ends_at"] = self._format_iso(now + timedelta(days=demo_days))
        app_config_service.set_license_config(lic)
        return True

    def disable_test_mode(self) -> bool:
        """Desactiva modo prueba (solo dev) sin borrar una licencia activa."""
        if not self._is_dev_mode():
            return False
        lic = app_config_service.get_license_config()
        lic["test_mode"] = False
        lic["force_expired"] = False
        app_config_service.set_license_config(lic)
        return True

    def force_expired_demo(self) -> bool:
        """Fuerza estado expirado (solo dev) para probar pantalla de activación."""
        if not self._is_dev_mode():
            return False
        lic = app_config_service.get_license_config()
        lic["test_mode"] = True
        lic["force_expired"] = True
        app_config_service.set_license_config(lic)
        return True

    def reset_demo(self, days: int = 30) -> bool:
        """Restablece demo como 'nueva' (solo dev). No borra una licencia activa."""
        if not self._is_dev_mode():
            return False
        days = max(0, int(days))
        lic = app_config_service.get_license_config()
        now = datetime.now()
        lic["first_run_date"] = self._format_iso(now)
        lic["demo_ends_at"] = self._format_iso(now + timedelta(days=days))
        lic["license_status"] = "demo"
        lic["force_expired"] = False
        app_config_service.set_license_config(lic)
        return True

    def get_status(self) -> Dict[str, Any]:
        """Devuelve el estado efectivo de la licencia/demo."""
        lic = self._ensure_first_run()
        now = datetime.now()

        first_run = self._parse_iso(lic.get("first_run_date"))
        demo_ends = self._parse_iso(lic.get("demo_ends_at"))
        license_expires = self._parse_iso(lic.get("license_expires_at"))
        license_key = lic.get("license_key")
        status = lic.get("license_status") or "unknown"

        # En modo prueba (solo dev), se puede forzar expiración de demo.
        force_expired = bool(lic.get("force_expired")) and bool(lic.get("test_mode")) and self._is_dev_mode()

        if license_key and license_expires:
            if now <= license_expires:
                mode = "licensed"
                effective_status = "active"
                remaining = (license_expires - now).days
            else:
                mode = "expired"
                effective_status = "expired"
                remaining = 0
        else:
            if force_expired:
                mode = "expired"
                effective_status = "expired"
                remaining = 0
            elif demo_ends and now <= demo_ends:
                mode = "demo"
                effective_status = "demo"
                remaining = (demo_ends - now).days
            else:
                mode = "expired"
                effective_status = "expired"
                remaining = 0

        if status != effective_status:
            lic["license_status"] = effective_status
            app_config_service.set_license_config(lic)

        return {
            "mode": mode,  # demo | licensed | expired
            "remaining_days": remaining,
            "first_run_date": first_run,
            "demo_ends_at": demo_ends,
            "license_expires_at": license_expires,
            "license_key": license_key,
        }

    def validate_key_with_keygen(self, key: str) -> Dict[str, Any]:
        """Valida la clave contra Keygen y devuelve resultado estructurado."""
        key = (key or "").strip()
        if not key:
            return {"ok": False, "reason": "validation", "message": "Ingrese una clave de licencia."}

        url = f"https://api.keygen.sh/v1/accounts/{self.KEYGEN_ACCOUNT}/licenses/actions/validate-key"
        payload = json.dumps({"meta": {"key": key}}).encode("utf-8")
        headers = {
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        }
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read().decode("utf-8")
                data = json.loads(body)
        except urllib.error.URLError as e:
            return {
                "ok": False,
                "reason": "network",
                "message": f"No se pudo conectar al servidor de licencias: {e}",
            }
        except Exception as e:
            return {
                "ok": False,
                "reason": "error",
                "message": f"Error inesperado al validar la licencia: {e}",
            }

        if "errors" in data:
            detail = data["errors"][0].get("detail") if data["errors"] else "Clave de licencia inválida."
            return {"ok": False, "reason": "invalid", "message": detail, "raw": data}

        attributes = data.get("data", {}).get("attributes", {})
        expires_at = (
            attributes.get("expiry")
            or attributes.get("expiration")
            or attributes.get("expiresAt")
            or None
        )

        return {
            "ok": True,
            "reason": None,
            "message": "Licencia válida.",
            "raw": data,
            "expires_at": expires_at,
        }

    def activate_license(self, key: str, expires_at: Optional[str]) -> Dict[str, Any]:
        """Guarda la licencia como activa."""
        lic = app_config_service.get_license_config()
        now = datetime.now()

        parsed_exp = self._parse_iso(expires_at) if expires_at else None
        if not parsed_exp:
            parsed_exp = now + timedelta(days=365)

        lic.update(
            {
                "license_key": key.strip(),
                "license_status": "active",
                "license_expires_at": self._format_iso(parsed_exp),
                "activated_at": self._format_iso(now),
            }
        )
        app_config_service.set_license_config(lic)
        return self.get_status()


license_service = LicenseService()

