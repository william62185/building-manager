"""
Vista para desactivar inquilinos
Permite dar de baja a un inquilino registrando información de salida
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Dict, Any, Optional
from datetime import datetime
import re

from ..components.theme_manager import theme_manager, Spacing
from ..components.icons import Icons
from ..components.modern_widgets import ModernButton, ModernCard, ModernSeparator
from app.services.tenant_service import tenant_service


class DeactivateTenantView(tk.Frame):
    """Vista para desactivar inquilinos"""
    
    def __init__(self, parent, on_back: Callable = None, on_success: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        
        self.on_back = on_back
        self.on_success = on_success
        self.selected_tenant = None
        self.form_fields = {}
        self.validation_errors = {}
        
        # Crear layout
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout principal"""
        # Header con navegación
        self._create_header()
        
        # Separador
        ModernSeparator(self)
        
        # Contenido principal
        self._create_content()
    
    def _create_header(self):
        """Crea el header con título y navegación"""
        header_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", pady=(0, Spacing.LG))
        
        # Título
        title_label = tk.Label(
            header_frame,
            text="Desactivar Inquilino",
            **theme_manager.get_style("label_title")
        )
        title_label.configure(font=("Segoe UI", 20, "bold"))
        title_label.pack(side="left")
        
        # Botón volver
        btn_back = ModernButton(
            header_frame,
            text="Volver",
            icon=Icons.ARROW_LEFT,
            style="secondary",
            command=self._on_back_clicked
        )
        btn_back.pack(side="right")
    
    def _create_content(self):
        """Crea el contenido principal con scroll"""
        # Crear Canvas para scroll
        self.canvas = tk.Canvas(self, **theme_manager.get_style("frame"), highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame scrollable interno
        self.scrollable_frame = tk.Frame(self.canvas, **theme_manager.get_style("frame"))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configurar scroll
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Habilitar scroll con rueda del mouse
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Paso 1: Selección de inquilino
        self._create_tenant_selection_section(self.scrollable_frame)
        
        # Separador
        ModernSeparator(self.scrollable_frame)
        
        # Paso 2: Formulario de desactivación (inicialmente oculto)
        self.form_section = tk.Frame(self.scrollable_frame, **theme_manager.get_style("frame"))
        self.form_section.pack(fill="x", expand=False, pady=(Spacing.LG, 0))
        
        self._create_deactivation_form()
        
        # Inicialmente ocultar el formulario
        self.form_section.pack_forget()
        
        # Botones de acción fijos en la parte inferior (fuera del scroll)
        self._create_fixed_action_buttons()
    
    def _on_frame_configure(self, event):
        """Configura el scroll cuando cambia el tamaño del frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Ajusta el tamaño del canvas"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _on_mousewheel(self, event):
        """Maneja el scroll con rueda del mouse"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _create_tenant_selection_section(self, parent):
        """Crea la sección de selección de inquilino"""
        # Título de sección
        section_title = tk.Label(
            parent,
            text="1. Seleccionar Inquilino a Desactivar",
            **theme_manager.get_style("label_subtitle")
        )
        section_title.configure(font=("Segoe UI", 14, "bold"))
        section_title.pack(anchor="w", pady=(0, Spacing.MD))
        
        # Frame de selección
        selection_frame = tk.Frame(parent, **theme_manager.get_style("frame"))
        selection_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        # Label
        tk.Label(
            selection_frame,
            text="Inquilino:",
            **theme_manager.get_style("label_body")
        ).pack(side="left", padx=(0, Spacing.SM))
        
        # Combobox de inquilinos activos
        self.tenant_combo = ttk.Combobox(
            selection_frame,
            state="readonly",
            width=60,
            font=("Segoe UI", 10)
        )
        self.tenant_combo.pack(side="left", padx=(0, Spacing.SM))
        self.tenant_combo.bind('<<ComboboxSelected>>', self._on_tenant_selected)
        
        # Cargar inquilinos activos
        self._load_active_tenants()
    
    def _create_deactivation_form(self):
        """Crea el formulario de desactivación"""
        # Título del formulario
        form_title = tk.Label(
            self.form_section,
            text="2. Información de Salida",
            **theme_manager.get_style("label_subtitle")
        )
        form_title.configure(font=("Segoe UI", 14, "bold"))
        form_title.pack(anchor="w", pady=(0, Spacing.MD))
        
        # Grid de 2 columnas
        form_grid = tk.Frame(self.form_section, **theme_manager.get_style("frame"))
        form_grid.pack(fill="x", pady=(0, Spacing.LG))
        
        # Columna izquierda
        left_column = tk.Frame(form_grid, **theme_manager.get_style("frame"))
        left_column.pack(side="left", fill="both", expand=True, padx=(0, Spacing.LG))
        
        # Columna derecha
        right_column = tk.Frame(form_grid, **theme_manager.get_style("frame"))
        right_column.pack(side="right", fill="both", expand=True)
        
        # Campos columna izquierda
        self._create_field(left_column, "Fecha de Salida *", "fecha_salida", "entry")
        self._create_field(left_column, "Estado Final de Pagos *", "estado_final_pago", "combobox", 
                          ["al_dia", "moroso"])
        self._create_field(left_column, "Motivo de Salida *", "motivo_salida", "combobox",
                          ["Fin de contrato", "Incumplimiento", "Voluntario", "Desalojo", "Otro"])
        
        # Campos columna derecha (condicionales)
        self.mora_frame = tk.Frame(right_column, **theme_manager.get_style("frame"))
        self.mora_frame.pack(fill="x", pady=(0, Spacing.SM))
        
        self._create_field(self.mora_frame, "Días en Mora", "dias_mora", "entry")
        self._create_field(self.mora_frame, "Valor Adeudado", "valor_mora", "entry")
        
        self._create_field(right_column, "Depósito Devuelto", "deposito_devuelto", "entry")
        
        # Campo de notas (ancho completo)
        notes_frame = tk.Frame(self.form_section, **theme_manager.get_style("frame"))
        notes_frame.pack(fill="x", pady=(Spacing.MD, 0))
        
        tk.Label(
            notes_frame,
            text="Notas Adicionales:",
            **theme_manager.get_style("label_body")
        ).pack(anchor="w")
        
        self.notes_text = tk.Text(
            notes_frame,
            height=4,
            width=80,
            **theme_manager.get_style("entry")
        )
        self.notes_text.pack(fill="x", pady=(Spacing.XS, 0))
        
        # Inicialmente ocultar campos de mora
        self.mora_frame.pack_forget()
    
    def _create_field(self, parent, label_text: str, field_name: str, field_type: str, values=None):
        """Crea un campo del formulario"""
        field_frame = tk.Frame(parent, **theme_manager.get_style("frame"))
        field_frame.pack(fill="x", pady=(0, Spacing.SM))
        
        # Label
        label = tk.Label(
            field_frame,
            text=label_text,
            **theme_manager.get_style("label_body")
        )
        label.pack(anchor="w")
        
        # Campo
        if field_type == "combobox":
            field = ttk.Combobox(
                field_frame,
                values=values or [],
                state="readonly",
                font=("Segoe UI", 10)
            )
            if field_name == "estado_final_pago":
                field.bind('<<ComboboxSelected>>', self._on_payment_status_changed)
        else:
            field = tk.Entry(
                field_frame,
                **theme_manager.get_style("entry")
            )
            
            # Placeholder para fecha
            if field_name == "fecha_salida":
                field.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        field.pack(fill="x", pady=(Spacing.XS, 0))
        self.form_fields[field_name] = field
    
    def _create_fixed_action_buttons(self):
        """Crea los botones de acción fijos en la parte inferior"""
        self.buttons_container = tk.Frame(self, **theme_manager.get_style("frame"))
        self.buttons_container.pack(side="bottom", fill="x", pady=(Spacing.SM, 0))
        
        # Separador
        ModernSeparator(self.buttons_container)
        
        # Frame para los botones
        buttons_frame = tk.Frame(self.buttons_container, **theme_manager.get_style("frame"))
        buttons_frame.pack(pady=(Spacing.SM, Spacing.SM))
        
        # Botón cancelar
        self.btn_cancel = ModernButton(
            buttons_frame,
            text="Cancelar",
            icon=Icons.CANCEL,
            style="secondary",
            command=self._on_back_clicked
        )
        self.btn_cancel.pack(side="right", padx=(Spacing.SM, 0))
        
        # Botón desactivar (inicialmente oculto)
        self.btn_deactivate = ModernButton(
            buttons_frame,
            text="Desactivar Inquilino",
            icon="⚠️",
            style="danger",
            command=self._deactivate_tenant
        )
        self.btn_deactivate.pack(side="right")
        
        # Inicialmente ocultar el botón de desactivar hasta que se seleccione un inquilino
        self.btn_deactivate.pack_forget()
    
    def _load_active_tenants(self):
        """Carga los inquilinos activos en el combobox"""
        active_tenants = [t for t in tenant_service.get_all_tenants() 
                         if t.get("estado_pago") in ["al_dia", "moroso"]]
        
        tenant_options = [f"{t.get('nombre', '')} - Apt. {t.get('apartamento', '')}" 
                         for t in active_tenants]
        
        self.tenant_combo['values'] = tenant_options
        self.active_tenants = active_tenants
        
        if not active_tenants:
            self.tenant_combo['values'] = ["No hay inquilinos activos"]
            self.tenant_combo.set("No hay inquilinos activos")
    
    def _on_tenant_selected(self, event=None):
        """Maneja la selección de inquilino"""
        selection = self.tenant_combo.get()
        if selection and selection != "No hay inquilinos activos":
            # Encontrar el inquilino seleccionado
            selected_index = self.tenant_combo.current()
            if 0 <= selected_index < len(self.active_tenants):
                self.selected_tenant = self.active_tenants[selected_index]
                
                # Mostrar el formulario
                self.form_section.pack(fill="x", expand=False, pady=(Spacing.LG, 0))
                
                # Mostrar el botón de desactivar
                self.btn_deactivate.pack(side="right")
                
                # Pre-llenar algunos campos basado en el estado actual
                current_status = self.selected_tenant.get("estado_pago", "al_dia")
                if "estado_final_pago" in self.form_fields:
                    self.form_fields["estado_final_pago"].set(current_status)
                    self._on_payment_status_changed()
                
                # Actualizar región de scroll
                self._on_frame_configure(None)
    
    def _on_payment_status_changed(self, event=None):
        """Maneja el cambio en el estado final de pagos"""
        if "estado_final_pago" not in self.form_fields:
            return
            
        status = self.form_fields["estado_final_pago"].get()
        
        if status == "moroso":
            # Mostrar campos de mora
            self.mora_frame.pack(fill="x", pady=(0, Spacing.SM))
        else:
            # Ocultar campos de mora
            self.mora_frame.pack_forget()
            # Limpiar campos de mora
            if "dias_mora" in self.form_fields:
                self.form_fields["dias_mora"].delete(0, tk.END)
            if "valor_mora" in self.form_fields:
                self.form_fields["valor_mora"].delete(0, tk.END)
    
    def _validate_form(self) -> bool:
        """Valida el formulario"""
        self.validation_errors = {}
        
        if not self.selected_tenant:
            messagebox.showerror("Error", "Debe seleccionar un inquilino")
            return False
        
        # Campos requeridos
        required_fields = {
            'fecha_salida': 'Fecha de salida',
            'estado_final_pago': 'Estado final de pagos',
            'motivo_salida': 'Motivo de salida'
        }
        
        for field, label in required_fields.items():
            if field not in self.form_fields:
                continue
                
            value = self.form_fields[field].get().strip()
            if not value:
                self.validation_errors[field] = f"{label} es requerido"
        
        # Validar fecha
        if 'fecha_salida' in self.form_fields and 'fecha_salida' not in self.validation_errors:
            date_str = self.form_fields['fecha_salida'].get().strip()
            if not self._validate_date(date_str):
                self.validation_errors['fecha_salida'] = "Formato de fecha inválido (DD/MM/AAAA)"
        
        # Validar campos numéricos si están presentes
        if self.form_fields.get("estado_final_pago", ttk.Combobox()).get() == "moroso":
            if "dias_mora" in self.form_fields:
                dias_value = self.form_fields["dias_mora"].get().strip()
                if dias_value:
                    try:
                        int(dias_value)
                    except ValueError:
                        self.validation_errors['dias_mora'] = "Días en mora debe ser un número"
            
            if "valor_mora" in self.form_fields:
                valor_value = self.form_fields["valor_mora"].get().strip()
                if valor_value:
                    try:
                        float(valor_value.replace(',', ''))
                    except ValueError:
                        self.validation_errors['valor_mora'] = "Valor adeudado debe ser numérico"
        
        if "deposito_devuelto" in self.form_fields:
            deposito_value = self.form_fields["deposito_devuelto"].get().strip()
            if deposito_value:
                try:
                    float(deposito_value.replace(',', ''))
                except ValueError:
                    self.validation_errors['deposito_devuelto'] = "Depósito devuelto debe ser numérico"
        
        if self.validation_errors:
            error_msg = "Por favor corrija los siguientes errores:\n\n"
            for field, error in self.validation_errors.items():
                error_msg += f"• {error}\n"
            messagebox.showerror("Errores de validación", error_msg)
            return False
        
        return True
    
    def _validate_date(self, date_str: str) -> bool:
        """Valida formato de fecha DD/MM/AAAA"""
        try:
            datetime.strptime(date_str.strip(), "%d/%m/%Y")
            return True
        except ValueError:
            return False
    
    def _deactivate_tenant(self):
        """Desactiva el inquilino"""
        if not self._validate_form():
            return
        
        # Confirmar acción
        tenant_name = self.selected_tenant.get("nombre", "")
        apartment = self.selected_tenant.get("apartamento", "")
        
        confirm = messagebox.askyesno(
            "Confirmar Desactivación",
            f"¿Está seguro de desactivar al inquilino?\n\n"
            f"Nombre: {tenant_name}\n"
            f"Apartamento: {apartment}\n\n"
            f"Esta acción no se puede deshacer."
        )
        
        if not confirm:
            return
        
        try:
            # Recopilar datos del formulario
            deactivation_data = self._collect_form_data()
            
            # Actualizar inquilino
            tenant_id = self.selected_tenant.get("id")
            updated_data = self.selected_tenant.copy()
            updated_data.update(deactivation_data)
            updated_data["estado_pago"] = "inactivo"
            updated_data["updated_at"] = datetime.now().isoformat()
            
            result = tenant_service.update_tenant(tenant_id, updated_data)
            
            if result:
                messagebox.showinfo(
                    "Éxito",
                    f"Inquilino desactivado correctamente.\n\n"
                    f"Nombre: {tenant_name}\n"
                    f"Apartamento: {apartment}\n"
                    f"Fecha de salida: {deactivation_data['fecha_salida']}"
                )
                
                # Notificar éxito
                if self.on_success:
                    self.on_success()
            else:
                messagebox.showerror("Error", "No se pudo desactivar el inquilino")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al desactivar inquilino: {str(e)}")
    
    def _collect_form_data(self) -> Dict[str, Any]:
        """Recopila los datos del formulario"""
        data = {}
        
        for field_name, field_widget in self.form_fields.items():
            if hasattr(field_widget, 'get'):
                value = field_widget.get()
                if isinstance(value, str):
                    value = value.strip()
                data[field_name] = value
        
        # Agregar notas
        data['notas_salida'] = self.notes_text.get("1.0", tk.END).strip()
        
        # Convertir valores numéricos
        for field in ['dias_mora', 'valor_mora', 'deposito_devuelto']:
            if field in data and data[field]:
                try:
                    if field == 'dias_mora':
                        data[field] = int(data[field])
                    else:
                        data[field] = float(data[field].replace(',', ''))
                except ValueError:
                    data[field] = 0
        
        return data
    
    def _on_back_clicked(self):
        """Maneja el clic en volver"""
        if self.on_back:
            self.on_back() 