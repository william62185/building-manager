# Checkpoint 2026-03-06 — Building Manager Pro v1.0.1

**Fecha:** 2026-03-06  
**Versión:** 1.0.1  
**Tag sugerido:** `v1.0.1` o `checkpoint-20260306`

## Contenido de este checkpoint

- **CreateAdminView:** Ventana de creación del primer administrador más compacta; texto "Bienvenido..." con `wraplength` para que no se recorte; sin scroll; espaciado reducido.
- **PaymentsView — Registrar nuevo pago:** Eliminado el listado de pagos en la misma pantalla; formulario reorganizado con sección "Datos del pago" (card con borde sutil). Campos de solo lectura que se rellenan al seleccionar inquilino: **Apartamento/Unidad** (edificio + tipo + número) y **Nombre del inquilino**. Label "Apartamento/Unidad" en lugar de "Tipo/unidad y número de apartamento/local".
- **TenantsView — Búsqueda avanzada:** Campos de fecha de ingreso (Desde/Hasta) con fondo igual al panel (`#e3f2fd`) para quitar el recuadro blanco alrededor del DatePickerWidget.

Incluye todo lo de checkpoints anteriores (v1.0, 2026-03-05).

## Restaurar a este checkpoint

- Código: `git checkout v1.0.1` (o el tag que se cree).
- Instalador: `dist/BuildingManagerPro_Setup_1.0.1.exe`.
