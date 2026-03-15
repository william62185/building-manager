# Checkpoint 2026-03-10 — Building Manager Pro

**Fecha:** 2026-03-10  
**Alcance:** Splash más breve; tras registrar pago, cierre automático y vuelta al listado de inquilinos.

## Cambios registrados en esta sesión

### Splash
- **Duración:** Reducida de 2 s a 1,2 s (`SPLASH_DURATION_MS = 1200` en `main.py`).

### Flujo tras registrar un pago
- **Cierre y navegación:** Tras registrar un pago (desde detalles del inquilino o desde el módulo Pagos), la ventana de registro se cierra y la app vuelve automáticamente al listado de inquilinos.
- **Sin diálogo de recibo:** Eliminado el `messagebox.askyesno` "¿Desea abrir el recibo ahora?". El PDF se sigue generando y se reproduce solo el sonido de confirmación.
- **Callback unificado:** En `MainWindow` se usa `_on_payment_saved_go_to_tenants()` como `on_payment_saved` de `PaymentsView` (al cargar Pagos y al abrir "Registrar Pago" con inquilino preseleccionado), de modo que siempre se refresca la lista y se navega a Inquilinos.

## Archivos modificados (resumen)

- `manager/app/main.py`: `SPLASH_DURATION_MS` 2000 → 1200.
- `manager/app/ui/views/payments_view.py`: Eliminado diálogo "Recibo generado" y uso de `webbrowser`; se mantiene generación de PDF y sonido.
- `manager/app/ui/views/main_window.py`: Nuevo `_on_payment_saved_go_to_tenants()`; `PaymentsView` recibe `on_payment_saved=self._on_payment_saved_go_to_tenants` en todas las rutas (load_view payments, _show_register_payment directo, navigate_to_payments con inquilino).

## Base

Incluye el estado de `CHECKPOINT_20260309.md` y anteriores.

## Continuar desde aquí

- Código listo para seguir desarrollo a partir de este punto.
