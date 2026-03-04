# Auditoría técnica v1.0 — Building Manager Pro

**Objetivo:** Preparación para venta comercial (versión 1.0 estable).  
**Enfoque:** Optimizar, limpiar y blindar el sistema.

**Correcciones ya aplicadas (tras esta auditoría):**
- Módulo `manager/app/logger.py` creado; **todos** los `print` de diagnóstico/error en `manager/app/` sustituidos por `logger` (incl. `main_window.py`, `tenant_service`, `backup_service`).
- Ruta del icono: `paths_config.get_icon_path()` y uso en `main_window.py` (dev y frozen).
- **AppConfigService:** un solo `_default_config()` reutilizado en `_ensure_config_file` y `_load_config`.
- **Escritura atómica:** módulo `manager/app/persistence.py` con `save_json_atomic()`; usada en `tenant_service`, `payment_service`, `user_service`, `app_config_service` para `tenants.json`, `payments.json`, `users.json`, `user_activity.json`, `app_config.json`.
- **Fallback JSON corrupto:** en `_load_data` de tenant, payment, user y app_config, si hay `JSONDecodeError` se renombra el archivo a `.json.bak` y se arranca con lista/dict por defecto; se registra en log.
- **Instancias globales:** `MainWindow`, `PaymentsView`, `EditDeletePaymentsView` y `PaymentModal` usan `payment_service` y `tenant_service` (no instancian `PaymentService()` / `TenantService()`).
- `ARCHITECTURE.md` y regla `.cursor/rules/architecture.mdc` actualizados (logging, auditoría, icono).

---

## 1. Limpieza y calidad de código

### 1.1 Prints de debugging

| Archivo | Línea | Uso | Acción |
|---------|--------|-----|--------|
| `manager/app/main.py` | 31 | `print` en fallo de `ensure_dirs()` | Reemplazar por logging (o eliminar si se usa solo en dev). |
| `manager/app/services/payment_service.py` | 71-73, 91, 94, 117 | `print` + `traceback.print_exc()` en errores de actualización de estado de pago | Reemplazar por módulo `logging`. |
| `manager/app/services/tenant_service.py` | 99, 115, 223 | `print` en create/update y en `calculate_payment_status` | Reemplazar por logging. |
| `manager/app/services/app_config_service.py` | 106 | `print` en fallo de `_save_config` | Reemplazar por logging. |
| `manager/app/services/backup_service.py` | 108, 198, 310-311, 321 | `print` en creación de backup, estadísticas, recarga de servicios, metadatos | Reemplazar por logging. |
| `manager/app/services/apartment_service.py` | 28, 42, 48, 69 | `print` informativos y en fallo de guardado | Reemplazar por logging. |
| `manager/app/services/building_service.py` | 30, 38 | `print` en fallos de carga/guardado | Reemplazar por logging. |

**Solución:** Introducir un módulo `manager/app/logger.py` que configure `logging` (nivel INFO por defecto, rotación opcional) y usar `logger.warning(...)` / `logger.error(...)` / `logger.exception(...)` en lugar de `print`. En producción no debe quedar ningún `print` de diagnóstico en el código de aplicación (sí se permiten en `build_installer.py`, que es CLI).

### 1.2 Código muerto e imports innecesarios

- **PaymentService / TenantsView:** Las vistas instancian `PaymentService()` y `TenantService()`; conviene usar las instancias globales `payment_service` y `tenant_service` para consistencia y para no duplicar carga de datos (ver acoplamiento).
- **Imports:** Revisar en cada archivo que no queden `import` sin usar (ej. `os`, `Path` donde solo se use `paths_config`). No se detectaron graves; recomendación: ejecutar un linter (ruff, pylint) en CI.

### 1.3 Funciones duplicadas o lógica repetida

- **Config por defecto:** `AppConfigService` tiene el diccionario de configuración por defecto repetido en `_ensure_config_file` y en `_load_config`. **Solución:** Extraer a un método `_default_config()` y reutilizarlo en ambos.
- **Escritura JSON:** Varios servicios repiten el patrón `open(..., 'w', encoding='utf-8')` + `json.dump(..., ensure_ascii=False, indent=2)`. Para v1.0 es aceptable; a medio plazo se puede extraer un helper en `paths_config` o en un módulo `persistence.py` (ej. `save_json(path, data)`).

---

## 2. Revisión de arquitectura y acoplamiento

### 2.1 Vistas sin lógica de negocio innecesaria

- Las vistas delegan correctamente en servicios. La lógica de formato (fechas, moneda) en vistas es aceptable si es solo presentación.
- **PaymentsView** y otras instancian `PaymentService()` / `TenantService()` en lugar de usar las instancias globales; eso puede provocar múltiples cargas de datos. **Solución:** Usar `from manager.app.services.payment_service import payment_service` (y análogo para tenant) e inyectar o usar la instancia global.

### 2.2 Servicios que no dependen de la UI

- **Confirmado:** Los servicios no importan vistas ni tkinter.  
- **Excepción:** `LicenseService` importa solo `app_config_service` (otro servicio), correcto.

### 2.3 Violaciones de separación por capas

- No hay violaciones graves. El único punto es el uso de `print`/`traceback` en servicios: debería ser logging para mantener la capa de servicios libre de “UI” de consola.

### 2.4 Alto acoplamiento

- **PaymentService ↔ TenantService:** `PaymentService` importa y llama a `tenant_service.update_payment_status()` dentro de `add_payment`, `update_payment` y `delete_payment`. Está documentado en ARCHITECTURE (actualización de estado). Para v1.0 es aceptable; alternativa futura: evento/callback “pago guardado” para que MainWindow o un orquestador llame a `update_payment_status`.
- **Vistas que instancian servicios:** Ver 2.1; unificar uso de instancias globales reduce acoplamiento a “una sola fuente de verdad” por servicio.

---

## 3. Rutas y persistencia

### 3.1 Uso de paths_config

- **Confirmado:** Los servicios usan `DATA_DIR`, `BACKUPS_DIR`, `DOCUMENTOS_INQUILINOS_DIR`, etc. desde `paths_config`. No se detectan rutas absolutas hardcodeadas en la capa de aplicación.

### 3.2 Rutas hardcodeadas

- **`manager/app/ui/views/main_window.py` línea 90:**  
  `self.root.iconbitmap("assets/icon.ico")`  
  Ruta relativa al directorio de trabajo; en modo frozen (ejecutable en otra carpeta) falla silenciosamente (está en `try/except`).  
  **Solución:** Resolver el icono respecto a la raíz del proyecto o del ejecutable. Por ejemplo, en `paths_config` definir `ASSETS_DIR` o `ICON_PATH`: en desarrollo `Path(__file__).resolve().parent.parent.parent / "assets" / "icon.ico`, en frozen `BASE_PATH / "assets" / "icon.ico` si se incluyen assets en el paquete, o usar un recurso embebido. Si no hay assets en el instalador, mantener el try/except pero documentar que el icono solo se usa en desarrollo.

### 3.3 Riesgos al empaquetar (modo frozen)

- **run.py:** En frozen, `_root = Path(sys.executable).parent` (y subir si `_internal`). Eso solo afecta a `sys.path` para importar `manager.app.paths_config`.  
- **paths_config:** En frozen, `_get_base_path()` usa `%APPDATA%/Building Manager Pro`. Los datos se escriben ahí; no hay conflicto con run.py.  
- **Riesgo:** Si en el instalador no se crea la carpeta en AppData, `ensure_dirs()` la crea al arrancar. Asegurar que el instalador no ejecute la app con permisos restringidos que impidan crear carpetas en AppData.

### 3.4 BASE_PATH dinámico

- El sistema está preparado: en desarrollo BASE_PATH es la raíz del paquete `manager`, en frozen es AppData. No se encontraron referencias a rutas fijas que asuman desarrollo.

---

## 4. Robustez y manejo de errores

### 4.1 Try/except críticos

- **Servicios:** `_load_data()` suelen tener `try/except (FileNotFoundError, json.JSONDecodeError)` y fallback a lista vacía. Correcto.
- **Escritura:** `_save_data()` en la mayoría no tienen try/except. Si el disco falla o hay permisos insuficientes, la excepción sube y puede cerrar la app.  
  **Solución:** Envolver `_save_data()` en try/except en cada servicio; en caso de error, registrar con logging y, si hay callback de “error crítico”, notificar a la UI (mensaje al usuario). No tragar la excepción; devolver bool o lanzar una excepción de aplicación.

### 4.2 Corrupción de JSON

- Si la app se cierra a mitad de `json.dump`, el archivo puede quedar truncado.  
  **Solución recomendada:** Escribir a un archivo temporal en el mismo directorio y luego `os.replace(temp_path, data_file)` (atómico en la misma unidad). Aplicar en al menos los archivos más críticos: `tenants.json`, `payments.json`, `users.json`, `app_config.json`.

### 4.3 Datos incompletos

- **tenant_service:** `get_tenant_by_id`, `calculate_payment_status` usan `.get()` y valores por defecto; si falta un campo, el comportamiento es degradado pero no suele romper.  
- **building_service / apartment_service:** Si el JSON no es una lista, se devuelve `[]`. Correcto.  
- **Recomendación:** En puntos donde se asume estructura (ej. `tenant["nombre"]`), usar `.get("nombre", "")` o validar antes; ya se hace en la mayoría de sitios.

---

## 5. Seguridad mínima viable

### 5.1 Contraseñas

- **user_service.py:** `_hash_password` usa `hashlib.sha256(password.encode()).hexdigest()` sin sal.  
  **Riesgo:** SHA-256 sin sal es vulnerable a tablas arcoíris y no cumple mejores prácticas (por ejemplo OWASP).  
  **Para v1.0:** Documentar como limitación conocida. **Mejora recomendada (antes de escalar):** Usar `hashlib` con sal único por usuario (guardado en `users.json`) o, preferiblemente, una librería como `passlib` con bcrypt/argon2. Mientras tanto, no almacenar contraseñas en claro; el hash actual ya evita el riesgo más básico.

### 5.2 Datos sensibles

- Los hashes de contraseña están en `users.json`; el archivo está en disco local. Recomendación: asegurar que el instalador no deje `users.json` con permisos de lectura global en sistemas multi-usuario (Windows típicamente por usuario, bajo AppData).
- **get_user_by_username** devuelve `user.copy()` con el hash incluido; quien llama (ej. login) debe no exponerlo. En `MainWindow` se elimina `password_hash` del `current_user`. Revisar que en ningún flujo se envíe el hash a la UI (logs, mensajes); no se detectaron fugas.

### 5.3 LicenseService

- **KEYGEN_ACCOUNT** está hardcodeado; correcto para una sola cuenta.  
- **validate_key_with_keygen:** Timeout 10 s; manejo de `URLError` y genérico. Adecuado.  
- **Modo dev (BM_DEV_MODE):** Solo con variable de entorno; no activable desde la UI. Correcto para producción.  
- **Riesgo menor:** Si Keygen no está disponible, la activación falla; el mensaje se muestra al usuario. No hay riesgo de bypass local sin clave.

---

## 6. Experiencia de usuario

### 6.1 Validaciones débiles

- Formularios (inquilino, pago, etc.): revisar en vistas que campos obligatorios (nombre, monto, etc.) no se envíen vacíos; si hay validación solo en UI, un usuario podría bypassear con datos corruptos. Recomendación: validar también en el servicio (ej. `create_tenant` rechazar si `nombre` vacío) y devolver mensaje claro.
- **tenant_service.create_tenant:** No valida longitud ni formato de documento/cédula; aceptable para v1.0 si no hay requisito normativo.

### 6.2 Flujos confusos

- Sin revisión exhaustiva de cada pantalla: mantener textos de botones consistentes (“Guardar”, “Cancelar”, “× Cerrar” en reportes) y mensajes de error claros (“No se pudo guardar. Compruebe permisos de la carpeta de datos.” en lugar de solo “Error”).

### 6.3 Profesionalismo

- Sustituir todos los `print` por logging evita que en instalaciones con consola oculta aparezcan ventanas de error o salida inesperada.  
- Icono de ventana: resolver ruta del icono en frozen para que la app instalada muestre icono en la barra de tareas.

---

## 7. Preparación para versión 1.0

### 7.1 Mejoras estratégicas pequeñas

1. **Logging:** Un solo módulo `logger.py`, uso en todos los servicios y en main.  
2. **Escritura atómica:** Al menos para `tenants.json`, `payments.json`, `users.json`, `app_config.json`.  
3. **Icono:** Ruta del icono vía `paths_config` o recurso.  
4. **Config por defecto:** Un solo `_default_config()` en AppConfigService.  
5. **Instancias globales en vistas:** Usar `payment_service` y `tenant_service` en lugar de instanciar nuevos servicios.

### 7.2 Soporte técnico

- Evitar `traceback.print_exc()` en producción; usar `logger.exception(...)`.  
- Mensajes al usuario en español y sin jerga técnica (“No se pudo conectar al servidor de licencias” está bien).  
- Si un archivo JSON se corrompe, el arranque puede fallar; considerar en `_load_data()` un fallback: si JSONDecodeError, renombrar el archivo a `.json.bak` y empezar con lista vacía, y registrar en log.

### 7.3 Riesgos ocultos

- **TenantService.data_file:** Se usa `str(DATA_DIR / "tenants.json")` y luego `os.path.dirname(self.data_file)`. En Windows con Path esto funciona; si en algún entorno `DATA_DIR` fuera relativo, podría fallar. Recomendación: usar siempre `Path` y `path.parent.mkdir(...)`.  
- **Backup restore:** Al extraer, se sobrescriben archivos; si falla a mitad, el estado puede ser inconsistente. El backup de seguridad previo mitiga; documentar en ayuda que “tras restaurar, conviene reiniciar la aplicación”.

---

## Resumen de prioridades

| Prioridad | Acción |
|----------|--------|
| Alta | Sustituir todos los `print` por logging en manager/app. |
| Alta | Ruta del icono en main_window vía paths_config o recurso. |
| Media | Escritura atómica (temp + replace) en archivos JSON críticos. |
| Media | Try/except en _save_data con logging y retorno bool o re-raise controlado. |
| Media | Unificar uso de instancias globales payment_service/tenant_service en vistas. |
| Baja | Config por defecto única en AppConfigService. |
| Baja | Documentar hash de contraseña sin sal como limitación; plan de mejora con sal/bcrypt. |

Este documento debe actualizarse cuando se apliquen cambios o se detecten nuevos hallazgos. Se recomienda vincularlo desde ARCHITECTURE.md.
