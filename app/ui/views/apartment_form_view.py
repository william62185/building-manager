import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict, Any

from manager.app.services.apartment_service import apartment_service
from manager.app.services.building_service import building_service
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import ModernButton, create_rounded_button, get_module_colors

class ApartmentFormView(tk.Frame):
    """Vista de formulario para apartamentos con selección de edificio"""

    def __init__(self, parent, on_back: Callable, on_save_success: Callable, apartment_data: Optional[Dict[str, Any]] = None, on_navigate: Optional[Callable] = None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.on_back = on_back
        self.on_save_success = on_save_success
        self.on_navigate = on_navigate
        self.is_edit_mode = apartment_data is not None
        self.apartment_data = apartment_data if apartment_data else {}
        self._scroll_area_hover_count = 0
        self.canvas = None
        self.bind("<Destroy>", self._on_destroy)
        self._create_layout()

    def _create_layout(self):
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        title_text = "Editar Apartamento" if self.is_edit_mode else "Registrar Nuevo Apartamento"
        
        header = tk.Frame(self, bg=cb)
        header.pack(fill="x", pady=(0, Spacing.SM), padx=Spacing.MD)
        tk.Label(header, text=title_text, font=("Segoe UI", 16, "bold"), bg=cb, fg=theme["text_primary"]).pack(side="left")
        buttons_frame = tk.Frame(header, bg=cb)
        buttons_frame.pack(side="right")
        self._create_navigation_buttons(buttons_frame, self.on_back)
        
        # Botones Guardar/Cancelar (compactos, arriba a la derecha o abajo)
        bottom_btns = tk.Frame(self, bg=cb)
        bottom_btns.pack(side="bottom", fill="x", pady=(Spacing.SM, Spacing.MD), padx=Spacing.MD)
        ModernButton(bottom_btns, text="Guardar Cambios", icon="💾", style="purple", small=True, command=self._save_apartment).pack(side="right")
        ModernButton(bottom_btns, text="Cancelar", style="secondary", small=True, command=self.on_back).pack(side="right", padx=(0, Spacing.SM))

        container = tk.Frame(self, bg=cb)
        container.pack(fill="both", expand=True, padx=Spacing.MD, pady=(0, Spacing.SM))
        form_container = tk.Frame(container, bg=cb)
        form_container.pack(fill="x", expand=True)
        self._create_form_fields(form_container)

    def _create_form_fields(self, parent):
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        fg = theme.get("text_primary", "#1f2937")
        frame = tk.Frame(parent, bg=cb)
        frame.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
        
        def create_label(p, text, w=14):
            return tk.Label(p, text=text, font=("Segoe UI", 10), fg=fg, bg=cb, width=w, anchor="w")

        row_pady = 1
        col0_w = 14

        def half_width_holder(parent):
            """Frame donde el widget ocupa la mitad izquierda del espacio (pegado a la etiqueta); la otra mitad queda vacía a la derecha."""
            rest = tk.Frame(parent, bg=cb)
            rest.pack(side="left", fill="x", expand=True)
            rest.grid_columnconfigure(0, weight=1)
            rest.grid_columnconfigure(1, weight=1)
            holder = tk.Frame(rest, bg=cb)
            holder.grid(row=0, column=0, sticky="ew")
            holder.grid_columnconfigure(0, weight=1)
            return holder

        # --- Selector de Edificio (solo para nuevos apartamentos) ---
        if not self.is_edit_mode:
            building_row_frame = tk.Frame(frame, bg=cb)
            building_row_frame.pack(fill="x", pady=row_pady)
            create_label(building_row_frame, "Edificio*:", col0_w).pack(side="left")
            self.building_var = tk.StringVar()
            building_holder = half_width_holder(building_row_frame)
            self.building_selector = ttk.Combobox(building_holder, textvariable=self.building_var, state="readonly", width=24, font=("Segoe UI", 10))
            self.building_selector.pack(fill="x", expand=True)
            self.buildings = building_service.get_all_buildings()
            if not self.buildings:
                messagebox.showwarning("Sin Edificios", "No hay edificios registrados. Por favor, cree uno desde 'Gestionar Edificio' antes de añadir apartamentos.")
                self.on_back()
                return
            building_names = [b.get('name', f"Edificio ID {b.get('id', 'N/A')}") for b in self.buildings]
            self.building_selector['values'] = building_names
            if building_names:
                self.building_selector.current(0)

        # --- Tipo de Unidad ---
        unit_types = ["Apartamento Estándar", "Local Comercial", "Penthouse", "Depósito", "Otro"]
        unit_type_frame = tk.Frame(frame, bg=cb)
        unit_type_frame.pack(fill="x", pady=row_pady)
        create_label(unit_type_frame, "Tipo de Unidad*:", col0_w).pack(side="left")
        self.unit_type_var = tk.StringVar()
        unit_holder = half_width_holder(unit_type_frame)
        self.unit_type_combo = ttk.Combobox(unit_holder, textvariable=self.unit_type_var, values=unit_types, state="readonly", width=24, font=("Segoe UI", 10))
        self.unit_type_combo.pack(fill="x", expand=True)
        self.unit_type_combo.bind("<<ComboboxSelected>>", self._on_unit_type_selected)

        self.other_type_frame = tk.Frame(frame, bg=cb)
        create_label(self.other_type_frame, "Especificar Otro*:", col0_w).pack(side="left")
        self.other_type_var = tk.StringVar()
        other_holder = half_width_holder(self.other_type_frame)
        self.other_type_entry = ttk.Entry(other_holder, textvariable=self.other_type_var, width=28, font=("Segoe UI", 10))
        self.other_type_entry.pack(fill="x", expand=True)
        self.unit_type_row_frame = unit_type_frame

        if self.is_edit_mode:
            saved_unit_type = self.apartment_data.get('unit_type', '')
            if saved_unit_type in unit_types:
                self.unit_type_var.set(saved_unit_type)
            elif saved_unit_type:
                self.unit_type_var.set("Otro")
                self.other_type_var.set(saved_unit_type)

        fields = [
            ("Número/Letra*:", "number", "entry"), ("Piso*:", "floor", "entry"),
            ("Habitaciones*:", "rooms", "entry"), ("Baños*:", "bathrooms", "entry"),
            ("Área (m²):", "area", "entry"), ("Arriendo Base ($)*:", "base_rent", "entry"),
            ("Estado*:", "status", "combo"), ("Descripción:", "description", "text")
        ]
        self.form_vars = {}
        for key in [f[1] for f in fields]:
            self.form_vars[key] = tk.StringVar(value=self.apartment_data.get(key, ""))
        if not self.is_edit_mode:
            self.form_vars["status"].set("Disponible")

        self.field_rows = []
        for i, (label_text, key, widget_type) in enumerate(fields):
            row_frame = tk.Frame(frame, bg=cb)
            row_frame.pack(fill="x", pady=row_pady)
            create_label(row_frame, label_text, col0_w).pack(side="left")
            holder = half_width_holder(row_frame)
            if widget_type == "entry":
                widget = ttk.Entry(holder, textvariable=self.form_vars[key], width=28, font=("Segoe UI", 10))
            elif widget_type == "combo":
                widget = ttk.Combobox(holder, textvariable=self.form_vars[key], values=["Disponible", "Ocupado", "Mantenimiento"], state="readonly", width=24, font=("Segoe UI", 10))
            elif widget_type == "text":
                widget = tk.Text(holder, height=2, width=28, font=("Segoe UI", 10), relief="solid", bd=1)
                widget.insert("1.0", self.form_vars[key].get())
                self.description_text_widget = widget
            widget.pack(fill="x", expand=True)
            self.field_rows.append(row_frame)

        self._on_unit_type_selected()

    def _on_unit_type_selected(self, event=None):
        """Muestra u oculta el campo para 'Otro' tipo de unidad."""
        if self.unit_type_var.get() == "Otro":
            self.other_type_frame.pack(after=self.unit_type_row_frame, fill="x", pady=(0, 1))
        else:
            self.other_type_frame.pack_forget()

    def _validate_form(self) -> bool:
        if not self.is_edit_mode:
            if not self.building_var.get():
                messagebox.showerror("Error de Validación", "Debe seleccionar un edificio.")
                return False
            if not self.unit_type_var.get():
                messagebox.showerror("Error de Validación", "Debe seleccionar un tipo de unidad.")
                return False
            if self.unit_type_var.get() == "Otro" and not self.other_type_var.get().strip():
                messagebox.showerror("Error de Validación", "Debe especificar el tipo de unidad en el campo 'Otro'.")
                return False

        required_fields = ["number", "floor", "rooms", "bathrooms", "base_rent", "status"]
        for key in required_fields:
            if not self.form_vars[key].get().strip():
                messagebox.showerror("Error de Validación", f"El campo '{key.replace('_', ' ').capitalize()}' es obligatorio.")
                return False
        return True

    def _save_apartment(self):
        if not self._validate_form():
            return
        
        data_to_save = {key: var.get() for key, var in self.form_vars.items()}
        if hasattr(self, 'description_text_widget'):
            data_to_save['description'] = self.description_text_widget.get("1.0", "end-1c").strip()

        unit_type = self.unit_type_var.get()
        data_to_save['unit_type'] = self.other_type_var.get().strip() if unit_type == "Otro" else unit_type

        try:
            if self.is_edit_mode:
                apartment_id = self.apartment_data["id"]
                apartment_service.update_apartment(apartment_id, data_to_save)
                messagebox.showinfo("Éxito", "Apartamento actualizado correctamente.")
            else:
                selected_building_name = self.building_var.get()
                building_id = None
                for building in self.buildings:
                    if building.get('name') == selected_building_name:
                        building_id = building.get('id')
                        break
                
                if building_id is None:
                    messagebox.showerror("Error Interno", "No se pudo determinar el edificio seleccionado.")
                    return
                
                apartment_service.create_apartment(data_to_save, building_id)
                messagebox.showinfo("Éxito", "Apartamento registrado correctamente.")
            
            self.on_save_success()
            self.on_back()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el apartamento: {str(e)}")
            
    def _on_destroy(self, event):
        if event.widget == self:
            self._unbind_mousewheel(event)

    def _on_mousewheel(self, event):
        pass # Ya no se necesita scroll

    def _bind_mousewheel(self, event):
        pass # Ya no se necesita scroll

    def _unbind_mousewheel(self, event):
        pass # Ya no se necesita scroll

    def _create_navigation_buttons(self, parent, on_back_command):
        """Crea los botones Volver y Dashboard con estilo consistente"""
        from manager.app.ui.components.icons import Icons
        theme = theme_manager.themes[theme_manager.current_theme]
        colors = get_module_colors("administración")
        purple_primary = colors["primary"]
        purple_hover = colors["hover"]
        purple_light = colors["light"]
        purple_text = colors["text"]
        btn_bg = theme.get("btn_secondary_bg", "#e5e7eb")
        
        def go_to_dashboard():
            # Prioridad 1: Usar callback directo si está disponible
            if hasattr(self, 'on_navigate') and self.on_navigate is not None:
                try:
                    self.on_navigate("dashboard")
                    return
                except Exception as e:
                    print(f"Error en callback de navegación: {e}")
            
            # Prioridad 2: Buscar desde el root window (más confiable)
            try:
                root = self.winfo_toplevel()
                # Buscar MainWindow entre los hijos del root
                for child in root.winfo_children():
                    if (hasattr(child, '_navigate_to') and 
                        hasattr(child, '_load_view') and 
                        hasattr(child, 'views_container')):
                        try:
                            child._navigate_to("dashboard")
                            return
                        except Exception as e:
                            print(f"Error al navegar desde root: {e}")
            except Exception as e:
                print(f"Error en búsqueda desde root: {e}")
            
            # Prioridad 3: Buscar MainWindow en la jerarquía de widgets
            widget = self.master
            max_depth = 15
            depth = 0
            while widget and depth < max_depth:
                if (hasattr(widget, '_navigate_to') and 
                    hasattr(widget, '_load_view') and 
                    hasattr(widget, 'views_container')):
                    try:
                        widget._navigate_to("dashboard")
                        return
                    except Exception as e:
                        print(f"Error al navegar: {e}")
                        break
                widget = getattr(widget, 'master', None)
                depth += 1
            
            # Prioridad 4: Si no se encontró MainWindow, usar on_back como fallback
            if on_back_command:
                on_back_command()
        
        # Botón "Volver"
        btn_back = create_rounded_button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color=btn_bg,
            fg_color=purple_primary,
            hover_bg=purple_light,
            hover_fg=purple_text,
            command=on_back_command,
            padx=12,
            pady=5,
            radius=4,
            border_color=purple_light
        )
        btn_back.pack(side="right", padx=(Spacing.SM, 0))
        # Botón "Dashboard"
        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=purple_primary,
            fg_color="white",
            hover_bg=purple_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=12,
            pady=5,
            radius=4,
            border_color=purple_hover
        )
        btn_dashboard.pack(side="right")
