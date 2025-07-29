"""
Vista visual para mostrar el estado de ocupación de los apartamentos.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Dict, Any

from manager.app.services.apartment_service import apartment_service
from manager.app.services.tenant_service import tenant_service
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import ModernButton

class OccupationStatusView(tk.Frame):
    """Vista de estado de ocupación con una cuadrícula visual."""

    def __init__(self, parent, on_back: Callable):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_back = on_back
        
        self._create_layout()
        self._load_and_display_apartments()

    def _create_layout(self):
        # Header
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)
        tk.Label(header, text="Estado de Ocupación", **theme_manager.get_style("label_title")).pack(side="left")
        ModernButton(header, text="← Volver", style="secondary", command=self.on_back).pack(side="right")

        # Legend
        self._create_legend()

        # Apartments Grid Container
        self.grid_container = tk.Frame(self, **theme_manager.get_style("frame"))
        self.grid_container.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)

    def _create_legend(self):
        legend_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        legend_frame.pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.MD))
        
        statuses = [("Disponible", "green"), ("Ocupado", "orange"), ("En Mantenimiento", "blue")]
        
        tk.Label(legend_frame, text="Leyenda:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, Spacing.SM))

        for status, color in statuses:
            legend_item = tk.Frame(legend_frame, **theme_manager.get_style("frame"))
            legend_item.pack(side="left", padx=Spacing.SM)
            tk.Label(legend_item, text="●", fg=color, font=("Segoe UI", 12, "bold")).pack(side="left")
            tk.Label(legend_item, text=status, font=("Segoe UI", 10)).pack(side="left")

    def _load_and_display_apartments(self):
        apartments = apartment_service.get_all_apartments()
        
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
        
        # Crear encabezados de pisos
        for i, floor in enumerate(sorted_floors):
            # Encabezado del piso
            floor_header = tk.Frame(self.grid_container, bg="#f8f9fa", relief="solid", bd=1, height=40)
            floor_header.grid(row=0, column=i, padx=Spacing.SM, pady=(0, Spacing.SM), sticky="ew")
            floor_header.pack_propagate(False)
            
            floor_label = tk.Label(
                floor_header, 
                text=f"Piso {floor}", 
                font=("Segoe UI", 12, "bold"), 
                bg="#f8f9fa", 
                fg="#495057"
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
            # Buscar el inquilino que ocupa este apartamento
            apartment_id = apt.get('id')
            tenant_name = "No asignado"
            tenant_rent = "0"
            
            # Buscar inquilino por ID del apartamento
            all_tenants = tenant_service.get_all_tenants()
            for tenant in all_tenants:
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