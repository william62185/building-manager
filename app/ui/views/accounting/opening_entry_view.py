"""
Vista de Asientos de apertura del módulo de contabilidad.
Permite registrar saldos iniciales (migración desde Excel u otro sistema).
Layout: formulario izquierda + lista derecha.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import get_module_colors, bind_combobox_dropdown_on_click
from manager.app.ui.views.register_expense_view import DatePickerWidget
from manager.app.services.accounting_service import accounting_service
from manager.app.logger import logger


class OpeningEntryView(tk.Frame):
    """Vista para gestionar asientos de apertura (saldos iniciales)."""

    def __init__(self, parent, on_back=None, presenter=None):
        super().__init__(parent)
        self.configure(bg=parent.cget("bg"))
        self._bg = parent.cget("bg")
        self.on_back = on_back
        self._colors = get_module_colors("contabilidad")
        self._edit_id = None

        self._build_layout()
        self._load_entries()

    # ------------------------------------------------------------------
    # Layout principal
    # ------------------------------------------------------------------

    def _build_layout(self):
        bg = self._bg

        header = tk.Frame(self, bg=bg)
        header.pack(fill="x", pady=(0, Spacing.SM))

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

        # Panel izquierdo — formulario (ancho fijo 290px)
        form_panel = tk.Frame(outer, bg=bg, width=290)
        form_panel.pack(side="left", fill="y", padx=(0, Spacing.LG))
        form_panel.pack_propagate(False)
        self._build_form(form_panel)

        # Panel derecho — lista
        right_panel = tk.Frame(outer, bg=bg)
        right_panel.pack(side="left", fill="both", expand=True)
        self._build_list_panel(right_panel)

    # ------------------------------------------------------------------
    # Formulario
    # ------------------------------------------------------------------

    def _build_form(self, parent):
        bg = self._bg
        theme = theme_manager.themes[theme_manager.current_theme]
        teal = self._colors["primary"]
        teal_hover = self._colors["hover"]

        tk.Label(
            parent, text="Asiento de apertura",
            font=("Segoe UI", 11, "bold"),
            bg=bg, fg=theme["text_primary"],
        ).pack(anchor="w", pady=(0, 6))

        # --- Fecha ---
        tk.Label(parent, text="Fecha:", font=("Segoe UI", 10),
                 bg=bg, fg=theme["text_primary"]).pack(anchor="w")
        self._date_picker = DatePickerWidget(parent)
        self._date_picker.pack(anchor="w", pady=(0, 6))
        self._date_picker.set(datetime.now().strftime("%d/%m/%Y"))

        # --- Descripción ---
        tk.Label(parent, text="Descripción *:", font=("Segoe UI", 10),
                 bg=bg, fg=theme["text_primary"]).pack(anchor="w")
        self._desc_var = tk.StringVar()
        tk.Entry(parent, textvariable=self._desc_var,
                 font=("Segoe UI", 10), width=28).pack(anchor="w", fill="x", pady=(0, 1))
        self._desc_error = tk.Label(parent, text="", font=("Segoe UI", 8),
                                    bg=bg, fg="#dc2626")
        self._desc_error.pack(anchor="w", pady=(0, 6))

        # --- Ingresos acumulados ---
        tk.Label(parent, text="Ingresos acumulados ($):", font=("Segoe UI", 10),
                 bg=bg, fg=theme["text_primary"]).pack(anchor="w")
        self._ingresos_var = tk.StringVar(value="0")
        tk.Entry(parent, textvariable=self._ingresos_var,
                 font=("Segoe UI", 10), width=18).pack(anchor="w", pady=(0, 1))
        self._ingresos_error = tk.Label(parent, text="", font=("Segoe UI", 8),
                                        bg=bg, fg="#dc2626")
        self._ingresos_error.pack(anchor="w", pady=(0, 6))

        # --- Egresos acumulados ---
        tk.Label(parent, text="Egresos acumulados ($):", font=("Segoe UI", 10),
                 bg=bg, fg=theme["text_primary"]).pack(anchor="w")
        self._egresos_var = tk.StringVar(value="0")
        tk.Entry(parent, textvariable=self._egresos_var,
                 font=("Segoe UI", 10), width=18).pack(anchor="w", pady=(0, 1))
        self._egresos_error = tk.Label(parent, text="", font=("Segoe UI", 8),
                                       bg=bg, fg="#dc2626")
        self._egresos_error.pack(anchor="w", pady=(0, 10))

        # Botones lado a lado
        btn_row = tk.Frame(parent, bg=bg)
        btn_row.pack(fill="x", pady=(8, 0))

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

        tk.Label(
            top_bar, text="Asientos registrados",
            font=("Segoe UI", 12, "bold"),
            bg=bg, fg=theme["text_primary"],
        ).pack(side="left")

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

        columns = ("fecha", "descripcion", "ingresos", "egresos")
        self._tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        col_config = [
            ("fecha",       "Fecha",        100, "center"),
            ("descripcion", "Descripción",  260, "center"),
            ("ingresos",    "Ingresos",     120, "center"),
            ("egresos",     "Egresos",      120, "center"),
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
            entries = accounting_service.get_entries_by_type("apertura")
            entries.sort(key=lambda e: e.get("fecha", ""), reverse=True)
            if not entries:
                self._tree.insert("", "end", values=(
                    "", "No hay asientos de apertura registrados.", "", "",
                ))
                return
            for entry in entries:
                fecha = entry.get("fecha", "")
                try:
                    fecha_display = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
                except Exception:
                    fecha_display = fecha
                ingresos = float(entry.get("monto_ingresos", 0) or 0)
                egresos = float(entry.get("monto_egresos", 0) or 0)
                self._tree.insert("", "end", iid=str(entry["id"]), values=(
                    fecha_display,
                    entry.get("descripcion", ""),
                    f"${ingresos:,.2f}",
                    f"${egresos:,.2f}",
                ))
        except Exception as exc:
            logger.exception("Error al cargar asientos de apertura: %s", exc)
            messagebox.showerror("Error", f"No se pudieron cargar los asientos:\n{exc}")

    # ------------------------------------------------------------------
    # Eventos
    # ------------------------------------------------------------------

    def _on_select(self, event=None):
        selected = self._tree.selection()
        self._btn_delete.config(state="normal" if selected else "disabled")

    def _on_double_click(self, event=None):
        selected = self._tree.selection()
        if not selected:
            return
        entry_id = int(selected[0])
        try:
            entries = accounting_service.get_entries_by_type("apertura")
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
            self._desc_var.set(entry.get("descripcion", ""))
            self._ingresos_var.set(str(entry.get("monto_ingresos", 0) or 0))
            self._egresos_var.set(str(entry.get("monto_egresos", 0) or 0))
            self._clear_errors()
        except Exception as exc:
            logger.exception("Error al cargar asiento para edición: %s", exc)

    # ------------------------------------------------------------------
    # Validación
    # ------------------------------------------------------------------

    def _validate(self):
        valid = True
        if not self._desc_var.get().strip():
            self._desc_error.config(text="La descripción es requerida.")
            valid = False
        else:
            self._desc_error.config(text="")
        try:
            val = float(self._ingresos_var.get())
            if val < 0:
                raise ValueError
            self._ingresos_error.config(text="")
        except (ValueError, TypeError):
            self._ingresos_error.config(text="Número válido >= 0.")
            valid = False
        try:
            val = float(self._egresos_var.get())
            if val < 0:
                raise ValueError
            self._egresos_error.config(text="")
        except (ValueError, TypeError):
            self._egresos_error.config(text="Número válido >= 0.")
            valid = False
        return valid

    def _clear_errors(self):
        self._desc_error.config(text="")
        self._ingresos_error.config(text="")
        self._egresos_error.config(text="")

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
        data = {
            "tipo": "apertura",
            "fecha": fecha_iso,
            "descripcion": self._desc_var.get().strip(),
            "monto_ingresos": float(self._ingresos_var.get()),
            "monto_egresos": float(self._egresos_var.get()),
        }
        try:
            if self._edit_id is not None:
                accounting_service.update_entry(self._edit_id, data)
                logger.info("Asiento de apertura actualizado id=%s", self._edit_id)
            else:
                accounting_service.add_entry(data)
                logger.info("Asiento de apertura creado.")
            self._clear_form()
            self._load_entries()
        except Exception as exc:
            logger.exception("Error al guardar asiento de apertura: %s", exc)
            messagebox.showerror("Error", f"No se pudo guardar el asiento:\n{exc}")

    def _delete_entry(self):
        selected = self._tree.selection()
        if not selected:
            return
        entry_id = int(selected[0])
        if not messagebox.askyesno("Confirmar eliminación",
                                   "¿Está seguro de que desea eliminar este asiento?"):
            return
        try:
            if accounting_service.delete_entry(entry_id):
                self._clear_form()
                self._load_entries()
            else:
                messagebox.showwarning("No encontrado", "No se encontró el asiento a eliminar.")
        except Exception as exc:
            logger.exception("Error al eliminar asiento de apertura: %s", exc)
            messagebox.showerror("Error", f"No se pudo eliminar el asiento:\n{exc}")

    def _clear_form(self):
        self._edit_id = None
        self._btn_save.config(text="Guardar asiento")
        self._date_picker.set(datetime.now().strftime("%d/%m/%Y"))
        self._desc_var.set("")
        self._ingresos_var.set("0")
        self._egresos_var.set("0")
        self._clear_errors()
        for item in self._tree.selection():
            self._tree.selection_remove(item)
        self._btn_delete.config(state="disabled")

    def _on_back(self):
        if self.on_back:
            self.on_back()
