"""
Vista de reporte de Mantenimiento y Costos por Apartamento
Muestra el historial de mantenimiento y costos asociados por unidad
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
from manager.app.services.expense_service import expense_service
from manager.app.services.apartment_service import apartment_service

class MaintenanceCostReportView(tk.Frame):
    """Vista de reporte de mantenimiento y costos por apartamento"""
    
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
        
        title = tk.Label(header, text="Mantenimiento y Costos", **theme_manager.get_style("label_title"))
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
        
        tk.Label(filters_frame, text="Categoría:", font=("Segoe UI", 10)).pack(side="left", padx=(Spacing.LG, Spacing.SM))
        self.category_var = tk.StringVar(value="Todos")
        self.category_combo = ttk.Combobox(filters_frame, textvariable=self.category_var, state="readonly", width=20)
        self.category_combo.pack(side="left", padx=Spacing.SM)
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())
        
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
        """Carga y procesa los datos de gastos"""
        # Obtener todos los gastos
        all_expenses = expense_service.get_all_expenses()
        
        # Filtrar solo gastos de mantenimiento y reparaciones
        maintenance_categories = ["Mantenimiento", "Reparaciones"]
        maintenance_expenses = [
            e for e in all_expenses 
            if e.get("categoria") in maintenance_categories
        ]
        
        # Agrupar por apartamento
        self.apartment_expenses = defaultdict(list)
        for expense in maintenance_expenses:
            apt = expense.get("apartamento", "---")
            if apt == "---":
                apt = "General"
            self.apartment_expenses[apt].append(expense)
        
        # Preparar datos para filtros
        apartments = apartment_service.get_all_apartments()
        apartment_names = ["Todos"] + [
            f"{apt.get('unit_type', 'Apto')}: {apt.get('number', '')}" 
            for apt in apartments
        ] + ["General"]
        
        categories = ["Todos"] + maintenance_categories
        
        self.apartment_combo['values'] = apartment_names
        self.category_combo['values'] = categories
        
        self._apply_filters()
    
    def _apply_filters(self):
        """Aplica los filtros y muestra los resultados"""
        # Limpiar contenido anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        selected_apt = self.apartment_var.get()
        selected_category = self.category_var.get()
        
        # Filtrar datos
        filtered_data = {}
        for apt, expenses in self.apartment_expenses.items():
            filtered_expenses = expenses.copy()
            
            if selected_apt != "Todos":
                if selected_apt == "General" and apt != "General":
                    continue
                elif selected_apt != "General":
                    # Extraer número del apartamento del formato "Apto: 101"
                    apt_number = selected_apt.split(":")[-1].strip()
                    apt_obj = next((a for a in apartment_service.get_all_apartments() 
                                  if str(a.get('number')) == apt_number), None)
                    if not apt_obj or apt != f"{apt_obj.get('unit_type', 'Apto')}: {apt_obj.get('number', '')}":
                        continue
            
            if selected_category != "Todos":
                filtered_expenses = [e for e in filtered_expenses if e.get("categoria") == selected_category]
            
            if filtered_expenses:
                filtered_data[apt] = filtered_expenses
        
        if not filtered_data:
            tk.Label(
                self.content_frame,
                text="No se encontraron gastos de mantenimiento con los filtros seleccionados.",
                font=("Segoe UI", 12),
                fg="#666"
            ).pack(pady=Spacing.XL)
            return
        
        # Mostrar resumen general
        total_cost = sum(sum(float(e.get("monto", 0)) for e in expenses) 
                        for expenses in filtered_data.values())
        
        summary_frame = tk.Frame(self.content_frame, **theme_manager.get_style("card"))
        summary_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        tk.Label(
            summary_frame,
            text=f"Total de Gastos de Mantenimiento: ${total_cost:,.2f}",
            font=("Segoe UI", 14, "bold"),
            fg="#8b5cf6"
        ).pack(pady=Spacing.MD)
        
        tk.Label(
            summary_frame,
            text=f"Unidades con gastos: {len(filtered_data)}",
            font=("Segoe UI", 11),
            fg="#666"
        ).pack()
        
        # Mostrar detalles por apartamento
        for apt_name, expenses in sorted(filtered_data.items()):
            self._create_apartment_section(apt_name, expenses)
    
    def _create_apartment_section(self, apt_name: str, expenses: List[Dict[str, Any]]):
        """Crea una sección para un apartamento"""
        section_frame = tk.Frame(self.content_frame, **theme_manager.get_style("card"))
        section_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        # Header de la sección
        header_frame = tk.Frame(section_frame, bg="#f8f9fa", relief="solid", bd=1)
        header_frame.pack(fill="x", padx=Spacing.MD, pady=(Spacing.MD, 0))
        
        total_apt_cost = sum(float(e.get("monto", 0)) for e in expenses)
        
        tk.Label(
            header_frame,
            text=f"{apt_name}",
            font=("Segoe UI", 13, "bold"),
            bg="#f8f9fa",
            fg="#8b5cf6"
        ).pack(side="left", padx=Spacing.MD, pady=Spacing.SM)
        
        tk.Label(
            header_frame,
            text=f"Total: ${total_apt_cost:,.2f}",
            font=("Segoe UI", 12, "bold"),
            bg="#f8f9fa",
            fg="#333"
        ).pack(side="right", padx=Spacing.MD, pady=Spacing.SM)
        
        # Tabla de gastos
        table_frame = tk.Frame(section_frame, **theme_manager.get_style("card_content"))
        table_frame.pack(fill="x", padx=Spacing.MD, pady=Spacing.MD)
        
        # Encabezados
        headers = ["Fecha", "Categoría", "Subtipo", "Descripción", "Monto"]
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
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_columnconfigure(1, weight=1)
        table_frame.grid_columnconfigure(2, weight=1)
        table_frame.grid_columnconfigure(3, weight=2)
        table_frame.grid_columnconfigure(4, weight=1)
        
        # Filas de datos
        for row_idx, expense in enumerate(sorted(expenses, key=lambda x: x.get("fecha", ""), reverse=True), start=1):
            bg_color = "#ffffff" if row_idx % 2 == 0 else "#f8f9fa"
            
            # Fecha
            fecha_str = expense.get("fecha", "")
            fecha_display = ""
            if fecha_str:
                try:
                    fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d")
                    fecha_display = fecha_obj.strftime("%d/%m/%Y")
                except:
                    fecha_display = fecha_str
            
            tk.Label(
                table_frame,
                text=fecha_display,
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
                text=expense.get("categoria", ""),
                font=("Segoe UI", 9),
                bg=bg_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="w"
            ).grid(row=row_idx, column=1, sticky="ew", padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=expense.get("subtipo", ""),
                font=("Segoe UI", 9),
                bg=bg_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="w"
            ).grid(row=row_idx, column=2, sticky="ew", padx=1, pady=1)
            
            desc = expense.get("descripcion", "")
            desc_display = desc[:50] + "..." if len(desc) > 50 else desc
            tk.Label(
                table_frame,
                text=desc_display,
                font=("Segoe UI", 9),
                bg=bg_color,
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="w"
            ).grid(row=row_idx, column=3, sticky="ew", padx=1, pady=1)
            
            tk.Label(
                table_frame,
                text=f"${float(expense.get('monto', 0)):,.2f}",
                font=("Segoe UI", 9, "bold"),
                bg=bg_color,
                fg="#8b5cf6",
                relief="solid",
                bd=1,
                padx=Spacing.SM,
                pady=Spacing.XS,
                anchor="e"
            ).grid(row=row_idx, column=4, sticky="ew", padx=1, pady=1)
    
    def _create_navigation_buttons(self, parent):
        """Crea los botones de navegación con estilo moderno y colores naranjas del módulo de reportes"""
        from manager.app.ui.components.icons import Icons
        
        # Colores naranjas para módulo de reportes
        colors = get_module_colors("reportes")
        orange_primary = colors["primary"]
        orange_hover = colors["hover"]
        orange_light = colors["light"]
        orange_text = colors["text"]
        
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
        
        # Botón "Volver"
        btn_back = create_rounded_button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color="white",
            fg_color=orange_primary,
            hover_bg=orange_light,
            hover_fg=orange_text,
            command=self.on_back,
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
