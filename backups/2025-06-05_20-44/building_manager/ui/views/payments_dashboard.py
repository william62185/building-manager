import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from typing import Any, Dict, List, Optional
from datetime import date, timedelta
from decimal import Decimal

from ...services.payment_service import PaymentService
from ...services.tenant_service import TenantService
from ..components import MetricsCard


class PaymentsDashboard(ttk.Frame):
    """Dashboard específico para la gestión de pagos con estética Material Design."""
    
    def __init__(self, master: Any):
        super().__init__(master)
        self.payment_service = PaymentService()
        self.tenant_service = TenantService()
        
        # Variable para el modo oscuro
        self.dark_mode = False
        
        # Lista para almacenar referencias de botones para actualización dinámica
        self.module_buttons = []
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        """Configura la interfaz del dashboard de pagos."""
        # Contenedor principal OPTIMIZADO PARA PANTALLA COMPLETA
        self.configure(padding="4")

        # BOTÓN DE RETORNO SIMPLE
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 8))
        
        back_btn = ttk.Button(
            header_frame,
            text="← Volver al Dashboard",
            command=self._go_back_to_main,
            bootstyle="outline-secondary"
        )
        back_btn.pack(side=tk.RIGHT)

        # RESUMEN DE PAGOS (4 cards horizontales)
        metrics_section = ttk.LabelFrame(self, text="📊 Resumen de Pagos del Mes", padding="10")
        metrics_section.pack(fill=tk.X, pady=(0, 6))

        all_metrics = ttk.Frame(metrics_section)
        all_metrics.pack(fill=tk.X)

        # Métricas de pagos - ESPACIADO REDUCIDO
        self.monthly_total = MetricsCard(
            all_metrics,
            title="Pagos del Mes",
            value="$0.00",
            subtitle="Total recaudado",
            icon="💰",
            color="success"
        )
        self.monthly_total.pack(side=tk.LEFT, expand=True, padx=2)

        self.payments_received = MetricsCard(
            all_metrics,
            title="Pagos Recibidos",
            value="0",
            subtitle="Pagos completados",
            icon="✅",
            color="primary"
        )
        self.payments_received.pack(side=tk.LEFT, expand=True, padx=2)

        self.pending_payments = MetricsCard(
            all_metrics,
            title="Pagos Pendientes",
            value="0",
            subtitle="Por recibir",
            icon="⏰",
            color="warning"
        )
        self.pending_payments.pack(side=tk.LEFT, expand=True, padx=2)

        self.average_payment = MetricsCard(
            all_metrics,
            title="Promedio por Pago",
            value="$0.00",
            subtitle="Monto promedio",
            icon="📊",
            color="info"
        )
        self.average_payment.pack(side=tk.LEFT, expand=True, padx=2)

        # ACCIONES PRINCIPALES (Grid 2x3) - MUCHO MÁS GRANDES
        actions_section = ttk.LabelFrame(self, text="🚀 Acciones Principales", padding="8")
        actions_section.pack(fill=tk.BOTH, expand=True, pady=(4, 6))

        # Primera fila de acciones principales - MUCHO MÁS GRANDES
        first_row = ttk.Frame(actions_section)
        first_row.pack(fill=tk.BOTH, expand=True, pady=(2, 4))

        # Crear botones con sombra personalizada - COLORES ESPECÍFICOS PARA PAGOS
        self._create_shadow_button(
            first_row, "💵 Registrar Nuevo Pago\nAgregar pago recibido", 
            "#4CAF50", "white", self._register_payment, "register_payment"
        )

        self._create_shadow_button(
            first_row, "🔍 Buscar Pagos\nBúsqueda avanzada", 
            "#2196F3", "white", self._search_payments, "search_payments"
        )

        self._create_shadow_button(
            first_row, "📄 Generar Recibos\nCrear recibos PDF", 
            "#FF9800", "white", self._generate_receipts, "generate_receipts"
        )

        # Segunda fila de acciones principales
        second_row = ttk.Frame(actions_section)
        second_row.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        self._create_shadow_button(
            second_row, "📋 Pagos Pendientes\nGestionar morosos", 
            "#F44336", "white", self._pending_payments, "pending_payments"
        )

        self._create_shadow_button(
            second_row, "📊 Historial de Pagos\nVer historial completo", 
            "#9C27B0", "white", self._payment_history, "payment_history"
        )

        self._create_shadow_button(
            second_row, "⚙️ Configurar Pagos\nAjustes del sistema", 
            "#607D8B", "white", self._payment_settings, "payment_settings"
        )

        # ACCESO RÁPIDO (3 cards horizontales)
        quick_access_section = ttk.LabelFrame(self, text="⚡ Acceso Rápido", padding="8")
        quick_access_section.pack(fill=tk.X, pady=(4, 0))

        # Fila de acceso rápido
        quick_row = ttk.Frame(quick_access_section)
        quick_row.pack(fill=tk.BOTH, expand=True, pady=(2, 2))

        self._create_shadow_button(
            quick_row, "📱 Pagos del Día\nResumen diario", 
            "#00BCD4", "white", self._daily_payments, "daily_payments"
        )

        self._create_shadow_button(
            quick_row, "📈 Estadísticas\nGráficos y métricas", 
            "#673AB7", "white", self._payment_stats, "payment_stats"
        )

        self._create_shadow_button(
            quick_row, "📤 Exportar Datos\nExcel, PDF, reportes", 
            "#795548", "white", self._export_data, "export_data"
        )

    def _create_shadow_button(self, parent, text, bg_color, fg_color, command, module_id=None):
        """Crea un botón con efecto de sombra y tipografía mejorada - IDÉNTICO AL DASHBOARD."""
        # Frame contenedor para el efecto de sombra
        shadow_frame = ttk.Frame(parent)
        shadow_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4, pady=2)
        
        # Frame de sombra (fondo gris desplazado)
        shadow = tk.Frame(
            shadow_frame,
            bg="#404040",  # Color de sombra
            relief="flat"
        )
        shadow.place(x=3, y=3, relwidth=1, relheight=1)
        
        # Frame principal del botón para contener el contenido
        button_frame = tk.Frame(
            shadow_frame,
            bg=bg_color,
            relief="raised",
            bd=2,
            cursor="hand2"
        )
        button_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Separar el texto en líneas
        lines = text.split('\n')
        module_name = lines[0] if lines else text
        description = lines[1] if len(lines) > 1 else ""
        
        # Contenedor interno para centrar el contenido
        content_frame = tk.Frame(button_frame, bg=bg_color)
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título del módulo (más grande)
        title_label = tk.Label(
            content_frame,
            text=module_name,
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 16, "bold"),
            cursor="hand2"
        )
        title_label.pack()
        
        # Descripción (más pequeña y diferente estilo)
        desc_label = None
        if description:
            desc_label = tk.Label(
                content_frame,
                text=description,
                bg=bg_color,
                fg=fg_color,
                font=("Segoe UI", 11, "normal"),
                cursor="hand2"
            )
            desc_label.pack(pady=(2, 0))
        
        # FORZAR COLORES INMEDIATAMENTE - MISMA LÓGICA DEL DASHBOARD
        for _ in range(3):
            button_frame.configure(bg=bg_color)
            content_frame.configure(bg=bg_color)  
            title_label.configure(bg=bg_color, fg=fg_color)
            if desc_label:
                desc_label.configure(bg=bg_color, fg=fg_color)
                
        # Función para forzar colores después del renderizado
        def force_colors_delayed():
            try:
                button_frame.configure(bg=bg_color)
                content_frame.configure(bg=bg_color)
                title_label.configure(bg=bg_color, fg=fg_color)
                if desc_label:
                    desc_label.configure(bg=bg_color, fg=fg_color)
            except:
                pass
                
        # Programar aplicaciones adicionales en diferentes momentos
        self.after(10, force_colors_delayed)
        self.after(50, force_colors_delayed)
        self.after(100, force_colors_delayed)
        
        # Hacer que todos los elementos respondan al clic
        def on_button_click(event=None):
            try:
                command()
            except Exception as e:
                print(f"Error ejecutando comando del botón {module_id}: {e}")
                import traceback
                traceback.print_exc()
            
        # Vincular eventos de manera más robusta
        for widget in [button_frame, content_frame, title_label]:
            widget.bind("<Button-1>", on_button_click)
            widget.bind("<ButtonRelease-1>", on_button_click)
        
        if desc_label:
            desc_label.bind("<Button-1>", on_button_click)
            desc_label.bind("<ButtonRelease-1>", on_button_click)
        
        # Efectos hover - IDÉNTICOS AL DASHBOARD
        def on_enter(event):
            light_color = self._lighten_color(bg_color)
            button_frame.configure(bg=light_color, relief="raised", bd=3)
            content_frame.configure(bg=light_color)
            title_label.configure(bg=light_color)
            if desc_label:
                desc_label.configure(bg=light_color)
            shadow.configure(bg="#303030")
            
        def on_leave(event):
            button_frame.configure(bg=bg_color, relief="raised", bd=2)
            content_frame.configure(bg=bg_color)
            title_label.configure(bg=bg_color)
            if desc_label:
                desc_label.configure(bg=bg_color)
            shadow.configure(bg="#404040")
            
        # Aplicar eventos hover a todos los elementos
        widgets_to_bind = [button_frame, content_frame, title_label]
        if desc_label:
            widgets_to_bind.append(desc_label)
            
        for widget in widgets_to_bind:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    def _lighten_color(self, color):
        """Aclara un color hex - IDÉNTICO AL DASHBOARD."""
        color_map = {
            "#4CAF50": "#66BB6A",  # Verde claro
            "#2196F3": "#42A5F5",  # Azul claro
            "#FF9800": "#FFB74D",  # Naranja claro
            "#F44336": "#EF5350",  # Rojo claro
            "#9C27B0": "#AB47BC",  # Púrpura claro
            "#607D8B": "#78909C",  # Gris azulado claro
            "#00BCD4": "#26C6DA",  # Cian claro
            "#673AB7": "#7986CB",  # Indigo claro
            "#795548": "#8D6E63"   # Marrón claro
        }
        return color_map.get(color, color)

    def _load_data(self):
        """Carga los datos del dashboard de pagos."""
        try:
            # Obtener fechas del mes actual
            today = date.today()
            first_day = date(today.year, today.month, 1)
            if today.month == 12:
                last_day = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                last_day = date(today.year, today.month + 1, 1) - timedelta(days=1)
            
            # Obtener métricas de pagos del mes actual
            payment_metrics = self.payment_service.get_payment_metrics(first_day, last_day)
            
            monthly_total = payment_metrics.get("total_amount", Decimal("0"))
            payments_received_count = payment_metrics.get("completed_payments", 0)
            pending_payments_count = payment_metrics.get("total_payments", 0) - payments_received_count
            
            # Calcular promedio
            average = monthly_total / payments_received_count if payments_received_count > 0 else Decimal("0")
            
            # Actualizar métricas
            self.monthly_total.update_value(f"${monthly_total:,.2f}")
            self.payments_received.update_value(str(payments_received_count))
            self.pending_payments.update_value(str(pending_payments_count))
            self.average_payment.update_value(f"${average:,.2f}")
            
        except Exception as e:
            print(f"Error al cargar datos del dashboard de pagos: {e}")
            # Valores por defecto en caso de error
            self.monthly_total.update_value("$0.00")
            self.payments_received.update_value("0")
            self.pending_payments.update_value("0")
            self.average_payment.update_value("$0.00")

    def _go_back_to_main(self):
        """Vuelve al dashboard principal."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('dashboard')

    # FUNCIONES DE NAVEGACIÓN A CADA CARD
    def _register_payment(self):
        """Navega al formulario de registro de pagos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('payments')  # Navega a la vista actual de pagos

    def _search_payments(self):
        """Navega a la búsqueda avanzada de pagos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('payments_search')

    def _generate_receipts(self):
        """Navega a la generación de recibos."""
        messagebox.showinfo("Generar Recibos", "Función de generación de recibos en desarrollo...")

    def _pending_payments(self):
        """Navega a la gestión de pagos pendientes."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('payments_pending')

    def _payment_history(self):
        """Navega al historial completo de pagos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('payments_history')

    def _payment_settings(self):
        """Navega a la configuración de pagos."""
        messagebox.showinfo("Configuración", "Función de configuración de pagos en desarrollo...")

    def _daily_payments(self):
        """Navega al resumen de pagos del día."""
        messagebox.showinfo("Pagos del Día", "Función de pagos del día en desarrollo...")

    def _payment_stats(self):
        """Navega a las estadísticas de pagos."""
        messagebox.showinfo("Estadísticas", "Función de estadísticas en desarrollo...")

    def _export_data(self):
        """Navega a la exportación de datos."""
        messagebox.showinfo("Exportar Datos", "Función de exportación en desarrollo...")

    def refresh(self):
        """Actualiza los datos del dashboard."""
        self._load_data() 