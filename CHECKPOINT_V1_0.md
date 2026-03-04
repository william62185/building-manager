# Checkpoint v1.0 estable — Building Manager Pro

**Fecha:** 2025-03-04  
**Versión:** 1.0.0  
**Rama:** path-manager-20179 (o la rama actual en el momento del tag)

## Contenido de este checkpoint

- Auditoría técnica aplicada (ver `AUDIT_V1_0.md`).
- Logging centralizado (`manager/app/logger.py`); sin `print` en la app.
- Escritura atómica y fallback ante JSON corrupto (`persistence.py` + servicios).
- Config por defecto unificada en `AppConfigService`.
- Vistas usando instancias globales `payment_service` / `tenant_service`.
- Rutas documentadas: datos en `%APPDATA%\Building Manager Pro` en instalado; en desarrollo bajo `manager/` (data, backups, gastos_docs, exports).
- Documentación actualizada: `ARCHITECTURE.md`, `INSTALADOR.md`, `PROJECT_MANIFEST.md` (sin referencias a checkpoint.py).

## Cómo hacer backup de esta versión

1. **Desde la aplicación:** Abrir Building Manager Pro → Administración → Backups (o Configuración/Backups). Crear backup completo. Los ZIP se guardan en `%APPDATA%\Building Manager Pro\backups\` (instalado) o en `manager/backups/` (desarrollo).
2. **Desde Git:** Este checkpoint queda marcado con el tag `v1.0-stable`. Para volver a esta versión: `git checkout v1.0-stable` (o crear una rama desde el tag).

## Restaurar a este checkpoint

- Código: `git checkout v1.0-stable`
- Datos: usar la función de restauración desde backup dentro de la app (Administración/Backups), seleccionando un ZIP creado en esta versión.
