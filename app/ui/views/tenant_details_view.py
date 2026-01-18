"""
Vista de detalles de inquilino
Muestra toda la información de un inquilino de forma profesional
"""

import tkinter as tk
from tkinter import messagebox
from typing import Dict, Any, Callable
import json
import os
import subprocess
import platform
from ..components.theme_manager import theme_manager, Spacing
from ..components.icons import Icons
from ..components.modern_widgets import (
    ModernButton, ModernCard, ModernBadge, ModernSeparator
)
from manager.app.services.apartment_service import apartment_service
from manager.app.services.building_service import building_service
from manager.app.services.payment_service import payment_service
from manager.app.services.tenant_service import tenant_service
from manager.app.services.email_service import email_service
from datetime import datetime, timedelta

class TenantDetailsView(tk.Frame):
    """Vista de detalles de inquilino"""
    
    def __init__(self, parent, tenant_data: Dict[str, Any], on_back: Callable = None, on_edit: Callable = None, on_register_payment: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        
        # Recargar datos del inquilino desde el servicio para asegurar datos actualizados
        tenant_id = tenant_data.get("id")
        if tenant_id:
            try:
                tenant_service._load_data()
                updated_tenant = tenant_service.get_tenant_by_id(tenant_id)
                if updated_tenant:
                    self.tenant_data = updated_tenant
                else:
                    self.tenant_data = tenant_data
            except Exception as e:
                print(f"Error al recargar datos del inquilino: {str(e)}")
                self.tenant_data = tenant_data
        else:
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
        
        # --- Display amigable del apartamento ---
        apt_id = self.tenant_data.get('apartamento', None)
        apt_display = 'N/A'
        if apt_id is not None:
            apt = apartment_service.get_apartment_by_id(apt_id)
            if apt:
                building = building_service.get_building_by_id(apt.get('building_id')) if hasattr(building_service, 'get_building_by_id') else None
                if not building:
                    all_buildings = building_service.get_all_buildings()
                    building = next((b for b in all_buildings if b.get('id') == apt.get('building_id')), None)
                building_name = building.get('name') if building else ''
                tipo = apt.get('unit_type', 'Apartamento Estándar')
                numero = apt.get('number', '')
                if building_name:
                    apt_display = f"{building_name} - {tipo} {numero}" if tipo != 'Apartamento Estándar' else f"{building_name} - {numero}"
                else:
                    apt_display = f"{tipo} {numero}" if tipo != 'Apartamento Estándar' else str(numero)
        apt_label = tk.Label(
            info_frame,
            text=apt_display,
            **theme_manager.get_style("label_subtitle")
        )
        apt_label.pack(side="left")
        
        # Badge de estado
        status_colors = {
            "al_dia": "success",
            "moroso": "danger",
            "inactivo": "neutral",
            "pendiente_registro": "warning"
        }
        
        status_texts = {
            "al_dia": "Al día",
            "moroso": "Moroso",
            "inactivo": "Inactivo",
            "pendiente_registro": "Pendiente Registro"
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
        # --- Display amigable del apartamento ---
        apt_id = self.tenant_data.get('apartamento', None)
        apt_display = 'N/A'
        if apt_id is not None:
            apt = apartment_service.get_apartment_by_id(apt_id)
            if apt:
                building = building_service.get_building_by_id(apt.get('building_id')) if hasattr(building_service, 'get_building_by_id') else None
                if not building:
                    all_buildings = building_service.get_all_buildings()
                    building = next((b for b in all_buildings if b.get('id') == apt.get('building_id')), None)
                building_name = building.get('name') if building else ''
                tipo = apt.get('unit_type', 'Apartamento Estándar')
                numero = apt.get('number', '')
                if building_name:
                    apt_display = f"{building_name} - {tipo} {numero}" if tipo != 'Apartamento Estándar' else f"{building_name} - {numero}"
                else:
                    apt_display = f"{tipo} {numero}" if tipo != 'Apartamento Estándar' else str(numero)
        # --- Formatear valor_arriendo de forma segura ---
        valor_arriendo_display = "No registrado"
        if valor_arriendo is not None and valor_arriendo != "":
            try:
                valor_arriendo_num = float(valor_arriendo)
                valor_arriendo_display = f"${valor_arriendo_num:,.0f}"
            except Exception:
                valor_arriendo_display = str(valor_arriendo)
        
        # --- Formatear deposito de forma segura ---
        deposito = self.tenant_data.get("deposito")
        deposito_display = "No registrado"
        if deposito is not None and deposito != "":
            try:
                deposito_num = float(deposito)
                deposito_display = f"${deposito_num:,.0f}"
            except Exception:
                deposito_display = str(deposito)
        
        housing_data = [
            ("Apartamento", apt_display),
            ("Valor arriendo", valor_arriendo_display),
            ("Depósito", deposito_display),
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
        
        # Calcular información de pagos basándose en datos reales
        tenant_id = self.tenant_data.get("id")
        ultimo_pago_display = "No registrado"
        proximo_vencimiento_display = "No calculable"
        dias_mora_display = "0"
        
        if tenant_id:
            # Recargar datos de pagos para asegurar que estén actualizados
            payment_service._load_data()
            
            # Obtener todos los pagos del inquilino
            payments = payment_service.get_payments_by_tenant(tenant_id)
            
            if payments:
                # Ordenar pagos por fecha (más reciente primero)
                try:
                    payments.sort(key=lambda x: datetime.strptime(x.get("fecha_pago", "01/01/1900"), "%d/%m/%Y"), reverse=True)
                    ultimo_pago = payments[0]
                    fecha_ultimo_pago_str = ultimo_pago.get("fecha_pago", "")
                    ultimo_pago_display = fecha_ultimo_pago_str if fecha_ultimo_pago_str else "No registrado"
                    
                    # Calcular días de mora basándose en el último pago
                    try:
                        fecha_ultimo_pago = datetime.strptime(fecha_ultimo_pago_str, "%d/%m/%Y")
                        fecha_actual = datetime.now()
                        dias_desde_ultimo_pago = (fecha_actual - fecha_ultimo_pago).days
                        
                        # Si el último pago fue hace más de 30 días, hay mora
                        if dias_desde_ultimo_pago > 30:
                            dias_mora_display = str(dias_desde_ultimo_pago - 30)
                        else:
                            dias_mora_display = "0"
                            
                        # Calcular próximo vencimiento (30 días después del último pago)
                        try:
                            proximo_vencimiento = fecha_ultimo_pago + timedelta(days=30)
                            proximo_vencimiento_display = proximo_vencimiento.strftime("%d/%m/%Y")
                        except:
                            proximo_vencimiento_display = "No calculable"
                    except Exception as e:
                        print(f"Error al calcular días de mora: {str(e)}")
                        dias_mora_display = "0"
                except Exception as e:
                    print(f"Error al procesar pagos: {str(e)}")
        
        payment_data = [
            ("Último pago", ultimo_pago_display),
            ("Próximo vencimiento", proximo_vencimiento_display),
            ("Días de mora", dias_mora_display)
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
        """Muestra el historial completo de pagos del inquilino en una ventana modal"""
        tenant_id = self.tenant_data.get("id")
        if not tenant_id:
            messagebox.showwarning("Advertencia", "No se puede mostrar el historial: ID de inquilino no disponible.")
            return
        
        # Recargar datos de pagos para asegurar que estén actualizados
        payment_service._load_data()
        
        # Obtener todos los pagos del inquilino
        payments = payment_service.get_payments_by_tenant(tenant_id)
        
        # Crear ventana modal
        history_window = tk.Toplevel(self)
        history_window.title(f"Historial de Pagos - {self.tenant_data.get('nombre', 'Inquilino')}")
        history_window.transient(self)
        history_window.grab_set()
        
        # Configurar tamaño y centrar (ajustado para evitar la barra de tareas)
        history_window.update_idletasks()
        width = 900
        height = 650
        screen_width = history_window.winfo_screenwidth()
        screen_height = history_window.winfo_screenheight()
        # Calcular posición X (centrado horizontal)
        x = (screen_width // 2) - (width // 2)
        # Calcular posición Y (centrado vertical pero con margen superior para evitar barra de tareas)
        # Asumir ~40px para la barra de tareas, dejamos 50px de margen inferior
        available_height = screen_height - 50
        y = (available_height // 2) - (height // 2)
        # Asegurar que la ventana no esté fuera de la pantalla
        if y < 0:
            y = 50
        history_window.geometry(f"{width}x{height}+{x}+{y}")
        history_window.configure(bg="white")
        
        # Frame principal con padding
        main_frame = tk.Frame(history_window, bg="white", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título y nombre del inquilino
        title_frame = tk.Frame(main_frame, bg="white")
        title_frame.pack(fill="x", pady=(0, 15))
        
        title_label = tk.Label(
            title_frame,
            text="Historial de Pagos",
            font=("Segoe UI", 18, "bold"),
            bg="white",
            fg="#1976d2"
        )
        title_label.pack(side="left")
        
        tenant_name_label = tk.Label(
            title_frame,
            text=f"• {self.tenant_data.get('nombre', 'Inquilino')}",
            font=("Segoe UI", 14),
            bg="white",
            fg="#666"
        )
        tenant_name_label.pack(side="left", padx=(10, 0))
        
        # Estadísticas resumidas
        stats_frame = ModernCard(main_frame, title="Resumen")
        stats_frame.pack(fill="x", pady=(0, 15))
        
        total_pagos = len(payments)
        total_monto = sum(float(p.get("monto", 0)) for p in payments)
        
        stats_grid = tk.Frame(stats_frame.content_frame, bg="white")
        stats_grid.pack(fill="x")
        
        tk.Label(
            stats_grid,
            text=f"Total de pagos: {total_pagos}",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#333"
        ).pack(side="left", padx=(0, 30))
        
        tk.Label(
            stats_grid,
            text=f"Total pagado: ${total_monto:,.0f}",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#4caf50"
        ).pack(side="left")
        
        # Frame para la tabla con encabezado fijo
        table_container = tk.Frame(main_frame, bg="white")
        table_container.pack(fill="both", expand=True)
        
        # Encabezado fijo (fuera del área scrolleable)
        headers = [
            ("Fecha", 120),
            ("Monto", 120),
            ("Método", 100),
            ("Observaciones", 400),
            ("Registrado", 150)
        ]
        
        # Mostrar mensaje si no hay pagos
        if not payments:
            no_payments_label = tk.Label(
                table_container,
                text="No hay pagos registrados para este inquilino.",
                font=("Segoe UI", 12),
                bg="white",
                fg="#666",
                pady=30
            )
            no_payments_label.pack()
        else:
            # Ordenar pagos por fecha (más reciente primero)
            try:
                payments.sort(key=lambda x: datetime.strptime(x.get("fecha_pago", "01/01/1900"), "%d/%m/%Y"), reverse=True)
            except Exception:
                pass  # Si hay error al ordenar, mostrar en el orden original
            
            # Encabezado fijo (fuera del canvas scrolleable)
            header_frame = tk.Frame(table_container, bg="#f5f5f5", relief="solid", bd=1)
            header_frame.pack(fill="x", pady=(0, 2))
            
            headers = [
                ("Fecha", 120),
                ("Monto", 120),
                ("Método", 100),
                ("Observaciones", 400),
                ("Registrado", 150)
            ]
            
            for idx, (header_text, width) in enumerate(headers):
                header_label = tk.Label(
                    header_frame,
                    text=header_text,
                    font=("Segoe UI", 10, "bold"),
                    bg="#f5f5f5",
                    fg="#333",
                    anchor="w",
                    padx=10,
                    pady=10
                )
                header_label.grid(row=0, column=idx, sticky="ew", padx=(0, 1))
                header_frame.grid_columnconfigure(idx, weight=1 if idx == 3 else 0, minsize=width)
            
            # Frame para el área scrolleable (solo las filas de pagos)
            scroll_container = tk.Frame(table_container, bg="white")
            scroll_container.pack(fill="both", expand=True)
            
            # Canvas y scrollbar para las filas
            canvas = tk.Canvas(scroll_container, bg="white", highlightthickness=0)
            scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="white")
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Función para sincronizar el ancho del scrollable_frame con el canvas
            def on_canvas_configure(event):
                canvas_width = event.width
                canvas.itemconfig(canvas_window, width=canvas_width)
            
            canvas.bind('<Configure>', on_canvas_configure)
            
            # Scroll con mouse
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            def _bind_to_mousewheel(event):
                canvas.bind_all("<MouseWheel>", _on_mousewheel)
            def _unbind_from_mousewheel(event):
                canvas.unbind_all("<MouseWheel>")
            canvas.bind('<Enter>', _bind_to_mousewheel)
            canvas.bind('<Leave>', _unbind_from_mousewheel)
            scrollable_frame.bind('<Enter>', _bind_to_mousewheel)
            scrollable_frame.bind('<Leave>', _unbind_from_mousewheel)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Filas de pagos (dentro del scrollable_frame)
            zebra_colors = ("#ffffff", "#f8f9fa")
            for row_idx, payment in enumerate(payments):
                bg_color = zebra_colors[row_idx % 2]
                
                row_frame = tk.Frame(scrollable_frame, bg=bg_color, relief="solid", bd=1)
                row_frame.pack(fill="x", pady=(0, 2))
                
                # Fecha de pago
                fecha_pago = payment.get("fecha_pago", "N/A")
                fecha_label = tk.Label(
                    row_frame,
                    text=fecha_pago,
                    font=("Segoe UI", 10),
                    bg=bg_color,
                    fg="#333",
                    anchor="w",
                    padx=10,
                    pady=8
                )
                fecha_label.grid(row=0, column=0, sticky="ew")
                
                # Monto
                monto = float(payment.get("monto", 0))
                monto_label = tk.Label(
                    row_frame,
                    text=f"${monto:,.0f}",
                    font=("Segoe UI", 10, "bold"),
                    bg=bg_color,
                    fg="#4caf50",
                    anchor="w",
                    padx=10,
                    pady=8
                )
                monto_label.grid(row=0, column=1, sticky="ew")
                
                # Método de pago
                metodo = payment.get("metodo", "N/A")
                metodo_label = tk.Label(
                    row_frame,
                    text=metodo,
                    font=("Segoe UI", 10),
                    bg=bg_color,
                    fg="#666",
                    anchor="w",
                    padx=10,
                    pady=8
                )
                metodo_label.grid(row=0, column=2, sticky="ew")
                
                # Observaciones
                observaciones = payment.get("observaciones", "")
                if not observaciones:
                    observaciones = "-"
                obs_label = tk.Label(
                    row_frame,
                    text=observaciones,
                    font=("Segoe UI", 10),
                    bg=bg_color,
                    fg="#666",
                    anchor="w",
                    padx=10,
                    pady=8,
                    wraplength=380,
                    justify="left"
                )
                obs_label.grid(row=0, column=3, sticky="ew")
                
                # Fecha de registro (creado_en)
                creado_en = payment.get("creado_en", "")
                if creado_en:
                    try:
                        # Formatear fecha ISO a formato legible
                        fecha_dt = datetime.fromisoformat(creado_en.replace('Z', '+00:00'))
                        creado_en = fecha_dt.strftime("%d/%m/%Y %H:%M")
                    except:
                        pass
                else:
                    creado_en = "N/A"
                
                creado_label = tk.Label(
                    row_frame,
                    text=creado_en,
                    font=("Segoe UI", 9),
                    bg=bg_color,
                    fg="#999",
                    anchor="w",
                    padx=10,
                    pady=8
                )
                creado_label.grid(row=0, column=4, sticky="ew")
                
                # Configurar columnas
                for idx, (_, width) in enumerate(headers):
                    row_frame.grid_columnconfigure(idx, weight=1 if idx == 3 else 0, minsize=width)
        
        # Botones inferiores
        buttons_frame = tk.Frame(main_frame, bg="white")
        buttons_frame.pack(fill="x", pady=(15, 0))
        
        close_btn = ModernButton(
            buttons_frame,
            text="Cerrar",
            icon="❌",
            style="secondary",
            command=history_window.destroy
        )
        close_btn.pack(side="right")
    
    def _show_pdf_success_dialog(self, file_path: str, title: str = "PDF generado", message: str = "Ficha PDF generada exitosamente:", payment_data: Dict[str, Any] = None):
        """Muestra un diálogo personalizado con la ruta del archivo PDF generado
        
        Args:
            file_path: Ruta del archivo PDF generado
            title: Título del diálogo
            message: Mensaje a mostrar
            payment_data: Datos del pago (opcional, solo para recibos)
        """
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrar el diálogo (ajustado para evitar la barra de tareas)
        dialog.update_idletasks()
        width = 550
        height = 200
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        available_height = screen_height - 50
        y = (available_height // 2) - (height // 2)
        if y < 0:
            y = 50
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg="white", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Icono y mensaje
        info_frame = tk.Frame(main_frame, bg="white")
        info_frame.pack(fill="x", pady=(0, 15))
        
        # Icono de información
        icon_label = tk.Label(
            info_frame,
            text="ℹ️",
            font=("Segoe UI", 24),
            bg="white",
            fg="#1976d2"
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        # Texto del mensaje
        text_frame = tk.Frame(info_frame, bg="white")
        text_frame.pack(side="left", fill="x", expand=True)
        
        msg_label = tk.Label(
            text_frame,
            text=message,
            font=("Segoe UI", 10),
            bg="white",
            fg="#333",
            anchor="w"
        )
        msg_label.pack(fill="x")
        
        # Campo de entrada con la ruta (seleccionable)
        path_frame = tk.Frame(main_frame, bg="white")
        path_frame.pack(fill="x", pady=(0, 15))
        
        path_entry = tk.Entry(
            path_frame,
            font=("Segoe UI", 9),
            relief="solid",
            bd=1,
            bg="#ffffff",
            fg="#000000",
            selectbackground="#1976d2",
            selectforeground="white",
            readonlybackground="#ffffff",
            insertbackground="#000000"
        )
        path_entry.pack(side="left", fill="x", expand=True, ipady=5)
        # Insertar texto primero, luego configurar como readonly
        path_entry.config(state="normal")
        path_entry.insert(0, file_path)
        path_entry.config(state="readonly")
        # Seleccionar todo el texto para que sea visible y fácil de copiar
        path_entry.select_range(0, tk.END)
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg="white")
        buttons_frame.pack(fill="x")
        
        def copy_to_clipboard():
            dialog.clipboard_clear()
            dialog.clipboard_append(file_path)
            dialog.update()
            copy_btn.config(text="✓ Copiado", bg="#4caf50")
            dialog.after(1500, lambda: copy_btn.config(text="📋 Copiar", bg="#1976d2"))
        
        def open_folder():
            folder_path = os.path.dirname(file_path)
            try:
                if platform.system() == "Windows":
                    # Usar explorer.exe /select para abrir la carpeta y seleccionar el archivo
                    subprocess.Popen(['explorer.exe', '/select,', os.path.normpath(file_path)])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", "-R", file_path])  # -R revela el archivo en Finder
                else:  # Linux
                    # Para Linux, intentar usar el gestor de archivos con selección de archivo
                    try:
                        subprocess.Popen(["xdg-open", os.path.dirname(file_path)])
                    except:
                        subprocess.Popen(["nautilus", "--select", file_path])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la carpeta: {str(e)}")
        
        copy_btn = tk.Button(
            buttons_frame,
            text="📋 Copiar",
            font=("Segoe UI", 9, "bold"),
            bg="#1976d2",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2",
            command=copy_to_clipboard
        )
        copy_btn.pack(side="left", padx=(0, 10))
        
        open_btn = tk.Button(
            buttons_frame,
            text="📂 Abrir carpeta",
            font=("Segoe UI", 9),
            bg="#666",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2",
            command=open_folder
        )
        open_btn.pack(side="left", padx=(0, 10))
        
        # Botón "Enviar por Email" solo si es un recibo y el inquilino tiene email
        send_email_btn = None
        if payment_data:
            tenant_email = self.tenant_data.get("email", "").strip()
            if tenant_email and email_service.is_configured():
                def send_by_email():
                    payment_date = payment_data.get("fecha_pago", "")
                    payment_amount = float(payment_data.get("monto", 0))
                    tenant_name = self.tenant_data.get("nombre", "Inquilino")
                    
                    # Confirmar envío
                    if messagebox.askyesno("Confirmar envío", 
                        f"¿Desea enviar el recibo por email?\n\n"
                        f"Destinatario: {tenant_email}\n"
                        f"Fecha de pago: {payment_date}\n"
                        f"Monto: ${payment_amount:,.0f}"):
                        
                        success, msg = email_service.send_receipt_email(
                            recipient_email=tenant_email,
                            recipient_name=tenant_name,
                            pdf_path=file_path,
                            payment_date=payment_date,
                            payment_amount=payment_amount
                        )
                        
                        if success:
                            messagebox.showinfo("✅ Email enviado", f"El recibo ha sido enviado exitosamente a:\n{tenant_email}")
                        else:
                            messagebox.showerror("❌ Error al enviar", msg)
                
                send_email_btn = tk.Button(
                    buttons_frame,
                    text="📧 Enviar por Email",
                    font=("Segoe UI", 9, "bold"),
                    bg="#4caf50",
                    fg="white",
                    relief="flat",
                    padx=15,
                    pady=5,
                    cursor="hand2",
                    command=send_by_email
                )
                send_email_btn.pack(side="left", padx=(0, 10))
        
        ok_btn = tk.Button(
            buttons_frame,
            text="Aceptar",
            font=("Segoe UI", 9, "bold"),
            bg="#1976d2",
            fg="white",
            relief="flat",
            padx=20,
            pady=5,
            cursor="hand2",
            command=dialog.destroy
        )
        ok_btn.pack(side="right")
        
        # Permitir copiar con Ctrl+C en el campo de entrada
        path_entry.bind("<Control-c>", lambda e: copy_to_clipboard())
        
        # Enfocar el campo de entrada para facilitar selección
        path_entry.focus_set()
        
        # Hacer el diálogo modal
        dialog.wait_window()
    
    def _manage_documents(self):
        """Gestiona documentos del inquilino"""
        messagebox.showinfo("Info", "Gestión de documentos en desarrollo")
    
    def _register_payment(self):
        if hasattr(self, 'on_register_payment') and self.on_register_payment:
            self.on_register_payment(self.tenant_data)
        else:
            messagebox.showinfo("Navegación", "No se pudo navegar al módulo de pagos.")
    
    def _generate_receipt(self):
        """Muestra un selector de pagos para generar recibos"""
        tenant_id = self.tenant_data.get("id")
        if not tenant_id:
            messagebox.showwarning("Advertencia", "No se puede generar recibo: ID de inquilino no disponible.")
            return
        
        # Recargar datos de pagos para asegurar que estén actualizados
        payment_service._load_data()
        
        # Obtener todos los pagos del inquilino
        payments = payment_service.get_payments_by_tenant(tenant_id)
        
        if not payments:
            messagebox.showinfo("Sin pagos", "Este inquilino no tiene pagos registrados para generar recibos.")
            return
        
        # Crear ventana modal de selección
        selection_window = tk.Toplevel(self)
        selection_window.title(f"Generar Recibo - {self.tenant_data.get('nombre', 'Inquilino')}")
        selection_window.transient(self)
        selection_window.grab_set()
        
        # Configurar tamaño y centrar (aumentado el tamaño)
        selection_window.update_idletasks()
        width = 700
        height = 650  # Aumentado de 500 a 650
        screen_width = selection_window.winfo_screenwidth()
        screen_height = selection_window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        available_height = screen_height - 50
        y = (available_height // 2) - (height // 2)
        if y < 0:
            y = 50
        selection_window.geometry(f"{width}x{height}+{x}+{y}")
        selection_window.configure(bg="white")
        
        # Frame principal
        main_frame = tk.Frame(selection_window, bg="white", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Seleccione el pago para generar recibo",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg="#1976d2"
        )
        title_label.pack(pady=(0, 15))
        
        # Frame para la lista con scroll
        list_container = tk.Frame(main_frame, bg="white")
        list_container.pack(fill="both", expand=True)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(list_container, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        def on_canvas_configure(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        
        # Scroll con mouse mejorado - funciona en toda el área de la ventana
        def _on_mousewheel(event):
            try:
                # Verificar que el canvas todavía existe antes de hacer scroll
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                # El canvas ya no existe, hacer unbind para evitar más errores
                try:
                    selection_window.unbind_all("<MouseWheel>")
                except:
                    pass
        
        # Bind scroll a múltiples elementos para que funcione en toda el área
        def _bind_to_mousewheel(event):
            selection_window.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            selection_window.unbind_all("<MouseWheel>")
        
        # Bind scroll a la ventana completa, canvas, scrollable_frame, y list_container
        selection_window.bind('<Enter>', _bind_to_mousewheel)
        selection_window.bind('<Leave>', _unbind_from_mousewheel)
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        list_container.bind('<Enter>', _bind_to_mousewheel)
        list_container.bind('<Leave>', _unbind_from_mousewheel)
        scrollable_frame.bind('<Enter>', _bind_to_mousewheel)
        scrollable_frame.bind('<Leave>', _unbind_from_mousewheel)
        
        # Bind también a las tarjetas de pago
        def bind_scroll_to_widget(widget):
            widget.bind('<Enter>', _bind_to_mousewheel)
            widget.bind('<Leave>', _unbind_from_mousewheel)
            for child in widget.winfo_children():
                bind_scroll_to_widget(child)
        
        # Aplicar después de crear las tarjetas
        def apply_scroll_bindings():
            bind_scroll_to_widget(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Ordenar pagos por fecha (más reciente primero)
        try:
            payments.sort(key=lambda x: datetime.strptime(x.get("fecha_pago", "01/01/1900"), "%d/%m/%Y"), reverse=True)
        except Exception:
            pass
        
        # Mostrar cada pago como una tarjeta
        for payment in payments:
            payment_card = tk.Frame(scrollable_frame, bg="#f8f9fa", relief="solid", bd=1)
            payment_card.pack(fill="x", pady=(0, 10), padx=5)
            
            # Contenido de la tarjeta
            card_content = tk.Frame(payment_card, bg="#f8f9fa", padx=15, pady=12)
            card_content.pack(fill="x")
            
            # Información del pago
            fecha_pago = payment.get("fecha_pago", "N/A")
            monto = float(payment.get("monto", 0))
            metodo = payment.get("metodo", "N/A")
            observaciones = payment.get("observaciones", "")
            
            # Fila principal: Fecha y Monto
            row1 = tk.Frame(card_content, bg="#f8f9fa")
            row1.pack(fill="x", pady=(0, 5))
            
            fecha_label = tk.Label(
                row1,
                text=f"📅 {fecha_pago}",
                font=("Segoe UI", 11, "bold"),
                bg="#f8f9fa",
                fg="#333"
            )
            fecha_label.pack(side="left")
            
            monto_label = tk.Label(
                row1,
                text=f"💰 ${monto:,.0f}",
                font=("Segoe UI", 11, "bold"),
                bg="#f8f9fa",
                fg="#4caf50"
            )
            monto_label.pack(side="left", padx=(20, 0))
            
            # Fila secundaria: Método y Observaciones
            row2 = tk.Frame(card_content, bg="#f8f9fa")
            row2.pack(fill="x", pady=(0, 8))
            
            metodo_label = tk.Label(
                row2,
                text=f"Método: {metodo}",
                font=("Segoe UI", 10),
                bg="#f8f9fa",
                fg="#666"
            )
            metodo_label.pack(side="left")
            
            if observaciones:
                obs_label = tk.Label(
                    row2,
                    text=f"• {observaciones}",
                    font=("Segoe UI", 10),
                    bg="#f8f9fa",
                    fg="#666"
                )
                obs_label.pack(side="left", padx=(15, 0))
            
            # Botones: Generar Recibo y Enviar por Email
            btn_frame = tk.Frame(card_content, bg="#f8f9fa")
            btn_frame.pack(fill="x")
            
            # Frame para los botones (alineados a la derecha)
            buttons_container = tk.Frame(btn_frame, bg="#f8f9fa")
            buttons_container.pack(side="right")
            
            # Capturar el pago correctamente para evitar problemas de closure en el lambda
            def make_receipt_command(p):
                return lambda: self._generate_payment_receipt(p, selection_window)
            
            def make_send_email_command(p):
                return lambda: self._send_payment_receipt_email(p)
            
            # Botón "Enviar por Email" (solo si el inquilino tiene email y está configurado)
            tenant_email = self.tenant_data.get("email", "").strip()
            if tenant_email and email_service.is_configured():
                send_email_btn = ModernButton(
                    buttons_container,
                    text="📧 Enviar por Email",
                    icon="📧",
                    style="secondary",
                    small=True,
                    command=make_send_email_command(payment)
                )
                send_email_btn.pack(side="right", padx=(0, 8))
            
            # Botón "Generar Recibo"
            generate_btn = ModernButton(
                buttons_container,
                text="Generar Recibo",
                icon=Icons.RECEIPT,
                style="primary",
                small=True,
                command=make_receipt_command(payment)
            )
            generate_btn.pack(side="right")
            
            # Bind scroll a cada tarjeta de pago y todos sus elementos internos
            for widget_item in [payment_card, card_content, row1, row2, btn_frame]:
                widget_item.bind('<Enter>', _bind_to_mousewheel)
                widget_item.bind('<Leave>', _unbind_from_mousewheel)
            for label_item in [fecha_label, monto_label, metodo_label]:
                label_item.bind('<Enter>', _bind_to_mousewheel)
                label_item.bind('<Leave>', _unbind_from_mousewheel)
            if observaciones:
                obs_label.bind('<Enter>', _bind_to_mousewheel)
                obs_label.bind('<Leave>', _unbind_from_mousewheel)
        
        # Aplicar bindings de scroll después de crear todas las tarjetas
        apply_scroll_bindings()
        
        # Función para limpiar bindings antes de cerrar
        def cleanup_and_destroy():
            try:
                selection_window.unbind_all("<MouseWheel>")
            except:
                pass
            selection_window.destroy()
        
        # Botón cerrar
        buttons_frame = tk.Frame(main_frame, bg="white")
        buttons_frame.pack(fill="x", pady=(15, 0))
        
        close_btn = ModernButton(
            buttons_frame,
            text="Cerrar",
            icon="❌",
            style="secondary",
            command=cleanup_and_destroy
        )
        close_btn.pack(side="right")
    
    def _send_payment_receipt_email(self, payment: Dict[str, Any]):
        """Envía un recibo de pago específico por email"""
        tenant_email = self.tenant_data.get("email", "").strip()
        tenant_name = self.tenant_data.get("nombre", "Inquilino")
        payment_date = payment.get("fecha_pago", "")
        payment_amount = float(payment.get("monto", 0))
        
        # Verificar que el inquilino tenga email
        if not tenant_email:
            messagebox.showwarning(
                "Email no disponible",
                f"El inquilino {tenant_name} no tiene un email registrado.\n\n"
                f"Por favor, edite el inquilino y agregue su email para poder enviar recibos."
            )
            return
        
        # Verificar que el email esté configurado
        if not email_service.is_configured():
            messagebox.showwarning(
                "Email no configurado",
                "El sistema de email no está configurado.\n\n"
                "Por favor, configure las credenciales SMTP en Configuración antes de enviar emails."
            )
            return
        
        # Construir la ruta esperada del recibo
        nombre = payment.get("nombre_inquilino", tenant_name).replace(" ", "_")
        fecha = payment_date.replace("/", "-")
        base_filename = f"recibo_pago_{nombre}_{fecha}"
        folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../recibos'))
        pdf_path = os.path.join(folder, f"{base_filename}.pdf")
        
        # Verificar si el archivo existe
        if not os.path.exists(pdf_path):
            # Si no existe, ofrecer generarlo primero
            response = messagebox.askyesno(
                "Recibo no encontrado",
                f"No se encontró el recibo del pago del {payment_date}.\n\n"
                f"¿Desea generar el recibo ahora antes de enviarlo?"
            )
            if response:
                self._generate_payment_receipt(payment, None)
                # Verificar nuevamente si se generó
                if not os.path.exists(pdf_path):
                    messagebox.showerror("Error", "No se pudo generar el recibo. Por favor intente generar el recibo primero.")
                    return
            else:
                return
        
        # Confirmar envío
        confirm_msg = f"¿Desea enviar el recibo del pago del {payment_date} por email?\n\n"
        confirm_msg += f"Destinatario: {tenant_email}\n"
        confirm_msg += f"Monto: ${payment_amount:,.0f}"
        
        if not messagebox.askyesno("Confirmar envío", confirm_msg):
            return
        
        # Enviar email
        success, msg = email_service.send_receipt_email(
            recipient_email=tenant_email,
            recipient_name=tenant_name,
            pdf_path=pdf_path,
            payment_date=payment_date,
            payment_amount=payment_amount
        )
        
        if success:
            messagebox.showinfo("✅ Email enviado", f"El recibo ha sido enviado exitosamente a:\n{tenant_email}")
        else:
            messagebox.showerror("❌ Error al enviar", msg)
    
    def _generate_payment_receipt(self, payment: Dict[str, Any], parent_window=None):
        """Genera el recibo PDF de un pago específico"""
        import os
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from datetime import datetime
        
        try:
            # Obtener datos del inquilino
            tenant = self.tenant_data
            
            # Crear carpeta de recibos si no existe
            folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../recibos'))
            os.makedirs(folder, exist_ok=True)
            
            # Nombre del archivo base
            nombre = payment.get("nombre_inquilino", tenant.get("nombre", "Inquilino")).replace(" ", "_")
            fecha = payment.get("fecha_pago", "").replace("/", "-")
            base_filename = f"recibo_pago_{nombre}_{fecha}"
            filepath = os.path.join(folder, f"{base_filename}.pdf")
            
            # Verificar si el archivo existe y está bloqueado
            if os.path.exists(filepath):
                try:
                    # Intentar abrir el archivo para verificar si está bloqueado
                    test_file = open(filepath, 'r+b')
                    test_file.close()
                    # Si no está bloqueado, sobrescribiremos el archivo (comportamiento normal)
                    # No hacemos nada, simplemente usamos el mismo filepath
                except (IOError, PermissionError):
                    # El archivo está bloqueado (probablemente abierto en un visor PDF)
                    # Mostrar mensaje amigable al usuario
                    messagebox.showwarning(
                        "Archivo en uso",
                        f"El recibo ya existe y está abierto en otro programa.\n\n"
                        f"Por favor, cierre el archivo:\n{filepath}\n\n"
                        f"Luego intente generar el recibo nuevamente."
                    )
                    return  # No generar nuevo PDF, simplemente retornar
            
            # Obtener el número real del apartamento
            apt_display = "N/A"
            apt_id = tenant.get('apartamento', '')
            if apt_id:
                try:
                    apt = apartment_service.get_apartment_by_id(int(apt_id))
                    if apt and 'number' in apt:
                        apt_display = apt['number']
                    else:
                        apt_display = str(apt_id)
                except Exception:
                    apt_display = str(apt_id)
            
            # Generar PDF
            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter
            
            # Logo placeholder
            c.setFillColorRGB(0.2, 0.4, 0.7)
            c.rect(40, height-80, 80, 40, fill=1)
            c.setFillColorRGB(1,1,1)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height-60, "LOGO")
            
            # Encabezado
            c.setFillColorRGB(0,0,0)
            c.setFont("Helvetica-Bold", 18)
            c.drawString(140, height-60, "RECIBO DE PAGO DE ARRENDAMIENTO")
            c.setFont("Helvetica", 10)
            c.drawString(140, height-80, f"Emitido: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            
            # Datos del inquilino y pago
            y = height-120
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "Datos del Inquilino:")
            c.setFont("Helvetica", 11)
            y -= 18
            c.drawString(50, y, f"Nombre: {payment.get('nombre_inquilino', tenant.get('nombre', ''))}")
            y -= 15
            c.drawString(50, y, f"Apartamento: {apt_display}")
            y -= 15
            c.drawString(50, y, f"Documento: {tenant.get('numero_documento', 'N/A')}")
            y -= 25
            
            # Detalles del pago
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "Detalles del Pago:")
            c.setFont("Helvetica", 11)
            y -= 18
            c.drawString(50, y, f"Fecha de pago: {payment.get('fecha_pago', '')}")
            y -= 15
            c.drawString(50, y, f"Monto: ${payment.get('monto', 0):,.2f}")
            y -= 15
            c.drawString(50, y, f"Método: {payment.get('metodo', '')}")
            y -= 15
            obs = payment.get('observaciones', '')
            if obs:
                c.drawString(50, y, f"Observaciones: {obs}")
            else:
                c.drawString(50, y, "Observaciones: -")
            y -= 30
            
            # Certificación
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(40, y, "Este recibo certifica que el inquilino ha realizado el pago correspondiente al arriendo en la fecha indicada.")
            y -= 40
            
            # Firmas
            c.setFont("Helvetica", 10)
            c.drawString(40, y, "Firma administrador: _____________________________")
            c.drawString(320, y, "Firma inquilino: _____________________________")
            
            c.save()
            
            # Cerrar ventana de selección si está abierta
            if parent_window:
                parent_window.destroy()
            
            # Mostrar diálogo de éxito con ruta copiable y opción de enviar por email
            self._show_pdf_success_dialog(
                filepath, 
                title="Recibo generado", 
                message="Recibo PDF generado exitosamente:",
                payment_data=payment  # Pasar datos del pago para enviar por email
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el recibo: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _send_notification(self):
        """Envía recordatorio de pago al inquilino (funcionalidad futura)"""
        messagebox.showinfo("Info", "Envío de recordatorios de pago en desarrollo.\n\nEsta función permitirá enviar recordatorios automáticos a los inquilinos sobre pagos pendientes.")

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
        # Formatear depósito
        deposito = tenant.get('deposito', '')
        deposito_display = "No registrado"
        if deposito:
            try:
                deposito_num = float(deposito)
                deposito_display = f"${deposito_num:,.0f}"
            except:
                deposito_display = str(deposito)
        c.drawString(50, y, f"Depósito: {deposito_display}")
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
        
        # Mostrar diálogo personalizado con ruta copiable
        self._show_pdf_success_dialog(filepath)