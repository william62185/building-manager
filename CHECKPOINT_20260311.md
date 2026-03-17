# Checkpoint 2026-03-11 — Building Manager Pro

**Fecha:** 2026-03-11  
**Alcance:** Estado del código tras desarrollo reciente; punto de partida para continuar.

## Estado incluido en este checkpoint

### Código fuente (manager/app)
- **Navegación y presentadores:** `app_controller.py`, `presenters/` (dashboard, report, payment, tenant, expense, accounting).
- **Servicios:** Cambios en `tenant_service`, `app_config_service`, `backup_service`, `notification_service`; nuevo `accounting_service`.
- **Vistas:** Múltiples actualizaciones en vistas de inquilinos, pagos, gastos, edificios, apartamentos, configuración, backup; nueva `administration_view`, `dashboard_view`, `pending_payments_report_window`, `accounting/` (contabilidad, estado de resultados, libro de movimientos, asientos manuales y de apertura); eliminada `reports_view.py` (reemplazada por estructura actual).
- **Componentes:** Ajustes en `theme_manager`, `tenant_autocomplete`, `modern_widgets`.
- **Otros:** `paths_config`, `receipt_pdf`, `_view_template`, `prueba_view`.

### No incluido en el commit (datos de ejecución)
- Archivos de datos (`data/*.json`), exports, backups, documentos de inquilinos, fichas/recibos/gastos_docs y `__pycache__` permanecen sin versionar en este checkpoint.

## Base

Incluye el estado de `CHECKPOINT_20260310.md` y todo el desarrollo hasta la fecha de este checkpoint.

## Continuar desde aquí

- Código listo para seguir desarrollo a partir de este punto.
- Los datos de prueba y exports se mantienen locales; versionar solo cuando sea necesario.
