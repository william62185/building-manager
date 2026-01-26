"""
Vista de reporte de Análisis de Tendencias
Tendencias de ingresos y ocupación a lo largo del tiempo
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.services.apartment_service import apartment_service
from manager.app.services.tenant_service import tenant_service
from manager.app.services.payment_service import payment_service

class TrendsAnalysisReportView(tk.Frame):
    """Vista de reporte de análisis de tendencias"""
    
    def __init__(self, parent, on_back: Callable, on_navigate: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_back = on_back
        self.on_navigate = on_navigate
        self._create_layout()
        self._load_data()
    
    def _create_layout(self):
        """Crea el layout principal del reporte"""
        # Header
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)
        
        title = tk.Label(header, text="Análisis de Tendencias", **theme_manager.get_style("label_title"))
        title.pack(side="left")
        
        # Botones de navegación
        buttons_frame = tk.Frame(header, **theme_manager.get_style("frame"))
        buttons_frame.pack(side="right")
        self._create_navigation_buttons(buttons_frame)
        
        # Filtros de período
        filters_frame = tk.Frame(self, **theme_manager.get_style("card"))
        filters_frame.pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.MD))
        
        tk.Label(filters_frame, text="Período:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=Spacing.MD)
        
        self.period_var = tk.StringVar(value="Últimos 6 meses")
        period_combo = ttk.Combobox(
            filters_frame, 
            textvariable=self.period_var, 
            values=["Últimos 3 meses", "Últimos 6 meses", "Último año", "Todo el historial"],
            state="readonly",
            width=20
        )
        period_combo.pack(side="left", padx=Spacing.LG)
        period_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        # Métricas de tendencias
        metrics_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        metrics_frame.pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.MD))
        
        self.metrics_container = tk.Frame(metrics_frame, **theme_manager.get_style("frame"))
        self.metrics_container.pack(fill="x")
        
        # Contenedor principal con scroll
        container = tk.Frame(self, **theme_manager.get_style("frame"))
        container.pack(fill="both", expand=True, padx=Spacing.MD, pady=(0, Spacing.MD))
        
        # Canvas y scrollbar
        canvas = tk.Canvas(container, **theme_manager.get_style("frame"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.content_frame = tk.Frame(canvas, **theme_manager.get_style("frame"))
        
        self.content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _load_data(self):
        """Carga y procesa los datos para análisis de tendencias"""
        apartments = apartment_service.get_all_apartments()
        tenants = tenant_service.get_all_tenants()
        payments = payment_service.get_all_payments()
        
        # Procesar pagos por mes
        self.monthly_data = defaultdict(lambda: {"income": 0, "payments_count": 0})
        
        for payment in payments:
            fecha_pago = payment.get("fecha_pago", "")
            if fecha_pago:
                try:
                    fecha_dt = datetime.strptime(fecha_pago, "%d/%m/%Y")
                    month_key = fecha_dt.strftime("%Y-%m")
                    monto = float(payment.get("monto", 0))
                    self.monthly_data[month_key]["income"] += monto
                    self.monthly_data[month_key]["payments_count"] += 1
                except:
                    pass
        
        # Procesar ocupación por mes (basado en fecha de ingreso de inquilinos)
        self.monthly_occupancy = defaultdict(lambda: {"new_tenants": 0, "occupied": 0})
        
        for tenant in tenants:
            fecha_ingreso = tenant.get("fecha_ingreso", "")
            if fecha_ingreso:
                try:
                    fecha_dt = datetime.strptime(fecha_ingreso, "%d/%m/%Y")
                    month_key = fecha_dt.strftime("%Y-%m")
                    self.monthly_occupancy[month_key]["new_tenants"] += 1
                except:
                    pass
        
        # Calcular ocupación actual por mes (aproximación)
        current_month = datetime.now().strftime("%Y-%m")
        occupied_count = sum(1 for apt in apartments if apt.get("status") == "Ocupado")
        self.monthly_occupancy[current_month]["occupied"] = occupied_count
        
        # Calcular estadísticas de apartamentos
        total_apartments = len(apartments)
        occupied_apartments = sum(1 for apt in apartments if apt.get("status") == "Ocupado")
        available_apartments = sum(1 for apt in apartments if apt.get("status") == "Disponible")
        
        self.apartment_stats = {
            "total": total_apartments,
            "occupied": occupied_apartments,
            "available": available_apartments,
            "occupancy_rate": (occupied_apartments / total_apartments * 100) if total_apartments > 0 else 0
        }
        
        self._apply_filters()
    
    def _apply_filters(self):
        """Aplica los filtros y muestra los resultados"""
        # Limpiar contenido anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        for widget in self.metrics_container.winfo_children():
            widget.destroy()
        
        period = self.period_var.get()
        
        # Calcular fecha de inicio según el período
        now = datetime.now()
        if period == "Últimos 3 meses":
            start_date = now - timedelta(days=90)
        elif period == "Últimos 6 meses":
            start_date = now - timedelta(days=180)
        elif period == "Último año":
            start_date = now - timedelta(days=365)
        else:
            start_date = datetime(2000, 1, 1)  # Todo el historial
        
        # Filtrar datos mensuales
        filtered_monthly_data = {}
        for month_key, data in self.monthly_data.items():
            try:
                month_date = datetime.strptime(month_key, "%Y-%m")
                if month_date >= start_date:
                    filtered_monthly_data[month_key] = data
            except:
                pass
        
        # Calcular tendencias
        self._calculate_trends(filtered_monthly_data)
        
        # Mostrar métricas
        self._show_metrics(filtered_monthly_data)
        
        # Mostrar gráfico de tendencias
        self._show_trends_chart(filtered_monthly_data)
    
    def _calculate_trends(self, monthly_data: Dict[str, Dict[str, float]]):
        """Calcula las tendencias de los datos"""
        if len(monthly_data) < 2:
            self.trends = {
                "income_trend": "Sin datos suficientes",
                "occupancy_trend": "Sin datos suficientes"
            }
            return
        
        # Ordenar meses
        sorted_months = sorted(monthly_data.keys())
        
        # Calcular tendencia de ingresos
        if len(sorted_months) >= 2:
            first_half = sorted_months[:len(sorted_months)//2]
            second_half = sorted_months[len(sorted_months)//2:]
            
            first_avg = sum(monthly_data[m]["income"] for m in first_half) / len(first_half) if first_half else 0
            second_avg = sum(monthly_data[m]["income"] for m in second_half) / len(second_half) if second_half else 0
            
            if first_avg == 0:
                income_trend = "Sin datos previos"
            elif second_avg > first_avg * 1.1:
                income_trend = "📈 Creciente"
            elif second_avg < first_avg * 0.9:
                income_trend = "📉 Decreciente"
            else:
                income_trend = "➡️ Estable"
        else:
            income_trend = "Sin datos suficientes"
        
        self.trends = {
            "income_trend": income_trend,
            "occupancy_trend": f"{self.apartment_stats['occupancy_rate']:.1f}% ocupación"
        }
    
    def _show_metrics(self, monthly_data: Dict[str, Dict[str, float]]):
        """Muestra las métricas de tendencias"""
        # Calcular totales del período
        total_income = sum(data["income"] for data in monthly_data.values())
        total_payments = sum(data["payments_count"] for data in monthly_data.values())
        avg_monthly_income = total_income / len(monthly_data) if monthly_data else 0
        
        metrics = [
            ("Ingresos Totales", f"${total_income:,.2f}", "#10b981"),
            ("Promedio Mensual", f"${avg_monthly_income:,.2f}", "#3b82f6"),
            ("Total Pagos", str(total_payments), "#f59e0b"),
            ("Tasa Ocupación", f"{self.apartment_stats['occupancy_rate']:.1f}%", "#ec4899")
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            metric_frame = tk.Frame(self.metrics_container, **theme_manager.get_style("card"))
            metric_frame.pack(side="left", fill="both", expand=True, padx=Spacing.SM)
            
            tk.Label(
                metric_frame,
                text=label,
                font=("Segoe UI", 10),
                fg="#666"
            ).pack(pady=(Spacing.MD, Spacing.XS))
            
            tk.Label(
                metric_frame,
                text=value,
                font=("Segoe UI", 16, "bold"),
                fg=color
            ).pack(pady=(0, Spacing.MD))
    
    def _show_trends_chart(self, monthly_data: Dict[str, Dict[str, float]]):
        """Muestra un gráfico de tendencias"""
        if not monthly_data:
            tk.Label(
                self.content_frame,
                text="No hay datos disponibles para el período seleccionado.",
                font=("Segoe UI", 12),
                fg="#666"
            ).pack(pady=Spacing.XL)
            return
        
        # Frame para el gráfico
        chart_frame = tk.Frame(self.content_frame, **theme_manager.get_style("card"))
        chart_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        tk.Label(
            chart_frame,
            text="Tendencias Mensuales",
            font=("Segoe UI", 13, "bold"),
            fg="#ec4899"
        ).pack(pady=(Spacing.MD, Spacing.SM))
        
        # Indicador de tendencia
        trend_frame = tk.Frame(chart_frame, **theme_manager.get_style("card_content"))
        trend_frame.pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.MD))
        
        tk.Label(
            trend_frame,
            text=f"Tendencia de Ingresos: {self.trends.get('income_trend', 'N/A')}",
            font=("Segoe UI", 11, "bold"),
            fg="#333"
        ).pack(side="left")
        
        # Tabla de datos mensuales
        table_frame = tk.Frame(chart_frame, **theme_manager.get_style("card_content"))
        table_frame.pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.MD))
        
        # Encabezados
        headers = ["Mes", "Ingresos", "Número de Pagos", "Promedio por Pago"]
        for col, header in enumerate(headers):
            tk.Label(
                table_frame,
                text=header,
                font=("Segoe UI", 10, "bold"),
                bg="#e9ecef",
                fg="#333",
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS
            ).grid(row=0, column=col, sticky="ew", padx=1, pady=1)
        
        # Configurar pesos de columnas
        table_frame.grid_columnconfigure(0, weight=2)
        table_frame.grid_columnconfigure(1, weight=2)
        table_frame.grid_columnconfigure(2, weight=1)
        table_frame.grid_columnconfigure(3, weight=2)
        
        # Filas de datos
        sorted_months = sorted(monthly_data.keys())
        for row_idx, month_key in enumerate(sorted_months, start=1):
            bg_color = "#ffffff" if row_idx % 2 == 0 else "#f8f9fa"
            data = monthly_data[month_key]
            
            # Formatear mes
            try:
                month_date = datetime.strptime(month_key, "%Y-%m")
                month_display = month_date.strftime("%B %Y").title()
            except:
                month_display = month_key
            
            income = data["income"]
            payments_count = data["payments_count"]
            avg_payment = income / payments_count if payments_count > 0 else 0
            
            tk.Label(
                table_frame,
                text=month_display,
                font=("Segoe UI", 9),
                bg=bg_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="w"
            ).grid(row=row_idx, column=0, sticky="ew", padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=f"${income:,.2f}",
                font=("Segoe UI", 9, "bold"),
                bg=bg_color,
                fg="#10b981",
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="e"
            ).grid(row=row_idx, column=1, sticky="ew", padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=str(payments_count),
                font=("Segoe UI", 9),
                bg=bg_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="w"
            ).grid(row=row_idx, column=2, sticky="ew", padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=f"${avg_payment:,.2f}" if avg_payment > 0 else "---",
                font=("Segoe UI", 9),
                bg=bg_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="e"
            ).grid(row=row_idx, column=3, sticky="ew", padx=1, pady=1)
    
    def _create_navigation_buttons(self, parent):
        """Crea los botones de navegación"""
        from manager.app.ui.components.icons import Icons
        
        theme = theme_manager.themes[theme_manager.current_theme]
        hover_bg = theme.get("bg_tertiary", theme["btn_secondary_hover"])
        
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
        
        btn_back = tk.Button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            **button_config,
            command=self.on_back
        )
        btn_back.pack(side="right", padx=(Spacing.SM, 0))
        
        def on_enter_back(e):
            btn_back.configure(bg=hover_bg)
        def on_leave_back(e):
            btn_back.configure(bg=theme["btn_secondary_bg"])
        btn_back.bind("<Enter>", on_enter_back)
        btn_back.bind("<Leave>", on_leave_back)
        
        def go_to_dashboard():
            if hasattr(self, 'on_navigate') and self.on_navigate is not None:
                try:
                    self.on_navigate("dashboard")
                    return
                except Exception as e:
                    print(f"Error en callback de navegación: {e}")
            
            try:
                root = self.winfo_toplevel()
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
            
            if self.on_back:
                self.on_back()
        
        btn_dashboard = tk.Button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            **button_config,
            command=go_to_dashboard
        )
        btn_dashboard.pack(side="right")
        
        def on_enter_dashboard(e):
            btn_dashboard.configure(bg=hover_bg)
        def on_leave_dashboard(e):
            btn_dashboard.configure(bg=theme["btn_secondary_bg"])
        btn_dashboard.bind("<Enter>", on_enter_dashboard)
        btn_dashboard.bind("<Leave>", on_leave_dashboard)
