# Archivo vacío temporalmente. El usuario prefiere usar la vista de búsqueda avanzada y lista para editar/eliminar. 

# Copia independiente de la vista de inquilinos para Editar/Eliminar
# (Duplicado de tenants_view.py, ahora evolucionará de forma separada)

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.services.tenant_service import tenant_service
from manager.app.ui.views.tenant_form_view import TenantFormView
from manager.app.ui.views.tenant_details_view import TenantDetailsView
import csv
import os

class EditDeleteTenantsView(tk.Frame):
    """Vista profesional para Editar/Eliminar Inquilinos (independiente)"""
    def __init__(self, parent, on_navigate: Callable = None, on_data_change: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_navigate = on_navigate
        self.on_data_change = on_data_change
        self.current_view = "list"
        self.selected_tenant = None
        self._show_tenants_list()

    def _show_tenants_list(self):
        self.current_view = "list"
        for widget in self.winfo_children():
            widget.destroy()
        header_frame = tk.Frame(self, bg="#f8f9fa")
        header_frame.pack(fill="x", pady=(0, 15))
        title_label = tk.Label(
            header_frame,
            text="✏️ Editar/Eliminar inquilinos",
            font=("Segoe UI", 18, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        title_label.pack(side="left", padx=10)
        btn_back = tk.Button(
            header_frame,
            text="← Volver al Menú",
            font=("Segoe UI", 10),
            bg="#6c757d",
            fg="white",
            relief="flat",
            padx=15,
            command=self._on_back_clicked
        )
        btn_back.pack(side="right", padx=10)
        main_container = tk.Frame(self, bg="#ffffff")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        search_panel = self._create_search_panel(main_container)
        search_panel.pack(side="left", fill="y", padx=(0, 15))
        list_panel = self._create_list_panel(main_container)
        list_panel.pack(side="right", fill="both", expand=True)
        self._load_and_display_tenants()

    def _create_search_panel(self, parent):
        panel = tk.Frame(parent, bg="#e3f2fd", relief="solid", bd=2, width=380)
        panel.pack_propagate(False)
        header = tk.Frame(panel, bg="#1976d2", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        title = tk.Label(
            header,
            text="🔍 Búsqueda Avanzada",
            font=("Segoe UI", 12, "bold"),
            bg="#1976d2",
            fg="white"
        )
        title.pack(expand=True)
        content = tk.Frame(panel, bg="#e3f2fd")
        content.pack(fill="both", expand=True, padx=12, pady=12)
        tk.Label(content, text="Búsqueda general:", font=("Segoe UI", 10, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(0,2))
        tk.Label(content, text="(Nombre, Cédula, Apartamento, Email, Teléfono)", font=("Segoe UI", 8), bg="#e3f2fd", fg="#666666").pack(anchor="w", pady=(0,5))
        self.search_entry = tk.Entry(content, font=("Segoe UI", 10), relief="solid", bd=1)
        self.search_entry.pack(fill="x", pady=(0,10))
        self.search_entry.bind('<KeyRelease>', self._on_search_change)
        tk.Label(content, text="Filtro por apartamento:", font=("Segoe UI", 10, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(0,5))
        self.apartment_var = tk.StringVar(value="Todos")
        apartment_combo = ttk.Combobox(content, textvariable=self.apartment_var, font=("Segoe UI", 10))
        apartment_combo['values'] = ("Todos", "101", "102", "103", "106", "201", "202", "203", "301", "302", "303")
        apartment_combo.pack(fill="x", pady=(0,10))
        apartment_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        tk.Label(content, text="Estado:", font=("Segoe UI", 10, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(0,5))
        self.status_var = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(content, textvariable=self.status_var, font=("Segoe UI", 10))
        status_combo['values'] = ("Todos", "Activo", "En Mora", "Inactivo")
        status_combo.pack(fill="x", pady=(0,10))
        status_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        tk.Label(content, text="Fecha de ingreso:", font=("Segoe UI", 9, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(5,2))
        date_frame = tk.Frame(content, bg="#e3f2fd")
        date_frame.pack(fill="x", pady=(0,5))
        tk.Label(date_frame, text="Desde:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left")
        self.date_from = tk.Entry(date_frame, width=10, font=("Segoe UI", 8))
        self.date_from.pack(side="left", padx=(3,8))
        tk.Label(date_frame, text="Hasta:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left")
        self.date_to = tk.Entry(date_frame, width=10, font=("Segoe UI", 8))
        self.date_to.pack(side="left", padx=3)
        tk.Label(content, text="Rango de arriendo:", font=("Segoe UI", 9, "bold"), bg="#e3f2fd").pack(anchor="w", pady=(5,2))
        rent_frame = tk.Frame(content, bg="#e3f2fd")
        rent_frame.pack(fill="x", pady=(0,5))
        tk.Label(rent_frame, text="Min:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left")
        self.rent_min = tk.Entry(rent_frame, width=8, font=("Segoe UI", 8))
        self.rent_min.pack(side="left", padx=(3,8))
        tk.Label(rent_frame, text="Max:", bg="#e3f2fd", font=("Segoe UI", 8)).pack(side="left")
        self.rent_max = tk.Entry(rent_frame, width=8, font=("Segoe UI", 8))
        self.rent_max.pack(side="left", padx=3)
        self.results_indicator = tk.Label(
            content,
            text="📊 Resultados: mostrando todos",
            font=("Segoe UI", 8),
            bg="#e3f2fd",
            fg="#2e7d32"
        )
        self.results_indicator.pack(anchor="w", pady=(8,8))
        btn_frame = tk.Frame(content, bg="#e3f2fd")
        btn_frame.pack(fill="x", pady=8)
        btn_search = tk.Button(
            btn_frame,
            text="🔍 Aplicar",
            font=("Segoe UI", 9, "bold"),
            bg="#4caf50",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=self._apply_filters
        )
        btn_search.pack(side="left", padx=(0,8))
        btn_clear = tk.Button(
            btn_frame,
            text="🧹 Limpiar",
            font=("Segoe UI", 9),
            bg="#ff9800",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            command=self._clear_filters
        )
        btn_clear.pack(side="left")
        return panel

    def _create_list_panel(self, parent):
        panel = tk.Frame(parent, bg="#f1f8e9", relief="solid", bd=2)
        header = tk.Frame(panel, bg="#388e3c", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        header_content = tk.Frame(header, bg="#388e3c")
        header_content.pack(expand=True)
        self.list_title = tk.Label(
            header_content,
            text="📋 Lista de Inquilinos",
            font=("Segoe UI", 12, "bold"),
            bg="#388e3c",
            fg="white"
        )
        self.list_title.pack(side="left", padx=15)
        self.counter_label = tk.Label(
            header_content,
            text="(0 inquilinos)",
            font=("Segoe UI", 10),
            bg="#388e3c",
            fg="#c8e6c9"
        )
        self.counter_label.pack(side="left", padx=5)
        self.scroll_frame = tk.Frame(panel, bg="#f1f8e9")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.canvas = tk.Canvas(self.scroll_frame, bg="#f1f8e9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f1f8e9")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return panel

    def _load_and_display_tenants(self):
        try:
            tenants = tenant_service.get_all_tenants()
            self.all_tenants = tenants
            self._display_tenants(tenants)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar inquilinos: {str(e)}")

    def _display_tenants(self, tenants):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        if not tenants:
            self._show_empty_state()
            return
        active_tenants = []
        overdue_tenants = []
        inactive_tenants = []
        for tenant in tenants:
            estado = tenant.get('estado_pago', 'al_dia')
            if estado == 'inactivo':
                inactive_tenants.append(tenant)
            elif estado == 'moroso':
                overdue_tenants.append(tenant)
            else:
                active_tenants.append(tenant)
        current_row = 0
        if active_tenants:
            current_row = self._display_group("✅ ACTIVOS", active_tenants, "#4caf50", current_row)
        if overdue_tenants:
            current_row = self._display_group("⚠️ EN MORA", overdue_tenants, "#ff9800", current_row)
        if inactive_tenants:
            current_row = self._display_group("❌ INACTIVOS", inactive_tenants, "#f44336", current_row)
        total = len(tenants)
        self.counter_label.config(text=f"({total} inquilino{'s' if total != 1 else ''})")
        if hasattr(self, 'results_indicator'):
            total_available = len(getattr(self, 'all_tenants', []))
            if total == total_available:
                self.results_indicator.config(
                    text="📊 Resultados: mostrando todos",
                    fg="#2e7d32"
                )
            else:
                self.results_indicator.config(
                    text=f"🔍 Resultados: {total} de {total_available} inquilinos",
                    fg="#1976d2"
                )
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _display_group(self, title, tenants, color, start_row):
        separator = tk.Frame(self.scrollable_frame, bg=color, height=2)
        separator.pack(fill="x", pady=(10,0))
        group_title = tk.Label(
            self.scrollable_frame,
            text=f"{title} ({len(tenants)})",
            font=("Segoe UI", 11, "bold"),
            bg="#f1f8e9",
            fg=color
        )
        group_title.pack(anchor="w", pady=(5,5))
        for i, tenant in enumerate(tenants):
            self._create_tenant_row(tenant, color, i % 2 == 0)
        return start_row + len(tenants)

    def _create_tenant_row(self, tenant, status_color, is_even):
        bg_color = "#ffffff" if is_even else "#f8f9fa"
        row_frame = tk.Frame(self.scrollable_frame, bg=bg_color, relief="solid", bd=1)
        row_frame.pack(fill="x", pady=1)
        content = tk.Frame(row_frame, bg=bg_color)
        content.pack(fill="x", padx=10, pady=8)
        name = tenant.get('nombre', 'Sin nombre')
        apartment = tenant.get('apartamento', 'N/A')
        valor_arriendo = tenant.get('valor_arriendo', 0)
        estado_pago = tenant.get('estado_pago', 'al_dia')
        estado_texto = {
            'al_dia': 'Al día',
            'moroso': 'En mora',
            'inactivo': 'Inactivo'
        }.get(estado_pago, 'Al día')
        main_info = tk.Label(
            content,
            text=f"👤 {name}",
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            anchor="w"
        )
        main_info.pack(anchor="w")
        details = tk.Label(
            content,
            text=f"🏠 Apartamento: {apartment} | 💰 Arriendo: ${valor_arriendo:,.0f} | 📞 Teléfono: {tenant.get('telefono', 'No registrado')}",
            font=("Segoe UI", 9),
            bg=bg_color,
            anchor="w"
        )
        details.pack(anchor="w", pady=(2,0))
        fecha_ingreso = tenant.get('fecha_ingreso', None)
        dia_pago = None
        if fecha_ingreso:
            try:
                dia_pago = int(fecha_ingreso.split('/')[0])
            except Exception:
                dia_pago = None
        if dia_pago:
            dia_pago_label = tk.Label(
                content,
                text=f"📅 Día de pago: {dia_pago} de cada mes",
                font=("Segoe UI", 9),
                bg=bg_color,
                fg="#1976d2",
                anchor="w"
            )
            dia_pago_label.pack(anchor="w")
        estado_label = tk.Label(
            content,
            text=f"● {estado_texto}",
            font=("Segoe UI", 9, "bold"),
            fg=status_color,
            bg=bg_color
        )
        estado_label.pack(anchor="w", pady=(2,0))
        actions = tk.Frame(content, bg=bg_color)
        actions.pack(anchor="e", pady=(2,0))
        btn_edit = tk.Button(
            actions,
            text="Editar",
            font=("Segoe UI", 9, "bold"),
            bg="#3b82f6",
            fg="white",
            relief="flat",
            padx=10,
            command=lambda t=tenant: self._edit_tenant(t)
        )
        btn_edit.pack(side="left", padx=(0, 8))
        btn_delete = tk.Button(
            actions,
            text="Eliminar",
            font=("Segoe UI", 9, "bold"),
            bg="#ef4444",
            fg="white",
            relief="flat",
            padx=10,
            command=lambda t=tenant: self._confirm_delete_tenant(t)
        )
        btn_delete.pack(side="left")

    def _edit_tenant(self, tenant):
        self.current_view = "edit"
        self.selected_tenant = tenant
        for widget in self.winfo_children():
            widget.destroy()
        form_view = TenantFormView(
            self,
            on_back=self._show_tenants_list,
            tenant_data=tenant,
            on_save_success=self._load_and_display_tenants
        )
        form_view.pack(fill="both", expand=True)

    def _confirm_delete_tenant(self, tenant):
        nombre = tenant.get("nombre", "Inquilino")
        if messagebox.askyesno("Confirmar eliminación", f"¿Seguro que deseas eliminar a {nombre}? Esta acción no se puede deshacer."):
            success = tenant_service.delete_tenant(tenant.get("id"))
            if success:
                self._load_and_display_tenants()
                messagebox.showinfo("Eliminado", f"Inquilino '{nombre}' eliminado correctamente.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar el inquilino.")

    def _on_back_clicked(self):
        if self.on_navigate:
            self.on_navigate("tenants")

    def _on_search_change(self, event=None):
        self._apply_filters()

    def _on_filter_change(self, event=None):
        self._apply_filters()

    def _apply_filters(self):
        if not hasattr(self, 'all_tenants'):
            return
        filtered = self.all_tenants.copy()
        search_text = self.search_entry.get().lower().strip()
        if search_text:
            filtered = [t for t in filtered if 
                       search_text in t.get('nombre', '').lower() or
                       search_text in t.get('numero_documento', '').lower() or
                       search_text in t.get('apartamento', '').lower() or
                       search_text in t.get('email', '').lower() or
                       search_text in t.get('telefono', '').lower()]
        apartment = self.apartment_var.get()
        if apartment != "Todos" and not search_text:
            filtered = [t for t in filtered if t.get('apartamento') == apartment]
        elif apartment != "Todos" and search_text:
            filtered = [t for t in filtered if t.get('apartamento') == apartment]
        status = self.status_var.get()
        if status != "Todos":
            status_mapping = {
                "Activo": "al_dia",
                "En Mora": "moroso",
                "Inactivo": "inactivo"
            }
            target_status = status_mapping.get(status, status.lower())
            filtered = [t for t in filtered if t.get('estado_pago') == target_status]
        self._display_tenants(filtered)

    def _show_empty_state(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        label = tk.Label(self.scrollable_frame, text="No hay inquilinos para mostrar", font=("Segoe UI", 12, "bold"), fg="#666", bg="#f1f8e9")
        label.pack(pady=40)

    def _clear_filters(self):
        """Limpia todos los filtros de búsqueda y muestra todos los inquilinos"""
        self.search_entry.delete(0, tk.END)
        self.apartment_var.set("Todos")
        self.status_var.set("Todos")
        self.date_from.delete(0, tk.END)
        self.date_to.delete(0, tk.END)
        self.rent_min.delete(0, tk.END)
        self.rent_max.delete(0, tk.END)
        if hasattr(self, 'all_tenants'):
            self._display_tenants(self.all_tenants) 