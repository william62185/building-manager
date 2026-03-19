"""
Vista visual para mostrar el estado de ocupación de los apartamentos.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, Any

from manager.app.services.apartment_service import apartment_service
from manager.app.services.tenant_service import tenant_service
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import ModernButton, create_rounded_button, get_module_colors

class OccupationStatusView(tk.Frame):
    """Vista de estado de ocupación con una cuadrícula visual."""

    def __init__(self, parent, on_back: Callable, on_navigate: Callable = None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.on_back = on_back
        self.on_navigate = on_navigate
        self._create_layout()
        self._load_and_display_apartments()

    def _create_layout(self):
        cb = self._content_bg
        self.summary_frame = tk.Frame(self, bg=cb)
        self.summary_frame.pack(fill="x", padx=Spacing.MD, pady=(Spacing.SM, Spacing.SM))
        self.grid_container = tk.Frame(self, bg=cb)
        self.grid_container.pack(fill="both", expand=True, padx=Spacing.MD, pady=(0, Spacing.MD))

    def _create_legend(self):
        cb = self._content_bg
        fg = theme_manager.themes[theme_manager.current_theme].get("text_primary", "#1f2937")
        legend_frame = tk.Frame(self, bg=cb)
        legend_frame.pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.MD))
        statuses = [("Disponible", "green"), ("Ocupado", "orange"), ("En Mantenimiento", "blue")]
        tk.Label(legend_frame, text="Leyenda:", font=("Segoe UI", 10, "bold"), bg=cb, fg=fg).pack(side="left", padx=(0, Spacing.SM))
        for status, color in statuses:
            legend_item = tk.Frame(legend_frame, bg=cb)
            legend_item.pack(side="left", padx=Spacing.SM)
            tk.Label(legend_item, text="●", fg=color, font=("Segoe UI", 12, "bold"), bg=cb).pack(side="left")
            tk.Label(legend_item, text=status, font=("Segoe UI", 10), bg=cb, fg=fg).pack(side="left")

    def _update_summary(self, apartments: List[Dict[str, Any]]):
        """Actualiza el resumen de totales con formato destacado para identificación rápida."""
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        cb = self._content_bg
        fg = theme_manager.themes[theme_manager.current_theme].get("text_primary", "#1f2937")
        occupied = len([a for a in apartments if a.get("status") == "Ocupado"])
        available = len([a for a in apartments if a.get("status") == "Disponible"])
        maintenance = len([a for a in apartments if a.get("status") == "En Mantenimiento"])
        total = len(apartments)

        # Fondo del resumen para mayor impacto
        summary_bg = "#f3e8ff"
        summary_inner = tk.Frame(self.summary_frame, bg=summary_bg, relief="flat", bd=0)
        summary_inner.pack(fill="x", pady=(2, 0), ipadx=Spacing.MD, ipady=Spacing.SM)

        # Título del resumen
        tk.Label(
            summary_inner,
            text="Resumen",
            font=("Segoe UI", 11, "bold"),
            bg=summary_bg,
            fg="#4c1d95",
        ).pack(side="left", padx=(0, Spacing.LG))

        # Cada métrica en un bloque con color del estado y número destacado
        metrics = [
            ("Ocupados", occupied, "orange"),
            ("Disponibles", available, "green"),
            ("En Mantenimiento", maintenance, "blue"),
        ]
        for label, count, color in metrics:
            block = tk.Frame(summary_inner, bg=summary_bg)
            block.pack(side="left", padx=(0, Spacing.LG))
            tk.Label(block, text="●", fg=color, font=("Segoe UI", 14, "bold"), bg=summary_bg).pack(side="left", padx=(0, 4))
            tk.Label(block, text=f"{label}:", font=("Segoe UI", 10), bg=summary_bg, fg=fg).pack(side="left")
            tk.Label(block, text=str(count), font=("Segoe UI", 12, "bold"), bg=summary_bg, fg=fg).pack(side="left", padx=(2, 0))

        # Total al final, más destacado
        total_block = tk.Frame(summary_inner, bg=summary_bg)
        total_block.pack(side="left", padx=(Spacing.MD, 0))
        tk.Label(total_block, text="Total:", font=("Segoe UI", 10, "bold"), bg=summary_bg, fg="#4c1d95").pack(side="left")
        tk.Label(total_block, text=str(total), font=("Segoe UI", 14, "bold"), bg=summary_bg, fg="#4c1d95").pack(side="left", padx=(4, 0))

    def _load_and_display_apartments(self):
        apartments = apartment_service.get_all_apartments()

        # Actualizar resumen de totales (Ocupados, Disponibles, En Mantenimiento)
        self._update_summary(apartments)
        
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        # Agrupar apartamentos por piso
        apartments_by_floor = {}
        for apt in apartments:
            floor = apt.get('floor', '0')
            if floor not in apartments_by_floor:
                apartments_by_floor[floor] = []
            apartments_by_floor[floor].append(apt)

        # Ordenar pisos numéricamente
        sorted_floors = sorted(apartments_by_floor.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
        
        # Encabezados de pisos con color del tema (morado claro)
        floor_header_bg = "#f3e8ff"
        floor_fg = "#4c1d95"
        for i, floor in enumerate(sorted_floors):
            floor_header = tk.Frame(self.grid_container, bg=floor_header_bg, relief="solid", bd=1, height=40)
            floor_header.grid(row=0, column=i, padx=Spacing.SM, pady=(0, Spacing.SM), sticky="ew")
            floor_header.pack_propagate(False)
            floor_label = tk.Label(
                floor_header,
                text=f"Piso {floor}",
                font=("Segoe UI", 12, "bold"),
                bg=floor_header_bg,
                fg=floor_fg
            )
            floor_label.pack(expand=True)
            
            # Configurar peso de la columna
            self.grid_container.grid_columnconfigure(i, weight=1)

        # Crear apartamentos por piso
        max_apartments_per_floor = max(len(apts) for apts in apartments_by_floor.values()) if apartments_by_floor else 0
        
        for floor_idx, floor in enumerate(sorted_floors):
            floor_apartments = apartments_by_floor[floor]
            
            # Ordenar apartamentos del piso por número
            floor_apartments.sort(key=lambda x: str(x.get('number', '')))
            
            for apt_idx, apt in enumerate(floor_apartments):
                row = apt_idx + 1  # +1 porque la fila 0 es para los encabezados
                col = floor_idx
                self._create_apartment_cell(self.grid_container, apt, row, col)

    def _create_apartment_cell(self, parent, apt: Dict[str, Any], row: int, col: int):
        status_colors = {
            "Disponible": "#d4edda", "Ocupado": "#fff3cd", "En Mantenimiento": "#d1ecf1"
        }
        border_colors = {
            "Disponible": "#c3e6cb", "Ocupado": "#ffeeba", "En Mantenimiento": "#bee5eb"
        }
        text_colors = {
            "Disponible": "#155724", "Ocupado": "#856404", "En Mantenimiento": "#0c5460"
        }

        status = apt.get("status", "N/A")
        bg_color = status_colors.get(status, "#f8f9fa")
        border_color = border_colors.get(status, "#ced4da")
        text_color = text_colors.get(status, "black")

        # Ajustar altura según si está ocupado o no
        cell_height = 140 if status == "Ocupado" else 100
        
        cell = tk.Frame(parent, bg=bg_color, relief="solid", bd=2, highlightbackground=border_color, highlightcolor=border_color, height=cell_height)
        cell.grid(row=row, column=col, padx=Spacing.SM, pady=Spacing.SM, sticky="nsew")
        cell.pack_propagate(False)

        # Determinar el tipo de unidad para mostrar el título correcto
        unit_type = apt.get('unit_type', 'Apartamento Estándar')
        unit_number = apt.get('number', 'N/A')
        
        # Crear el título según el tipo de unidad
        if unit_type == "Local Comercial":
            title_text = f"Local: {unit_number}"
        elif unit_type == "Penthouse":
            title_text = f"Penthouse: {unit_number}"
        elif unit_type == "Depósito":
            title_text = f"Depósito: {unit_number}"
        elif unit_type == "Apartamento Estándar":
            title_text = f"Apto: {unit_number}"
        else:
            # Para tipos personalizados (como "Otro")
            title_text = f"{unit_type}: {unit_number}"

        # Título de la unidad
        title_label = tk.Label(cell, text=title_text, font=("Segoe UI", 11, "bold"), bg=bg_color, fg=text_color)
        title_label.pack(pady=(Spacing.SM, 2))
        
        # Estado
        status_label = tk.Label(cell, text=status, font=("Segoe UI", 9, "italic"), bg=bg_color, fg=text_color)
        status_label.pack(pady=(0, 2))

        # Información adicional si está ocupado
        if status == "Ocupado":
            # Buscar el inquilino activo que ocupa este apartamento (excluir desactivados)
            apartment_id = apt.get('id')
            tenant_name = "No asignado"
            tenant_rent = "0"
            
            all_tenants = tenant_service.get_all_tenants()
            # Solo inquilinos activos (estado_pago != "inactivo") para mostrar el ocupante actual
            active_tenants = [t for t in all_tenants if t.get('estado_pago') != 'inactivo']
            for tenant in active_tenants:
                if tenant.get('apartamento') == apartment_id:
                    tenant_name = tenant.get('nombre', 'No asignado')
                    tenant_rent = tenant.get('valor_arriendo', '0')
                    break
            
            # Shorten name if too long
            if len(tenant_name) > 15:
                tenant_name = tenant_name.split(' ')[0] + "..."
            
            tenant_label = tk.Label(
                cell, 
                text=tenant_name, 
                font=("Segoe UI", 8), 
                bg=bg_color, 
                fg=text_color, 
                wraplength=120
            )
            tenant_label.pack(pady=(2, 0), expand=True)
            
            # Mostrar el valor real del arriendo del inquilino
            if tenant_rent and tenant_rent != '0':
                try:
                    rent_display = f"${float(tenant_rent):,.0f}"
                    rent_label = tk.Label(
                        cell, 
                        text=rent_display, 
                        font=("Segoe UI", 8, "bold"), 
                        bg=bg_color, 
                        fg="#1976d2"
                    )
                    rent_label.pack(pady=(2, 0))
                except:
                    pass
    
    def _create_navigation_buttons(self, parent, on_back_command):
        """Crea los botones Volver y Dashboard con estilo moderno y colores morados del módulo de administración"""
        from manager.app.ui.components.icons import Icons
        
        # Colores morados para módulo de administración
        colors = get_module_colors("administración")
        purple_primary = colors["primary"]
        purple_hover = colors["hover"]
        purple_light = colors["light"]
        purple_text = colors["text"]
        
        # Botón "Dashboard" con icono de casita (siempre navega al dashboard principal)
        def go_to_dashboard():
            # Prioridad 1: Usar callback directo si está disponible
            if hasattr(self, 'on_navigate') and self.on_navigate is not None:
                try:
                    self.on_navigate("dashboard")
                    return
                except Exception as e:
                    print(f"Error en callback de navegación: {e}")
            
            # Prioridad 2: Buscar desde el root window (más confiable)
            try:
                root = self.winfo_toplevel()
                # Buscar MainWindow entre los hijos del root
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
            
            # Prioridad 3: Buscar MainWindow en la jerarquía de widgets
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
            
            # Prioridad 4: Si no se encontró MainWindow, usar on_back como fallback
            if on_back_command:
                on_back_command()
        
        theme = theme_manager.themes[theme_manager.current_theme]
        btn_bg = theme.get("btn_secondary_bg", "#e5e7eb")
        btn_back = create_rounded_button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color=btn_bg,
            fg_color=purple_primary,
            hover_bg=purple_light,
            hover_fg=purple_text,
            command=on_back_command,
            padx=16,
            pady=8,
            radius=4,
            border_color=purple_light
        )
        btn_back.pack(side="right", padx=(Spacing.MD, 0))
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
            border_color=purple_hover
        )
        btn_dashboard.pack(side="right") 