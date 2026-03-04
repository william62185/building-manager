"""
Vista de reporte de Historial de Ocupación
Análisis histórico de ocupación y rotación de inquilinos
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
from manager.app.services.apartment_service import apartment_service
from manager.app.services.tenant_service import tenant_service
from manager.app.services.payment_service import payment_service

class OccupationHistoryReportView(tk.Frame):
    """Vista de reporte de historial de ocupación"""
    
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
        
        title = tk.Label(header, text="Historial de Ocupación", **theme_manager.get_style("label_title"))
        title.pack(side="left")
        
        # Botones de navegación
        buttons_frame = tk.Frame(header, **theme_manager.get_style("frame"))
        buttons_frame.pack(side="right")
        self._create_navigation_buttons(buttons_frame)
        
        # Filtros
        filters_frame = tk.Frame(self, **theme_manager.get_style("card"))
        filters_frame.pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.MD))
        
        tk.Label(filters_frame, text="Filtros:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=Spacing.MD)
        
        tk.Label(filters_frame, text="Apartamento:", font=("Segoe UI", 10)).pack(side="left", padx=(Spacing.LG, Spacing.SM))
        self.apartment_var = tk.StringVar(value="Todos")
        self.apartment_combo = ttk.Combobox(filters_frame, textvariable=self.apartment_var, state="readonly", width=25)
        self.apartment_combo.pack(side="left", padx=Spacing.SM)
        self.apartment_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
        # Métricas
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
        """Carga y procesa los datos históricos"""
        apartments = apartment_service.get_all_apartments()
        tenants = tenant_service.get_all_tenants()
        payments = payment_service.get_all_payments()
        
        # Preparar datos para filtros
        apartment_names = ["Todos"] + [
            f"{apt.get('unit_type', 'Apto')}: {apt.get('number', '')}" 
            for apt in apartments
        ]
        self.apartment_combo['values'] = apartment_names
        
        # Crear mapa de apartamento -> inquilino
        apt_to_tenant = {}
        # Filtrar solo inquilinos activos
        active_tenants = [t for t in tenants if t.get("estado", "activo").lower() != "inactivo"]
        for tenant in active_tenants:
            apt_id = tenant.get("apartamento")
            if apt_id:
                apt_to_tenant[str(apt_id)] = tenant
        
        # Agrupar pagos por apartamento para calcular rotación (solo de inquilinos activos)
        apt_payments = defaultdict(list)
        for payment in payments:
            tenant_id = payment.get("id_inquilino")
            if tenant_id:
                tenant = next((t for t in active_tenants if t.get("id") == tenant_id), None)
                if tenant:
                    apt_id = str(tenant.get("apartamento", ""))
                    if apt_id:
                        apt_payments[apt_id].append(payment)
        
        # Procesar datos por apartamento
        self.apartment_history = []
        
        for apt in apartments:
            apt_id = str(apt.get("id"))
            tenant = apt_to_tenant.get(apt_id)
            
            # Calcular estadísticas
            payments_for_apt = apt_payments.get(apt_id, [])
            total_payments = len(payments_for_apt)
            
            # Calcular tiempo de ocupación actual
            current_occupancy_days = None
            if tenant:
                fecha_ingreso = tenant.get("fecha_ingreso", "")
                if fecha_ingreso:
                    try:
                        fecha_ingreso_dt = datetime.strptime(fecha_ingreso, "%d/%m/%Y")
                        current_occupancy_days = (datetime.now() - fecha_ingreso_dt).days
                    except:
                        pass
            
            # Calcular rotación (número de pagos puede indicar rotación)
            # Si hay muchos pagos en diferentes períodos, podría indicar rotación
            rotation_indicator = "Baja" if total_payments < 3 else "Media" if total_payments < 6 else "Alta"
            
            unit_type = apt.get('unit_type', 'Apartamento Estándar')
            unit_number = apt.get('number', 'N/A')
            
            if unit_type == "Local Comercial":
                title_text = f"Local: {unit_number}"
            elif unit_type == "Penthouse":
                title_text = f"Penthouse: {unit_number}"
            elif unit_type == "Depósito":
                title_text = f"Depósito: {unit_number}"
            elif unit_type == "Apartamento Estándar":
                title_text = f"Apto: {unit_number}"
            else:
                title_text = f"{unit_type}: {unit_number}"
            
            self.apartment_history.append({
                "id": apt.get("id"),
                "title": title_text,
                "status": apt.get("status", "Disponible"),
                "tenant": tenant.get("nombre") if tenant else None,
                "fecha_ingreso": tenant.get("fecha_ingreso") if tenant else None,
                "current_occupancy_days": current_occupancy_days,
                "total_payments": total_payments,
                "rotation_indicator": rotation_indicator,
                "floor": apt.get("floor", ""),
                "unit_type": unit_type
            })
        
        # Calcular métricas generales
        self._calculate_metrics()
        
        # Mostrar datos
        self._apply_filters()
    
    def _calculate_metrics(self):
        """Calcula métricas generales de rotación"""
        total_apartments = len(self.apartment_history)
        occupied = sum(1 for apt in self.apartment_history if apt.get("status") == "Ocupado")
        
        # Calcular promedio de días de ocupación
        occupancy_days_list = [
            apt.get("current_occupancy_days") 
            for apt in self.apartment_history 
            if apt.get("current_occupancy_days") is not None
        ]
        avg_occupancy_days = sum(occupancy_days_list) / len(occupancy_days_list) if occupancy_days_list else 0
        
        # Calcular rotación promedio
        rotation_counts = defaultdict(int)
        for apt in self.apartment_history:
            rotation_counts[apt.get("rotation_indicator")] += 1
        
        self.metrics = {
            "total": total_apartments,
            "occupied": occupied,
            "avg_occupancy_days": avg_occupancy_days,
            "rotation_counts": dict(rotation_counts)
        }
    
    def _apply_filters(self):
        """Aplica los filtros y muestra los resultados"""
        # Limpiar contenido anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        for widget in self.metrics_container.winfo_children():
            widget.destroy()
        
        selected_apt = self.apartment_var.get()
        
        # Filtrar datos
        filtered_data = self.apartment_history.copy()
        if selected_apt != "Todos":
            apt_number = selected_apt.split(":")[-1].strip()
            filtered_data = [
                apt for apt in filtered_data 
                if str(apt.get("title", "")).endswith(f": {apt_number}")
            ]
        
        # Mostrar métricas
        self._show_metrics(filtered_data)
        
        # Mostrar detalles
        self._show_details(filtered_data)
    
    def _show_metrics(self, filtered_data: List[Dict[str, Any]]):
        """Muestra las métricas generales"""
        if not filtered_data:
            return
        
        occupied = sum(1 for apt in filtered_data if apt.get("status") == "Ocupado")
        occupancy_days_list = [
            apt.get("current_occupancy_days") 
            for apt in filtered_data 
            if apt.get("current_occupancy_days") is not None
        ]
        avg_occupancy_days = sum(occupancy_days_list) / len(occupancy_days_list) if occupancy_days_list else 0
        
        metrics = [
            ("Unidades Analizadas", str(len(filtered_data)), "#3b82f6"),
            ("Ocupadas", str(occupied), "#10b981"),
            ("Promedio Días Ocupación", f"{avg_occupancy_days:.0f} días", "#f59e0b"),
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
    
    def _show_details(self, filtered_data: List[Dict[str, Any]]):
        """Muestra los detalles por apartamento"""
        if not filtered_data:
            tk.Label(
                self.content_frame,
                text="No se encontraron datos con los filtros seleccionados.",
                font=("Segoe UI", 12),
                fg="#666"
            ).pack(pady=Spacing.XL)
            return
        
        # Tabla de apartamentos
        table_frame = tk.Frame(self.content_frame, **theme_manager.get_style("card"))
        table_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        # Encabezados
        headers = ["Unidad", "Estado", "Inquilino Actual", "Fecha Ingreso", "Días Ocupación", "Pagos", "Rotación"]
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
        table_frame.grid_columnconfigure(1, weight=1)
        table_frame.grid_columnconfigure(2, weight=2)
        table_frame.grid_columnconfigure(3, weight=1)
        table_frame.grid_columnconfigure(4, weight=1)
        table_frame.grid_columnconfigure(5, weight=1)
        table_frame.grid_columnconfigure(6, weight=1)
        
        # Filas de datos
        for row_idx, apt_data in enumerate(sorted(filtered_data, key=lambda x: (
            x.get("unit_type") != "Apartamento Estándar",
            int(x.get("floor", 0)) if str(x.get("floor", "0")).isdigit() else 999,
            x.get("title")
        )), start=1):
            bg_color = "#ffffff" if row_idx % 2 == 0 else "#f8f9fa"
            
            status = apt_data.get("status", "Disponible")
            status_colors = {
                "Ocupado": "#10b981",
                "Disponible": "#f59e0b",
                "En Mantenimiento": "#6366f1"
            }
            status_color = status_colors.get(status, "#666")
            
            rotation = apt_data.get("rotation_indicator", "Baja")
            rotation_colors = {
                "Baja": "#10b981",
                "Media": "#f59e0b",
                "Alta": "#ef4444"
            }
            rotation_color = rotation_colors.get(rotation, "#666")
            
            tk.Label(
                table_frame,
                text=apt_data.get("title", ""),
                font=("Segoe UI", 9, "bold"),
                bg=bg_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="w"
            ).grid(row=row_idx, column=0, sticky="ew", padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=status,
                font=("Segoe UI", 9, "bold"),
                bg=bg_color,
                fg=status_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="w"
            ).grid(row=row_idx, column=1, sticky="ew", padx=1, pady=1)
            
            tenant_name = apt_data.get("tenant") or "---"
            tk.Label(
                table_frame,
                text=tenant_name,
                font=("Segoe UI", 9),
                bg=bg_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="w"
            ).grid(row=row_idx, column=2, sticky="ew", padx=1, pady=1)
            
            fecha_ingreso = apt_data.get("fecha_ingreso") or "---"
            tk.Label(
                table_frame,
                text=fecha_ingreso,
                font=("Segoe UI", 9),
                bg=bg_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="w"
            ).grid(row=row_idx, column=3, sticky="ew", padx=1, pady=1)
            
            occupancy_days = apt_data.get("current_occupancy_days")
            days_display = f"{occupancy_days} días" if occupancy_days is not None else "---"
            tk.Label(
                table_frame,
                text=days_display,
                font=("Segoe UI", 9),
                bg=bg_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="w"
            ).grid(row=row_idx, column=4, sticky="ew", padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=str(apt_data.get("total_payments", 0)),
                font=("Segoe UI", 9),
                bg=bg_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="w"
            ).grid(row=row_idx, column=5, sticky="ew", padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=rotation,
                font=("Segoe UI", 9, "bold"),
                bg=bg_color,
                fg=rotation_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="w"
            ).grid(row=row_idx, column=6, sticky="ew", padx=1, pady=1)
    
    def _create_navigation_buttons(self, parent):
        """Crea los botones de navegación con estilo moderno y colores morados del módulo de administración"""
        from manager.app.ui.components.icons import Icons
        
        # Colores morados para módulo de administración (este reporte está dentro de administración)
        colors = get_module_colors("administración")
        purple_primary = colors["primary"]
        purple_hover = colors["hover"]
        purple_light = colors["light"]
        purple_text = colors["text"]
        
        # Botón "Volver"
        btn_back = create_rounded_button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color="white",
            fg_color=purple_primary,
            hover_bg=purple_light,
            hover_fg=purple_text,
            command=self.on_back,
            padx=16,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_back.pack(side="right", padx=(Spacing.MD, 0))
        
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
        
        # Botón "Dashboard"
        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=purple_primary,
            fg_color="white",
            hover_bg=purple_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_dashboard.pack(side="right")
