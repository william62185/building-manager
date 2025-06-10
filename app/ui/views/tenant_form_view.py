"""
Formulario profesional para gestión de inquilinos
Incluye validaciones, diseño moderno y manejo de estados
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Optional, Callable
import re
from datetime import datetime
from ..components.theme_manager import theme_manager, Spacing
from ..components.icons import Icons
from ..components.modern_widgets import (
    ModernButton, ModernCard, ModernEntry, 
    ModernBadge, ModernSeparator
)
from app.services.tenant_service import tenant_service

class TenantFormView(tk.Frame):
    """Formulario profesional para inquilinos"""
    
    def __init__(self, parent, on_back: Callable = None, tenant_data: Dict[str, Any] = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        
        self.on_back = on_back
        self.tenant_data = tenant_data or {}
        self.is_edit_mode = bool(tenant_data)
        self.validation_errors = {}
        
        # Variables para los campos
        self._init_form_variables()
        
        # Crear layout
        self._create_layout()
        
        # Cargar datos si es modo edición
        if self.is_edit_mode:
            self._load_tenant_data()
    
    def _init_form_variables(self):
        """Inicializa las variables del formulario"""
        self.form_fields = {}
    
    def _clear_placeholder(self, event, placeholder_text):
        """Limpia el placeholder cuando se enfoca el campo"""
        if event.widget.get() == placeholder_text:
            event.widget.delete(0, tk.END)
            event.widget.config(fg=theme_manager.themes[theme_manager.current_theme]["text_primary"])
    
    def _restore_placeholder(self, event, placeholder_text):
        """Restaura el placeholder si el campo está vacío"""
        if not event.widget.get():
            event.widget.insert(0, placeholder_text)
            event.widget.config(fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"])
    
    def _create_inline_field(self, parent, label_text, field_name, placeholder_text="", field_type="entry", values=None, width=20):
        """Crea un campo inline con label al lado izquierdo"""
        row_frame = tk.Frame(parent, **theme_manager.get_style("frame"))
        row_frame.pack(fill="x", pady=(0, 2))
        
        # Label
        label_style = theme_manager.get_style("label_body").copy()
        label_style.update({
            "width": width,
            "anchor": "w"
        })
        label = tk.Label(
            row_frame,
            text=label_text,
            **label_style
        )
        label.pack(side="left", padx=(0, Spacing.SM))
        
        # Campo
        if field_type == "combobox":
            field = ttk.Combobox(
                row_frame,
                values=values or [],
                state="readonly"
            )
            if values:
                field.set(values[0])
        else:
            field = tk.Entry(row_frame, **theme_manager.get_style("entry"))
        
        field.pack(side="left", fill="x", expand=True)
        self.form_fields[field_name] = field
        
        return row_frame
        
    def _create_layout(self):
        """Crea el layout principal del formulario"""
        # Header con navegación - sin padding
        self._create_header()
        
        # Formulario principal directamente - sin scroll container
        self._create_form_content_direct()
        
        # Botones de acción fijos en la parte inferior
        self._create_action_buttons(self)
    
    def _create_header(self):
        """Crea el header con título y navegación"""
        header_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", pady=2)  # Padding mínimo
        
        # Título
        title_text = "Editar Inquilino" if self.is_edit_mode else "Nuevo Inquilino"
        title_label = tk.Label(
            header_frame,
            text=title_text,
            **theme_manager.get_style("label_title")
        )
        title_label.configure(font=("Segoe UI", 14, "bold"))
        title_label.pack(side="left", pady=0)
        
        # Botón volver - movido a la derecha
        btn_back = tk.Button(
            header_frame,
            text="← Volver",
            font=("Segoe UI", 10),
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            bd=1,
            relief="solid",
            width=10,
            height=1,
            padx=4,
            pady=2,
            command=self._on_back_clicked
        )
        btn_back.pack(side="right")
    
    def _create_form_content_direct(self):
        """Crea el contenido del formulario directamente sin scroll"""
        # Contenedor principal con padding ultra-mínimo
        main_container = tk.Frame(self, **theme_manager.get_style("frame"))
        main_container.pack(fill="both", expand=True, padx=2, pady=0)  # Padding horizontal ultra-reducido
        
        # Todas las secciones en una sola columna - completamente compacto
        self._create_personal_info_section(main_container)
        self._create_housing_info_section(main_container)
        self._create_emergency_contact_section(main_container)
        self._create_documents_section(main_container)
    
    def _create_separator(self, parent):
        """Crea un separador visual entre secciones"""
        separator_frame = tk.Frame(parent, **theme_manager.get_style("frame"))
        separator_frame.pack(fill="x", pady=2)  # Reducido considerablemente
        
        line = tk.Frame(
            separator_frame,
            height=1,
            bg=theme_manager.themes[theme_manager.current_theme]["border_light"]
        )
        line.pack(fill="x")
    
    def _create_personal_info_section(self, parent):
        """Crea la sección de información personal"""
        # Título de sección más pequeño
        title_label = tk.Label(
            parent,
            text=f"{Icons.TENANT_PROFILE} Información Personal",
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
            font=("Segoe UI", 12, "bold"),  # Fuente más pequeña
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 1))
        
        # Nombre completo - layout inline
        self._create_inline_field(parent, "Nombre Completo *", "nombre", "", width=18)
        
        # Fila de documentos
        doc_row = tk.Frame(parent, **theme_manager.get_style("frame"))
        doc_row.pack(fill="x", pady=(0, 2))
        
        # Tipo de documento (50% del ancho)
        doc_type_frame = tk.Frame(doc_row, **theme_manager.get_style("frame"))
        doc_type_frame.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
        
        type_label = tk.Label(
            doc_type_frame,
            text="Tipo de Documento *",
            width=18,
            anchor="w",
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        type_label.pack(side="left", padx=(0, Spacing.SM))
        
        self.form_fields['tipo_documento'] = ttk.Combobox(
            doc_type_frame,
            values=["Cédula de Ciudadanía", "Cédula de Extranjería", "Pasaporte"],
            state="readonly"
        )
        self.form_fields['tipo_documento'].pack(side="left", fill="x", expand=True)
        self.form_fields['tipo_documento'].set("Cédula de Ciudadanía")
        
        # Número de documento (50% del ancho)
        doc_num_frame = tk.Frame(doc_row, **theme_manager.get_style("frame"))
        doc_num_frame.pack(side="right", fill="x", expand=True, padx=(Spacing.SM, 0))
        
        num_label = tk.Label(
            doc_num_frame,
            text="Número de Documento *",
            width=18,
            anchor="w",
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        num_label.pack(side="left", padx=(0, Spacing.SM))
        
        self.form_fields['numero_documento'] = tk.Entry(doc_num_frame, **theme_manager.get_style("entry"))
        self.form_fields['numero_documento'].pack(side="left", fill="x", expand=True)
        
        # Fila de contacto
        contact_row = tk.Frame(parent, **theme_manager.get_style("frame"))
        contact_row.pack(fill="x", pady=(0, 2))
        
        # Teléfono (50% del ancho)
        phone_frame = tk.Frame(contact_row, **theme_manager.get_style("frame"))
        phone_frame.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
        
        phone_label = tk.Label(
            phone_frame,
            text="Teléfono *",
            width=18, anchor="w", bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"], fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        phone_label.pack(side="left", padx=(0, Spacing.SM))
        
        self.form_fields['telefono'] = tk.Entry(phone_frame, **theme_manager.get_style("entry"))
        self.form_fields['telefono'].pack(side="left", fill="x", expand=True)
        
        # Email (50% del ancho)
        email_frame = tk.Frame(contact_row, **theme_manager.get_style("frame"))
        email_frame.pack(side="right", fill="x", expand=True, padx=(Spacing.SM, 0))
        
        email_label = tk.Label(
            email_frame,
            text="Email",
            width=18, anchor="w", bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"], fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        email_label.pack(side="left", padx=(0, Spacing.SM))
        
        self.form_fields['email'] = tk.Entry(email_frame, **theme_manager.get_style("entry"))
        self.form_fields['email'].pack(side="left", fill="x", expand=True)
    
    def _create_housing_info_section(self, parent):
        """Crea la sección de información de vivienda"""
        # Título de sección más pequeño
        title_label = tk.Label(
            parent,
            text=f"{Icons.TENANT_ADDRESS} Información de Vivienda",
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
            font=("Segoe UI", 12, "bold"),  # Fuente más pequeña
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 1))
        
        # Fila 1: Apartamento y valor arriendo - layout inline
        apt_row = tk.Frame(parent, **theme_manager.get_style("frame"))
        apt_row.pack(fill="x", pady=(0, 2))
        
        # Apartamento (50% del ancho)
        apt_frame = tk.Frame(apt_row, **theme_manager.get_style("frame"))
        apt_frame.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
        
        apt_label = tk.Label(
            apt_frame,
            text="Número de Apartamento *",
            width=18, anchor="w", bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"], fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        apt_label.pack(side="left", padx=(0, Spacing.SM))
        
        self.form_fields['apartamento'] = tk.Entry(apt_frame, **theme_manager.get_style("entry"))
        self.form_fields['apartamento'].pack(side="left", fill="x", expand=True)
        
        # Valor arriendo (50% del ancho)
        rent_frame = tk.Frame(apt_row, **theme_manager.get_style("frame"))
        rent_frame.pack(side="right", fill="x", expand=True, padx=(Spacing.SM, 0))
        
        rent_label = tk.Label(
            rent_frame,
            text="Valor Arriendo *",
            width=18, anchor="w", bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"], fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        rent_label.pack(side="left", padx=(0, Spacing.SM))
        
        self.form_fields['valor_arriendo'] = tk.Entry(rent_frame, **theme_manager.get_style("entry"))
        self.form_fields['valor_arriendo'].pack(side="left", fill="x", expand=True)
        
        # Fila 2: Fechas - layout inline
        dates_row = tk.Frame(parent, **theme_manager.get_style("frame"))
        dates_row.pack(fill="x", pady=(0, 2))
        
        # Fecha de ingreso (50% del ancho)
        start_frame = tk.Frame(dates_row, **theme_manager.get_style("frame"))
        start_frame.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
        
        start_label = tk.Label(
            start_frame,
            text="Fecha de Ingreso *",
            width=18, anchor="w", bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"], fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        start_label.pack(side="left", padx=(0, Spacing.SM))
        
        self.form_fields['fecha_ingreso'] = tk.Entry(start_frame, **theme_manager.get_style("entry"))
        self.form_fields['fecha_ingreso'].pack(side="left", fill="x", expand=True)
        
        # Fecha fin contrato (50% del ancho)
        end_frame = tk.Frame(dates_row, **theme_manager.get_style("frame"))
        end_frame.pack(side="right", fill="x", expand=True, padx=(Spacing.SM, 0))
        
        end_label = tk.Label(
            end_frame,
            text="Fecha Fin Contrato",
            width=18, anchor="w", bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"], fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        end_label.pack(side="left", padx=(0, Spacing.SM))
        
        self.form_fields['fecha_fin_contrato'] = tk.Entry(end_frame, **theme_manager.get_style("entry"))
        self.form_fields['fecha_fin_contrato'].pack(side="left", fill="x", expand=True)
        
        # Fila 3: Estado y depósito - layout inline
        status_row = tk.Frame(parent, **theme_manager.get_style("frame"))
        status_row.pack(fill="x", pady=(0, 2))
        
        # Estado de pago (50% del ancho)
        status_frame = tk.Frame(status_row, **theme_manager.get_style("frame"))
        status_frame.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
        
        status_label = tk.Label(
            status_frame,
            text="Estado de Pago *",
            width=18, anchor="w", bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"], fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        status_label.pack(side="left", padx=(0, Spacing.SM))
        
        self.form_fields['estado_pago'] = ttk.Combobox(
            status_frame,
            values=["al_dia", "pendiente", "moroso"],
            state="readonly"
        )
        self.form_fields['estado_pago'].pack(side="left", fill="x", expand=True)
        self.form_fields['estado_pago'].set("al_dia")
        
        # Depósito (50% del ancho)
        deposit_frame = tk.Frame(status_row, **theme_manager.get_style("frame"))
        deposit_frame.pack(side="right", fill="x", expand=True, padx=(Spacing.SM, 0))
        
        deposit_label = tk.Label(
            deposit_frame,
            text="Depósito",
            width=18, anchor="w", bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"], fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        deposit_label.pack(side="left", padx=(0, Spacing.SM))
        
        self.form_fields['deposito'] = tk.Entry(deposit_frame, **theme_manager.get_style("entry"))
        self.form_fields['deposito'].pack(side="left", fill="x", expand=True)
    
    def _create_emergency_contact_section(self, parent):
        """Crea la sección de contacto de emergencia - layout inline compacto"""
        # Título de sección más pequeño
        title_label = tk.Label(
            parent,
            text=f"{Icons.EMERGENCY_CONTACT} Contacto de Emergencia",
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
            font=("Segoe UI", 12, "bold"),  # Fuente más pequeña
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 1))
        
        # Fila 1: Nombre y parentesco - layout inline
        contact_row = tk.Frame(parent, **theme_manager.get_style("frame"))
        contact_row.pack(fill="x", pady=(0, 2))
        
        # Nombre contacto (50% del ancho)
        name_frame = tk.Frame(contact_row, **theme_manager.get_style("frame"))
        name_frame.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
        
        name_label = tk.Label(
            name_frame,
            text="Nombre Completo",
            width=18, anchor="w", bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"], fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        name_label.pack(side="left", padx=(0, Spacing.SM))
        
        self.form_fields['contacto_emergencia_nombre'] = tk.Entry(name_frame, **theme_manager.get_style("entry"))
        self.form_fields['contacto_emergencia_nombre'].pack(side="left", fill="x", expand=True)
        
        # Parentesco (50% del ancho)
        relation_frame = tk.Frame(contact_row, **theme_manager.get_style("frame"))
        relation_frame.pack(side="right", fill="x", expand=True, padx=(Spacing.SM, 0))
        
        relation_label = tk.Label(
            relation_frame,
            text="Parentesco",
            width=18, anchor="w", bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"], fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        relation_label.pack(side="left", padx=(0, Spacing.SM))
        
        self.form_fields['contacto_emergencia_parentesco'] = ttk.Combobox(
            relation_frame,
            values=["Padre", "Madre", "Hermano/a", "Hijo/a", "Cónyuge", "Amigo/a", "Otro"],
            state="readonly"
        )
        self.form_fields['contacto_emergencia_parentesco'].pack(side="left", fill="x", expand=True)
        
        # Teléfono contacto - layout inline (ancho completo)
        self._create_inline_field(parent, "Teléfono", "contacto_emergencia_telefono", "", width=18)
    
    def _create_documents_section(self, parent):
        """Crea la sección de documentos - diseño horizontal compacto"""
        # Título de sección más pequeño
        title_label = tk.Label(
            parent,
            text=f"{Icons.TENANT_DOCUMENTS} Documentos",
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"],
            font=("Segoe UI", 12, "bold"),  # Fuente más pequeña
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 1))
        
        # Contenedor horizontal para ambos documentos
        docs_row = tk.Frame(parent, **theme_manager.get_style("frame"))
        docs_row.pack(fill="x")
        
        # Documento de identidad (lado izquierdo)
        doc_id_frame = tk.Frame(docs_row, **theme_manager.get_style("frame"))
        doc_id_frame.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
        
        doc_id_label = tk.Label(
            doc_id_frame,
            text="Documento de Identidad",
            **theme_manager.get_style("label_body")
        )
        doc_id_label.pack(anchor="w", pady=(0, 2))
        
        doc_id_buttons = tk.Frame(doc_id_frame, **theme_manager.get_style("frame"))
        doc_id_buttons.pack(fill="x")
        
        self.btn_upload_id = tk.Button(
            doc_id_buttons,
            text=f"{Icons.UPLOAD} Seleccionar",
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            width=10,
            height=1,
            padx=4,
            pady=2,
            cursor="hand2",
            command=lambda: self._upload_document("id")
        )
        self.btn_upload_id.pack(side="left", padx=(0, Spacing.XS))
        
        self.id_file_label = tk.Label(
            doc_id_buttons,
            text="No seleccionado",
            **theme_manager.get_style("label_body")
        )
        self.id_file_label.pack(side="left")
        
        # Contrato (lado derecho)
        contract_frame = tk.Frame(docs_row, **theme_manager.get_style("frame"))
        contract_frame.pack(side="right", fill="x", expand=True, padx=(Spacing.SM, 0))
        
        contract_label = tk.Label(
            contract_frame,
            text="Contrato de Arrendamiento",
            **theme_manager.get_style("label_body")
        )
        contract_label.pack(anchor="w", pady=(0, 2))
        
        contract_buttons = tk.Frame(contract_frame, **theme_manager.get_style("frame"))
        contract_buttons.pack(fill="x")
        
        self.btn_upload_contract = tk.Button(
            contract_buttons,
            text=f"{Icons.UPLOAD} Seleccionar",
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            width=10,
            height=1,
            padx=4,
            pady=2,
            cursor="hand2",
            command=lambda: self._upload_document("contract")
        )
        self.btn_upload_contract.pack(side="left", padx=(0, Spacing.XS))
        
        self.contract_file_label = tk.Label(
            contract_buttons,
            text="No seleccionado",
            **theme_manager.get_style("label_body")
        )
        self.contract_file_label.pack(side="left")
        
        # Variables para archivos
        self.selected_files = {
            "id": None,
            "contract": None
        }
    
    def _create_action_buttons(self, parent):
        """Crea los botones de acción del formulario"""
        actions_frame = tk.Frame(parent, **theme_manager.get_style("frame"))
        actions_frame.pack(fill="x", side="bottom", pady=(2, 0))
        
        # Separador
        ModernSeparator(actions_frame)
        
        # Botones
        buttons_frame = tk.Frame(actions_frame, **theme_manager.get_style("frame"))
        buttons_frame.pack(pady=(2, 0))
        
        # Botón cancelar
        btn_cancel = tk.Button(
            buttons_frame,
            text=f"{Icons.CANCEL} Cancelar",
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            width=10,
            height=1,
            padx=4,
            pady=2,
            cursor="hand2",
            command=self._on_back_clicked
        )
        btn_cancel.pack(side="right", padx=(Spacing.SM, 0))
        
        # Botón guardar
        save_text = "Actualizar" if self.is_edit_mode else "Guardar"
        btn_save = tk.Button(
            buttons_frame,
            text=f"{Icons.SAVE} {save_text}",
            bg=theme_manager.themes[theme_manager.current_theme]["btn_primary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_primary_fg"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            width=10,
            height=1,
            padx=4,
            pady=2,
            cursor="hand2",
            command=self._save_tenant
        )
        btn_save.pack(side="right")
        
        # Mensaje de campos requeridos
        required_label = tk.Label(
            buttons_frame,
            text="* Campos requeridos",
            **theme_manager.get_style("label_body")
        )
        required_label.configure(
            fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"]
        )
        required_label.pack(side="left")
    
    # Métodos de funcionalidad
    def _load_tenant_data(self):
        """Carga los datos del inquilino en modo edición"""
        if not self.tenant_data:
            return
            
        # Mapear datos a campos
        field_mapping = {
            'nombre': 'nombre',
            'numero_documento': 'numero_documento', 
            'telefono': 'telefono',
            'email': 'email',
            'apartamento': 'apartamento',
            'valor_arriendo': 'valor_arriendo',
            'fecha_ingreso': 'fecha_ingreso',
            'estado_pago': 'estado_pago'
        }
        
        for field_key, data_key in field_mapping.items():
            if field_key in self.form_fields and data_key in self.tenant_data:
                value = self.tenant_data[data_key]
                
                # Formatear valor de arriendo
                if field_key == 'valor_arriendo':
                    value = str(value)
                
                # Establecer valor según el tipo de campo
                if hasattr(self.form_fields[field_key], 'set'):
                    self.form_fields[field_key].set(str(value))
                else:
                    self.form_fields[field_key].set(str(value))
    
    def _upload_document(self, doc_type: str):
        """Maneja la subida de documentos"""
        filetypes = [
            ("Archivos PDF", "*.pdf"),
            ("Imágenes", "*.jpg *.jpeg *.png"),
            ("Todos los archivos", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title=f"Seleccionar {doc_type}",
            filetypes=filetypes
        )
        
        if filename:
            self.selected_files[doc_type] = filename
            
            # Actualizar label
            file_name = filename.split("/")[-1]
            if doc_type == "id":
                self.id_file_label.configure(text=file_name)
            else:
                self.contract_file_label.configure(text=file_name)
    
    def _validate_form(self) -> bool:
        """Valida todos los campos del formulario"""
        self.validation_errors = {}
        
        # Campos requeridos
        required_fields = {
            'nombre': 'Nombre completo',
            'numero_documento': 'Número de documento',
            'telefono': 'Teléfono',
            'apartamento': 'Número de apartamento',
            'valor_arriendo': 'Valor arriendo',
            'fecha_ingreso': 'Fecha de ingreso'
        }
        
        # Validar campos requeridos
        for field, label in required_fields.items():
            value = self.form_fields[field].get().strip()
            if not value:
                self.validation_errors[field] = f"{label} es requerido"
        
        # Validaciones específicas
        if 'telefono' not in self.validation_errors:
            phone = self.form_fields['telefono'].get().strip()
            if not re.match(r'^\+?[\d\s\-\(\)]+$', phone):
                self.validation_errors['telefono'] = "Formato de teléfono inválido"
        
        if 'email' not in self.validation_errors:
            email = self.form_fields['email'].get().strip()
            if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                self.validation_errors['email'] = "Formato de email inválido"
        
        if 'valor_arriendo' not in self.validation_errors:
            rent = self.form_fields['valor_arriendo'].get().strip()
            try:
                float(rent)
            except ValueError:
                self.validation_errors['valor_arriendo'] = "El valor debe ser numérico"
        
        # Validar fechas (solo la de ingreso es requerida)
        # Fecha de ingreso - requerida
        if 'fecha_ingreso' not in self.validation_errors:
            fecha_ingreso = self.form_fields['fecha_ingreso'].get().strip()
            if fecha_ingreso and not self._validate_date(fecha_ingreso):
                self.validation_errors['fecha_ingreso'] = "Formato de fecha inválido (DD/MM/AAAA)"
        
        # Otras fechas opcionales
        optional_date_fields = ['fecha_fin_contrato']
        for field in optional_date_fields:
            if field in self.form_fields:
                date_value = self.form_fields[field].get().strip()
                if date_value and not self._validate_date(date_value):
                    self.validation_errors[field] = "Formato de fecha inválido (DD/MM/AAAA)"
        
        return len(self.validation_errors) == 0
    
    def _validate_date(self, date_str: str) -> bool:
        """Valida formato de fecha DD/MM/AAAA"""
        if not date_str.strip():
            return True  # Fechas vacías son válidas para campos opcionales
            
        try:
            # Intentar varios formatos de fecha
            formats = ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"]
            for fmt in formats:
                try:
                    datetime.strptime(date_str.strip(), fmt)
                    return True
                except ValueError:
                    continue
            return False
        except Exception:
            return False
    
    def _save_tenant(self):
        """Guarda o actualiza el inquilino"""
        if not self._validate_form():
            self._show_validation_errors()
            return
        
        # Recopilar datos del formulario
        tenant_data = self._collect_form_data()
        
        try:
            if self.is_edit_mode:
                # Actualizar inquilino existente
                tenant_id = self.tenant_data.get("id")
                result = tenant_service.update_tenant(tenant_id, tenant_data)
                action = "actualizado"
            else:
                # Crear nuevo inquilino
                result = tenant_service.create_tenant(tenant_data)
                action = "guardado"
            
            if result:
                messagebox.showinfo(
                    "Éxito",
                    f"Inquilino {action} correctamente.\n\nNombre: {tenant_data['nombre']}\nApartamento: {tenant_data['apartamento']}"
                )
                
                # Volver a la lista
                self._on_back_clicked()
            else:
                messagebox.showerror("Error", "No se pudo guardar el inquilino")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def _collect_form_data(self) -> Dict[str, Any]:
        """Recopila todos los datos del formulario"""
        data = {}
        
        for field_name, field_widget in self.form_fields.items():
            if hasattr(field_widget, 'get'):
                value = field_widget.get()
                # Manejar valores vacíos y espacios
                if isinstance(value, str):
                    value = value.strip()
                data[field_name] = value
        
        # Agregar archivos seleccionados
        if hasattr(self, 'selected_files'):
            data['archivos'] = self.selected_files.copy()
        else:
            data['archivos'] = {"id": None, "contract": None}
        
        return data
    
    def _show_validation_errors(self):
        """Muestra los errores de validación"""
        if not self.validation_errors:
            return
        
        error_msg = "Por favor corrija los siguientes errores:\n\n"
        for field, error in self.validation_errors.items():
            error_msg += f"• {error}\n"
        
        messagebox.showerror("Errores de validación", error_msg)
    
    def _on_back_clicked(self):
        """Maneja el clic en volver"""
        if self.on_back:
            self.on_back() 