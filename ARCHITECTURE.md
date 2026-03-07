# Building Manager Pro — Arquitectura del sistema

## 1. Descripción general del sistema

**Building Manager Pro** es una aplicación de escritorio para la gestión integral de edificios: inquilinos, pagos de arriendo, gastos, unidades (apartamentos/locales), reportes y administración. Está desarrollada en **Python** con interfaz **Tkinter**, sin base de datos relacional: la persistencia se hace en archivos **JSON** y documentos (PDFs) en carpetas locales.

### Características principales
- Autenticación (login / creación de primer administrador).
- Módulos: **Inquilinos**, **Pagos**, **Gastos**, **Reportes**, **Administración** (edificio, unidades, usuarios, backups).
- Documentos por inquilino (cédula, contrato, recibos, ficha) en una carpeta única por inquilino.
- Reportes exportables a CSV/TXT (y en algunos casos Excel).
- Temas (claro/oscuro), backups automáticos y configuración persistente.

---

## 2. Arquitectura por capas

El código se organiza en capas claras dentro de `manager/app/`:

```
manager/
├── app/
│   ├── main.py              # Punto de entrada (login → MainWindow)
│   ├── app_controller.py     # Controlador de navegación (MVP)
│   ├── paths_config.py      # Rutas, get_icon_path(), carpetas de datos
│   ├── logger.py            # Logging centralizado (no usar print en app)
│   ├── persistence.py       # save_json_atomic para escritura segura de JSON
│   ├── presenters/          # Lógica de presentación por módulo (MVP, en expansión)
│   ├── services/            # Capa de servicios (lógica + persistencia)
│   └── ui/
│       ├── components/      # Componentes reutilizables (temas, widgets, iconos)
│       └── views/           # Vistas/pantallas (una por flujo o módulo)
```

### 2.1 Capa de presentación (UI)

| Ubicación | Responsabilidad |
|-----------|-----------------|
| **`ui/views/`** | Ventanas y pantallas: `main_window.py` (layout principal con sidebar), `login_view`, `tenants_view`, `payments_view`, `expenses_view`, `reports_view`, `settings_view`, etc. Cada vista es un `tk.Frame` o ventana que usa servicios y componentes. |
| **`ui/components/`** | Componentes reutilizables: `theme_manager` (temas, espaciado, colores por módulo), `modern_widgets` (botones, cards, badges), `icons`, `tenant_autocomplete`. |

- **Navegación:** `AppController` (`app_controller.py`) orquesta el cambio de vista: define los títulos (`VIEW_TITLES`), y en `navigate_to(view_name)` actualiza estado, botones del menú, título, limpia el contenedor y carga la vista. No se programa refresh retardado al entrar a inquilinos (evita parpadeo). `MainWindow` expone: `set_current_view`, `update_nav_buttons`, `set_page_title`, `clear_views_container`, `load_view`, `get_root`, `force_tenants_refresh`. La creación concreta de cada vista está en `MainWindow._load_view`.
- **Presenters:** La carpeta `presenters/` alberga la lógica de presentación por módulo (MVP). **Dashboard:** `DashboardPresenter` (estadísticas, pagos pendientes, ingresos/gastos del mes). **Inquilinos:** `TenantPresenter` (carga, filtrado, opciones de apartamentos). **Pagos:** `PaymentPresenter` (callbacks volver/notificar pago guardado, `get_active_tenants`). **Gastos:** `ExpensePresenter` (volver, `load_expenses`). **Reportes:** `ReportPresenter` (`reload_all_data`, `get_pending_payments_report_text()` para el texto del reporte de pagos pendientes; callbacks para ocupación y pagos pendientes). Cada vista delega en su presenter.
- **Dashboard:** La vista del dashboard está en `ui/views/dashboard_view.py` (`DashboardView`), usa `DashboardPresenter` y callbacks para acciones. `MainWindow` solo instancia `DashboardView`.
- **Reporte de pagos pendientes:** La generación del texto del reporte está en `ReportPresenter.get_pending_payments_report_text()`. La ventana modal (Toplevel con Exportar CSV/TXT, Cerrar) está en `ui/views/pending_payments_report_window.py` (`show_pending_payments_report`); el diálogo de exportación exitosa sigue en `MainWindow._show_export_success_dialog`.
- **Módulo Inquilinos:** Al hacer clic en "Inquilinos" en el sidebar se abre directamente la vista de lista/detalles (búsqueda avanzada, cards "Nuevo inquilino" y "Reportes", lista de inquilinos). No existe la pantalla intermedia "¿Qué deseas hacer?" con tres cards. El card "Reportes" abre la vista de reportes de gestión de inquilinos (`TenantManagementReportsView`); "Volver" desde reportes vuelve a la lista de inquilinos (`_back_to_list`), no al dashboard.
- **Temas:** `theme_manager` (`ui/components/theme_manager.py`) define la paleta del tema "light": **`header_bg`** (fondo de la barra del título de la página), **`content_bg`** (fondo del área de contenido principal). El título de página se dibuja en blanco sobre la barra. `get_module_colors(module)` asigna color primario/hover por módulo.

### 2.2 Capa de servicios

| Servicio | Archivo | Función |
|----------|---------|---------|
| **TenantService** | `tenant_service.py` | CRUD inquilinos, persistencia en `tenants.json`, recálculo de estado de pago. |
| **PaymentService** | `payment_service.py` | CRUD pagos en `payments.json`, filtros por inquilino. |
| **ExpenseService** | `expense_service.py` | CRUD gastos en `gastos.json`, filtros por período/categoría. |
| **ApartmentService** | `apartment_service.py` | CRUD unidades (apartamentos/locales) en `apartments.json`, asociados a `building_id`. |
| **BuildingService** | `building_service.py` | Estructura de edificios (pisos, unidades) en `building_structure.json`. |
| **UserService** | `user_service.py` | Usuarios y autenticación en `users.json`. |
| **AppConfigService** | `app_config_service.py` | Tema y preferencias en `app_config.json`. |
| **NotificationService** | `notification_service.py` | Envío de notificaciones/emails (recordatorios, recibos), historial en `notifications.json`. |
| **EmailService** | `email_service.py` | Envío de correos (SMTP). |
| **BackupService** | `backup_service.py` | Backups completos (ZIP con JSON + documentos), restauración, backups automáticos. |
| **LicenseService** | `license_service.py` | Validación de licencia/demo. |

Los servicios exponen métodos como `get_all_*`, `get_*_by_id`, `add_*`, `update_*`, `_load_data()`, `_save_data()`. No conocen la UI; son usados por las vistas.

### 2.3 Configuración y rutas (paths_config)

- **`paths_config.py`** centraliza rutas y helpers:
  - `BASE_PATH` / `DATA_DIR`: en desarrollo = raíz del paquete `manager`; empaquetado = `%APPDATA%/Building Manager Pro`.
  - Carpetas: `DATA_DIR`, `BACKUPS_DIR`, `DOCUMENTOS_INQUILINOS_DIR`, `GASTOS_DOCS_DIR`, `EXPORTS_DIR`.
  - `ensure_dirs()` crea todas las carpetas necesarias.
  - `get_tenant_document_folder_name(tenant)` devuelve el nombre de subcarpeta del inquilino (`{cedula}_{primer_nombre}`).

No existe una capa “utils” explícita; helpers genéricos están en `paths_config` o dentro de los propios servicios/vistas.

---

## 3. Flujo principal de ejecución

1. **Arranque**
   - `run.py` añade la raíz al `sys.path`, importa `paths_config` y llama a `ensure_dirs()`.
   - Importa `manager.app.main` y ejecuta `main()`.

2. **main() (main.py)**
   - Crea la ventana `tk.Tk`, aplica tema guardado (`app_config_service`).
   - Si no hay usuarios: muestra `CreateAdminView` (crear primer admin).
   - Si hay usuarios: muestra `LoginView`.
   - Tras login/creación exitosa: destruye la pantalla de “gate” y crea `MainWindow(root, current_user)`.

3. **MainWindow**
   - Construye sidebar (menú por módulos) y área de contenido.
   - Carga vistas bajo demanda (p. ej. `TenantsView`, `PaymentsView`, `ExpensesView`) y las muestra en el contenedor central.
   - Gestiona navegación (Volver, Dashboard), estado de licencia y onboarding.

4. **Interacción típica**
   - El usuario elige un módulo → se instancia la vista correspondiente → la vista usa uno o más servicios (`tenant_service`, `payment_service`, etc.) para cargar/guardar datos.
   - Los servicios leen/escriben JSON en `DATA_DIR` y, cuando aplica, documentos en `DOCUMENTOS_INQUILINOS_DIR` o `EXPORTS_DIR`.

---

## 4. Gestión de base de datos

No se utiliza una base de datos relacional. La “base de datos” son archivos **JSON** en `manager/data/` (o la ruta equivalente en instalado):

| Archivo | Contenido |
|---------|-----------|
| `tenants.json` | Lista de inquilinos (id, nombre, documento, apartamento, valor_arriendo, archivos, etc.). |
| `payments.json` | Lista de pagos (id, id_inquilino, fecha_pago, monto, metodo, observaciones). |
| `gastos.json` | Lista de gastos (categoría, subtipo, monto, fecha, apartamento, etc.). |
| `apartments.json` | Unidades (id, building_id, number, unit_type, etc.). |
| `building_structure.json` | Estructura de edificios (pisos, unidades lógicas). |
| `users.json` | Usuarios y hashes de contraseña. |
| `app_config.json` | Tema y preferencias. |
| `notifications.json` | Historial de notificaciones enviadas. |

- **Patrón:** cada servicio tiene `_load_data()` y `_save_data()`; mantiene una lista/diccionario en memoria y la persiste al modificar.
- **IDs:** generados en el servicio (p. ej. `max(ids) + 1`).
- **Integridad:** no hay transacciones; si la aplicación se cierra a mitad de escritura, el archivo puede quedar corrupto (los backups ayudan a recuperar).

---

## 5. Gestión de documentos

- **Documentos de inquilino (cédula, contrato, recibos, ficha)**  
  - Carpeta base: `DATA_DIR / "documentos_inquilinos"` (`DOCUMENTOS_INQUILINOS_DIR`).
  - Una subcarpeta por inquilino: `{cedula}_{primer_nombre}` (ej. `1223322_william`), generada con `get_tenant_document_folder_name(tenant)`.
  - Dentro: `cedula.pdf`, `contrato.pdf`, `recibo_{fecha}.pdf`, `ficha.pdf`.
  - En `tenants.json`, el inquilino guarda en `archivos` rutas **relativas** a esa carpeta (ej. `"2222223_William/cedula.pdf"`).
  - Al guardar desde el formulario de inquilino se **copian** los archivos seleccionados a la carpeta del inquilino; al generar recibo o ficha se escriben directamente ahí.

- **Documentos de gastos**  
  - Carpeta: `GASTOS_DOCS_DIR` (adjuntos de gastos, si se usan).

- **Exportaciones**  
  - Reportes exportados (CSV, TXT, a veces Excel) en `EXPORTS_DIR`.

- **Backups**  
  - Incluyen `data/*.json` y las carpetas de documentos (`documentos_inquilinos`, `gastos_docs`, `exports`) en un ZIP en `BACKUPS_DIR`.

---

## 6. Estructura de carpetas explicada

```
building_manager_cursor/          # Raíz del proyecto
├── run.py                        # Lanzador: path, ensure_dirs, main()
├── build_installer.py            # Script de empaquetado (ej. PyInstaller)
├── ARCHITECTURE.md               # Este documento
│
└── manager/                      # Paquete principal
    ├── app/
    │   ├── main.py               # Entry: login → MainWindow
    │   ├── paths_config.py       # Rutas, get_icon_path(), DOCUMENTOS_INQUILINOS_DIR
    │   ├── logger.py             # Logging centralizado
    │   ├── persistence.py        # save_json_atomic
    │   │
    │   ├── services/             # Capa de servicios (JSON + lógica)
    │   │   ├── tenant_service.py
    │   │   ├── payment_service.py
    │   │   ├── expense_service.py
    │   │   ├── apartment_service.py
    │   │   ├── building_service.py
    │   │   ├── user_service.py
    │   │   ├── app_config_service.py
    │   │   ├── notification_service.py
    │   │   ├── email_service.py
    │   │   ├── backup_service.py
    │   │   ├── license_service.py
    │   │   └── ...
    │   │
    │   └── ui/
    │       ├── components/       # Reutilizables
    │       │   ├── theme_manager.py
    │       │   ├── modern_widgets.py
    │       │   ├── icons.py
    │       │   └── tenant_autocomplete.py
    │       │
    │       └── views/            # Pantallas
    │           ├── main_window.py
    │           ├── login_view.py
    │           ├── create_admin_view.py
    │           ├── tenants_view.py
    │           ├── tenant_form_view.py
    │           ├── tenant_details_view.py
    │           ├── deactivate_tenant_view.py
    │           ├── payments_view.py
    │           ├── edit_delete_payments_view.py
    │           ├── payment_reports_view.py
    │           ├── expenses_view.py
    │           ├── expense_reports_view.py
    │           ├── register_expense_view.py
    │           ├── edit_delete_expenses_view.py
│           ├── reports_view.py
│           ├── tenant_management_reports_view.py
│           ├── pending_payments_report_window.py  # Ventana modal reporte pagos pendientes
│           ├── reports/       # Subreportes (ocupación, tendencias, etc.)
    │           ├── building_setup_view.py
    │           ├── building_management_view.py
    │           ├── apartment_management_view.py
    │           ├── apartment_form_view.py
    │           ├── apartments_list_view.py
    │           ├── occupation_status_view.py
    │           ├── settings_view.py
    │           ├── backup_view.py
    │           ├── user_management_view.py
    │           └── ...
    │
    ├── data/                     # Datos en ejecución (desarrollo)
    │   ├── *.json                # tenants, payments, gastos, apartments, etc.
    │   └── documentos_inquilinos/
    │       └── {cedula}_{nombre}/
    │           ├── cedula.pdf
    │           ├── contrato.pdf
    │           ├── recibo_*.pdf
    │           └── ficha.pdf
    ├── backups/
    ├── gastos_docs/
    └── exports/
```

En instalado (frozen), `BASE_PATH` suele ser `%APPDATA%/Building Manager Pro`, y bajo él se crean `data/`, `backups/`, `exports/`, etc.

---

## 7. Convenciones usadas

- **Rutas:** Siempre a través de `paths_config` (`DATA_DIR`, `DOCUMENTOS_INQUILINOS_DIR`, etc.); no rutas absolutas hardcodeadas.
- **Encoding:** UTF-8 en JSON y archivos de texto (`encoding='utf-8'` o `'utf-8-sig'` en exportaciones).
- **Nombres de carpeta de inquilino:** `get_tenant_document_folder_name(tenant)` → `{cedula}_{primer_nombre}` sanitizado.
- **UI:** Tkinter; colores por módulo con `get_module_colors(module)`; botones de reportes con hover y texto "× Cerrar" según `.cursorrules`.
- **Servicios:** Instancias globales (ej. `tenant_service`, `payment_service`); las vistas los importan y llaman a métodos; los servicios no importan vistas.
- **Callbacks:** Las vistas reciben `on_back`, `on_navigate`, `on_data_change`, `on_payment_saved`, etc., para comunicar con `MainWindow` o otras vistas sin acoplamiento directo.

---

## 8. Posibles puntos de mejora futura

1. **Persistencia**
   - Introducir una base de datos (SQLite) para transacciones, integridad y consultas más ricas, manteniendo una capa de servicios que abstraiga lectura/escritura.

2. **Capa de dominio**
   - Extraer reglas de negocio (cálculo de mora, validaciones, reglas de negocio de contratos) a una capa de dominio o “use cases”, dejando servicios más delgados y vistas solo como presentación.

3. **Testing**
   - Tests unitarios para servicios (CRUD, filtros) y de integración para flujos críticos (registro de pago, creación de inquilino con documentos).

4. **Documentos**
   - Validación de tipos MIME y tamaños al subir; opción de compresión o almacenamiento externo para muchos documentos.

5. **Concurrencia y rendimiento**
   - Carga perezosa de listas grandes (paginación o virtualización); `_load_data()` en hilo secundario para no bloquear la UI en datos grandes.

6. **Seguridad**
   - No almacenar contraseñas en texto plano; ya se usan hashes (verificar que sea un esquema seguro). Revisar permisos de archivos en datos sensibles.

7. **Internacionalización**
   - Extraer textos a recursos (ej. JSON o gettext) para soportar varios idiomas.

8. **Logging y diagnóstico**
   - Reemplazar `print` por un módulo `logging` configurable (niveles, rotación) para producción. **Regla:** En `manager/app/` no usar `print` para diagnóstico; usar `manager.app.logger` (ver `AUDIT_V1_0.md`).

9. **API estable para reportes**
   - Unificar la generación de reportes (CSV/TXT/Excel) en un módulo común con el mismo formato de botones y exportación (alineado con `.cursorrules`).

10. **Backups**
    - Opción de backup remoto o en la nube; verificación de integridad del ZIP tras generación.

---

## 9. Auditoría y preparación para venta (v1.0)

- **Documento de auditoría:** `AUDIT_V1_0.md` en la raíz del proyecto recoge la auditoría técnica completa para la versión 1.0 estable (limpieza de código, arquitectura, rutas, robustez, seguridad, UX).
- **Convenciones reforzadas tras auditoría:**
  - **Logging:** Todo diagnóstico/error en `manager/app/` debe usar el módulo `logger` (no `print`). El script `build_installer.py` puede seguir usando `print` (CLI).
  - **Icono de ventana:** La ruta del icono (`icon.ico`) debe resolverse vía `paths_config` o recurso empaquetado para que funcione en modo frozen; ver `AUDIT_V1_0.md` § 3.2.
  - **Escritura JSON:** Se usa `manager.app.persistence.save_json_atomic()` en tenants, payments, users, app_config (temp + `os.replace`). En `_load_data`, si el JSON está corrupto se renombra a `.json.bak` y se arranca con datos por defecto.
  - **Instancias globales:** Las vistas usan `payment_service` y `tenant_service` (no instanciar servicios nuevos).
- Se debe mantener `ARCHITECTURE.md` y `AUDIT_V1_0.md` actualizados cuando se apliquen cambios estructurales o se detecten nuevos hallazgos.

---

## 10. Cambios en la UI (v1.0.1 y posteriores)

- **CreateAdminView** (`create_admin_view.py`): Ventana de creación del primer administrador compacta; texto de bienvenida con `wraplength`; espaciado reducido.
- **PaymentsView — Registrar nuevo pago** (`payments_view.py`): Solo formulario de registro; campos de solo lectura al seleccionar inquilino (Apartamento/Unidad, Nombre). Orden: Apartamento, Nombre, Fecha, Monto, Método, Observaciones, Registrar Pago.
- **TenantsView** (`tenants_view.py`): Entrada directa a la vista de lista/detalles (sin pantalla "¿Qué deseas hacer?"). Columna izquierda: dos cards ("Nuevo inquilino", "Reportes") encima y panel de Búsqueda Avanzada debajo; derecha: lista de inquilinos. Card "Reportes" abre `TenantManagementReportsView`; "Volver" desde reportes vuelve a la lista. Búsqueda avanzada compacta; descripción "(Nombre, Cédula, …)" en la misma línea que "Búsqueda general:". Fechas de ingreso con fondo del panel (`#e3f2fd`).
- **Tema (theme_manager.py):** **`header_bg`**: fondo de la barra del título de página (ej. `#733E24`). **`content_bg`**: fondo del área de contenido principal (ej. `#8395a7`). El título de la barra se dibuja en blanco; sin contorno. Modificar estos valores en el diccionario del tema "light" para cambiar la apariencia global.
- **Reporte de pagos pendientes:** Texto generado por `ReportPresenter.get_pending_payments_report_text()`; ventana modal en `pending_payments_report_window.show_pending_payments_report()`. Sin refresh retardado al abrir inquilinos (evita parpadeo).
