"""
Vista de reporte de Ocupación y Vacancia
Muestra la tasa de ocupación y tiempo de vacancia por apartamento
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Any
from datetime import datetime, timedelta
from collections import defaultdict

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.services.apartment_service import apartment_service
from manager.app.services.tenant_service import tenant_service

class OccupancyVacancyReportView(tk.Frame):
    """Vista de reporte de ocupación y vacancia"""
    
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
        
        title = tk.Label(header, text="Ocupación y Vacancia", **theme_manager.get_style("label_title"))
        title.pack(side="left")
        
        # Botones de navegación
        buttons_frame = tk.Frame(header, **theme_manager.get_style("frame"))
        buttons_frame.pack(side="right")
        self._create_navigation_buttons(buttons_frame)
        
        # Métricas generales
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
        """Carga y procesa los datos de ocupación"""
        apartments = apartment_service.get_all_apartments()
        tenants = tenant_service.get_all_tenants()
        
        # Filtrar solo inquilinos activos (excluir inactivos)
        active_tenants = [t for t in tenants if t.get('estado_pago') != 'inactivo']
        
        # Crear mapa de apartamento -> inquilino (solo activos)
        apt_to_tenant = {}
        for tenant in active_tenants:
            apt_id = tenant.get("apartamento")
            if apt_id:
                apt_to_tenant[str(apt_id)] = tenant
        
        # Calcular estadísticas
        total_apartments = len(apartments)
        occupied = 0
        available = 0
        maintenance = 0
        
        self.apartment_data = []
        
        for apt in apartments:
            apt_id = str(apt.get("id"))
            status = apt.get("status", "Disponible")
            tenant = apt_to_tenant.get(apt_id)
            
            if status == "Ocupado":
                occupied += 1
            elif status == "Disponible":
                available += 1
            elif status == "En Mantenimiento":
                maintenance += 1
            
            # Calcular días de vacancia si está disponible
            vacancy_days = None
            if status == "Disponible" and tenant:
                # Si hay un inquilino pero el apartamento está disponible, 
                # podría ser que el inquilino se fue recientemente
                fecha_ingreso = tenant.get("fecha_ingreso", "")
                if fecha_ingreso:
                    try:
                        fecha_ingreso_dt = datetime.strptime(fecha_ingreso, "%d/%m/%Y")
                        vacancy_days = (datetime.now() - fecha_ingreso_dt).days
                    except:
                        pass
            
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
            
            self.apartment_data.append({
                "id": apt.get("id"),
                "title": title_text,
                "status": status,
                "tenant": tenant.get("nombre") if tenant else None,
                "rent": tenant.get("valor_arriendo") if tenant else apt.get("base_rent", 0),
                "vacancy_days": vacancy_days,
                "floor": apt.get("floor", ""),
                "unit_type": unit_type
            })
        
        # Mostrar métricas
        self._show_metrics(total_apartments, occupied, available, maintenance)
        
        # Mostrar detalles
        self._show_details()
    
    def _show_metrics(self, total: int, occupied: int, available: int, maintenance: int):
        """Muestra las métricas generales"""
        for widget in self.metrics_container.winfo_children():
            widget.destroy()
        
        occupancy_rate = (occupied / total * 100) if total > 0 else 0
        vacancy_rate = (available / total * 100) if total > 0 else 0
        
        metrics = [
            ("Total Unidades", str(total), "#3b82f6"),
            ("Ocupadas", f"{occupied} ({occupancy_rate:.1f}%)", "#10b981"),
            ("Disponibles", f"{available} ({vacancy_rate:.1f}%)", "#f59e0b"),
            ("Mantenimiento", str(maintenance), "#6366f1")
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
    
    def _show_details(self):
        """Muestra los detalles por apartamento"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if not self.apartment_data:
            tk.Label(
                self.content_frame,
                text="No hay apartamentos registrados.",
                font=("Segoe UI", 12),
                fg="#666"
            ).pack(pady=Spacing.XL)
            return
        
        # Tabla de apartamentos
        table_frame = tk.Frame(self.content_frame, **theme_manager.get_style("card"))
        table_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        # Encabezados
        headers = ["Unidad", "Estado", "Inquilino", "Arriendo", "Piso", "Tipo"]
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
        
        # Filas de datos
        for row_idx, apt_data in enumerate(sorted(self.apartment_data, key=lambda x: (
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
            
            rent = apt_data.get("rent", 0)
            rent_display = f"${float(rent):,.0f}" if rent else "---"
            tk.Label(
                table_frame,
                text=rent_display,
                font=("Segoe UI", 9),
                bg=bg_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="e"
            ).grid(row=row_idx, column=3, sticky="ew", padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=str(apt_data.get("floor", "")),
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
                text=apt_data.get("unit_type", ""),
                font=("Segoe UI", 9),
                bg=bg_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="w"
            ).grid(row=row_idx, column=5, sticky="ew", padx=1, pady=1)
    
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
