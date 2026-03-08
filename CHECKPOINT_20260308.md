# Checkpoint 2026-03-08 — Building Manager Pro

**Fecha:** 2026-03-08  
**Alcance:** UX módulo Inquilinos, combobox unificado, documentación y reglas.

## Cambios registrados en esta sesión

### Módulo Inquilinos
- **Botón "Volver" eliminado:** En la vista de lista/detalles de inquilinos solo se muestra el botón "Dashboard" (sin "Volver").
- **Título eliminado:** Quitado el título "Ver detalles inquilinos" (y el icono) del encabezado de la vista; solo permanecen los botones de navegación.

### Combobox (ttk.Combobox) — UX unificada
- **Helper reutilizable:** `bind_combobox_dropdown_on_click(combobox)` en `manager/app/ui/components/modern_widgets.py`. Al hacer clic en el **campo de texto** del combobox se abre el listado (simulación de tecla Down); en la **flecha** no se interfiere (comportamiento nativo).
- **Aplicado en toda la app:** Búsqueda Avanzada inquilinos (Filtro por apartamento, Estado), método de pago en formularios y modales de Pagos (PaymentsView, EditDeletePaymentsView, PaymentModal, PaymentsManagerWindow).

### Documentación y reglas
- **ARCHITECTURE.md:** Nueva entrada en §10 (Cambios en la UI) para Combobox — UX unificada; indicación de usar el helper en todos los combobox actuales y futuros.
- **.cursor/rules/architecture.mdc:** Nueva regla: tras crear cualquier `ttk.Combobox`, llamar a `bind_combobox_dropdown_on_click(combobox)`.

### Ajuste previo (checkpoint Pagos UX)
- En `payments_view.py`, callback `_on_payment_saved` sin mensaje "Éxito" (solo sonido).

## Archivos modificados (resumen)

- `manager/app/ui/components/modern_widgets.py`: Función `bind_combobox_dropdown_on_click`.
- `manager/app/ui/views/tenants_view.py`: Sin botón Volver, sin título "Ver detalles inquilinos"; combobox con helper; eliminado `_open_combobox_dropdown`.
- `manager/app/ui/views/payments_view.py`: Import y uso del helper en 3 combobox; `_on_payment_saved` sin messagebox.
- `manager/app/ui/views/edit_delete_payments_view.py`: Import y uso del helper en combobox Método.
- `ARCHITECTURE.md`: §10 Combobox.
- `.cursor/rules/architecture.mdc`: Regla Combobox.

## Base

Incluye el estado de `CHECKPOINT_20260306_pagos_ux.md`, `CHECKPOINT_20260306.md` y anteriores.

## Continuar desde aquí

- Código y documentación listos para seguir desarrollo a partir de este punto.
- Al añadir nuevos combobox, usar `bind_combobox_dropdown_on_click(combobox)` (regla en Cursor y ARCHITECTURE.md).
