"""
Vista de detalles de inquilino
Muestra toda la información de un inquilino de forma profesional
"""

import tkinter as tk
from tkinter import messagebox
from typing import Dict, Any, Callable
import json
import os
from ..components.theme_manager import theme_manager, Spacing
from ..components.icons import Icons
from ..components.modern_widgets import (
    ModernButton, ModernCard, ModernBadge, ModernSeparator
)

class TenantDetailsView(tk.Frame):
    """Vista de detalles de inquilino"""
    
    def __init__(self, parent, tenant_data: Dict[str, Any], on_back: Callable = None, on_edit: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        
        self.tenant_data = tenant_data
        self.on_back = on_back
        self.on_edit = on_edit
        
        # Crear layout
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout principal de la vista"""
        # Header con navegación
        self._create_header()
        
        # Separador
        ModernSeparator(self)
        
        # Container principal con scroll
        self._create_scroll_container()
        
        # Contenido principal
        self._create_content()
        
        # Botones de acción
        self._create_action_buttons()
    
    def _create_header(self):
        """Crea el header con título y navegación"""
        header_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", pady=(0, Spacing.LG))
        
        # Botón volver
        nav_frame = tk.Frame(header_frame, **theme_manager.get_style("frame"))
        nav_frame.pack(side="left")
        
        btn_back = ModernButton(
            nav_frame,
            text="Volver",
            icon=Icons.ARROW_LEFT,
            style="secondary",
            command=self._on_back_clicked
        )
        btn_back.pack(side="left")
        
        # Título con nombre del inquilino
        title_frame = tk.Frame(header_frame, **theme_manager.get_style("frame"))
        title_frame.pack(side="left", fill="x", expand=True, padx=(Spacing.LG, 0))
        
        # Nombre del inquilino
        name_label = tk.Label(
            title_frame,
            text=self.tenant_data.get("nombre", "Inquilino"),
            **theme_manager.get_style("label_title")
        )
        name_label.configure(font=("Segoe UI", 20, "bold"))
        name_label.pack(anchor="w")
        
        # Información básica con badge de estado
        info_frame = tk.Frame(title_frame, **theme_manager.get_style("frame"))
        info_frame.pack(anchor="w", pady=(Spacing.XS, 0))
        
        apt_label = tk.Label(
            info_frame,
            text=f"Apartamento {self.tenant_data.get('apartamento', 'N/A')}",
            **theme_manager.get_style("label_subtitle")
        )
        apt_label.pack(side="left")
        
        # Badge de estado
        status_colors = {
            "al_dia": "success",
            "pendiente": "warning", 
            "moroso": "danger"
        }
        
        status_texts = {
            "al_dia": "Al día",
            "pendiente": "Pendiente",
            "moroso": "Moroso"
        }
        
        status = self.tenant_data.get("estado_pago", "al_dia")
        status_badge = ModernBadge(
            info_frame,
            text=status_texts.get(status, "Desconocido"),
            style=status_colors.get(status, "neutral")
        )
        status_badge.pack(side="left", padx=(Spacing.MD, 0))
        
        # Botón editar
        actions_frame = tk.Frame(header_frame, **theme_manager.get_style("frame"))
        actions_frame.pack(side="right")
        
        btn_edit = ModernButton(
            actions_frame,
            text="Editar",
            icon=Icons.EDIT,
            style="primary",
            command=self._on_edit_clicked
        )
        btn_edit.pack(side="right")
    
    def _create_scroll_container(self):
        """Crea el container con scroll"""
        self.scroll_container = tk.Frame(self, **theme_manager.get_style("frame"))
        self.scroll_container.pack(fill="both", expand=True, pady=(0, Spacing.LG))
    
    def _create_content(self):
        """Crea el contenido principal"""
        # Grid de 2 columnas
        content_grid = tk.Frame(self.scroll_container, **theme_manager.get_style("frame"))
        content_grid.pack(fill="both", expand=True)
        
        # Columna izquierda
        left_column = tk.Frame(content_grid, **theme_manager.get_style("frame"))
        left_column.pack(side="left", fill="both", expand=True, padx=(0, Spacing.MD))
        
        # Columna derecha
        right_column = tk.Frame(content_grid, **theme_manager.get_style("frame"))
        right_column.pack(side="right", fill="both", expand=True, padx=(Spacing.MD, 0))
        
        # Secciones de información
        self._create_personal_info_section(left_column)
        self._create_contact_info_section(left_column)
        self._create_emergency_contact_section(left_column)
        
        self._create_housing_info_section(right_column)
        self._create_payment_info_section(right_column)
        self._create_documents_section_simple(right_column)
    
    def _create_personal_info_section(self, parent):
        """Crea la sección de información personal"""
        section = ModernCard(
            parent,
            title="Información Personal",
            subtitle="Datos básicos del inquilino"
        )
        section.pack(fill="x", pady=(0, Spacing.LG))
        
        # Información personal en formato de tabla
        info_data = [
            ("Nombre completo", self.tenant_data.get("nombre", "N/A")),
            ("Documento", self.tenant_data.get("numero_documento", "N/A")),
            ("Teléfono", self.tenant_data.get("telefono", "N/A")),
            ("Email", self.tenant_data.get("email", "N/A"))
        ]
        
        for label, value in info_data:
            self._create_info_row(section.content_frame, label, value)
    
    def _create_contact_info_section(self, parent):
        """Crea la sección de información de contacto"""
        section = ModernCard(
            parent,
            title="Información de Contacto",
            subtitle="Dirección y datos adicionales"
        )
        section.pack(fill="x", pady=(0, Spacing.LG))
        
        # Dirección
        direccion = self.tenant_data.get("direccion", "No registrada")
        self._create_info_row(section.content_frame, "Dirección", direccion)
    
    def _create_emergency_contact_section(self, parent):
        """Crea la sección de contacto de emergencia"""
        section = ModernCard(
            parent,
            title="Contacto de Emergencia",
            subtitle="Persona a contactar en caso de emergencia"
        )
        section.pack(fill="x")
        
        # Información de contacto de emergencia
        emergency_data = [
            ("Nombre", self.tenant_data.get("contacto_emergencia_nombre", "No registrado")),
            ("Teléfono", self.tenant_data.get("contacto_emergencia_telefono", "No registrado"))
        ]
        
        for label, value in emergency_data:
            self._create_info_row(section.content_frame, label, value)
    
    def _create_housing_info_section(self, parent):
        """Crea la sección de información de vivienda"""
        section = ModernCard(
            parent,
            title="Información de Vivienda",
            subtitle="Datos del apartamento y arriendo"
        )
        section.pack(fill="x", pady=(0, Spacing.LG))
        
        # Información de vivienda
        valor_arriendo = self.tenant_data.get("valor_arriendo")
        housing_data = [
            ("Apartamento", self.tenant_data.get("apartamento", "N/A")),
            ("Valor arriendo", f"${valor_arriendo:,}" if valor_arriendo else "No registrado"),
            ("Fecha de ingreso", self.tenant_data.get("fecha_ingreso", "No registrada")),
            ("Estado de pago", self.tenant_data.get("estado_pago", "N/A").replace("_", " ").title())
        ]
        
        for label, value in housing_data:
            self._create_info_row(section.content_frame, label, value)
    
    def _create_payment_info_section(self, parent):
        """Crea la sección de información de pagos"""
        section = ModernCard(
            parent,
            title="Información de Pagos",
            subtitle="Historial y estado de pagos"
        )
        section.pack(fill="x", pady=(0, Spacing.LG))
        
        # Información de pagos (expandir cuando tengamos servicio de pagos)
        payment_data = [
            ("Último pago", "15/12/2024"),  # Mock data
            ("Próximo vencimiento", "15/01/2025"),  # Mock data
            ("Días de mora", "0" if self.tenant_data.get("estado_pago") == "al_dia" else "5")  # Mock logic
        ]
        
        for label, value in payment_data:
            self._create_info_row(section.content_frame, label, value)
        
        # Botón para ver historial completo
        btn_history = ModernButton(
            section.content_frame,
            text="Ver Historial Completo",
            icon=Icons.PAYMENT_RECEIVED,
            style="secondary",
            command=self._view_payment_history
        )
        btn_history.pack(pady=(Spacing.MD, 0))
    
    def _create_documents_section(self, parent):
        """Crea la sección de documentos"""
        try:
            section = ModernCard(
                parent,
                title="Documentos Adjuntos",
                subtitle="Archivos del inquilino"
            )
            section.pack(fill="x", pady=(0, Spacing.LG))
            
            # Obtener archivos reales del inquilino
            archivos = self.tenant_data.get("archivos", {})
            if isinstance(archivos, str):
                # Si archivos es un string, intentar parsearlo como JSON
                try:
                    archivos = json.loads(archivos)
                except:
                    archivos = {}
            
            # Documentos disponibles
            documentos = [
                ("Documento de Identidad", "id", archivos.get("id")),
                ("Contrato de Arrendamiento", "contract", archivos.get("contract"))
            ]
            
            # Contar documentos disponibles
            docs_count = sum(1 for _, _, path in documentos if path and str(path).strip())
            total_docs = len(documentos)
            
            # Estado general de documentos
            docs_frame = tk.Frame(section.content_frame, **theme_manager.get_style("frame"))
            docs_frame.pack(fill="x", pady=(0, Spacing.MD))
            
            icon_text = "📄"  # Usar emoji simple en lugar de Icons.TENANT_DOCUMENTS por si hay problema
            status_text = f"Documentos: {docs_count}/{total_docs}"
            
            if docs_count == total_docs and total_docs > 0:
                color = theme_manager.themes[theme_manager.current_theme]["success"]
                status_text += " ✓ Completos"
            elif docs_count > 0:
                color = theme_manager.themes[theme_manager.current_theme]["warning"] 
                status_text += " ⚠ Incompletos"
            else:
                color = theme_manager.themes[theme_manager.current_theme]["error"]
                status_text += " ✗ Faltantes"
            
            status_label = tk.Label(
                docs_frame,
                text=f"{icon_text} {status_text}",
                fg=color,
                **theme_manager.get_style("frame")
            )
            status_label.configure(font=("Segoe UI", 12, "bold"))
            status_label.pack(anchor="w")
            
            # Lista de documentos individuales
            for doc_name, doc_key, doc_path in documentos:
                doc_row = tk.Frame(section.content_frame, **theme_manager.get_style("frame"))
                doc_row.pack(fill="x", pady=(Spacing.XS, 0))
                
                # Nombre del documento
                doc_label = tk.Label(
                    doc_row,
                    text=f"• {doc_name}:",
                    **theme_manager.get_style("label_body")
                )
                doc_label.pack(side="left")
                
                # Estado y archivo
                if doc_path and str(doc_path).strip():
                    # Extraer solo el nombre del archivo
                    try:
                        file_name = os.path.basename(str(doc_path)) if doc_path else "Archivo"
                    except:
                        file_name = "Archivo adjunto"
                    
                    # Mostrar nombre del archivo
                    file_label = tk.Label(
                        doc_row,
                        text=file_name,
                        fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"],
                        **theme_manager.get_style("frame")
                    )
                    file_label.configure(font=("Segoe UI", 10, "normal"))
                    file_label.pack(side="right", padx=(Spacing.XS, 0))
                    
                    # Icono de éxito
                    status_icon = tk.Label(
                        doc_row,
                        text="✓",
                        fg=theme_manager.themes[theme_manager.current_theme]["success"],
                        **theme_manager.get_style("frame")
                    )
                    status_icon.configure(font=("Segoe UI", 12, "bold"))
                    status_icon.pack(side="right")
                else:
                    # No hay archivo
                    no_file_label = tk.Label(
                        doc_row,
                        text="No adjuntado",
                        fg=theme_manager.themes[theme_manager.current_theme]["text_tertiary"],
                        **theme_manager.get_style("frame")
                    )
                    no_file_label.configure(font=("Segoe UI", 10, "italic"))
                    no_file_label.pack(side="right", padx=(Spacing.XS, 0))
                    
                    # Icono de falta
                    status_icon = tk.Label(
                        doc_row,
                        text="✗",
                        fg=theme_manager.themes[theme_manager.current_theme]["error"],
                        **theme_manager.get_style("frame")
                    )
                    status_icon.configure(font=("Segoe UI", 12, "bold"))
                    status_icon.pack(side="right")
            
            # Botón para gestionar documentos
            btn_docs = ModernButton(
                section.content_frame,
                text="Gestionar Documentos",
                icon=Icons.UPLOAD,
                style="secondary",
                command=self._manage_documents
            )
            btn_docs.pack(pady=(Spacing.MD, 0))
            
        except Exception as e:
            # Si hay error, crear una sección simple
            print(f"Error creando sección de documentos: {e}")
            simple_section = ModernCard(
                parent,
                title="Documentos",
                subtitle="Sección en desarrollo"
            )
            simple_section.pack(fill="x", pady=(0, Spacing.LG))
            
            error_label = tk.Label(
                simple_section.content_frame,
                text="Error al cargar documentos. Funcionalidad en desarrollo.",
                **theme_manager.get_style("label_body")
            )
            error_label.pack()
    
    def _create_info_row(self, parent, label: str, value: str):
        """Crea una fila de información"""
        row_frame = tk.Frame(parent, **theme_manager.get_style("frame"))
        row_frame.pack(fill="x", pady=(0, Spacing.SM))
        
        # Label
        label_widget = tk.Label(
            row_frame,
            text=f"{label}:",
            **theme_manager.get_style("label_body")
        )
        label_widget.configure(font=("Segoe UI", 12, "bold"))
        label_widget.pack(side="left")
        
        # Value
        value_widget = tk.Label(
            row_frame,
            text=str(value),
            **theme_manager.get_style("label_body")
        )
        value_widget.pack(side="right")
    
    def _create_action_buttons(self):
        """Crea los botones de acción"""
        actions_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        actions_frame.pack(fill="x", pady=(Spacing.LG, 0))
        
        # Separador
        ModernSeparator(actions_frame)
        
        # Botones
        buttons_frame = tk.Frame(actions_frame, **theme_manager.get_style("frame"))
        buttons_frame.pack(pady=(Spacing.MD, 0))
        
        # Botón registrar pago
        btn_payment = ModernButton(
            buttons_frame,
            text="Registrar Pago",
            icon=Icons.PAYMENT_RECEIVED,
            style="primary",
            command=self._register_payment
        )
        btn_payment.pack(side="left")
        
        # Botón generar recibo
        btn_receipt = ModernButton(
            buttons_frame,
            text="Generar Recibo",
            icon=Icons.RECEIPT,
            style="secondary",
            command=self._generate_receipt
        )
        btn_receipt.pack(side="left", padx=(Spacing.SM, 0))
        
        # Botón enviar notificación
        btn_notify = ModernButton(
            buttons_frame,
            text="Enviar Notificación",
            icon=Icons.EMAIL,
            style="secondary",
            command=self._send_notification
        )
        btn_notify.pack(side="left", padx=(Spacing.SM, 0))
    
    # Event handlers
    def _on_back_clicked(self):
        """Maneja el clic en volver"""
        if self.on_back:
            self.on_back()
    
    def _on_edit_clicked(self):
        """Maneja el clic en editar"""
        if self.on_edit:
            self.on_edit(self.tenant_data)
    
    def _view_payment_history(self):
        """Muestra el historial de pagos"""
        messagebox.showinfo("Info", "Historial de pagos en desarrollo")
    
    def _manage_documents(self):
        """Gestiona documentos del inquilino"""
        messagebox.showinfo("Info", "Gestión de documentos en desarrollo")
    
    def _register_payment(self):
        """Registra un nuevo pago"""
        messagebox.showinfo("Info", "Registro de pagos en desarrollo")
    
    def _generate_receipt(self):
        """Genera un recibo"""
        messagebox.showinfo("Info", "Generación de recibos en desarrollo")
    
    def _send_notification(self):
        """Envía notificación al inquilino"""
        messagebox.showinfo("Info", "Envío de notificaciones en desarrollo")
    
    def _create_documents_section_simple(self, parent):
        """Crea la sección de documentos de forma simple y segura"""
        section = ModernCard(
            parent,
            title="Documentos Adjuntos",
            subtitle="Archivos del inquilino"
        )
        section.pack(fill="x")
        
        # Obtener archivos del inquilino
        archivos = self.tenant_data.get("archivos", {})
        
        # Si archivos es string, intentar convertir a dict
        if isinstance(archivos, str):
            try:
                import json
                archivos = json.loads(archivos)
            except:
                archivos = {}
        
        # Lista de documentos
        doc_id = archivos.get("id") if archivos else None
        doc_contract = archivos.get("contract") if archivos else None
        
        # Documento de Identidad
        id_row = tk.Frame(section.content_frame, **theme_manager.get_style("frame"))
        id_row.pack(fill="x", pady=(0, Spacing.SM))
        
        id_label = tk.Label(
            id_row,
            text="• Documento de Identidad:",
            **theme_manager.get_style("label_body")
        )
        id_label.pack(side="left")
        
        if doc_id and str(doc_id).strip():
            import os
            filename = os.path.basename(str(doc_id))
            id_status = tk.Label(
                id_row,
                text=f"✓ {filename}",
                fg=theme_manager.themes[theme_manager.current_theme]["success"],
                **theme_manager.get_style("frame")
            )
        else:
            id_status = tk.Label(
                id_row,
                text="✗ No adjuntado",
                fg=theme_manager.themes[theme_manager.current_theme]["error"],
                **theme_manager.get_style("frame")
            )
        id_status.pack(side="right")
        
        # Contrato de Arrendamiento
        contract_row = tk.Frame(section.content_frame, **theme_manager.get_style("frame"))
        contract_row.pack(fill="x", pady=(0, Spacing.SM))
        
        contract_label = tk.Label(
            contract_row,
            text="• Contrato de Arrendamiento:",
            **theme_manager.get_style("label_body")
        )
        contract_label.pack(side="left")
        
        if doc_contract and str(doc_contract).strip():
            import os
            filename = os.path.basename(str(doc_contract))
            contract_status = tk.Label(
                contract_row,
                text=f"✓ {filename}",
                fg=theme_manager.themes[theme_manager.current_theme]["success"],
                **theme_manager.get_style("frame")
            )
        else:
            contract_status = tk.Label(
                contract_row,
                text="✗ No adjuntado",
                fg=theme_manager.themes[theme_manager.current_theme]["error"],
                **theme_manager.get_style("frame")
            )
        contract_status.pack(side="right")
        
        # Botón gestionar documentos
        btn_docs = ModernButton(
            section.content_frame,
            text="Gestionar Documentos",
            icon=Icons.UPLOAD,
            style="secondary",
            command=self._manage_documents
        )
        btn_docs.pack(pady=(Spacing.MD, 0))