"""
Vista completa de reportes consolidados para Building Manager Pro
Sistema escalable con múltiples tipos de reportes de alto nivel
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import os
import csv
import subprocess
from pathlib import Path

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import ModernButton, ModernCard, create_rounded_button, get_module_colors
from manager.app.ui.components.icons import Icons
from manager.app.services.tenant_service import tenant_service
from manager.app.services.payment_service import payment_service
from manager.app.services.apartment_service import apartment_service
from manager.app.services.building_service import building_service
from manager.app.services.expense_service import expense_service


class ReportsView(tk.Frame):
    """Vista completa de reportes consolidados del sistema"""
    
    def __init__(self, parent, on_back: Callable = None, on_navigate_to_dashboard: Callable = None,
                 on_show_occupancy_vacancy_report: Callable = None, on_show_pending_payments_report: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        # Fondo igual al del área de contenido para que no se vea el recuadro blanco
        self.configure(bg=parent.cget("bg"))
        self.on_back = on_back
        self.on_navigate_to_dashboard = on_navigate_to_dashboard
        self.on_show_occupancy_vacancy_report = on_show_occupancy_vacancy_report
        self.on_show_pending_payments_report = on_show_pending_payments_report
        
        # Recargar datos antes de generar reportes
        self._reload_all_data()
        
        self._create_layout()
    
    def _reload_all_data(self):
        """Recarga todos los datos necesarios para los reportes"""
        try:
            tenant_service._load_data()
            payment_service._load_data()
            apartment_service._load_data()
            building_service._load_buildings()
            expense_service._load_data()
        except Exception as e:
            print(f"Error al recargar datos: {e}")
    
    def _create_layout(self):
        """Crea el layout principal de la vista de reportes"""
        # Fondo de la vista (transparente respecto al área de contenido)
        bg_view = self.cget("bg")
        # Header con botones de navegación (título eliminado según solicitud del usuario)
        header = tk.Frame(self, bg=bg_view)
        header.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)
        
        # Frame para botones de navegación (alineados a la derecha)
        buttons_frame = tk.Frame(header, bg=bg_view)
        buttons_frame.pack(side="right")
        
        if self.on_back:
            self._create_navigation_buttons(buttons_frame, self.on_back)
        
        # Subtítulo
        theme = theme_manager.themes[theme_manager.current_theme]
        question_label = tk.Label(
            self,
            text="Reportes Consolidados del Sistema",
            font=("Segoe UI", 14),
            fg=theme["text_primary"],
            bg=bg_view
        )
        question_label.pack(pady=(0, Spacing.MD))
        
        # Contenedor principal (fondo transparente)
        main_container = tk.Frame(self, bg=bg_view)
        main_container.pack(fill="both", expand=True, padx=Spacing.XL, pady=(0, Spacing.MD))
        
        # Contenido de reportes
        self._create_reports_content(main_container)
    
    def _create_reports_content(self, parent):
        """Crea el contenido de los reportes consolidados (mismo tamaño/espaciado que Administración)"""
        bg_view = parent.cget("bg")
        cards_container = tk.Frame(parent, bg=bg_view)
        cards_container.pack(fill="both", expand=True)
        
        cards_grid = tk.Frame(cards_container, bg=bg_view)
        cards_grid.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.MD)
        
        # Mismo tamaño que módulo de gastos (expenses_view: 260x220)
        CARD_WIDTH = 260
        CARD_HEIGHT = 220
        row_minsize = CARD_HEIGHT + 2 * Spacing.MD
        for c in range(3):
            cards_grid.columnconfigure(c, weight=1, uniform="col", minsize=CARD_WIDTH)
        for r in range(1):
            cards_grid.rowconfigure(r, weight=0, minsize=row_minsize)
        
        # Definir los reportes consolidados: el primero abre la vista Ocupación y Vacancia
        reports = [
            ("💰", "Reporte de Ocupación",
             "Mismo informe y vista del reporte de ocupación y vacancia.",
             "#c2410c",
             self._on_financial_report_card_click),
            ("📈", "Reporte de Pagos Pendientes",
             "Inquilinos con pagos pendientes o en mora. Misma vista e informe.",
             "#ea580c",
             self._on_pending_payments_report_card_click),
            ("📊", "Estado de Resultados",
             "Ingresos menos gastos: utilidad o déficit. Incluye información del edificio.",
             "#f97316",
             self._generate_building_status_report),
        ]
        
        # Colores naranja del módulo de reportes para cards
        colors = get_module_colors("reportes")
        orange_light = colors["light"]   # fondo base (#fed7aa orange-200)
        orange_hover_bg = "#fdba74"      # orange-300, más oscuro que el fondo para que el hover se vea

        # Colocar cards en grid (mismo espaciado que Administración)
        row = 0
        col = 0
        for icon, title, description, color, command in reports:
            card = self._create_report_card(
                cards_grid,
                icon,
                title,
                description,
                color,
                command,
                card_bg=orange_light,
                card_hover_bg=orange_hover_bg
            )
            card.grid(row=row, column=col, sticky="n", padx=Spacing.MD, pady=Spacing.MD)
            col += 1
            if col >= 3:
                col = 0
                row += 1
    
    def _create_report_card(self, parent, icon, title, description, color, command,
                            card_bg=None, card_hover_bg=None):
        """Crea una tarjeta de reporte (mismo tamaño y estilo que cards de Administración)"""
        if card_bg is None:
            colors = get_module_colors("reportes")
            card_bg = colors["light"]
        if card_hover_bg is None:
            colors = get_module_colors("reportes")
            card_hover_bg = colors["hover"]

        colors = get_module_colors("reportes")
        icon_fg = colors["text"]  # mismo color oscuro para todos los iconos (#c2410c) y buen contraste

        # Mismo tamaño que cards del módulo de gastos (260x220)
        card = tk.Frame(
            parent,
            bg=card_bg,
            relief="raised",
            bd=2,
            width=260,
            height=220
        )
        card.pack_propagate(False)
        card.configure(cursor="hand2")
        
        content_frame = tk.Frame(card, bg=card_bg)
        content_frame.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
        
        top_spacer = tk.Frame(content_frame, bg=card_bg, height=1)
        top_spacer.pack(fill="x", expand=True)
        
        content_container = tk.Frame(content_frame, bg=card_bg)
        content_container.pack()
        
        icon_label = tk.Label(
            content_container,
            text=icon,
            font=("Segoe UI", 22),
            fg=icon_fg,
            bg=card_bg
        )
        icon_label.pack(pady=(0, Spacing.SM))
        
        title_label = tk.Label(
            content_container,
            text=title,
            font=("Segoe UI", 11, "bold"),
            fg="#000000",
            bg=card_bg,
            wraplength=180,
            justify="center"
        )
        title_label.pack()
        
        bottom_spacer = tk.Frame(content_frame, bg=card_bg, height=1)
        bottom_spacer.pack(fill="x", expand=True)
        
        # Hacer que toda la tarjeta sea clickeable
        def on_card_click(e):
            """Ejecuta el comando cuando se hace clic en la tarjeta"""
            command()
        
        # Hover effect para el card (naranja más intenso)
        def on_enter(e):
            card.configure(bg=card_hover_bg, cursor="hand2")
            content_frame.configure(bg=card_hover_bg)
            content_container.configure(bg=card_hover_bg)
            top_spacer.configure(bg=card_hover_bg)
            bottom_spacer.configure(bg=card_hover_bg)
            icon_label.configure(bg=card_hover_bg)
            title_label.configure(bg=card_hover_bg)
        
        def on_leave(e):
            # Solo resetear si el puntero salió del card (evitar parpadeo al pasar entre icono y título)
            def _check_leave():
                try:
                    root = card.winfo_toplevel()
                    root.update_idletasks()
                    x, y = root.winfo_pointerx(), root.winfo_pointery()
                    w = root.winfo_containing(x, y)
                    cur = w
                    while cur:
                        if cur == card:
                            return  # aún dentro del card
                        try:
                            cur = cur.master
                        except (tk.TclError, AttributeError):
                            break
                except (tk.TclError, AttributeError):
                    pass
                card.configure(bg=card_bg, cursor="hand2")
                content_frame.configure(bg=card_bg)
                content_container.configure(bg=card_bg)
                top_spacer.configure(bg=card_bg)
                bottom_spacer.configure(bg=card_bg)
                icon_label.configure(bg=card_bg)
                title_label.configure(bg=card_bg)
            card.after(10, _check_leave)
        
        # Aplicar eventos a todos los elementos del card
        card_widgets = [card, content_frame, top_spacer, content_container, bottom_spacer, icon_label, title_label]
        for widget in card_widgets:
            widget.configure(cursor="hand2")
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_card_click)
        
        return card
    
    def _create_navigation_buttons(self, parent, on_back_command):
        """Crea el botón Dashboard con estilo moderno y colores naranja del módulo de reportes"""
        # Colores naranja para módulo de reportes
        colors = get_module_colors("reportes")
        orange_primary = colors["primary"]
        orange_hover = colors["hover"]
        
        # Botón "Dashboard"
        def go_to_dashboard():
            if self.on_navigate_to_dashboard:
                try:
                    self.on_navigate_to_dashboard()
                    return
                except Exception as e:
                    print(f"Error en callback de navegación: {e}")
            
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
            
            if self.on_back:
                self.on_back()
        
        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=orange_primary,
            fg_color="white",
            hover_bg=orange_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_dashboard.pack(side="right")
    
    # ==================== GENERADORES DE REPORTES ====================

    def _on_financial_report_card_click(self):
        """Abre la vista de Ocupación y Vacancia si hay callback; si no, genera el reporte financiero."""
        if self.on_show_occupancy_vacancy_report:
            self.on_show_occupancy_vacancy_report()
        else:
            self._generate_financial_report()

    def _on_pending_payments_report_card_click(self):
        """Abre el reporte de pagos pendientes si hay callback; si no, genera el reporte de rendimiento."""
        if self.on_show_pending_payments_report:
            self.on_show_pending_payments_report()
        else:
            self._generate_performance_report()
    
    def _generate_financial_report(self):
        """Genera reporte financiero consolidado"""
        try:
            self._reload_all_data()
            
            payments = payment_service.get_all_payments()
            expenses = expense_service.get_all_expenses()
            
            # Calcular totales
            total_income = sum(float(p.get('monto', 0)) for p in payments)
            total_expenses = sum(float(e.get('monto', 0)) for e in expenses)
            net_income = total_income - total_expenses
            
            # Análisis por período
            monthly_data = self._calculate_monthly_financials(payments, expenses)
            yearly_data = self._calculate_yearly_financials(payments, expenses)
            
            self._show_report_window(
                "Reporte Financiero Consolidado",
                self._format_financial_report(
                    total_income, total_expenses, net_income,
                    len(payments), len(expenses),
                    monthly_data, yearly_data
                ),
                "financial"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte financiero: {str(e)}")
    
    def _generate_performance_report(self):
        """Genera reporte de rendimiento general (KPIs)"""
        try:
            self._reload_all_data()
            
            tenants = tenant_service.get_all_tenants()
            apartments = apartment_service.get_all_apartments()
            payments = payment_service.get_all_payments()
            expenses = expense_service.get_all_expenses()
            
            active_tenants = [t for t in tenants if t.get('estado_pago') != 'inactivo']
            occupied_apartments = [a for a in apartments if a.get('estado') == 'Ocupado']
            
            # Calcular KPIs
            occupancy_rate = (len(occupied_apartments) / len(apartments) * 100) if apartments else 0
            total_income = sum(float(p.get('monto', 0)) for p in payments)
            total_expenses = sum(float(e.get('monto', 0)) for e in expenses)
            net_income = total_income - total_expenses
            profitability_rate = (net_income / total_income * 100) if total_income > 0 else 0
            
            # Morosidad
            delinquent_tenants = [t for t in active_tenants if t.get('estado_pago') == 'moroso']
            delinquency_rate = (len(delinquent_tenants) / len(active_tenants) * 100) if active_tenants else 0
            
            self._show_report_window(
                "Reporte de Rendimiento General",
                self._format_performance_report(
                    len(apartments), len(occupied_apartments), occupancy_rate,
                    len(active_tenants), len(delinquent_tenants), delinquency_rate,
                    total_income, total_expenses, net_income, profitability_rate,
                    len(payments), len(expenses)
                ),
                "performance"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de rendimiento: {str(e)}")
    
    def _generate_building_status_report(self):
        """Abre el selector de período y genera el Estado de Resultados para el período elegido."""
        try:
            self._reload_all_data()
            building = building_service.get_active_building() or {}
            apartments = apartment_service.get_all_apartments()
            tenants = tenant_service.get_all_tenants()
            payments = payment_service.get_all_payments()
            expenses = expense_service.get_all_expenses()
            active_tenants = [t for t in tenants if t.get('estado_pago') != 'inactivo']
            occupied_apartments = [a for a in apartments if a.get('estado') == 'Ocupado']
            available_apartments = [a for a in apartments if a.get('estado') == 'Disponible']
            occupancy_rate = (len(occupied_apartments) / len(apartments) * 100) if apartments else 0
            total_monthly_income = sum(float(t.get('valor_arriendo', 0)) for t in active_tenants)

            def on_generate(period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry, win):
                period_label, filter_fn = self._resolve_period_estado_resultados(
                    period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry
                )
                if period_label is None or filter_fn is None:
                    messagebox.showwarning("Período inválido", "Seleccione un período válido e intente de nuevo.")
                    return
                filtered_payments = [p for p in payments if filter_fn(self._parse_payment_date(p))]
                filtered_expenses = [e for e in expenses if filter_fn(self._parse_expense_date(e))]
                total_ingresos = sum(float(p.get('monto', 0)) for p in filtered_payments)
                total_costos = sum(float(e.get('monto', 0)) for e in filtered_expenses)
                utilidad_o_deficit = total_ingresos - total_costos
                win.destroy()
                title = f"Estado de Resultados {period_label}"
                self._show_report_window(
                    title,
                    self._format_building_status_report(
                        building, None, None, None, 0, 0, 0, 0,
                        total_ingresos, total_costos, utilidad_o_deficit,
                        period_label=period_label
                    ),
                    "estado_resultados"
                )

            self._create_estado_resultados_period_window(on_generate)
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar Estado de Resultados: {str(e)}")

    def _create_estado_resultados_period_window(self, on_generate):
        """Ventana para seleccionar el período del Estado de Resultados (mes actual, año actual, mes/año específicos, año completo)."""
        period_window = tk.Toplevel(self)
        period_window.title("Seleccionar período")
        period_window.geometry("550x520")
        period_window.transient(self)
        period_window.grab_set()

        tk.Label(
            period_window,
            text="Seleccione el período para el reporte:",
            font=("Segoe UI", 13, "bold"),
            pady=15
        ).pack()

        main_container = tk.Frame(period_window)
        main_container.pack(fill="x", padx=25, pady=(10, 8))

        period_type = tk.StringVar(value="current_month")

        # Opciones rápidas
        quick_frame = tk.LabelFrame(
            main_container,
            text="Opciones Rápidas",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=10
        )
        quick_frame.pack(fill="x", pady=(0, 12))

        tk.Radiobutton(
            quick_frame,
            text="Mes actual",
            variable=period_type,
            value="current_month",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=4)
        tk.Radiobutton(
            quick_frame,
            text="Año actual",
            variable=period_type,
            value="current_year",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=4)

        # Mes y año específicos
        specific_frame = tk.LabelFrame(
            main_container,
            text="Seleccionar Mes y Año Específicos",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=10
        )
        specific_frame.pack(fill="x", pady=(0, 12))

        tk.Radiobutton(
            specific_frame,
            text="Mes y año específicos",
            variable=period_type,
            value="specific_month",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 8))

        month_year_frame = tk.Frame(specific_frame)
        month_year_frame.pack(fill="x", padx=20)
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 9, current_year + 1)]
        years.reverse()
        months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        tk.Label(month_year_frame, text="Año:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        year_combo = ttk.Combobox(month_year_frame, values=years, width=12, state="readonly")
        year_combo.set(str(current_year))
        year_combo.pack(side="left", padx=(0, 20))
        tk.Label(month_year_frame, text="Mes:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        month_combo = ttk.Combobox(month_year_frame, values=months, width=15, state="readonly")
        month_combo.set(months[datetime.now().month - 1])
        month_combo.pack(side="left")

        # Año completo
        year_only_frame = tk.LabelFrame(
            main_container,
            text="Seleccionar Año Completo",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=10
        )
        year_only_frame.pack(fill="x", pady=(0, 12))

        tk.Radiobutton(
            year_only_frame,
            text="Año específico completo (todos los meses)",
            variable=period_type,
            value="specific_year",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 8))
        year_only_select_frame = tk.Frame(year_only_frame)
        year_only_select_frame.pack(fill="x", padx=20)
        tk.Label(year_only_select_frame, text="Año:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        year_only_combo = ttk.Combobox(year_only_select_frame, values=years, width=12, state="readonly")
        year_only_combo.set(str(current_year))
        year_only_combo.pack(side="left")

        # Rango personalizado (placeholders para on_generate)
        date_from_entry = tk.Entry(main_container, width=1)
        date_to_entry = tk.Entry(main_container, width=1)

        button_frame = tk.Frame(period_window)
        button_frame.pack(fill="x", pady=(0, 15))

        def generate_wrapper():
            on_generate(period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry, period_window)

        colors = get_module_colors("reportes")
        btn_bg = colors.get("primary", "#ea580c")
        tk.Button(
            button_frame,
            text="Generar Reporte",
            font=("Segoe UI", 11, "bold"),
            bg=btn_bg,
            fg="white",
            relief="flat",
            padx=30,
            pady=10,
            cursor="hand2",
            command=generate_wrapper
        ).pack()

    def _resolve_period_estado_resultados(self, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry):
        """Resuelve el período seleccionado y retorna (period_label, filter_fn). filter_fn(datetime|None) -> bool."""
        months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        period = period_type.get()

        if period == "current_month":
            now = datetime.now()
            def fn(dt):
                return dt is not None and dt.year == now.year and dt.month == now.month
            return f"{months[now.month - 1]} {now.year}", fn

        if period == "current_year":
            y = datetime.now().year
            def fn(dt):
                return dt is not None and dt.year == y
            return f"Año {y}", fn

        if period == "specific_month":
            sy = year_combo.get()
            sm = month_combo.get()
            if not sy or not sm:
                return None, None
            year_num = int(sy)
            month_num = months.index(sm) + 1
            def fn(dt):
                return dt is not None and dt.year == year_num and dt.month == month_num
            return f"{sm} {sy}", fn

        if period == "specific_year":
            sy = year_only_combo.get()
            if not sy:
                return None, None
            year_num = int(sy)
            def fn(dt):
                return dt is not None and dt.year == year_num
            return f"Año {sy}", fn

        return None, None

    def _parse_payment_date(self, payment):
        """Obtiene la fecha de un pago como datetime. Acepta 'fecha' (Y-m-d) o 'fecha_pago' (d/m/Y)."""
        for key in ("fecha", "fecha_pago"):
            s = payment.get(key, "")
            if not s:
                continue
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(s.strip(), fmt)
                except ValueError:
                    pass
        return None

    def _parse_expense_date(self, expense):
        """Obtiene la fecha de un gasto como datetime (campo 'fecha' en Y-m-d)."""
        s = expense.get("fecha", "")
        if not s:
            return None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(s.strip(), fmt)
            except ValueError:
                pass
        return None

    # ==================== CÁLCULOS Y ANÁLISIS ====================
    
    def _calculate_monthly_financials(self, payments, expenses):
        """Calcula datos financieros mensuales"""
        monthly_income = defaultdict(float)
        monthly_expenses = defaultdict(float)
        
        for payment in payments:
            fecha_str = payment.get('fecha', '')
            if fecha_str:
                try:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                    key = f"{fecha.year}-{fecha.month:02d}"
                    monthly_income[key] += float(payment.get('monto', 0))
                except:
                    pass
        
        for expense in expenses:
            fecha_str = expense.get('fecha', '')
            if fecha_str:
                try:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                    key = f"{fecha.year}-{fecha.month:02d}"
                    monthly_expenses[key] += float(expense.get('monto', 0))
                except:
                    pass
        
        # Combinar y ordenar
        all_months = sorted(set(list(monthly_income.keys()) + list(monthly_expenses.keys())))
        result = []
        for month in all_months:
            income = monthly_income.get(month, 0)
            expense = monthly_expenses.get(month, 0)
            result.append({
                'month': month,
                'income': income,
                'expense': expense,
                'net': income - expense
            })
        
        return result
    
    def _calculate_yearly_financials(self, payments, expenses):
        """Calcula datos financieros anuales"""
        yearly_income = defaultdict(float)
        yearly_expenses = defaultdict(float)
        
        for payment in payments:
            fecha_str = payment.get('fecha', '')
            if fecha_str:
                try:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                    year = str(fecha.year)
                    yearly_income[year] += float(payment.get('monto', 0))
                except:
                    pass
        
        for expense in expenses:
            fecha_str = expense.get('fecha', '')
            if fecha_str:
                try:
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                    year = str(fecha.year)
                    yearly_expenses[year] += float(expense.get('monto', 0))
                except:
                    pass
        
        # Combinar y ordenar
        all_years = sorted(set(list(yearly_income.keys()) + list(yearly_expenses.keys())))
        result = []
        for year in all_years:
            income = yearly_income.get(year, 0)
            expense = yearly_expenses.get(year, 0)
            result.append({
                'year': year,
                'income': income,
                'expense': expense,
                'net': income - expense
            })
        
        return result
    
    # ==================== FORMATEADORES DE REPORTES ====================
    
    def _format_financial_report(self, total_income, total_expenses, net_income,
                                num_payments, num_expenses, monthly_data, yearly_data):
        """Formatea el reporte financiero consolidado"""
        report = []
        report.append("=" * 70)
        report.append("REPORTE FINANCIERO CONSOLIDADO")
        report.append("=" * 70)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        
        # Resumen general
        report.append("RESUMEN GENERAL")
        report.append("-" * 70)
        report.append(f"Total de Ingresos: ${total_income:,.2f}")
        report.append(f"Total de Gastos: ${total_expenses:,.2f}")
        report.append(f"Ingreso Neto: ${net_income:,.2f}")
        profitability = (net_income / total_income * 100) if total_income > 0 else 0
        report.append(f"Tasa de Rentabilidad: {profitability:.2f}%")
        report.append(f"Total de Pagos Registrados: {num_payments}")
        report.append(f"Total de Gastos Registrados: {num_expenses}")
        report.append("")
        
        # Análisis mensual
        if monthly_data:
            report.append("ANÁLISIS MENSUAL")
            report.append("-" * 70)
            report.append(f"{'Período':<15} {'Ingresos':<15} {'Gastos':<15} {'Neto':<15}")
            report.append("-" * 70)
            for data in monthly_data[-12:]:  # Últimos 12 meses
                month_name = datetime.strptime(data['month'] + '-01', "%Y-%m-%d").strftime("%b %Y")
                report.append(f"{month_name:<15} ${data['income']:>13,.2f} ${data['expense']:>13,.2f} ${data['net']:>13,.2f}")
            report.append("")
        
        # Análisis anual
        if yearly_data:
            report.append("ANÁLISIS ANUAL")
            report.append("-" * 70)
            report.append(f"{'Año':<10} {'Ingresos':<15} {'Gastos':<15} {'Neto':<15}")
            report.append("-" * 70)
            for data in yearly_data:
                report.append(f"{data['year']:<10} ${data['income']:>13,.2f} ${data['expense']:>13,.2f} ${data['net']:>13,.2f}")
            report.append("")
        
        return "\n".join(report)
    
    def _format_performance_report(self, total_apts, occupied_apts, occupancy_rate,
                                  total_tenants, delinquent_tenants, delinquency_rate,
                                  total_income, total_expenses, net_income, profitability_rate,
                                  num_payments, num_expenses):
        """Formatea el reporte de rendimiento general"""
        report = []
        report.append("=" * 70)
        report.append("REPORTE DE RENDIMIENTO GENERAL (KPIs)")
        report.append("=" * 70)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        
        # KPIs de Ocupación
        report.append("INDICADORES DE OCUPACIÓN")
        report.append("-" * 70)
        report.append(f"Total de Apartamentos: {total_apts}")
        report.append(f"Apartamentos Ocupados: {occupied_apts}")
        report.append(f"Apartamentos Disponibles: {total_apts - occupied_apts}")
        report.append(f"Tasa de Ocupación: {occupancy_rate:.2f}%")
        report.append("")
        
        # KPIs de Inquilinos
        report.append("INDICADORES DE INQUILINOS")
        report.append("-" * 70)
        report.append(f"Total de Inquilinos Activos: {total_tenants}")
        report.append(f"Inquilinos en Mora: {delinquent_tenants}")
        report.append(f"Tasa de Morosidad: {delinquency_rate:.2f}%")
        report.append("")
        
        # KPIs Financieros
        report.append("INDICADORES FINANCIEROS")
        report.append("-" * 70)
        report.append(f"Total de Ingresos: ${total_income:,.2f}")
        report.append(f"Total de Gastos: ${total_expenses:,.2f}")
        report.append(f"Ingreso Neto: ${net_income:,.2f}")
        report.append(f"Tasa de Rentabilidad: {profitability_rate:.2f}%")
        report.append(f"Total de Transacciones: {num_payments + num_expenses}")
        report.append("")
        
        return "\n".join(report)
    
    def _format_building_status_report(self, building, apartments, tenants,
                                      occupied_apts, available_apts,
                                      occupancy_rate, total_monthly_income, num_payments,
                                      total_ingresos=0, total_costos=0, utilidad_o_deficit=0,
                                      period_label=""):
        """Formatea el reporte Estado de Resultados (contable) e información del edificio."""
        report = []
        report.append("=" * 70)
        title_line = "ESTADO DE RESULTADOS"
        if period_label:
            title_line += f" - {period_label}"
        report.append(title_line)
        report.append("Building Manager Pro")
        report.append("=" * 70)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        
        # Información del Edificio (justo después de la fecha)
        report.append("INFORMACIÓN DEL EDIFICIO")
        report.append("-" * 70)
        report.append(f"Nombre: {building.get('name', 'N/A')}")
        report.append(f"Dirección: {building.get('address', 'N/A')}")
        report.append(f"Ciudad: {building.get('city', 'N/A')}")
        report.append(f"País: {building.get('country', 'N/A')}")
        report.append("")
        
        # Estado de resultados (contable): Ingresos - Gastos = Utilidad o Pérdida
        report.append("RESULTADO DEL PERÍODO")
        report.append("-" * 70)
        report.append("Fórmula contable: Ingresos - Gastos = Utilidad o Pérdida")
        report.append("")
        report.append(f"  Ingresos (pagos recibidos):     ${total_ingresos:>15,.2f}")
        report.append(f"  (-) Gastos (gastos del edificio): ${total_costos:>14,.2f}")
        report.append("-" * 70)
        if utilidad_o_deficit >= 0:
            report.append(f"  = UTILIDAD:                       ${utilidad_o_deficit:>15,.2f}")
        else:
            report.append(f"  = PÉRDIDA (DÉFICIT):              ${abs(utilidad_o_deficit):>15,.2f}")
        report.append("")
        
        return "\n".join(report)
    
    def _get_apartment_display(self, tenant):
        """Obtiene la representación del apartamento para un inquilino"""
        apartment_display = 'N/A'
        apartment_id = tenant.get('apartamento', None)
        if apartment_id is not None:
            try:
                apartment_id_int = int(apartment_id)
                apt = apartment_service.get_apartment_by_id(apartment_id_int) if hasattr(apartment_service, 'get_apartment_by_id') else None
                if not apt:
                    all_apts = apartment_service.get_all_apartments()
                    apt = next((a for a in all_apts if a.get('id') == apartment_id_int), None)
                if apt:
                    apt_number = apt.get('number', 'N/A')
                    apt_type = apt.get('unit_type', 'Apartamento Estándar')
                    if apt_type == "Apartamento Estándar":
                        apartment_display = apt_number
                    else:
                        apartment_display = f"{apt_type} {apt_number}"
                else:
                    apartment_display = str(apartment_id)
            except Exception:
                apartment_display = str(apartment_id)
        return apartment_display
    
    # ==================== VENTANA DE VISUALIZACIÓN ====================
    
    def _show_report_window(self, title, content, report_type):
        """Muestra el reporte en una ventana con opciones de exportar (reglas: Exportar CSV, Exportar TXT, Cerrar)."""
        colors = get_module_colors("reportes")
        header_bg = colors.get("hover", "#ea580c")

        window = tk.Toplevel(self)
        window.title(title)
        window.geometry("900x700")
        window.transient(self)
        window.grab_set()

        header = tk.Frame(window, bg=header_bg, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg=header_bg,
            fg="white"
        ).pack(side="left", padx=Spacing.LG, pady=12)

        btn_frame = tk.Frame(header, bg=header_bg)
        btn_frame.pack(side="right", padx=Spacing.LG)

        def export_csv():
            self._export_to_csv(content, title, report_type)

        def export_txt():
            self._export_to_txt(content, title, report_type)

        # Orden establecido: Exportar CSV, Exportar TXT, Cerrar (color naranja reportes + hover suave)
        btn_export_bg = colors.get("primary", "#f97316")
        btn_export_hover = colors.get("hover", "#ea580c")
        btn_close_bg = "#dc2626"
        btn_close_hover = "#b91c1c"
        btn_opts = dict(font=("Segoe UI", 9), fg="white", relief="flat", padx=14, pady=6, cursor="hand2")

        btn_csv = tk.Button(btn_frame, text="💾 Exportar CSV", bg=btn_export_bg, **btn_opts, command=export_csv)
        btn_csv.pack(side="left", padx=Spacing.SM)
        btn_csv.bind("<Enter>", lambda e: btn_csv.config(bg=btn_export_hover))
        btn_csv.bind("<Leave>", lambda e: btn_csv.config(bg=btn_export_bg))

        btn_txt = tk.Button(btn_frame, text="📄 Exportar TXT", bg=btn_export_bg, **btn_opts, command=export_txt)
        btn_txt.pack(side="left", padx=Spacing.SM)
        btn_txt.bind("<Enter>", lambda e: btn_txt.config(bg=btn_export_hover))
        btn_txt.bind("<Leave>", lambda e: btn_txt.config(bg=btn_export_bg))

        btn_close = tk.Button(btn_frame, text="× Cerrar", bg=btn_close_bg, width=10, **btn_opts, command=window.destroy)
        btn_close.pack(side="left", padx=Spacing.SM)
        btn_close.bind("<Enter>", lambda e: btn_close.config(bg=btn_close_hover))
        btn_close.bind("<Leave>", lambda e: btn_close.config(bg=btn_close_bg))

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
        text_widget.config(state="disabled")
    
    def _show_export_success_dialog(self, filepath: Path):
        """Diálogo de confirmación tras exportar: Copiar, Abrir carpeta, Abrir archivo, Aceptar (reglas establecidas)."""
        colors = get_module_colors("reportes")
        win = tk.Toplevel(self.winfo_toplevel())
        win.title("Exportación exitosa")
        win.geometry("520x220")
        win.transient(self.winfo_toplevel())
        win.resizable(True, False)
        win.grab_set()

        content_f = tk.Frame(win, padx=Spacing.LG, pady=Spacing.LG)
        content_f.pack(fill="both", expand=True)
        top = tk.Frame(content_f)
        top.pack(fill="x")
        tk.Label(top, text="ℹ", font=("Segoe UI", 28), fg=colors.get("primary", "#ea580c")).pack(side="left", padx=(0, Spacing.MD))
        msg = tk.Frame(top)
        msg.pack(side="left", fill="x", expand=True)
        tk.Label(msg, text="Exportación exitosa. Archivo guardado en:", font=("Segoe UI", 11)).pack(anchor="w")
        path_var = tk.StringVar(value=str(filepath))
        path_entry = tk.Entry(msg, textvariable=path_var, font=("Segoe UI", 10))
        path_entry.pack(fill="x", pady=(Spacing.SM, 0))
        path_entry.bind("<Key>", lambda e: "break")
        btns = tk.Frame(content_f)
        btns.pack(fill="x", pady=(Spacing.LG, 0))

        def copy_path():
            win.clipboard_clear()
            win.clipboard_append(str(filepath))

        def open_folder():
            folder = str(filepath.resolve().parent)
            if os.name == "nt":
                os.startfile(folder)
            else:
                subprocess.run(["xdg-open", folder], check=False)

        def open_file():
            path = str(filepath.resolve())
            if os.name == "nt":
                os.startfile(path)
            else:
                subprocess.run(["xdg-open", path], check=False)

        tk.Button(btns, text="📋 Copiar", font=("Segoe UI", 10), bg="#2563eb", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=copy_path).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btns, text="📁 Abrir carpeta", font=("Segoe UI", 10), bg="#6b7280", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=open_folder).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btns, text="📄 Abrir archivo", font=("Segoe UI", 10), bg="#059669", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=open_file).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btns, text="Aceptar", font=("Segoe UI", 10), bg="#2563eb", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=win.destroy).pack(side="right")

    def _export_to_csv(self, content, title, report_type):
        """Exporta el reporte a CSV y muestra diálogo de éxito con Copiar / Abrir carpeta / Abrir archivo."""
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
        """Exporta el reporte a TXT y muestra diálogo de éxito con Copiar / Abrir carpeta / Abrir archivo."""
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
