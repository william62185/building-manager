"""
Vista de Asientos manuales del módulo de contabilidad.
Permite registrar ajustes: descuentos, garantías, mora, notas de crédito, etc.
Layout: formulario izquierda + lista derecha.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import get_module_colors, bind_combobox_dropdown_on_click
from manager.app.ui.components.tenant_autocomplete import TenantAutocompleteEntry
from manager.app.ui.views.register_expense_view import DatePickerWidget
from manager.app.services.accounting_service import accounting_service
from manager.app.services.tenant_service import tenant_service
from manager.app.logger import logger

TIPOS_AJUSTE = [
    "Descuento",
    "Depósito de garantía",
    "Interés de mora",
    "Nota de crédito",
    "Otro",
]

DIRECCIONES = ["Ingreso (entrada)", "Egreso (salida)"]


class ManualEntryView(tk.Frame):
    """Vista para gestionar asientos manuales (ajustes contables)."""

    def __init__(self, parent, on_back=None, presenter=None):
        super().__init__(parent)
        self.configure(bg=parent.cget("bg"))
        self._bg = parent.cget("bg")
        self.on_back = on_back
        self._colors = get_module_colors("contabilidad")
        self._edit_id = None
        self._selected_tenant = None

        self._build_layout()
        self._load_entries()

    # ------------------------------------------------------------------
    # Layout principal
    # ------------------------------------------------------------------

    def _build_layout(self):
        bg = self._bg

        header = tk.Frame(self, bg=bg)
        header.pack(fill="x", pady=(0, 4))

        if self.on_back:
            btn_back = tk.Button(
                header, text="× Volver",
                font=("Segoe UI", 10, "bold"),
                bg="#dc2626", fg="white",
                relief="flat", padx=10, pady=6,
                cursor="hand2", command=self._on_back,
            )
            btn_back.pack(side="left")
            btn_back.bind("<Enter>", lambda e: btn_back.config(bg="#b91c1c"))
            btn_back.bind("<Leave>", lambda e: btn_back.config(bg="#dc2626"))

        outer = tk.Frame(self, bg=bg)
        outer.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.MD))

        # Panel izquierdo — ancho fijo 300px, sin scroll
        form_panel = tk.Frame(outer, bg=bg, width=300)
        form_panel.pack(side="left", fill="y", padx=(0, Spacing.LG))
        form_panel.pack_propagate(False)
        self._build_form(form_panel)

        # Panel derecho — lista
        right_panel = tk.Frame(outer, bg=bg)
        right_panel.pack(side="left", fill="both", expand=True)
        self._build_list_panel(right_panel)

    # ------------------------------------------------------------------
    # Formulario compacto
    # ------------------------------------------------------------------

    def _build_form(self, parent):
        bg = self._bg
        theme = theme_manager.themes[theme_manager.current_theme]
        teal = self._colors["primary"]
        teal_hover = self._colors["hover"]

        tk.Label(parent, text="Asiento manual",
                 font=("Segoe UI", 10, "bold"),
                 bg=bg, fg=theme["text_primary"]).pack(anchor="w", pady=(0, 2))

        def lbl(text):
            tk.Label(parent, text=text, font=("Segoe UI", 9),
                     bg=bg, fg=theme["text_primary"]).pack(anchor="w")

        def err_lbl():
            l = tk.Label(parent, text="", font=("Segoe UI", 8), bg=bg, fg="#dc2626")
            l.pack(anchor="w")
            return l

        # Fecha
        lbl("Fecha:")
        self._date_picker = DatePickerWidget(parent)
        self._date_picker.pack(anchor="w", pady=(0, 3))
        self._date_picker.set(datetime.now().strftime("%d/%m/%Y"))

        # Tipo de ajuste
        lbl("Tipo de ajuste *:")
        self._tipo_var = tk.StringVar()
        tipo_combo = ttk.Combobox(parent, textvariable=self._tipo_var,
                                  values=TIPOS_AJUSTE, state="readonly", width=26)
        tipo_combo.pack(anchor="w", pady=(0, 0))
        bind_combobox_dropdown_on_click(tipo_combo)
        self._tipo_error = err_lbl()

        # Inquilino
        lbl("Inquilino (opcional):")
        try:
            tenants = tenant_service.get_all_tenants()
        except Exception:
            tenants = []
        self._tenant_widget = TenantAutocompleteEntry(
            parent, tenants=tenants, on_select=self._on_tenant_selected,
            width=28, placeholder="Buscar inquilino...", bg=bg,
        )
        self._tenant_widget.pack(anchor="w", pady=(0, 3))

        # Monto
        lbl("Monto ($) *:")
        self._monto_var = tk.StringVar()
        tk.Entry(parent, textvariable=self._monto_var,
                 font=("Segoe UI", 9), width=16).pack(anchor="w", pady=(0, 0))
        self._monto_error = err_lbl()

        # Dirección
        lbl("Dirección *:")
        self._dir_var = tk.StringVar(value=DIRECCIONES[0])
        dir_combo = ttk.Combobox(parent, textvariable=self._dir_var,
                                 values=DIRECCIONES, state="readonly", width=20)
        dir_combo.pack(anchor="w", pady=(0, 3))
        bind_combobox_dropdown_on_click(dir_combo)

        # Descripción
        lbl("Descripción *:")
        self._desc_var = tk.StringVar()
        tk.Entry(parent, textvariable=self._desc_var,
                 font=("Segoe UI", 9), width=26).pack(anchor="w", fill="x", pady=(0, 0))
        self._desc_error = err_lbl()

        # Separador
        tk.Frame(parent, height=1, bg="#cbd5e1").pack(fill="x", pady=(4, 4))

        # Botones lado a lado
        btn_row = tk.Frame(parent, bg=bg)
        btn_row.pack(fill="x")

        self._btn_save = tk.Button(
            btn_row, text="Guardar",
            font=("Segoe UI", 9, "bold"),
            bg=teal, fg="white",
            relief="flat", padx=8, pady=5,
            cursor="hand2", command=self._save_entry,
        )
        self._btn_save.pack(side="left", fill="x", expand=True, padx=(0, 2))
        self._btn_save.bind("<Enter>", lambda e: self._btn_save.config(bg=teal_hover))
        self._btn_save.bind("<Leave>", lambda e: self._btn_save.config(bg=teal))

        btn_cancel = tk.Button(
            btn_row, text="Cancelar",
            font=("Segoe UI", 9),
            bg="#6b7280", fg="white",
            relief="flat", padx=8, pady=5,
            cursor="hand2", command=self._clear_form,
        )
        btn_cancel.pack(side="left", fill="x", expand=True, padx=(2, 0))
        btn_cancel.bind("<Enter>", lambda e: btn_cancel.config(bg="#4b5563"))
        btn_cancel.bind("<Leave>", lambda e: btn_cancel.config(bg="#6b7280"))

    # ------------------------------------------------------------------
    # Panel de lista
    # ------------------------------------------------------------------

    def _build_list_panel(self, parent):
        bg = self._bg
        theme = theme_manager.themes[theme_manager.current_theme]

        top_bar = tk.Frame(parent, bg=bg)
        top_bar.pack(fill="x", pady=(0, Spacing.SM))

        tk.Label(top_bar, text="Asientos manuales registrados",
                 font=("Segoe UI", 12, "bold"),
                 bg=bg, fg=theme["text_primary"]).pack(side="left")

        self._btn_delete = tk.Button(
            top_bar, text="Eliminar",
            font=("Segoe UI", 10, "bold"),
            bg="#dc2626", fg="white",
            relief="flat", padx=10, pady=4,
            cursor="hand2", state="disabled",
            command=self._delete_entry,
        )
        self._btn_delete.pack(side="right")
        self._btn_delete.bind("<Enter>", lambda e: self._btn_delete.config(
            bg="#b91c1c") if self._btn_delete["state"] == "normal" else None)
        self._btn_delete.bind("<Leave>", lambda e: self._btn_delete.config(
            bg="#dc2626") if self._btn_delete["state"] == "normal" else None)

        columns = ("fecha", "tipo_ajuste", "referencia", "monto", "direccion")
        self._tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        col_config = [
            ("fecha",       "Fecha",       100, "center"),
            ("tipo_ajuste", "Tipo ajuste", 140, "center"),
            ("referencia",  "Referencia",  160, "center"),
            ("monto",       "Monto",       110, "center"),
            ("direccion",   "Dirección",    90, "center"),
        ]
        for col_id, heading, width, anchor in col_config:
            self._tree.heading(col_id, text=heading, anchor="center")
            self._tree.column(col_id, width=width, minwidth=60, anchor=anchor)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._tree.bind("<<TreeviewSelect>>", self._on_select)
        self._tree.bind("<Double-1>", self._on_double_click)

    # ------------------------------------------------------------------
    # Carga
    # ------------------------------------------------------------------

    def _load_entries(self):
        for item in self._tree.get_children():
            self._tree.delete(item)
        try:
            entries = accounting_service.get_entries_by_type("manual")
            entries.sort(key=lambda e: e.get("fecha", ""), reverse=True)
            if not entries:
                self._tree.insert("", "end", values=(
                    "", "No hay asientos manuales registrados.", "", "", ""))
                return
            for entry in entries:
                fecha = entry.get("fecha", "")
                try:
                    fecha_display = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
                except Exception:
                    fecha_display = fecha
                nombre = entry.get("nombre_inquilino", "")
                tipo_ajuste = entry.get("tipo_ajuste", "")
                referencia = nombre if nombre else tipo_ajuste
                monto = float(entry.get("monto", 0))
                dir_display = "Ingreso" if entry.get("direccion", "") == "entrada" else "Egreso"
                self._tree.insert("", "end", iid=str(entry["id"]), values=(
                    fecha_display, tipo_ajuste, referencia,
                    f"${monto:,.2f}", dir_display,
                ))
        except Exception as exc:
            logger.exception("Error al cargar asientos manuales: %s", exc)
            messagebox.showerror("Error", f"No se pudieron cargar los asientos:\n{exc}")

    # ------------------------------------------------------------------
    # Eventos
    # ------------------------------------------------------------------

    def _on_select(self, event=None):
        self._btn_delete.config(state="normal" if self._tree.selection() else "disabled")

    def _on_double_click(self, event=None):
        selected = self._tree.selection()
        if not selected:
            return
        entry_id = int(selected[0])
        try:
            entries = accounting_service.get_entries_by_type("manual")
            entry = next((e for e in entries if e.get("id") == entry_id), None)
            if not entry:
                return
            self._edit_id = entry_id
            self._btn_save.config(text="Actualizar asiento")
            fecha = entry.get("fecha", "")
            try:
                fecha_display = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
            except Exception:
                fecha_display = fecha
            self._date_picker.set(fecha_display)
            self._tipo_var.set(entry.get("tipo_ajuste", ""))
            self._monto_var.set(str(entry.get("monto", "")))
            dir_raw = entry.get("direccion", "entrada")
            self._dir_var.set(DIRECCIONES[0] if dir_raw == "entrada" else DIRECCIONES[1])
            self._desc_var.set(entry.get("descripcion", ""))
            nombre = entry.get("nombre_inquilino", "")
            if nombre:
                self._tenant_widget.var.set(nombre)
            else:
                self._tenant_widget.clear_selection()
            self._clear_errors()
        except Exception as exc:
            logger.exception("Error al cargar asiento manual para edición: %s", exc)

    def _on_tenant_selected(self, tenant):
        self._selected_tenant = tenant

    # ------------------------------------------------------------------
    # Validación
    # ------------------------------------------------------------------

    def _validate(self):
        valid = True
        if not self._tipo_var.get():
            self._tipo_error.config(text="Seleccione un tipo.")
            valid = False
        else:
            self._tipo_error.config(text="")
        try:
            val = float(self._monto_var.get())
            if val <= 0:
                raise ValueError
            self._monto_error.config(text="")
        except (ValueError, TypeError):
            self._monto_error.config(text="Monto válido > 0.")
            valid = False
        if not self._desc_var.get().strip():
            self._desc_error.config(text="Descripción requerida.")
            valid = False
        else:
            self._desc_error.config(text="")
        return valid

    def _clear_errors(self):
        self._tipo_error.config(text="")
        self._monto_error.config(text="")
        self._desc_error.config(text="")

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def _save_entry(self):
        if not self._validate():
            return
        fecha_str = self._date_picker.get().strip()
        try:
            fecha_iso = datetime.strptime(fecha_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Fecha inválida", "Ingrese la fecha en formato DD/MM/AAAA.")
            return
        direccion = "entrada" if self._dir_var.get() == DIRECCIONES[0] else "salida"
        tenant = self._tenant_widget.get_selected_tenant()
        id_inquilino = tenant.get("id") if tenant else None
        nombre_inquilino = tenant.get("nombre", "") if tenant else ""
        apartamento = ""
        if tenant:
            apt_id = tenant.get("apartamento")
            if apt_id is not None:
                try:
                    from manager.app.services.apartment_service import apartment_service
                    apt = apartment_service.get_apartment_by_id(int(apt_id))
                    if apt:
                        apartamento = str(apt.get("number", ""))
                except Exception:
                    pass
        data = {
            "tipo": "manual",
            "fecha": fecha_iso,
            "tipo_ajuste": self._tipo_var.get(),
            "id_inquilino": id_inquilino,
            "nombre_inquilino": nombre_inquilino,
            "apartamento": apartamento,
            "monto": float(self._monto_var.get()),
            "direccion": direccion,
            "descripcion": self._desc_var.get().strip(),
        }
        try:
            if self._edit_id is not None:
                accounting_service.update_entry(self._edit_id, data)
                logger.info("Asiento manual actualizado id=%s", self._edit_id)
            else:
                accounting_service.add_entry(data)
                logger.info("Asiento manual creado.")
            self._clear_form()
            self._load_entries()
        except Exception as exc:
            logger.exception("Error al guardar asiento manual: %s", exc)
            messagebox.showerror("Error", f"No se pudo guardar el asiento:\n{exc}")

    def _delete_entry(self):
        selected = self._tree.selection()
        if not selected:
            return
        entry_id = int(selected[0])
        if not messagebox.askyesno("Confirmar eliminación",
                                   "¿Está seguro de que desea eliminar este asiento manual?"):
            return
        try:
            if accounting_service.delete_entry(entry_id):
                self._clear_form()
                self._load_entries()
            else:
                messagebox.showwarning("No encontrado", "No se encontró el asiento a eliminar.")
        except Exception as exc:
            logger.exception("Error al eliminar asiento manual: %s", exc)
            messagebox.showerror("Error", f"No se pudo eliminar el asiento:\n{exc}")

    def _clear_form(self):
        self._edit_id = None
        self._selected_tenant = None
        self._btn_save.config(text="Guardar asiento")
        self._date_picker.set(datetime.now().strftime("%d/%m/%Y"))
        self._tipo_var.set("")
        self._monto_var.set("")
        self._dir_var.set(DIRECCIONES[0])
        self._desc_var.set("")
        self._tenant_widget.clear_selection()
        self._clear_errors()
        for item in self._tree.selection():
            self._tree.selection_remove(item)
        self._btn_delete.config(state="disabled")

    def _on_back(self):
        if self.on_back:
            self.on_back()
