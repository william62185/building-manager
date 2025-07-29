import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional, Dict, Any

from manager.app.services.apartment_service import apartment_service
from manager.app.services.building_service import building_service
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import ModernButton

class ApartmentFormView(tk.Frame):
    """Vista de formulario para apartamentos con selección de edificio"""

    def __init__(self, parent, on_back: Callable, on_save_success: Callable, apartment_data: Optional[Dict[str, Any]] = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_back = on_back
        self.on_save_success = on_save_success
        self.is_edit_mode = apartment_data is not None
        self.apartment_data = apartment_data if apartment_data else {}
        self._scroll_area_hover_count = 0
        self.canvas = None
        
        self.bind("<Destroy>", self._on_destroy)
        self._create_layout()

    def _create_layout(self):
        title_text = "Editar Apartamento" if self.is_edit_mode else "Registrar Nuevo Apartamento"
        
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)
        
        tk.Label(header, text=title_text, **theme_manager.get_style("label_title")).pack(side="left")
        
        buttons_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        buttons_frame.pack(side="bottom", fill="x", pady=Spacing.MD, padx=Spacing.MD)
        ModernButton(buttons_frame, text="Guardar Cambios", icon="💾", command=self._save_apartment).pack(side="right")
        ModernButton(buttons_frame, text="Cancelar", style="secondary", command=self.on_back).pack(side="right", padx=(0, Spacing.SM))

        # Contenedor principal sin scroll
        container = tk.Frame(self, **theme_manager.get_style("frame"))
        container.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)

        form_container = tk.Frame(container, **theme_manager.get_style("card"))
        form_container.pack(fill="x", expand=True)

        self._create_form_fields(form_container)

    def _create_form_fields(self, parent):
        frame = tk.Frame(parent, **theme_manager.get_style("card_content"))
        frame.pack(fill='both', expand=True, padx=Spacing.LG, pady=Spacing.LG)
        
        def create_label(parent, text):
            style = theme_manager.get_style("label_body")
            style.pop("anchor", None)
            return tk.Label(parent, text=text, **style, width=20, anchor="w")

        # --- Selector de Edificio (solo para nuevos apartamentos) ---
        if not self.is_edit_mode:
            building_row_frame = tk.Frame(frame, **theme_manager.get_style("card_content"))
            building_row_frame.pack(fill="x", pady=2)
            
            create_label(building_row_frame, "Edificio*:").pack(side="left")
            
            self.building_var = tk.StringVar()
            self.building_selector = ttk.Combobox(building_row_frame, textvariable=self.building_var, state="readonly", width=38, font=("Segoe UI", 10))
            
            self.buildings = building_service.get_all_buildings()
            if not self.buildings:
                messagebox.showwarning("Sin Edificios", "No hay edificios registrados. Por favor, cree uno desde 'Gestionar Edificio' antes de añadir apartamentos.")
                self.on_back()
                return

            building_names = [b.get('name', f"Edificio ID {b.get('id', 'N/A')}") for b in self.buildings]
            self.building_selector['values'] = building_names
            if building_names:
                self.building_selector.current(0)
            
            self.building_selector.pack(side="left", fill="x", expand=True)

        # --- Tipo de Unidad (nuevo)---
        unit_type_frame = tk.Frame(frame, **theme_manager.get_style("card_content"))
        unit_type_frame.pack(fill="x", pady=2)
        create_label(unit_type_frame, "Tipo de Unidad*:").pack(side="left")

        self.unit_type_var = tk.StringVar()
        unit_types = ["Apartamento Estándar", "Local Comercial", "Penthouse", "Depósito", "Otro"]
        self.unit_type_combo = ttk.Combobox(unit_type_frame, textvariable=self.unit_type_var, values=unit_types, state="readonly", width=38, font=("Segoe UI", 10))
        self.unit_type_combo.pack(side="left", fill="x", expand=True)
        self.unit_type_combo.bind("<<ComboboxSelected>>", self._on_unit_type_selected)

        # --- Campo condicional para "Otro" ---
        # Este frame se insertará dinámicamente debajo del selector de tipo de unidad.
        self.other_type_frame = tk.Frame(frame, **theme_manager.get_style("card_content"))
        create_label(self.other_type_frame, "Especificar Otro*:").pack(side="left")
        self.other_type_var = tk.StringVar()
        self.other_type_entry = ttk.Entry(self.other_type_frame, textvariable=self.other_type_var, width=40, font=("Segoe UI", 10))
        self.other_type_entry.pack(side="left", fill="x", expand=True)
        
        # --- Guardar referencia a los widgets para reordenarlos ---
        self.unit_type_row_frame = unit_type_frame

        # --- Set initial values for unit type in edit mode ---
        if self.is_edit_mode:
            saved_unit_type = self.apartment_data.get('unit_type', '')
            if saved_unit_type in unit_types:
                self.unit_type_var.set(saved_unit_type)
            elif saved_unit_type: # If it's a custom type
                self.unit_type_var.set("Otro")
                self.other_type_var.set(saved_unit_type)

        fields = [
            ("Número/Letra*:", "number", "entry"), ("Piso*:", "floor", "entry"),
            ("Habitaciones*:", "rooms", "entry"), ("Baños*:", "bathrooms", "entry"),
            ("Área (m²)*:", "area", "entry"), ("Arriendo Base ($)*:", "base_rent", "entry"),
            ("Estado*:", "status", "combo"), ("Descripción:", "description", "text")
        ]
        
        self.form_vars = {}
        for key in [f[1] for f in fields]:
            self.form_vars[key] = tk.StringVar(value=self.apartment_data.get(key, ""))
        
        if not self.is_edit_mode:
            self.form_vars["status"].set("Disponible")

        self.field_rows = [] # Para mantener el orden de los campos
        for i, (label_text, key, widget_type) in enumerate(fields):
            row_frame = tk.Frame(frame, **theme_manager.get_style("card_content"))
            row_frame.pack(fill="x", pady=2)
            create_label(row_frame, label_text).pack(side="left")
            if widget_type == "entry":
                widget = ttk.Entry(row_frame, textvariable=self.form_vars[key], width=40, font=("Segoe UI", 10))
            elif widget_type == "combo":
                widget = ttk.Combobox(row_frame, textvariable=self.form_vars[key], values=["Disponible", "Ocupado", "Mantenimiento"], state="readonly", width=38, font=("Segoe UI", 10))
            elif widget_type == "text":
                widget = tk.Text(row_frame, height=4, width=40, font=("Segoe UI", 10), relief="solid", bd=1)
                widget.insert("1.0", self.form_vars[key].get())
                self.description_text_widget = widget
            
            widget.pack(side="left", fill="x", expand=True)
            self.field_rows.append(row_frame)

        self._on_unit_type_selected() # Ensure correct initial state for "Otro" field

    def _on_unit_type_selected(self, event=None):
        """Muestra u oculta el campo para 'Otro' tipo de unidad."""
        if self.unit_type_var.get() == "Otro":
            self.other_type_frame.pack(after=self.unit_type_row_frame, fill="x", pady=(0, 2))
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

        required_fields = ["number", "floor", "rooms", "bathrooms", "area", "base_rent", "status"]
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
