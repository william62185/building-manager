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
    
    def __init__(self, parent, tenant_data: Dict[str, Any], on_back: Callable = None, on_edit: Callable = None, on_register_payment: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        
        self.tenant_data = tenant_data
        self.on_back = on_back
        self.on_edit = on_edit
        self.on_register_payment = on_register_payment
        
        # Crear layout
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout principal de la vista (compacta y sin espacios extra)"""
        # Header con navegación
        self._create_header()
        # Contenedor principal con scroll
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
            "moroso": "danger",
            "inactivo": "neutral"
        }
        
        status_texts = {
            "al_dia": "Al día",
            "moroso": "Moroso",
            "inactivo": "Inactivo"
        }
        
        status = self.tenant_data.get("estado_pago", "al_dia")
        status_badge = ModernBadge(
            info_frame,
            text=status_texts.get(status, "Desconocido"),
            style=status_colors.get(status, "neutral")
        )
        status_badge.pack(side="left", padx=(Spacing.MD, 0))
        
        # Botones de acción
        actions_frame = tk.Frame(header_frame, **theme_manager.get_style("frame"))
        actions_frame.pack(side="right")
        
        btn_pdf = ModernButton(
            actions_frame,
            text="Generar Ficha PDF",
            icon="📄",
            style="pdf",
            command=self._generate_pdf
        )
        btn_pdf.pack(side="right", padx=(0, Spacing.MD))
        btn_edit = ModernButton(
            actions_frame,
            text="Editar",
            icon=Icons.EDIT,
            style="primary",
            command=self._on_edit_clicked
        )
        btn_edit.pack(side="right")
    
    def _create_scroll_container(self):
        """Crea el container con scroll vertical funcional y compacto"""
        self.canvas = tk.Canvas(self, **theme_manager.get_style("frame"), highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, pady=(0, 0), padx=(0, 0))
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.scrollable_frame = tk.Frame(self.canvas, **theme_manager.get_style("frame"))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
    
    def _create_content(self):
        """Crea el contenido principal (aún más compacto, sin espacios extra)"""
        content_grid = tk.Frame(self.scrollable_frame, **theme_manager.get_style("frame"))
        content_grid.pack(fill="both", expand=True, pady=(0, 0), padx=(0, 0))
        left_column = tk.Frame(content_grid, **theme_manager.get_style("frame"))
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 2))
        right_column = tk.Frame(content_grid, **theme_manager.get_style("frame"))
        right_column.pack(side="right", fill="both", expand=True, padx=(2, 0))
        self._create_personal_info_section(left_column)
        self._create_emergency_contact_section(left_column)
        self._create_documents_section_simple(left_column)
        self._create_housing_info_section(right_column)
        self._create_payment_info_section(right_column)
    
    def _create_personal_info_section(self, parent):
        """Crea la sección de información personal"""
        section = ModernCard(
            parent,
            title="Información Personal"
        )
        section.pack(fill="x", pady=(0, 2), ipady=0, ipadx=0)
        section.content_frame.pack_configure(pady=(0, 0))
        info_data = [
            ("Nombre completo", self.tenant_data.get("nombre", "N/A")),
            ("Documento", self.tenant_data.get("numero_documento", "N/A")),
            ("Teléfono", self.tenant_data.get("telefono", "N/A")),
            ("Email", self.tenant_data.get("email", "N/A"))
        ]
        for label, value in info_data:
            self._create_info_row(section.content_frame, label, value)
    
    def _create_emergency_contact_section(self, parent):
        """Crea la sección de contacto de emergencia"""
        section = ModernCard(
            parent,
            title="Contacto de Emergencia"
        )
        section.pack(fill="x", pady=(0, 2), ipady=0, ipadx=0)
        section.content_frame.pack_configure(pady=(0, 0))
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
            title="Información de Vivienda"
        )
        section.pack(fill="x", pady=(0, 2), ipady=0, ipadx=0)
        section.content_frame.pack_configure(pady=(0, 0))
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
            title="Información de Pagos"
        )
        section.pack(fill="x", pady=(0, 2), ipady=0, ipadx=0)
        section.content_frame.pack_configure(pady=(0, 0))
        payment_data = [
            ("Último pago", "15/12/2024"),
            ("Próximo vencimiento", "15/01/2025"),
            ("Días de mora", "0" if self.tenant_data.get("estado_pago") == "al_dia" else "5")
        ]
        for label, value in payment_data:
            self._create_info_row(section.content_frame, label, value)
        btn_history = ModernButton(
            section.content_frame,
            text="Ver Historial Completo",
            icon=Icons.PAYMENT_RECEIVED,
            style="secondary",
            command=self._view_payment_history,
            small=True
        )
        btn_history.pack(anchor="w", pady=(2, 0), padx=(0, 0))
    
    def _create_documents_section_simple(self, parent):
        section = ModernCard(
            parent,
            title="Documentos Adjuntos",
        )
        section.pack(fill="x")
        archivos = self.tenant_data.get("archivos", {})
        if isinstance(archivos, str):
            try:
                import json
                archivos = json.loads(archivos)
            except:
                archivos = {}
        doc_id = archivos.get("id") if archivos else None
        doc_contract = archivos.get("contract") if archivos else None
        id_row = tk.Frame(section.content_frame, **theme_manager.get_style("frame"))
        id_row.pack(fill="x", pady=(0, 2))
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
        contract_row = tk.Frame(section.content_frame, **theme_manager.get_style("frame"))
        contract_row.pack(fill="x", pady=(0, 2))
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
        btn_docs = ModernButton(
            section.content_frame,
            text="Gestionar Documentos",
            icon=Icons.UPLOAD,
            style="secondary",
            command=self._manage_documents,
            small=True
        )
        btn_docs.pack(anchor="w", pady=(2, 0), padx=(0, 0))
    
    def _create_info_row(self, parent, label: str, value: str):
        """Crea una fila de información ultra compacta"""
        row_frame = tk.Frame(parent, **theme_manager.get_style("frame"))
        row_frame.pack(fill="x", pady=(0, 0), ipady=0, ipadx=0)
        # Label
        label_widget = tk.Label(
            row_frame,
            text=f"{label}:",
            **theme_manager.get_style("label_body")
        )
        label_widget.configure(font=("Segoe UI", 10, "bold"), pady=0, padx=0)
        label_widget.pack(side="left", padx=(0, 2))
        # Value
        value_widget = tk.Label(
            row_frame,
            text=str(value),
            **theme_manager.get_style("label_body")
        )
        value_widget.configure(font=("Segoe UI", 10), pady=0, padx=0)
        value_widget.pack(side="right", padx=(0, 2))
    
    def _create_action_buttons(self):
        """Crea los botones de acción (sin espacio extra arriba)"""
        actions_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        actions_frame.pack(fill="x", pady=(0, 0))
        buttons_frame = tk.Frame(actions_frame, **theme_manager.get_style("frame"))
        buttons_frame.pack(pady=(0, 0))
        btn_payment = ModernButton(
            buttons_frame,
            text="Registrar Pago",
            icon=Icons.PAYMENT_RECEIVED,
            style="primary",
            command=self._register_payment
        )
        btn_payment.pack(side="left")
        btn_receipt = ModernButton(
            buttons_frame,
            text="Generar Recibo",
            icon=Icons.RECEIPT,
            style="secondary",
            command=self._generate_receipt
        )
        btn_receipt.pack(side="left", padx=(Spacing.SM, 0))
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
        if hasattr(self, 'on_register_payment') and self.on_register_payment:
            self.on_register_payment(self.tenant_data)
        else:
            messagebox.showinfo("Navegación", "No se pudo navegar al módulo de pagos.")
    
    def _generate_receipt(self):
        """Genera un recibo"""
        messagebox.showinfo("Info", "Generación de recibos en desarrollo")
    
    def _send_notification(self):
        """Envía notificación al inquilino"""
        messagebox.showinfo("Info", "Envío de notificaciones en desarrollo")

    def _generate_pdf(self):
        """Genera la ficha PDF del inquilino"""
        import os
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from tkinter import messagebox
        from datetime import datetime

        tenant = self.tenant_data
        nombre = tenant.get("nombre", "Inquilino").replace(" ", "_")
        apartamento = str(tenant.get("apartamento", "N/A")).replace(" ", "_")
        filename = f"ficha_{nombre}_{apartamento}.pdf"
        folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../fichas'))
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        y = height - 40
        c.setFont("Helvetica-Bold", 18)
        c.drawString(40, y, "Ficha de Inquilino")
        c.setFont("Helvetica", 10)
        c.drawString(40, y-20, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        y -= 50
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Información Personal")
        c.setFont("Helvetica", 11)
        y -= 18
        c.drawString(50, y, f"Nombre: {tenant.get('nombre', '')}")
        y -= 15
        c.drawString(50, y, f"Documento: {tenant.get('numero_documento', '')}")
        y -= 15
        c.drawString(50, y, f"Teléfono: {tenant.get('telefono', '')}")
        y -= 15
        c.drawString(50, y, f"Email: {tenant.get('email', '')}")
        y -= 25
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Información de Vivienda")
        c.setFont("Helvetica", 11)
        y -= 18
        c.drawString(50, y, f"Apartamento: {tenant.get('apartamento', '')}")
        y -= 15
        c.drawString(50, y, f"Valor arriendo: {tenant.get('valor_arriendo', '')}")
        y -= 15
        c.drawString(50, y, f"Fecha de ingreso: {tenant.get('fecha_ingreso', '')}")
        y -= 15
        c.drawString(50, y, f"Estado de pago: {tenant.get('estado_pago', '')}")
        y -= 25
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Contacto de Emergencia")
        c.setFont("Helvetica", 11)
        y -= 18
        c.drawString(50, y, f"Nombre: {tenant.get('contacto_emergencia_nombre', '')}")
        y -= 15
        c.drawString(50, y, f"Teléfono: {tenant.get('contacto_emergencia_telefono', '')}")
        y -= 25
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Información de Pagos")
        c.setFont("Helvetica", 11)
        y -= 18
        c.drawString(50, y, f"Último pago: {tenant.get('ultimo_pago', 'N/A')}")
        y -= 15
        c.drawString(50, y, f"Próximo vencimiento: {tenant.get('proximo_vencimiento', 'N/A')}")
        y -= 15
        c.drawString(50, y, f"Días de mora: {tenant.get('dias_mora', '0')}")
        y -= 25
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Documentos Adjuntos")
        c.setFont("Helvetica", 11)
        y -= 18
        archivos = tenant.get('archivos', {})
        if isinstance(archivos, str):
            import json
            try:
                archivos = json.loads(archivos)
            except:
                archivos = {}
        doc_id = archivos.get('id')
        doc_contract = archivos.get('contract')
        c.drawString(50, y, f"Documento de Identidad: {'Adjuntado' if doc_id else 'No adjuntado'}")
        y -= 15
        c.drawString(50, y, f"Contrato de Arrendamiento: {'Adjuntado' if doc_contract else 'No adjuntado'}")
        c.save()
        messagebox.showinfo("PDF generado", f"Ficha PDF generada exitosamente:\n{filepath}")