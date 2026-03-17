"""
Vista completa de reportes de pagos para Building Manager Pro
Sistema escalable con múltiples tipos de reportes específicos de pagos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, List, Any, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import csv
from pathlib import Path

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton, create_rounded_button, get_module_colors
from manager.app.ui.views.register_expense_view import DatePickerWidget
from manager.app.services.payment_service import payment_service
from manager.app.services.tenant_service import tenant_service
from manager.app.services.apartment_service import apartment_service


# Verde más oscuro del módulo para iconos, títulos y botones (contraste)
DARK_GREEN = "#166534"
# Fondo sólido de las cards (verde claro) para que no queden transparentes
CARD_BG = "#dcfce7"


class PaymentReportsView(tk.Frame):
    """Vista completa de reportes de pagos del sistema"""
    
    def __init__(self, parent, on_back: Callable = None, on_navigate_to_dashboard: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.on_back = on_back
        self.on_navigate_to_dashboard = on_navigate_to_dashboard  # Callback para navegar al dashboard
        
        # Recargar datos antes de generar reportes
        self._reload_all_data()
        
        self._create_layout()
    
    def _reload_all_data(self):
        """Recarga todos los datos necesarios para los reportes"""
        try:
            payment_service._load_data()
            tenant_service._load_data()
            apartment_service._load_data()
        except Exception as e:
            print(f"Error al recargar datos: {e}")
    
    def _create_layout(self):
        """Crea el layout principal de la vista de reportes"""
        cb = self._content_bg
        theme = theme_manager.themes[theme_manager.current_theme]
        # Header
        header = tk.Frame(self, bg=cb, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=cb)
        title_frame.pack(side="left", padx=15, fill="y", expand=True)
        
        tk.Label(
            title_frame,
            text="📊 Reportes de Pagos",
            font=("Segoe UI", 18, "bold"),
            bg=cb,
            fg=theme["text_primary"]
        ).pack(side="left", pady=15)
        
        # Frame para botones de navegación (alineados a la derecha)
        buttons_frame = tk.Frame(header, bg=cb)
        buttons_frame.pack(side="right", padx=15, pady=15)
        
        if self.on_back:
            self._create_navigation_buttons(buttons_frame, self.on_back)
        
        # Contenedor principal sin scroll (sin fondo blanco)
        main_container = tk.Frame(self, bg=cb)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Contenido de reportes directamente en el contenedor principal
        self._create_reports_content(main_container)
    
    def _create_reports_content(self, parent):
        """Crea el contenido de los reportes"""
        cb = self._content_bg
        # Contenedor principal que usa todo el espacio disponible (sin fondo blanco)
        cards_container = tk.Frame(parent, bg=cb)
        cards_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Grid de cards - 4 columnas que se ajustan al espacio disponible
        cards_grid = tk.Frame(cards_container, bg=cb)
        cards_grid.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Configurar grid para que las columnas se distribuyan equitativamente (4 columnas)
        cards_grid.columnconfigure(0, weight=1, uniform="cards", minsize=200)
        cards_grid.columnconfigure(1, weight=1, uniform="cards", minsize=200)
        cards_grid.columnconfigure(2, weight=1, uniform="cards", minsize=200)
        cards_grid.columnconfigure(3, weight=1, uniform="cards", minsize=200)
        
        # Definir los reportes específicos de pagos (solo los 4 que se mantienen)
        reports = [
            ("👤 Reporte por Inquilino",
             "Historial completo de pagos de un inquilino con estadísticas.",
             self._generate_tenant_payments_report),
            ("💳 Reporte por Método de Pago",
             "Análisis de pagos agrupados por método de pago.",
             self._generate_payment_method_report),
            ("⚠️ Reporte de Pagos Pendientes",
             "Lista de inquilinos con pagos pendientes y días de mora.",
             self._generate_pending_payments_report),
            ("🏢 Reporte por Apartamento",
             "Análisis de pagos agrupados por apartamento.",
             self._generate_apartment_payments_report),
        ]
        
        # Colocar cards en grid 4 columnas (2 filas de 4 cards)
        row = 0
        col = 0
        for title, description, command in reports:
            card = self._create_report_card(
                cards_grid,
                title,
                description,
                command
            )
            card.grid(row=row, column=col, padx=10, pady=8, sticky="nsew")
            
            # Avanzar a la siguiente posición (4 columnas)
            col += 1
            if col >= 4:
                col = 0
                row += 1
        
        # Configurar las filas para que se distribuyan equitativamente (2 filas) - altura aumentada
        for r in range(row + 1):
            cards_grid.rowconfigure(r, weight=1, uniform="rows", minsize=200)
    
    def _create_report_card(self, parent, title, description, command):
        """Crea una tarjeta de reporte con fondo sólido (CARD_BG), verde oscuro para icono, título y botón."""
        theme = theme_manager.themes[theme_manager.current_theme]
        card_bg = CARD_BG
        card = tk.Frame(
            parent,
            bg=card_bg,
            relief="raised",
            bd=2
        )
        
        content = tk.Frame(card, bg=card_bg)
        content.pack(fill="both", expand=True, padx=14, pady=12)
        
        title_frame = tk.Frame(content, bg=card_bg)
        title_frame.pack(anchor="w", pady=(0, 6), fill="x")
        
        # Icono y título en verde oscuro
        title_label = tk.Label(
            title_frame,
            text=title,
            font=("Segoe UI", 13, "bold"),
            bg=card_bg,
            fg=DARK_GREEN,
            anchor="w",
            justify="left",
            wraplength=1
        )
        title_label.pack(anchor="w", fill="x")
        
        # Descripción con color de texto del tema
        desc_label = tk.Label(
            content,
            text=description,
            font=("Segoe UI", 9),
            bg=card_bg,
            fg=theme.get("text_secondary", "#666"),
            justify="left",
            anchor="w",
            wraplength=1
        )
        desc_label.pack(anchor="w", pady=(0, 8), fill="x", expand=True)
        
        # Botón con fondo verde oscuro (contraste) y hover suave
        btn_frame = tk.Frame(content, bg=card_bg)
        btn_frame.pack(fill="x", side="bottom", pady=(4, 0))
        
        btn_green_hover = "#15803d"
        btn = tk.Button(
            btn_frame,
            text="Generar Reporte",
            font=("Segoe UI", 9, "bold"),
            bg=DARK_GREEN,
            fg="white",
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=command
        )
        btn.pack(fill="x")
        btn.bind("<Enter>", lambda e: btn.config(bg=btn_green_hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=DARK_GREEN))
        
        def update_wraplength(event=None):
            if event:
                card_width = card.winfo_width()
                if card_width > 20:
                    available_width = card_width - 28
                    title_label.config(wraplength=max(available_width, 100))
                    desc_label.config(wraplength=max(available_width, 100))
        
        card.bind("<Configure>", update_wraplength)
        
        # Hover en toda el área del card: Enter en card y todos los hijos; Leave solo en el card
        hover_bg = "#bbf7d0"
        def on_enter(event):
            card.configure(bg=hover_bg)
            content.configure(bg=hover_bg)
            title_frame.configure(bg=hover_bg)
            title_label.configure(bg=hover_bg)
            desc_label.configure(bg=hover_bg)
            btn_frame.configure(bg=hover_bg)
        
        def on_leave(event):
            # Solo quitar hover cuando el ratón sale del card (no al pasar entre hijos)
            card.configure(bg=card_bg)
            content.configure(bg=card_bg)
            title_frame.configure(bg=card_bg)
            title_label.configure(bg=card_bg)
            desc_label.configure(bg=card_bg)
            btn_frame.configure(bg=card_bg)
        
        def bind_enter_to_children(widget):
            widget.bind("<Enter>", on_enter)
            for child in widget.winfo_children():
                bind_enter_to_children(child)
        
        bind_enter_to_children(card)
        card.bind("<Leave>", on_leave)
        
        return card
    
    # ==================== GENERADORES DE REPORTES ====================
    
    def _create_period_selection_window(self, title="Seleccionar Período", on_generate=None, button_color="#22c55e"):
        """Ventana compacta para seleccionar período de reporte (misma UX que reportes de gastos)."""
        period_window = tk.Toplevel(self)
        period_window.title(title)
        period_window.geometry("420x455")
        period_window.transient(self)
        period_window.grab_set()
        period_window.bind("<Escape>", lambda e: period_window.destroy())

        title_label = tk.Label(
            period_window,
            text="Seleccione el período para el reporte:",
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(pady=(10, 6))

        main_container = tk.Frame(period_window)
        main_container.pack(fill="x", padx=20, pady=(4, 6))

        period_type = tk.StringVar(value="specific_month")

        specific_frame = tk.LabelFrame(
            main_container,
            text="Mes y Año Específicos",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=6
        )
        specific_frame.pack(fill="x", pady=(0, 8))

        tk.Radiobutton(
            specific_frame,
            text="Mes y año específicos",
            variable=period_type,
            value="specific_month",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 4))

        month_year_frame = tk.Frame(specific_frame)
        month_year_frame.pack(fill="x", padx=16)

        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 9, current_year + 1)]
        years.reverse()

        tk.Label(month_year_frame, text="Año:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        year_combo = ttk.Combobox(month_year_frame, values=years, width=12, state="readonly")
        year_combo.set(str(current_year))
        year_combo.pack(side="left", padx=(0, 20))
        year_combo.bind("<<ComboboxSelected>>", lambda e: period_type.set("specific_month"))

        months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        tk.Label(month_year_frame, text="Mes:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        month_combo = ttk.Combobox(month_year_frame, values=months, width=15, state="readonly")
        month_combo.set(months[datetime.now().month - 1])
        month_combo.pack(side="left")
        month_combo.bind("<<ComboboxSelected>>", lambda e: period_type.set("specific_month"))

        year_only_frame = tk.LabelFrame(
            main_container,
            text="Año Completo",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=6
        )
        year_only_frame.pack(fill="x", pady=(0, 8))

        tk.Radiobutton(
            year_only_frame,
            text="Año específico completo (todos los meses)",
            variable=period_type,
            value="specific_year",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 4))

        year_only_select_frame = tk.Frame(year_only_frame)
        year_only_select_frame.pack(fill="x", padx=16)

        tk.Label(year_only_select_frame, text="Año:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        year_only_combo = ttk.Combobox(year_only_select_frame, values=years, width=12, state="readonly")
        year_only_combo.set(str(current_year))
        year_only_combo.pack(side="left")
        year_only_combo.bind("<<ComboboxSelected>>", lambda e: period_type.set("specific_year"))

        custom_frame = tk.LabelFrame(
            main_container,
            text="Rango Personalizado",
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=6
        )
        custom_frame.pack(fill="x", pady=(0, 4))

        tk.Radiobutton(
            custom_frame,
            text="Rango de fechas personalizado",
            variable=period_type,
            value="custom",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 4))

        date_range_frame = tk.Frame(custom_frame)
        date_range_frame.pack(fill="x", padx=16, pady=(0, 4))

        row_from = tk.Frame(date_range_frame)
        row_from.pack(fill="x", pady=(0, 6))
        tk.Label(row_from, text="Desde:", font=("Segoe UI", 9), width=8, anchor="w").pack(side="left", padx=(0, 8))
        date_from_entry = DatePickerWidget(row_from, on_change=lambda: period_type.set("custom"))
        date_from_entry.pack(side="left", fill="x", expand=True)

        row_to = tk.Frame(date_range_frame)
        row_to.pack(fill="x")
        tk.Label(row_to, text="Hasta:", font=("Segoe UI", 9), width=8, anchor="w").pack(side="left", padx=(0, 8))
        date_to_entry = DatePickerWidget(row_to, on_change=lambda: period_type.set("custom"))
        date_to_entry.pack(side="left", fill="x", expand=True)

        button_frame = tk.Frame(period_window)
        button_frame.pack(fill="x", pady=(6, 10))

        def generate_wrapper():
            if on_generate:
                on_generate(period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry, period_window)

        tk.Button(
            button_frame,
            text="Generar Reporte",
            font=("Segoe UI", 10, "bold"),
            bg=button_color,
            fg="white",
            relief="flat",
            padx=22,
            pady=6,
            cursor="hand2",
            command=generate_wrapper
        ).pack()

        period_window.after(50, period_window.focus_force)
        return period_window, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry
    
    def _filter_payments_by_period(self, payments, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry):
        """Filtra pagos según el período seleccionado y retorna (filtered_payments, period_name)"""
        filtered = []
        period_name = ""
        months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        period = period_type.get()
        
        if period == "current_month":
            now = datetime.now()
            filtered = [p for p in payments if self._is_this_month(p.get('fecha_pago', ''))]
            period_name = f"{now.strftime('%B %Y')}"
            
        elif period == "current_year":
            filtered = [p for p in payments if self._is_this_year(p.get('fecha_pago', ''))]
            period_name = f"{datetime.now().year}"
            
        elif period == "specific_month":
            # Obtener año y mes seleccionados
            selected_year = year_combo.get()
            selected_month = month_combo.get()
            
            if not selected_year or not selected_month:
                return None, None
            
            # Convertir mes a número
            month_num = months.index(selected_month) + 1
            year_num = int(selected_year)
            
            # Filtrar pagos del mes y año seleccionados
            for payment in payments:
                try:
                    date_str = payment.get('fecha_pago', '')
                    if date_str:
                        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                        if date_obj.year == year_num and date_obj.month == month_num:
                            filtered.append(payment)
                except Exception:
                    pass
            
            period_name = f"{selected_month} {selected_year}"
            
        elif period == "specific_year":
            # Obtener año seleccionado
            selected_year = year_only_combo.get()
            
            if not selected_year:
                return None, None
            
            year_num = int(selected_year)
            
            # Filtrar pagos del año seleccionado (todos los meses)
            for payment in payments:
                try:
                    date_str = payment.get('fecha_pago', '')
                    if date_str:
                        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                        if date_obj.year == year_num:
                            filtered.append(payment)
                except Exception:
                    pass
            
            period_name = f"Año {selected_year}"
            
        else:  # custom
            date_from = date_from_entry.get().strip()
            date_to = date_to_entry.get().strip()
            if not date_from or not date_to:
                return None, None
            try:
                date_from_obj = datetime.strptime(date_from, "%d/%m/%Y")
                date_to_obj = datetime.strptime(date_to, "%d/%m/%Y")
                filtered = [p for p in payments if self._is_in_range(p.get('fecha_pago', ''), date_from_obj, date_to_obj)]
                period_name = f"{date_from} a {date_to}"
            except ValueError:
                return None, None
        
        return filtered, period_name
    
    def _generate_period_report(self):
        """Genera reporte de pagos por período"""
        try:
            self._reload_all_data()
            
            payments = payment_service.get_all_payments()
            
            def on_generate(period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry, period_window):
                filtered, period_name = self._filter_payments_by_period(
                    payments, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry
                )
                
                if filtered is None:
                    messagebox.showerror("Error", "Por favor complete todos los campos requeridos.")
                    return
                
                if not filtered:
                    messagebox.showinfo("Sin datos", f"No hay pagos registrados para el período seleccionado.")
                    period_window.destroy()
                    return
                
                period_window.destroy()
                self._show_report_window(
                    f"Reporte de Pagos - {period_name}",
                    self._format_period_report(filtered, period_name),
                    "payment_period"
                )
            
            self._create_period_selection_window("Seleccionar Período", on_generate)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte por período: {str(e)}")
    
    def _generate_tenant_payments_report(self):
        """Genera reporte de pagos por inquilino"""
        try:
            self._reload_all_data()
            
            tenants = tenant_service.get_all_tenants()
            if not tenants:
                messagebox.showinfo("Sin datos", "No hay inquilinos registrados.")
                return
            
            tenant_window = tk.Toplevel(self)
            tenant_window.title("Seleccionar Inquilino")
            tenant_window.geometry("550x400")
            tenant_window.transient(self)
            tenant_window.grab_set()
            tenant_window.bind("<Escape>", lambda e: tenant_window.destroy())

            tk.Label(
                tenant_window,
                text="Seleccione el inquilino:",
                font=("Segoe UI", 13, "bold")
            ).pack(pady=20)
            
            # Lista de inquilinos
            listbox_frame = tk.Frame(tenant_window)
            listbox_frame.pack(fill="both", expand=True, padx=25, pady=15)
            
            scrollbar = tk.Scrollbar(listbox_frame)
            scrollbar.pack(side="right", fill="y")
            
            tenant_listbox = tk.Listbox(listbox_frame, font=("Segoe UI", 10), yscrollcommand=scrollbar.set)
            tenant_listbox.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=tenant_listbox.yview)
            
            tenant_dict = {}
            for tenant in tenants:
                display_name = f"{tenant.get('nombre', 'N/A')} - Apt. {self._get_apartment_number(tenant)}"
                tenant_listbox.insert(tk.END, display_name)
                tenant_dict[display_name] = tenant
            
            def generate():
                selection = tenant_listbox.curselection()
                if not selection:
                    messagebox.showwarning("Advertencia", "Por favor seleccione un inquilino.")
                    return
                
                selected_display = tenant_listbox.get(selection[0])
                selected_tenant = tenant_dict[selected_display]
                
                payments = payment_service.get_payments_by_tenant(selected_tenant.get('id'))
                
                if not payments:
                    messagebox.showinfo("Sin datos", f"No hay pagos registrados para {selected_tenant.get('nombre', 'N/A')}.")
                    tenant_window.destroy()
                    return
                
                tenant_window.destroy()
                self._show_report_window(
                    f"Reporte de Pagos - {selected_tenant.get('nombre', 'N/A')}",
                    self._format_tenant_payments_report(selected_tenant, payments),
                    "tenant_payments"
                )
            
            button_frame = tk.Frame(tenant_window)
            button_frame.pack(fill="x", pady=(8, 12))
            tk.Button(
                button_frame,
                text="Generar Reporte",
                font=("Segoe UI", 10, "bold"),
                bg="#22c55e",
                fg="white",
                relief="flat",
                padx=22,
                pady=6,
                cursor="hand2",
                command=generate
            ).pack()

            tenant_window.after(50, tenant_window.focus_force)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte por inquilino: {str(e)}")
    
    def _generate_payment_method_report(self):
        """Genera reporte de pagos por método de pago"""
        try:
            self._reload_all_data()
            
            payments = payment_service.get_all_payments()
            
            if not payments:
                messagebox.showinfo("Sin datos", "No hay pagos registrados para generar el reporte.")
                return
            
            def on_generate(period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry, period_window):
                filtered, period_name = self._filter_payments_by_period(
                    payments, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry
                )
                
                if filtered is None:
                    messagebox.showerror("Error", "Por favor complete todos los campos requeridos.")
                    return
                
                if not filtered:
                    messagebox.showinfo("Sin datos", f"No hay pagos registrados para el período seleccionado.")
                    period_window.destroy()
                    return
                
                # Agrupar por método
                methods_dict = {}
                for payment in filtered:
                    method = payment.get('metodo', 'No especificado')
                    if method not in methods_dict:
                        methods_dict[method] = {
                            'count': 0,
                            'total': 0,
                            'payments': []
                        }
                    methods_dict[method]['count'] += 1
                    methods_dict[method]['total'] += float(payment.get('monto', 0))
                    methods_dict[method]['payments'].append(payment)
                
                period_window.destroy()
                self._show_report_window(
                    f"Reporte por Método de Pago - {period_name}",
                    self._format_payment_method_report(methods_dict, len(filtered), period_name),
                    "payment_method"
                )
            
            self._create_period_selection_window("Seleccionar Período - Método de Pago", on_generate, button_color="#16a34a")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte por método: {str(e)}")
    
    def _generate_pending_payments_report(self):
        """Genera reporte de pagos pendientes"""
        try:
            self._reload_all_data()
            
            tenants = tenant_service.get_all_tenants()
            tenant_service.recalculate_all_payment_statuses()
            tenant_service._load_data()
            tenants = tenant_service.get_all_tenants()
            
            pending_tenants = [
                t for t in tenants
                if t.get('estado_pago') in ('pendiente_registro', 'pendiente_pago', 'moroso')
            ]
            
            if not pending_tenants:
                messagebox.showinfo("Sin datos", "No hay inquilinos con pagos pendientes.")
                return
            
            self._show_report_window(
                "Reporte de Pagos Pendientes",
                self._format_pending_payments_report(pending_tenants),
                "pending_payments"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de pendientes: {str(e)}")
    
    def _generate_consolidated_income_report(self):
        """Genera reporte de ingresos consolidado"""
        try:
            self._reload_all_data()
            
            payments = payment_service.get_all_payments()
            
            if not payments:
                messagebox.showinfo("Sin datos", "No hay pagos registrados para generar el reporte.")
                return
            
            def on_generate(period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry, period_window):
                filtered, period_name = self._filter_payments_by_period(
                    payments, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry
                )
                
                if filtered is None:
                    messagebox.showerror("Error", "Por favor complete todos los campos requeridos.")
                    return
                
                if not filtered:
                    messagebox.showinfo("Sin datos", f"No hay pagos registrados para el período seleccionado.")
                    period_window.destroy()
                    return
                
                total_income = sum(float(p.get('monto', 0)) for p in filtered)
                
                # Filtrar por período para comparativas
                now = datetime.now()
                this_month = [p for p in filtered if self._is_this_month(p.get('fecha_pago', ''))]
                this_year = [p for p in filtered if self._is_this_year(p.get('fecha_pago', ''))]
                
                monthly_income = sum(float(p.get('monto', 0)) for p in this_month)
                yearly_income = sum(float(p.get('monto', 0)) for p in this_year)
                
                # Calcular promedios
                avg_payment = total_income / len(filtered) if filtered else 0
                avg_monthly = monthly_income if this_month else 0
                
                # Proyección anual basada en el mes actual
                if this_month:
                    projected_yearly = monthly_income * 12
                else:
                    projected_yearly = 0
                
                period_window.destroy()
                self._show_report_window(
                    f"Reporte de Ingresos Consolidado - {period_name}",
                    self._format_consolidated_income_report(
                        total_income, monthly_income, yearly_income, len(filtered),
                        avg_payment, avg_monthly, projected_yearly, this_month, this_year, period_name
                    ),
                    "consolidated_income"
                )
            
            self._create_period_selection_window("Seleccionar Período - Ingresos Consolidado", on_generate, button_color="#166534")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte consolidado: {str(e)}")
    
    def _create_apartment_period_selection_window(self, title, on_generate, button_color):
        """Ventana compacta para seleccionar apartamento y período (misma UX que reportes de gastos)."""
        period_window = tk.Toplevel(self)
        period_window.title(title)
        period_window.geometry("420x540")
        period_window.transient(self)
        period_window.grab_set()
        period_window.bind("<Escape>", lambda e: period_window.destroy())

        title_label = tk.Label(
            period_window,
            text="Seleccione el apartamento y período:",
            font=("Segoe UI", 12, "bold")
        )
        title_label.pack(pady=(6, 4))

        main_container = tk.Frame(period_window)
        main_container.pack(fill="x", padx=16, pady=(2, 4))

        apartment_frame = tk.LabelFrame(
            main_container,
            text="Apartamento",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=4
        )
        apartment_frame.pack(fill="x", pady=(0, 4))

        apartment_type = tk.StringVar(value="all")

        tk.Radiobutton(
            apartment_frame,
            text="Todos los apartamentos",
            variable=apartment_type,
            value="all",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 2))

        tk.Radiobutton(
            apartment_frame,
            text="Apartamento específico",
            variable=apartment_type,
            value="specific",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 2))

        apartment_list_frame = tk.Frame(apartment_frame)
        apartment_list_frame.pack(fill="x", padx=12)
        tk.Label(apartment_list_frame, text="Apartamento:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        apartment_combo = ttk.Combobox(apartment_list_frame, width=20, state="readonly")
        apartments = apartment_service.get_all_apartments()
        if apartments:
            apartment_values = ["Todos"] + [f"{apt.get('number', 'N/A')}" for apt in apartments]
            apartment_combo['values'] = apartment_values
            apartment_combo.set("Todos")
        else:
            apartment_combo['values'] = ["No hay apartamentos"]
            apartment_combo.set("No hay apartamentos")
        apartment_combo.pack(side="left")

        def _on_apartment_combo_change():
            val = apartment_combo.get()
            if val and val != "Todos" and val != "No hay apartamentos":
                apartment_type.set("specific")
            else:
                apartment_type.set("all")
        apartment_combo.bind("<<ComboboxSelected>>", lambda e: _on_apartment_combo_change())

        period_type = tk.StringVar(value="specific_month")

        specific_frame = tk.LabelFrame(
            main_container,
            text="Mes y Año Específicos",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=4
        )
        specific_frame.pack(fill="x", pady=(0, 4))
        tk.Radiobutton(
            specific_frame,
            text="Mes y año específicos",
            variable=period_type,
            value="specific_month",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 2))
        month_year_frame = tk.Frame(specific_frame)
        month_year_frame.pack(fill="x", padx=12)

        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 9, current_year + 1)]
        years.reverse()

        tk.Label(month_year_frame, text="Año:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        year_combo = ttk.Combobox(month_year_frame, values=years, width=12, state="readonly")
        year_combo.set(str(current_year))
        year_combo.pack(side="left", padx=(0, 20))
        year_combo.bind("<<ComboboxSelected>>", lambda e: period_type.set("specific_month"))

        months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        tk.Label(month_year_frame, text="Mes:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        month_combo = ttk.Combobox(month_year_frame, values=months, width=15, state="readonly")
        month_combo.set(months[datetime.now().month - 1])
        month_combo.pack(side="left")
        month_combo.bind("<<ComboboxSelected>>", lambda e: period_type.set("specific_month"))

        year_only_frame = tk.LabelFrame(
            main_container,
            text="Año Completo",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=4
        )
        year_only_frame.pack(fill="x", pady=(0, 4))
        tk.Radiobutton(
            year_only_frame,
            text="Año específico completo (todos los meses)",
            variable=period_type,
            value="specific_year",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 2))
        year_only_select_frame = tk.Frame(year_only_frame)
        year_only_select_frame.pack(fill="x", padx=12)

        tk.Label(year_only_select_frame, text="Año:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        year_only_combo = ttk.Combobox(year_only_select_frame, values=years, width=12, state="readonly")
        year_only_combo.set(str(current_year))
        year_only_combo.pack(side="left")
        year_only_combo.bind("<<ComboboxSelected>>", lambda e: period_type.set("specific_year"))

        custom_frame = tk.LabelFrame(
            main_container,
            text="Rango Personalizado",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=4
        )
        custom_frame.pack(fill="x", pady=(0, 4))
        tk.Radiobutton(
            custom_frame,
            text="Rango de fechas personalizado",
            variable=period_type,
            value="custom",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 2))
        date_range_frame = tk.Frame(custom_frame)
        date_range_frame.pack(fill="x", padx=12, pady=(0, 2))
        row_from = tk.Frame(date_range_frame)
        row_from.pack(fill="x", pady=(0, 4))
        tk.Label(row_from, text="Desde:", font=("Segoe UI", 9), width=8, anchor="w").pack(side="left", padx=(0, 8))
        date_from_entry = DatePickerWidget(row_from, on_change=lambda: period_type.set("custom"))
        date_from_entry.pack(side="left", fill="x", expand=True)
        row_to = tk.Frame(date_range_frame)
        row_to.pack(fill="x")
        tk.Label(row_to, text="Hasta:", font=("Segoe UI", 9), width=8, anchor="w").pack(side="left", padx=(0, 8))
        date_to_entry = DatePickerWidget(row_to, on_change=lambda: period_type.set("custom"))
        date_to_entry.pack(side="left", fill="x", expand=True)

        button_frame = tk.Frame(period_window)
        button_frame.pack(fill="x", pady=(6, 8))

        def generate_wrapper():
            if on_generate:
                on_generate(apartment_type, apartment_combo, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry, period_window)

        tk.Button(
            button_frame,
            text="Generar Reporte",
            font=("Segoe UI", 10, "bold"),
            bg=button_color,
            fg="white",
            relief="flat",
            padx=22,
            pady=6,
            cursor="hand2",
            command=generate_wrapper
        ).pack()

        period_window.after(50, period_window.focus_force)
        return period_window
    
    def _generate_apartment_payments_report(self):
        """Genera reporte de pagos por apartamento"""
        try:
            self._reload_all_data()
            
            payments = payment_service.get_all_payments()
            tenants = tenant_service.get_all_tenants()
            apartments = apartment_service.get_all_apartments()
            
            if not payments:
                messagebox.showinfo("Sin datos", "No hay pagos registrados para generar el reporte.")
                return
            
            def on_generate(apartment_type, apartment_combo, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry, period_window):
                # Filtrar por período
                filtered, period_name = self._filter_payments_by_period(
                    payments, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry
                )
                
                if filtered is None:
                    messagebox.showerror("Error", "Por favor complete todos los campos requeridos.")
                    return
                
                if not filtered:
                    messagebox.showinfo("Sin datos", f"No hay pagos registrados para el período seleccionado.")
                    period_window.destroy()
                    return
                
                # Filtrar por apartamento si se seleccionó uno específico
                selected_apartment = None
                if apartment_type.get() == "specific":
                    selected_apt_number = apartment_combo.get()
                    if selected_apt_number and selected_apt_number != "Todos" and selected_apt_number != "No hay apartamentos":
                        selected_apartment = selected_apt_number
                
                # Agrupar pagos por apartamento
                apt_payments = {}
                for payment in filtered:
                    tenant_id = payment.get('id_inquilino')
                    tenant = next((t for t in tenants if t.get('id') == tenant_id), None)
                    if tenant:
                        apt_id = tenant.get('apartamento')
                        if apt_id:
                            try:
                                apt = apartment_service.get_apartment_by_id(int(apt_id))
                                if apt:
                                    apt_num = apt.get('number', str(apt_id))
                                    
                                    # Si se seleccionó un apartamento específico, filtrar
                                    if selected_apartment and apt_num != selected_apartment:
                                        continue
                                    
                                    if apt_num not in apt_payments:
                                        apt_payments[apt_num] = {
                                            'payments': [],
                                            'total': 0,
                                            'count': 0,
                                            'apartment': apt
                                        }
                                    apt_payments[apt_num]['payments'].append(payment)
                                    apt_payments[apt_num]['total'] += float(payment.get('monto', 0))
                                    apt_payments[apt_num]['count'] += 1
                            except Exception:
                                pass
                
                if not apt_payments:
                    messagebox.showinfo("Sin datos", f"No hay pagos registrados para el apartamento y período seleccionados.")
                    period_window.destroy()
                    return
                
                apartment_label = f" - {selected_apartment}" if selected_apartment else ""
                period_window.destroy()
                self._show_report_window(
                    f"Reporte de Pagos por Apartamento{apartment_label} - {period_name}",
                    self._format_apartment_payments_report(apt_payments, period_name, selected_apartment),
                    "apartment_payments"
                )
            
            self._create_apartment_period_selection_window("Seleccionar Apartamento y Período", on_generate, button_color="#22c55e")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte por apartamento: {str(e)}")
    
    def _generate_trends_report(self):
        """Genera análisis de tendencias de pagos"""
        try:
            self._reload_all_data()
            
            payments = payment_service.get_all_payments()
            
            if not payments:
                messagebox.showinfo("Sin datos", "No hay suficientes pagos para analizar tendencias.")
                return
            
            # Agrupar por mes
            monthly_data = {}
            for payment in payments:
                try:
                    date_str = payment.get('fecha_pago', '')
                    if date_str:
                        date_obj = datetime.strptime(date_str, "%d/%m/%Y")
                        month_key = date_obj.strftime("%Y-%m")
                        month_name = date_obj.strftime("%B %Y")
                        
                        if month_key not in monthly_data:
                            monthly_data[month_key] = {
                                'name': month_name,
                                'total': 0,
                                'count': 0
                            }
                        monthly_data[month_key]['total'] += float(payment.get('monto', 0))
                        monthly_data[month_key]['count'] += 1
                except Exception:
                    pass
            
            # Ordenar por fecha
            sorted_months = sorted(monthly_data.items())
            
            self._show_report_window(
                "Análisis de Tendencias de Pagos",
                self._format_trends_report(sorted_months, payments),
                "payment_trends"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de tendencias: {str(e)}")
    
    def _generate_collection_efficiency_report(self):
        """Genera reporte de eficiencia de cobro"""
        try:
            self._reload_all_data()
            
            tenants = tenant_service.get_all_tenants()
            payments = payment_service.get_all_payments()
            
            if not tenants:
                messagebox.showinfo("Sin datos", "No hay inquilinos registrados.")
                return
            
            # Calcular eficiencia por inquilino
            tenant_efficiency = []
            for tenant in tenants:
                tenant_payments = [p for p in payments if p.get('id_inquilino') == tenant.get('id')]
                expected_rent = float(tenant.get('valor_arriendo', 0))
                
                if expected_rent > 0:
                    # Calcular pagos esperados (asumiendo 12 meses)
                    months_active = 12  # Simplificado, se puede mejorar calculando meses reales
                    expected_total = expected_rent * months_active
                    received_total = sum(float(p.get('monto', 0)) for p in tenant_payments)
                    efficiency = (received_total / expected_total * 100) if expected_total > 0 else 0
                    
                    tenant_efficiency.append({
                        'tenant': tenant,
                        'expected': expected_total,
                        'received': received_total,
                        'efficiency': efficiency,
                        'payment_count': len(tenant_payments)
                    })
            
            self._show_report_window(
                "Reporte de Eficiencia de Cobro",
                self._format_collection_efficiency_report(tenant_efficiency, tenants),
                "collection_efficiency"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de eficiencia: {str(e)}")
    
    # ==================== FORMATEADORES DE REPORTES ====================
    
    def _format_period_report(self, payments, period_name):
        """Formatea el reporte por período"""
        report = []
        report.append("=" * 60)
        report.append(f"REPORTE DE PAGOS - {period_name.upper()}")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append("RESUMEN:")
        report.append(f"  • Total de pagos: {len(payments)}")
        report.append(f"  • Total recaudado: ${sum(float(p.get('monto', 0)) for p in payments):,.2f}")
        report.append("")
        report.append("DETALLE DE PAGOS:")
        report.append("-" * 60)
        
        # Ordenar por fecha
        payments_sorted = sorted(payments, key=lambda x: self._parse_date(x.get('fecha_pago', '01/01/1900')), reverse=True)
        
        for payment in payments_sorted:
            tenant_name = payment.get('nombre_inquilino', 'N/A')
            apt_num = self._get_apartment_number_from_payment(payment)
            report.append(f"Fecha: {payment.get('fecha_pago', 'N/A')}")
            report.append(f"  • Inquilino: {tenant_name} (Apt. {apt_num})")
            report.append(f"  • Monto: ${float(payment.get('monto', 0)):,.2f}")
            report.append(f"  • Método: {payment.get('metodo', 'N/A')}")
            if payment.get('observaciones'):
                report.append(f"  • Observaciones: {payment.get('observaciones')}")
            report.append("")
        
        return "\n".join(report)
    
    def _format_tenant_payments_report(self, tenant, payments):
        """Formatea el reporte de pagos por inquilino"""
        report = []
        report.append("=" * 60)
        report.append(f"REPORTE DE PAGOS - {tenant.get('nombre', 'N/A').upper()}")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append("INFORMACIÓN DEL INQUILINO:")
        report.append(f"  • Nombre: {tenant.get('nombre', 'N/A')}")
        report.append(f"  • Apartamento: {self._get_apartment_number(tenant)}")
        report.append(f"  • Documento: {tenant.get('numero_documento', 'N/A')}")
        report.append(f"  • Valor de arriendo: ${float(tenant.get('valor_arriendo', 0)):,.2f}")
        report.append("")
        report.append("RESUMEN DE PAGOS:")
        total_paid = sum(float(p.get('monto', 0)) for p in payments)
        report.append(f"  • Total de pagos registrados: {len(payments)}")
        report.append(f"  • Total pagado: ${total_paid:,.2f}")
        report.append("")
        report.append("HISTORIAL DE PAGOS:")
        report.append("-" * 60)
        
        # Ordenar por fecha (más reciente primero)
        payments_sorted = sorted(payments, key=lambda x: self._parse_date(x.get('fecha_pago', '01/01/1900')), reverse=True)
        
        for idx, payment in enumerate(payments_sorted, 1):
            report.append(f"Pago #{idx}:")
            report.append(f"  • Fecha: {payment.get('fecha_pago', 'N/A')}")
            report.append(f"  • Monto: ${float(payment.get('monto', 0)):,.2f}")
            report.append(f"  • Método: {payment.get('metodo', 'N/A')}")
            if payment.get('observaciones'):
                report.append(f"  • Observaciones: {payment.get('observaciones')}")
            report.append("")
        
        return "\n".join(report)
    
    def _format_payment_method_report(self, methods_dict, total_payments, period_name=None):
        """Formatea el reporte por método de pago"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE POR MÉTODO DE PAGO")
        if period_name:
            report.append(f"Período: {period_name}")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append("RESUMEN GENERAL:")
        report.append(f"  • Total de pagos: {total_payments}")
        report.append(f"  • Total recaudado: ${sum(m['total'] for m in methods_dict.values()):,.2f}")
        report.append("")
        report.append("ANÁLISIS POR MÉTODO:")
        report.append("-" * 60)
        
        # Ordenar por total (mayor a menor)
        sorted_methods = sorted(methods_dict.items(), key=lambda x: x[1]['total'], reverse=True)
        
        for method, data in sorted_methods:
            percentage = (data['total'] / sum(m['total'] for m in methods_dict.values()) * 100) if methods_dict else 0
            report.append(f"Método: {method}")
            report.append(f"  • Cantidad de pagos: {data['count']}")
            report.append(f"  • Total recaudado: ${data['total']:,.2f}")
            report.append(f"  • Porcentaje del total: {percentage:.2f}%")
            report.append("")
        
        return "\n".join(report)
    
    def _parse_fecha_for_report(self, fecha_str):
        """Parsea fecha como en tenant_service: DD/MM/YYYY o ISO."""
        if not fecha_str or not isinstance(fecha_str, str):
            return None
        s = (fecha_str or "").strip()
        try:
            return datetime.strptime(s, "%d/%m/%Y").replace(hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            try:
                return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(hour=0, minute=0, second=0, microsecond=0)
            except Exception:
                return None

    def _compute_arrears_for_report(self, tenant, payments):
        """Calcula mora para el reporte con la misma lógica que tenant_service (períodos desde fecha_ingreso)."""
        try:
            fecha_ingreso = self._parse_fecha_for_report(tenant.get("fecha_ingreso"))
            if not fecha_ingreso:
                return None
            valor_arriendo = float(tenant.get("valor_arriendo") or 0)
            hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            n = 0
            periods_due = 0
            while True:
                due_n = fecha_ingreso + relativedelta(months=n)
                if due_n > hoy:
                    break
                periods_due += 1
                n += 1
            total_expected = round(periods_due * valor_arriendo, 2)
            total_paid = round(sum(float(p.get("monto") or 0) for p in payments), 2)
            if valor_arriendo <= 0:
                periods_covered = periods_due if total_paid >= total_expected else 0
            else:
                periods_covered = min(periods_due, int(total_paid / valor_arriendo))
            periods_in_arrears = max(0, periods_due - periods_covered)

            if periods_in_arrears <= 0:
                return None
            inicio_periodo_actual = fecha_ingreso + relativedelta(months=periods_due - 1)
            dias_del_periodo = (hoy - inicio_periodo_actual).days if hoy >= inicio_periodo_actual else 0
            current_period_due = fecha_ingreso + relativedelta(months=periods_due - 1)
            return {
                "meses_mora": periods_in_arrears,
                "dias_del_periodo_actual": max(0, dias_del_periodo),
                "current_period_due": current_period_due,
                "total_expected": total_expected,
                "total_paid": total_paid,
            }
        except Exception:
            return None

    def _format_pending_payments_report(self, pending_tenants):
        """Formatea el reporte de pagos pendientes con lógica de mora integral (calculada aquí para garantizar consistencia)."""
        self._reload_all_data()
        payment_service._load_data()

        report = []
        report.append("=" * 60)
        report.append("REPORTE DE PAGOS PENDIENTES")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append("RESUMEN:")
        report.append(f"  • Inquilinos con pagos pendientes: {len(pending_tenants)}")
        report.append("")
        report.append("DETALLE DE INQUILINOS:")
        report.append("-" * 60)

        for tenant in pending_tenants:
            estado = tenant.get('estado_pago', 'N/A')
            if estado == 'moroso':
                estado_text = 'En Mora'
            elif estado == 'pendiente_pago':
                estado_text = 'Pendiente de pago'
            else:
                estado_text = 'Pendiente Registro'

            report.append(f"Inquilino: {tenant.get('nombre', 'N/A')}")
            report.append(f"  • Apartamento: {self._get_apartment_number(tenant)}")
            report.append(f"  • Documento: {tenant.get('numero_documento', 'N/A')}")
            report.append(f"  • Teléfono: {tenant.get('telefono', 'N/A')}")
            report.append(f"  • Estado: {estado_text}")
            report.append(f"  • Valor de arriendo: ${float(tenant.get('valor_arriendo', 0)):,.2f}")

            raw_id = tenant.get('id')
            tenant_id = int(raw_id) if raw_id is not None else None
            # Usar get_arrears_info del servicio (misma lógica que lista/detalles); si falla, calcular aquí
            arrears = tenant_service.get_arrears_info(tenant_id) if tenant_id is not None else None
            if not arrears or arrears.get("estado_pago") not in ("moroso", "pendiente_pago", "pendiente_registro"):
                payments = payment_service.get_payments_by_tenant(tenant_id) if tenant_id is not None else []
                arrears = self._compute_arrears_for_report(tenant, payments) if tenant_id is not None else None
                if arrears:
                    arrears["current_period_due"] = arrears.get("current_period_due")
            else:
                first_unpaid = arrears.get("first_unpaid_due_date")
                meses_mora = int(arrears.get("meses_mora", 0) or 0)
                if first_unpaid and meses_mora >= 1:
                    arrears["current_period_due"] = first_unpaid + relativedelta(months=meses_mora - 1)
                else:
                    arrears["current_period_due"] = first_unpaid

            if arrears and (arrears.get("meses_mora", 0) or arrears.get("dias_del_periodo_actual", 0) or arrears.get("total_expected", 0)):
                current_due = arrears.get("current_period_due")
                if current_due and hasattr(current_due, "strftime"):
                    report.append(f"  • Fecha de pago (vencimiento): {current_due.strftime('%d/%m/%Y')}")
                meses_mora = int(arrears.get("meses_mora", 0) or 0)
                dias_del_periodo = int(arrears.get("dias_del_periodo_actual", 0) or 0)
                if meses_mora == 1:
                    mora_texto = f"{dias_del_periodo} día{'s' if dias_del_periodo != 1 else ''}"
                else:
                    meses_completos = meses_mora - 1
                    partes = []
                    if meses_completos > 0:
                        partes.append(f"{meses_completos} mes{'es' if meses_completos != 1 else ''}")
                    if dias_del_periodo > 0:
                        partes.append(f"{dias_del_periodo} día{'s' if dias_del_periodo != 1 else ''}")
                    mora_texto = " y ".join(partes) if partes else "0"
                report.append(f"  • Días en mora: {mora_texto}")
                pending = float(arrears.get("amount_pending", arrears.get("total_expected", 0)) or 0)
                paid = float(arrears.get("total_paid", 0) or 0)
                report.append(f"  • Monto total en mora: ${max(0.0, pending - paid):,.2f}")

            report.append("")

        return "\n".join(report)
    
    def _format_consolidated_income_report(self, total, monthly, yearly, count, avg_payment, avg_monthly, projected, this_month, this_year, period_name=None):
        """Formatea el reporte de ingresos consolidado"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE INGRESOS CONSOLIDADO")
        if period_name:
            report.append(f"Período: {period_name}")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        if period_name:
            report.append(f"PERÍODO SELECCIONADO: {period_name}")
            report.append("")
        report.append("RESUMEN FINANCIERO:")
        report.append(f"  • Ingresos totales (histórico): ${total:,.2f}")
        report.append(f"  • Ingresos del mes actual: ${monthly:,.2f}")
        report.append(f"  • Ingresos del año actual: ${yearly:,.2f}")
        report.append(f"  • Total de pagos procesados: {count}")
        report.append("")
        report.append("ESTADÍSTICAS:")
        report.append(f"  • Promedio por pago: ${avg_payment:,.2f}")
        report.append(f"  • Promedio mensual (mes actual): ${avg_monthly:,.2f}")
        if projected > 0:
            report.append(f"  • Proyección anual (basada en mes actual): ${projected:,.2f}")
        report.append("")
        report.append("DETALLE POR PERÍODO:")
        report.append("-" * 60)
        report.append(f"  • Pagos en el mes actual: {len(this_month)}")
        report.append(f"  • Pagos en el año actual: {len(this_year)}")
        
        return "\n".join(report)
    
    def _format_apartment_payments_report(self, apt_payments, period_name=None, selected_apartment=None):
        """Formatea el reporte de pagos por apartamento"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE PAGOS POR APARTAMENTO")
        if period_name:
            report.append(f"Período: {period_name}")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        if selected_apartment:
            report.append(f"APARTAMENTO SELECCIONADO: {selected_apartment}")
            report.append("")
        report.append(f"Total de apartamentos con pagos: {len(apt_payments)}")
        report.append("")
        report.append("DETALLE POR APARTAMENTO:")
        report.append("-" * 60)
        
        # Ordenar por número de apartamento
        sorted_apts = sorted(apt_payments.items(), key=lambda x: x[0])

        for i, (apt_num, data) in enumerate(sorted_apts):
            if i > 0:
                report.append("")
                report.append("-" * 60)
                report.append("")
            apt = data.get("apartment", {})
            unit_label = self._get_apartment_display_name(apt) if apt else f"Apartamento {apt_num}"
            report.append(f"{unit_label}:")
            report.append(f"  • Total de pagos: {data['count']}")
            report.append(f"  • Total recaudado: ${data['total']:,.2f}")
            report.append("")
            report.append("  Historial de pagos:")
            # Ordenar pagos por fecha
            sorted_payments = sorted(data['payments'], key=lambda x: self._parse_date(x.get('fecha_pago', '01/01/1900')), reverse=True)
            for payment in sorted_payments[:5]:  # Mostrar últimos 5
                report.append(f"    - {payment.get('fecha_pago', 'N/A')}: ${float(payment.get('monto', 0)):,.2f} ({payment.get('metodo', 'N/A')})")
            if len(sorted_payments) > 5:
                report.append(f"    ... y {len(sorted_payments) - 5} pago(s) más")
            report.append("")

        return "\n".join(report)
    
    def _format_trends_report(self, monthly_data, all_payments):
        """Formatea el reporte de tendencias"""
        report = []
        report.append("=" * 60)
        report.append("ANÁLISIS DE TENDENCIAS DE PAGOS")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append("EVOLUCIÓN MENSUAL:")
        report.append("-" * 60)
        
        if not monthly_data:
            report.append("No hay datos suficientes para analizar tendencias.")
            return "\n".join(report)
        
        for month_key, data in monthly_data:
            report.append(f"{data['name']}:")
            report.append(f"  • Total recaudado: ${data['total']:,.2f}")
            report.append(f"  • Cantidad de pagos: {data['count']}")
            report.append(f"  • Promedio por pago: ${data['total']/data['count']:,.2f}" if data['count'] > 0 else "  • Promedio por pago: $0.00")
            report.append("")
        
        # Análisis comparativo
        if len(monthly_data) >= 2:
            report.append("ANÁLISIS COMPARATIVO:")
            report.append("-" * 60)
            current_month = monthly_data[-1][1]
            previous_month = monthly_data[-2][1] if len(monthly_data) >= 2 else None
            
            if previous_month:
                change = current_month['total'] - previous_month['total']
                change_percent = (change / previous_month['total'] * 100) if previous_month['total'] > 0 else 0
                report.append(f"Variación respecto al mes anterior: ${change:,.2f} ({change_percent:+.2f}%)")
        
        return "\n".join(report)
    
    def _format_collection_efficiency_report(self, tenant_efficiency, all_tenants):
        """Formatea el reporte de eficiencia de cobro"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE EFICIENCIA DE COBRO")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append("RESUMEN:")
        report.append(f"  • Total de inquilinos: {len(all_tenants)}")
        report.append(f"  • Inquilinos analizados: {len(tenant_efficiency)}")
        report.append("")
        
        if not tenant_efficiency:
            report.append("No hay datos suficientes para calcular eficiencia.")
            return "\n".join(report)
        
        # Calcular eficiencia promedio
        avg_efficiency = sum(t['efficiency'] for t in tenant_efficiency) / len(tenant_efficiency)
        report.append(f"  • Eficiencia promedio: {avg_efficiency:.2f}%")
        report.append("")
        report.append("DETALLE POR INQUILINO:")
        report.append("-" * 60)
        
        # Ordenar por eficiencia (mayor a menor)
        sorted_tenants = sorted(tenant_efficiency, key=lambda x: x['efficiency'], reverse=True)
        
        for data in sorted_tenants:
            tenant = data['tenant']
            report.append(f"Inquilino: {tenant.get('nombre', 'N/A')}")
            report.append(f"  • Apartamento: {self._get_apartment_number(tenant)}")
            report.append(f"  • Esperado: ${data['expected']:,.2f}")
            report.append(f"  • Recibido: ${data['received']:,.2f}")
            report.append(f"  • Eficiencia: {data['efficiency']:.2f}%")
            report.append(f"  • Pagos registrados: {data['payment_count']}")
            report.append("")
        
        return "\n".join(report)
    
    # ==================== VENTANA DE VISUALIZACIÓN ====================
    
    def _show_report_window(self, title, content, report_type):
        """Muestra el reporte en una ventana con opciones de exportar (reglas: Exportar CSV, Exportar TXT, Cerrar; colores módulo pagos; utf-8-sig)."""
        colors = get_module_colors("pagos")
        header_bg = colors.get("hover", "#16a34a")
        btn_export_bg = colors.get("primary", "#22c55e")

        window = tk.Toplevel(self)
        window.title(title)
        window.geometry("800x600")
        window.transient(self)
        window.grab_set()

        header = tk.Frame(window, bg=header_bg, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        btn_frame = tk.Frame(header, bg=header_bg)
        btn_frame.pack(side="right", padx=Spacing.LG, pady=12)

        def export_csv():
            self._export_to_csv(content, title, report_type)
        def export_txt():
            self._export_to_txt(content, title, report_type)

        # Colores para hover suave (verde más oscuro para exportar, rojo más oscuro para cerrar)
        btn_export_hover = colors.get("hover", "#16a34a")
        btn_close_bg = "#dc2626"
        btn_close_hover = "#b91c1c"

        btn_opts = dict(font=("Segoe UI", 9), fg="white", relief="flat", bd=0, highlightthickness=0, padx=14, pady=6, cursor="hand2")

        btn_csv = tk.Button(btn_frame, text="💾 Exportar CSV", bg=btn_export_bg, **btn_opts, command=export_csv)
        btn_csv.pack(side="left", padx=Spacing.SM)
        btn_csv.bind("<Enter>", lambda e: btn_csv.config(bg=btn_export_hover))
        btn_csv.bind("<Leave>", lambda e: btn_csv.config(bg=btn_export_bg))

        btn_txt = tk.Button(btn_frame, text="📄 Exportar TXT", bg=btn_export_bg, **btn_opts, command=export_txt)
        btn_txt.pack(side="left", padx=Spacing.SM)
        btn_txt.bind("<Enter>", lambda e: btn_txt.config(bg=btn_export_hover))
        btn_txt.bind("<Leave>", lambda e: btn_txt.config(bg=btn_export_bg))

        # Cerrar: ancho suficiente para que "× Cerrar" no se corte en ningún tema/fuente
        btn_close_opts = {**btn_opts, "padx": 18}
        btn_close = tk.Button(btn_frame, text="× Cerrar", bg=btn_close_bg, width=12, **btn_close_opts, command=window.destroy)
        btn_close.pack(side="left", padx=Spacing.SM)
        btn_close.bind("<Enter>", lambda e: btn_close.config(bg=btn_close_hover))
        btn_close.bind("<Leave>", lambda e: btn_close.config(bg=btn_close_bg))

        # Título a la izquierda: ocupa el espacio restante sin empujar los botones
        title_label = tk.Label(
            header,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg=header_bg,
            fg="white",
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True, padx=Spacing.LG, pady=12)

        text_frame = tk.Frame(window)
        text_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)
        
        text_widget = tk.Text(
            text_frame,
            font=("Consolas", 10),
            wrap="word",
            bg="#ffffff",
            fg="#000000"
        )
        text_widget.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.insert("1.0", content)
        if report_type == "apartment_payments":
            text_widget.tag_configure("apt_header", font=("Consolas", 13, "bold"))
            num_lines = int(text_widget.index("end-1c").split(".")[0])
            # Encabezados de unidad (tipo + número) en negrita y tamaño 13
            unit_prefixes = ("Apto:", "Local:", "Penthouse:", "Depósito:", "Apartamento ", "Otro:", "Unidad:")
            for i in range(1, num_lines + 1):
                line_text = text_widget.get(f"{i}.0", f"{i}.0 lineend")
                s = line_text.strip()
                if s.endswith(":") and s.startswith(unit_prefixes):
                    text_widget.tag_add("apt_header", f"{i}.0", f"{i}.0 lineend")
        elif report_type == "pending_payments":
            # Negrita para "Inquilino:" y "  • Apartamento:"
            text_widget.tag_configure("bold", font=("Consolas", 10, "bold"))
            num_lines = int(text_widget.index("end-1c").split(".")[0])
            for i in range(1, num_lines + 1):
                line_text = text_widget.get(f"{i}.0", f"{i}.0 lineend")
                if line_text.strip().startswith("Inquilino:") or "• Apartamento:" in line_text:
                    text_widget.tag_add("bold", f"{i}.0", f"{i}.0 lineend")
        text_widget.config(state="disabled")
    
    def _show_export_success_dialog(self, filepath):
        """Ventana de confirmación tras exportar: Copiar, Abrir carpeta, Abrir archivo, Aceptar (reglas establecidas)."""
        path = Path(filepath) if not isinstance(filepath, Path) else filepath
        colors = get_module_colors("pagos")
        win = tk.Toplevel(self.winfo_toplevel())
        win.title("Exportación exitosa")
        win.geometry("520x220")
        win.transient(self.winfo_toplevel())
        win.resizable(True, False)
        win.grab_set()
        content = tk.Frame(win, padx=Spacing.LG, pady=Spacing.LG)
        content.pack(fill="both", expand=True)
        top = tk.Frame(content)
        top.pack(fill="x")
        tk.Label(top, text="ℹ", font=("Segoe UI", 28), fg=colors.get("primary", "#2563eb")).pack(side="left", padx=(0, Spacing.MD))
        msg = tk.Frame(top)
        msg.pack(side="left", fill="x", expand=True)
        tk.Label(msg, text="Exportación exitosa. Archivo guardado en:", font=("Segoe UI", 11)).pack(anchor="w")
        path_var = tk.StringVar(value=str(path))
        path_entry = tk.Entry(msg, textvariable=path_var, font=("Segoe UI", 10))
        path_entry.pack(fill="x", pady=(Spacing.SM, 0))
        path_entry.bind("<Key>", lambda e: "break")
        btns = tk.Frame(content)
        btns.pack(fill="x", pady=(Spacing.LG, 0))
        def copy_path():
            win.clipboard_clear()
            win.clipboard_append(str(path))
        def open_folder():
            folder = str(path.resolve().parent)
            if os.name == "nt":
                os.startfile(folder)
            else:
                import subprocess
                subprocess.run(["xdg-open", folder], check=False)
        def open_file():
            p = str(path.resolve())
            if os.name == "nt":
                os.startfile(p)
            else:
                import subprocess
                subprocess.run(["xdg-open", p], check=False)
        tk.Button(btns, text="📋 Copiar", font=("Segoe UI", 10), bg="#2563eb", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=copy_path).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btns, text="📁 Abrir carpeta", font=("Segoe UI", 10), bg="#6b7280", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=open_folder).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btns, text="📄 Abrir archivo", font=("Segoe UI", 10), bg="#059669", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=open_file).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btns, text="Aceptar", font=("Segoe UI", 10), bg="#2563eb", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=win.destroy).pack(side="right")
    
    def _export_to_csv(self, content, title, report_type):
        """Exporta el reporte a CSV"""
        try:
            from manager.app.paths_config import EXPORTS_DIR, ensure_dirs
            ensure_dirs()
            filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = EXPORTS_DIR / filename
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                for line in content.split('\n'):
                    writer.writerow([line])
            
            self._show_export_success_dialog(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar CSV: {str(e)}")
    
    def _export_to_txt(self, content, title, report_type):
        """Exporta el reporte a TXT"""
        try:
            from manager.app.paths_config import EXPORTS_DIR, ensure_dirs
            ensure_dirs()
            filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = EXPORTS_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                f.write(content)
            
            self._show_export_success_dialog(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar TXT: {str(e)}")
    
    # ==================== HELPERS ====================
    
    def _get_apartment_display_name(self, apt):
        """Devuelve el nombre de la unidad para el reporte: Apto, Local, Penthouse, Depósito, etc."""
        if not apt:
            return "Unidad"
        unit_type = apt.get("unit_type", "Apartamento Estándar")
        unit_number = apt.get("number", "N/A")
        if unit_type == "Local Comercial" or unit_type == "Local comercial":
            return f"Local: {unit_number}"
        if unit_type == "Penthouse":
            return f"Penthouse: {unit_number}"
        if unit_type == "Depósito" or "Depósito" in str(unit_type) or "Bodega" in str(unit_type):
            return f"Depósito: {unit_number}"
        if unit_type == "Apartamento Estándar" or unit_type == "Apartamento Estandar":
            return f"Apto: {unit_number}"
        return f"{unit_type}: {unit_number}"

    def _get_apartment_number(self, tenant):
        """Obtiene el número del apartamento de un inquilino"""
        apt_id = tenant.get('apartamento', None)
        if apt_id is not None:
            try:
                apt = apartment_service.get_apartment_by_id(int(apt_id))
                if apt and 'number' in apt:
                    return apt.get('number', 'N/A')
            except Exception:
                pass
        return str(apt_id) if apt_id else 'N/A'
    
    def _get_apartment_number_from_payment(self, payment):
        """Obtiene el número del apartamento desde un pago"""
        tenant_id = payment.get('id_inquilino')
        tenants = tenant_service.get_all_tenants()
        tenant = next((t for t in tenants if t.get('id') == tenant_id), None)
        if tenant:
            return self._get_apartment_number(tenant)
        return 'N/A'
    
    def _is_this_month(self, date_str):
        """Verifica si una fecha corresponde al mes actual"""
        try:
            date = datetime.strptime(date_str, "%d/%m/%Y")
            now = datetime.now()
            return date.year == now.year and date.month == now.month
        except:
            return False
    
    def _is_this_year(self, date_str):
        """Verifica si una fecha corresponde al año actual"""
        try:
            date = datetime.strptime(date_str, "%d/%m/%Y")
            return date.year == datetime.now().year
        except:
            return False
    
    def _is_in_range(self, date_str, date_from, date_to):
        """Verifica si una fecha está en un rango"""
        try:
            date = datetime.strptime(date_str, "%d/%m/%Y")
            return date_from <= date <= date_to
        except:
            return False
    
    def _parse_date(self, date_str):
        """Parsea una fecha en formato DD/MM/YYYY"""
        try:
            return datetime.strptime(date_str, "%d/%m/%Y")
        except:
            return datetime(1900, 1, 1)
    
    def _create_navigation_buttons(self, parent, on_back_command):
        """Crea los botones Volver y Dashboard con estilo consistente"""
        theme = theme_manager.themes[theme_manager.current_theme]
        hover_bg = theme.get("bg_tertiary", theme["btn_secondary_hover"])
        
        # Configuración común para ambos botones (misma altura)
        button_config = {
            "font": ("Segoe UI", 10, "bold"),
            "bg": theme["btn_secondary_bg"],
            "fg": theme["btn_secondary_fg"],
            "activebackground": hover_bg,
            "activeforeground": theme["btn_secondary_fg"],
            "bd": 1,
            "relief": "solid",
            "padx": 12,
            "pady": 5,
            "cursor": "hand2"
        }
        
        # Colores verdes para módulo de pagos
        colors = get_module_colors("pagos")
        green_primary = colors["primary"]
        green_hover = colors["hover"]
        green_light = colors["light"]
        green_text = colors["text"]
        
        # Botón "Dashboard" con icono de casita (siempre navega al dashboard principal)
        def go_to_dashboard():
            # Prioridad 1: Usar callback directo si está disponible
            if self.on_navigate_to_dashboard:
                try:
                    self.on_navigate_to_dashboard()
                    return
                except Exception as e:
                    print(f"Error en callback de navegación: {e}")
            
            # Prioridad 2: Buscar MainWindow en la jerarquía
            widget = self.master
            max_depth = 10
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
            
            # Prioridad 3: Si on_back navega al dashboard principal (desde main_window)
            if self.on_back:
                self.on_back()
        
        # Botón "Volver"
        btn_back = create_rounded_button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color="white",
            fg_color=green_primary,
            hover_bg=green_light,
            hover_fg=green_text,
            command=on_back_command,
            padx=16,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_back.pack(side="right", padx=(Spacing.MD, 0))
        
        # Botón "Dashboard"
        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=green_primary,
            fg_color="white",
            hover_bg=green_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_dashboard.pack(side="right")