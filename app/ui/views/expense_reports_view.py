"""
Vista completa de reportes de gastos para Building Manager Pro
Sistema escalable con múltiples tipos de reportes específicos de gastos
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from typing import Callable, Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
import csv
from pathlib import Path

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import ModernButton
from manager.app.services.expense_service import ExpenseService
from manager.app.services.apartment_service import apartment_service


class ExpenseReportsView(tk.Frame):
    """Vista completa de reportes de gastos del sistema"""
    
    def __init__(self, parent, on_back: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_back = on_back
        self.expense_service = ExpenseService()
        
        # Recargar datos antes de generar reportes
        self._reload_all_data()
        
        self._create_layout()
    
    def _reload_all_data(self):
        """Recarga todos los datos necesarios para los reportes"""
        try:
            self.expense_service._load_data()
            apartment_service._load_data()
        except Exception as e:
            print(f"Error al recargar datos: {e}")
    
    def _create_layout(self):
        """Crea el layout principal de la vista de reportes"""
        # Header
        header = tk.Frame(self, bg="#f8f9fa", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg="#f8f9fa")
        title_frame.pack(side="left", padx=15, fill="y", expand=True)
        
        tk.Label(
            title_frame,
            text="📊 Reportes de Gastos",
            font=("Segoe UI", 18, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        ).pack(side="left", pady=15)
        
        if self.on_back:
            ModernButton(
                header,
                text="← Volver",
                style="secondary",
                command=self.on_back
            ).pack(side="right", padx=15, pady=15)
        
        # Contenedor principal sin scroll
        main_container = tk.Frame(self, bg="#ffffff")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Contenido de reportes directamente en el contenedor principal
        self._create_reports_content(main_container)
    
    def _create_reports_content(self, parent):
        """Crea el contenido de los reportes"""
        # Contenedor principal que usa todo el espacio disponible
        cards_container = tk.Frame(parent, bg="#ffffff")
        cards_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Grid de cards - 4 columnas que se ajustan al espacio disponible
        cards_grid = tk.Frame(cards_container, bg="#ffffff")
        cards_grid.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Configurar grid para que las columnas se distribuyan equitativamente (4 columnas)
        cards_grid.columnconfigure(0, weight=1, uniform="cards", minsize=200)
        cards_grid.columnconfigure(1, weight=1, uniform="cards", minsize=200)
        cards_grid.columnconfigure(2, weight=1, uniform="cards", minsize=200)
        cards_grid.columnconfigure(3, weight=1, uniform="cards", minsize=200)
        
        # Definir los reportes específicos de gastos
        reports = [
            ("📅 Reporte por Período", 
             "Análisis de gastos por rango de fechas con comparativas.",
             "#2196F3", 
             self._generate_period_report),
            ("📂 Reporte por Categoría", 
             "Gastos agrupados por categoría con estadísticas.",
             "#9C27B0", 
             self._generate_category_report),
            ("🏢 Reporte por Apartamento", 
             "Análisis de gastos agrupados por apartamento.",
             "#4CAF50", 
             self._generate_apartment_report),
            ("💰 Reporte Consolidado", 
             "Vista financiera con totales, promedios y proyecciones.",
             "#F44336", 
             self._generate_consolidated_report),
            ("📈 Análisis de Tendencias", 
             "Evolución de gastos en el tiempo con comparativas.",
             "#FF9800", 
             self._generate_trends_report),
            ("🔍 Reporte por Subtipo", 
             "Gastos agrupados por subtipo dentro de cada categoría.",
             "#00BCD4", 
             self._generate_subtype_report),
            ("📊 Comparativa Anual", 
             "Comparar gastos entre diferentes años.",
             "#FF5722", 
             self._generate_year_comparison_report),
            ("🔄 Gastos Recurrentes", 
             "Identificar gastos que se repiten periódicamente.",
             "#795548", 
             self._generate_recurring_expenses_report)
        ]
        
        # Colocar cards en grid 4 columnas (2 filas de 4 cards)
        row = 0
        col = 0
        for title, description, color, command in reports:
            card = self._create_report_card(
                cards_grid,
                title,
                description,
                color,
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
    
    def _create_report_card(self, parent, title, description, color, command):
        """Crea una tarjeta de reporte que se ajusta uniformemente al espacio disponible"""
        card = tk.Frame(
            parent,
            bg="white",
            relief="raised",
            bd=2
        )
        
        content = tk.Frame(card, bg="white")
        # Padding ajustado para mejor distribución
        content.pack(fill="both", expand=True, padx=14, pady=12)
        
        # Contenedor para título con wraplength dinámico
        title_frame = tk.Frame(content, bg="white")
        title_frame.pack(anchor="w", pady=(0, 6), fill="x")
        
        # Icono y título
        title_label = tk.Label(
            title_frame,
            text=title,
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg=color,
            anchor="w",
            justify="left",
            wraplength=1  # Se ajustará automáticamente al ancho del frame
        )
        title_label.pack(anchor="w", fill="x")
        
        # Descripción - se ajusta al ancho disponible, más compacta
        desc_label = tk.Label(
            content,
            text=description,
            font=("Segoe UI", 9),
            bg="white",
            fg="#666",
            justify="left",
            anchor="w",
            wraplength=1  # Se ajustará automáticamente
        )
        desc_label.pack(anchor="w", pady=(0, 8), fill="x", expand=True)
        
        # Botón generar - siempre al fondo con tamaño consistente
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(fill="x", side="bottom", pady=(4, 0))
        
        btn = tk.Button(
            btn_frame,
            text="Generar Reporte",
            font=("Segoe UI", 9, "bold"),
            bg=color,
            fg="white",
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=command
        )
        btn.pack(fill="x")
        
        # Función para actualizar wraplength cuando el card cambie de tamaño
        def update_wraplength(event=None):
            if event:
                card_width = card.winfo_width()
                if card_width > 20:  # Solo actualizar si el card tiene un tamaño válido
                    # Calcular wraplength considerando el padding
                    available_width = card_width - 28  # 14px padding a cada lado
                    title_label.config(wraplength=max(available_width, 100))
                    desc_label.config(wraplength=max(available_width, 100))
        
        card.bind("<Configure>", update_wraplength)
        
        # Hover effect
        def on_enter(event):
            card.configure(bg="#f5f5f5")
            content.configure(bg="#f5f5f5")
            title_frame.configure(bg="#f5f5f5")
            title_label.configure(bg="#f5f5f5")
            desc_label.configure(bg="#f5f5f5")
            btn_frame.configure(bg="#f5f5f5")
        
        def on_leave(event):
            card.configure(bg="white")
            content.configure(bg="white")
            title_frame.configure(bg="white")
            title_label.configure(bg="white")
            desc_label.configure(bg="white")
            btn_frame.configure(bg="white")
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        content.bind("<Enter>", on_enter)
        content.bind("<Leave>", on_leave)
        
        return card
    
    # ==================== GENERADORES DE REPORTES ====================
    
    def _create_period_selection_window(self, title="Seleccionar Período", on_generate=None, button_color="#2196F3"):
        """Crea una ventana reutilizable para seleccionar período de reporte"""
        period_window = tk.Toplevel(self)
        period_window.title(title)
        period_window.geometry("550x640")
        period_window.transient(self)
        period_window.grab_set()
        
        # Título
        title_label = tk.Label(
            period_window,
            text="Seleccione el período para el reporte:",
            font=("Segoe UI", 13, "bold"),
            pady=15
        )
        title_label.pack()
        
        # Contenedor principal con padding - sin expand para evitar espacio extra
        main_container = tk.Frame(period_window)
        main_container.pack(fill="x", padx=25, pady=(10, 8))
        
        period_type = tk.StringVar(value="specific_month")
        
        # Opción 1: Selección rápida (Mes/Año actual)
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
        
        # Opción 2: Selección por año y mes específicos
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
        
        # Contenedor para los comboboxes de año y mes
        month_year_frame = tk.Frame(specific_frame)
        month_year_frame.pack(fill="x", padx=20)
        
        # Años disponibles (últimos 10 años + año actual)
        current_year = datetime.now().year
        years = [str(y) for y in range(current_year - 9, current_year + 1)]
        years.reverse()
        
        tk.Label(month_year_frame, text="Año:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        year_combo = ttk.Combobox(month_year_frame, values=years, width=12, state="readonly")
        year_combo.set(str(current_year))
        year_combo.pack(side="left", padx=(0, 20))
        
        # Meses
        months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        tk.Label(month_year_frame, text="Mes:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        month_combo = ttk.Combobox(month_year_frame, values=months, width=15, state="readonly")
        month_combo.set(months[datetime.now().month - 1])
        month_combo.pack(side="left")
        
        # Opción 3: Año específico completo (sin mes)
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
        
        # Contenedor para el combobox de año
        year_only_select_frame = tk.Frame(year_only_frame)
        year_only_select_frame.pack(fill="x", padx=20)
        
        tk.Label(year_only_select_frame, text="Año:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
        year_only_combo = ttk.Combobox(year_only_select_frame, values=years, width=12, state="readonly")
        year_only_combo.set(str(current_year))
        year_only_combo.pack(side="left")
        
        # Opción 4: Rango personalizado
        custom_frame = tk.LabelFrame(
            main_container,
            text="Rango Personalizado",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=10
        )
        custom_frame.pack(fill="x", pady=(0, 0))
        
        tk.Radiobutton(
            custom_frame,
            text="Rango de fechas personalizado",
            variable=period_type,
            value="custom",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(0, 8))
        
        # Campos para rango personalizado
        date_range_frame = tk.Frame(custom_frame)
        date_range_frame.pack(fill="x", padx=20)
        
        tk.Label(date_range_frame, text="Desde (DD/MM/YYYY):", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        date_from_entry = tk.Entry(date_range_frame, width=15, font=("Segoe UI", 9))
        date_from_entry.pack(side="left", padx=(0, 15))
        
        tk.Label(date_range_frame, text="Hasta (DD/MM/YYYY):", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
        date_to_entry = tk.Entry(date_range_frame, width=15, font=("Segoe UI", 9))
        date_to_entry.pack(side="left")
        
        # Botón generar - SIEMPRE VISIBLE al final, directamente después del main_container
        button_frame = tk.Frame(period_window)
        button_frame.pack(fill="x", pady=(0, 15))
        
        def generate_wrapper():
            if on_generate:
                on_generate(period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry, period_window)
        
        tk.Button(
            button_frame,
            text="Generar Reporte",
            font=("Segoe UI", 11, "bold"),
            bg=button_color,
            fg="white",
            relief="flat",
            padx=30,
            pady=10,
            cursor="hand2",
            command=generate_wrapper
        ).pack()
        
        return period_window, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry
    
    def _filter_expenses_by_period(self, expenses, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry):
        """Filtra gastos según el período seleccionado y retorna (filtered_expenses, period_name)"""
        filtered = []
        period_name = ""
        months = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        period = period_type.get()
        
        if period == "current_month":
            now = datetime.now()
            filtered = [e for e in expenses if self._is_this_month(e.get('fecha', ''))]
            period_name = f"{months[now.month - 1]} {now.year}"
            
        elif period == "current_year":
            filtered = [e for e in expenses if self._is_this_year(e.get('fecha', ''))]
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
            
            # Filtrar gastos del mes y año seleccionados
            for expense in expenses:
                try:
                    date_str = expense.get('fecha', '')
                    if date_str:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        if date_obj.year == year_num and date_obj.month == month_num:
                            filtered.append(expense)
                except Exception:
                    pass
            
            period_name = f"{selected_month} {selected_year}"
            
        elif period == "specific_year":
            # Obtener año seleccionado
            selected_year = year_only_combo.get()
            
            if not selected_year:
                return None, None
            
            year_num = int(selected_year)
            
            # Filtrar gastos del año seleccionado (todos los meses)
            for expense in expenses:
                try:
                    date_str = expense.get('fecha', '')
                    if date_str:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        if date_obj.year == year_num:
                            filtered.append(expense)
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
                filtered = [e for e in expenses if self._is_in_range(e.get('fecha', ''), date_from_obj, date_to_obj)]
                period_name = f"{date_from} a {date_to}"
            except ValueError:
                return None, None
        
        return filtered, period_name
    
    def _generate_period_report(self):
        """Genera reporte de gastos por período"""
        try:
            self._reload_all_data()
            
            expenses = self.expense_service.get_all_expenses()
            
            def on_generate(period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry, period_window):
                filtered, period_name = self._filter_expenses_by_period(
                    expenses, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry
                )
                
                if filtered is None:
                    messagebox.showerror("Error", "Por favor complete todos los campos requeridos.")
                    return
                
                if not filtered:
                    messagebox.showinfo("Sin datos", f"No hay gastos registrados para el período seleccionado.")
                    period_window.destroy()
                    return
                
                period_window.destroy()
                self._show_report_window(
                    f"Reporte de Gastos - {period_name}",
                    self._format_period_report(filtered, period_name),
                    "expense_period"
                )
            
            self._create_period_selection_window("Seleccionar Período", on_generate)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte por período: {str(e)}")
    
    def _generate_category_report(self):
        """Genera reporte de gastos por categoría"""
        try:
            self._reload_all_data()
            
            expenses = self.expense_service.get_all_expenses()
            
            if not expenses:
                messagebox.showinfo("Sin datos", "No hay gastos registrados para generar el reporte.")
                return
            
            def on_generate(period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry, period_window):
                filtered, period_name = self._filter_expenses_by_period(
                    expenses, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry
                )
                
                if filtered is None:
                    messagebox.showerror("Error", "Por favor complete todos los campos requeridos.")
                    return
                
                if not filtered:
                    messagebox.showinfo("Sin datos", f"No hay gastos registrados para el período seleccionado.")
                    period_window.destroy()
                    return
                
                # Agrupar por categoría
                categories_dict = {}
                for expense in filtered:
                    category = expense.get('categoria', 'Sin categoría')
                    if category not in categories_dict:
                        categories_dict[category] = {
                            'count': 0,
                            'total': 0,
                            'expenses': []
                        }
                    categories_dict[category]['count'] += 1
                    categories_dict[category]['total'] += float(expense.get('monto', 0))
                    categories_dict[category]['expenses'].append(expense)
                
                period_window.destroy()
                self._show_report_window(
                    f"Reporte por Categoría - {period_name}",
                    self._format_category_report(categories_dict, len(filtered), period_name),
                    "category"
                )
            
            self._create_period_selection_window("Seleccionar Período - Categoría", on_generate, button_color="#9C27B0")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte por categoría: {str(e)}")
    
    def _generate_apartment_report(self):
        """Genera reporte de gastos por apartamento"""
        try:
            self._reload_all_data()
            
            expenses = self.expense_service.get_all_expenses()
            apartments = apartment_service.get_all_apartments()
            
            if not expenses:
                messagebox.showinfo("Sin datos", "No hay gastos registrados para generar el reporte.")
                return
            
            # Crear ventana de selección con apartamento y período
            period_window = tk.Toplevel(self)
            period_window.title("Seleccionar Apartamento y Período")
            period_window.geometry("550x700")
            period_window.transient(self)
            period_window.grab_set()
            
            # Título
            title_label = tk.Label(
                period_window,
                text="Seleccione el apartamento y período:",
                font=("Segoe UI", 13, "bold"),
                pady=15
            )
            title_label.pack()
            
            # Contenedor principal
            main_container = tk.Frame(period_window)
            main_container.pack(fill="x", padx=25, pady=(10, 8))
            
            # Selección de apartamento
            apartment_frame = tk.LabelFrame(
                main_container,
                text="Seleccionar Apartamento",
                font=("Segoe UI", 10, "bold"),
                padx=15,
                pady=10
            )
            apartment_frame.pack(fill="x", pady=(0, 12))
            
            apartment_type = tk.StringVar(value="all")
            
            tk.Radiobutton(
                apartment_frame,
                text="Todos los apartamentos",
                variable=apartment_type,
                value="all",
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(3, 6))
            
            tk.Radiobutton(
                apartment_frame,
                text="Apartamento específico",
                variable=apartment_type,
                value="specific",
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(3, 6))
            
            # Lista de apartamentos
            apartment_list_frame = tk.Frame(apartment_frame)
            apartment_list_frame.pack(fill="x", padx=20)
            
            tk.Label(apartment_list_frame, text="Apartamento:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
            apartment_combo = ttk.Combobox(apartment_list_frame, width=20, state="readonly")
            
            if apartments:
                apartment_values = ["Todos"] + [f"{apt.get('number', 'N/A')}" for apt in apartments]
                apartment_combo['values'] = apartment_values
                apartment_combo.set("Todos")
            else:
                apartment_combo['values'] = ["No hay apartamentos"]
                apartment_combo.set("No hay apartamentos")
            
            apartment_combo.pack(side="left")
            
            # Ahora agregar el selector de período (reutilizando la lógica)
            period_type = tk.StringVar(value="specific_month")
            
            # Opción 1: Selección rápida (Mes/Año actual)
            quick_frame = tk.LabelFrame(
                main_container,
                text="Opciones Rápidas",
                font=("Segoe UI", 10, "bold"),
                padx=15,
                pady=8
            )
            quick_frame.pack(fill="x", pady=(0, 10))
            
            tk.Radiobutton(
                quick_frame,
                text="Mes actual",
                variable=period_type,
                value="current_month",
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=3)
            
            tk.Radiobutton(
                quick_frame,
                text="Año actual",
                variable=period_type,
                value="current_year",
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=3)
            
            # Opción 2: Selección por año y mes específicos
            specific_frame = tk.LabelFrame(
                main_container,
                text="Seleccionar Mes y Año Específicos",
                font=("Segoe UI", 10, "bold"),
                padx=15,
                pady=8
            )
            specific_frame.pack(fill="x", pady=(0, 10))
            
            tk.Radiobutton(
                specific_frame,
                text="Mes y año específicos",
                variable=period_type,
                value="specific_month",
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(0, 6))
            
            month_year_frame = tk.Frame(specific_frame)
            month_year_frame.pack(fill="x", padx=20)
            
            current_year = datetime.now().year
            years = [str(y) for y in range(current_year - 9, current_year + 1)]
            years.reverse()
            
            tk.Label(month_year_frame, text="Año:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
            year_combo = ttk.Combobox(month_year_frame, values=years, width=12, state="readonly")
            year_combo.set(str(current_year))
            year_combo.pack(side="left", padx=(0, 20))
            
            months = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
            
            tk.Label(month_year_frame, text="Mes:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
            month_combo = ttk.Combobox(month_year_frame, values=months, width=15, state="readonly")
            month_combo.set(months[datetime.now().month - 1])
            month_combo.pack(side="left")
            
            # Opción 3: Año específico completo
            year_only_frame = tk.LabelFrame(
                main_container,
                text="Seleccionar Año Completo",
                font=("Segoe UI", 10, "bold"),
                padx=15,
                pady=8
            )
            year_only_frame.pack(fill="x", pady=(0, 10))
            
            tk.Radiobutton(
                year_only_frame,
                text="Año específico completo (todos los meses)",
                variable=period_type,
                value="specific_year",
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(0, 6))
            
            year_only_select_frame = tk.Frame(year_only_frame)
            year_only_select_frame.pack(fill="x", padx=20)
            
            tk.Label(year_only_select_frame, text="Año:", font=("Segoe UI", 10)).pack(side="left", padx=(0, 10))
            year_only_combo = ttk.Combobox(year_only_select_frame, values=years, width=12, state="readonly")
            year_only_combo.set(str(current_year))
            year_only_combo.pack(side="left")
            
            # Opción 4: Rango personalizado
            custom_frame = tk.LabelFrame(
                main_container,
                text="Rango Personalizado",
                font=("Segoe UI", 10, "bold"),
                padx=15,
                pady=8
            )
            custom_frame.pack(fill="x", pady=(0, 0))
            
            tk.Radiobutton(
                custom_frame,
                text="Rango de fechas personalizado",
                variable=period_type,
                value="custom",
                font=("Segoe UI", 10)
            ).pack(anchor="w", pady=(0, 6))
            
            date_range_frame = tk.Frame(custom_frame)
            date_range_frame.pack(fill="x", padx=20)
            
            tk.Label(date_range_frame, text="Desde (DD/MM/YYYY):", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
            date_from_entry = tk.Entry(date_range_frame, width=15, font=("Segoe UI", 9))
            date_from_entry.pack(side="left", padx=(0, 15))
            
            tk.Label(date_range_frame, text="Hasta (DD/MM/YYYY):", font=("Segoe UI", 9)).pack(side="left", padx=(0, 5))
            date_to_entry = tk.Entry(date_range_frame, width=15, font=("Segoe UI", 9))
            date_to_entry.pack(side="left")
            
            # Botón generar
            button_frame = tk.Frame(period_window)
            button_frame.pack(fill="x", pady=(0, 15))
            
            def generate_wrapper():
                # Filtrar por período
                filtered, period_name = self._filter_expenses_by_period(
                    expenses, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry
                )
                
                if filtered is None:
                    messagebox.showerror("Error", "Por favor complete todos los campos requeridos.")
                    return
                
                if not filtered:
                    messagebox.showinfo("Sin datos", f"No hay gastos registrados para el período seleccionado.")
                    period_window.destroy()
                    return
                
                # Filtrar por apartamento si se seleccionó uno específico
                selected_apartment = None
                if apartment_type.get() == "specific":
                    selected_apartment = apartment_combo.get()
                    if selected_apartment and selected_apartment != "Todos":
                        filtered = [e for e in filtered if e.get('apartamento', '---') == selected_apartment]
                
                if not filtered:
                    messagebox.showinfo("Sin datos", f"No hay gastos registrados para los criterios seleccionados.")
                    period_window.destroy()
                    return
                
                # Agrupar por apartamento
                apt_expenses = {}
                for expense in filtered:
                    apt = expense.get('apartamento', 'General')
                    if apt == '---':
                        apt = 'General'
                    if apt not in apt_expenses:
                        apt_expenses[apt] = {
                            'count': 0,
                            'total': 0,
                            'expenses': []
                        }
                    apt_expenses[apt]['count'] += 1
                    apt_expenses[apt]['total'] += float(expense.get('monto', 0))
                    apt_expenses[apt]['expenses'].append(expense)
                
                period_window.destroy()
                self._show_report_window(
                    f"Reporte por Apartamento - {period_name}",
                    self._format_apartment_report(apt_expenses, period_name, selected_apartment),
                    "apartment"
                )
            
            tk.Button(
                button_frame,
                text="Generar Reporte",
                font=("Segoe UI", 11, "bold"),
                bg="#4CAF50",
                fg="white",
                relief="flat",
                padx=30,
                pady=10,
                cursor="hand2",
                command=generate_wrapper
            ).pack()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte por apartamento: {str(e)}")
    
    def _generate_consolidated_report(self):
        """Genera reporte consolidado de gastos"""
        try:
            self._reload_all_data()
            
            expenses = self.expense_service.get_all_expenses()
            
            if not expenses:
                messagebox.showinfo("Sin datos", "No hay gastos registrados para generar el reporte.")
                return
            
            def on_generate(period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry, period_window):
                filtered, period_name = self._filter_expenses_by_period(
                    expenses, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry
                )
                
                if filtered is None:
                    messagebox.showerror("Error", "Por favor complete todos los campos requeridos.")
                    return
                
                if not filtered:
                    messagebox.showinfo("Sin datos", f"No hay gastos registrados para el período seleccionado.")
                    period_window.destroy()
                    return
                
                # Calcular totales
                total_expenses = sum(float(e.get('monto', 0)) for e in filtered)
                avg_expense = total_expenses / len(filtered) if filtered else 0
                
                # Filtrar por período para comparativas
                now = datetime.now()
                this_month = [e for e in filtered if self._is_this_month(e.get('fecha', ''))]
                this_year = [e for e in filtered if self._is_this_year(e.get('fecha', ''))]
                
                monthly_expenses = sum(float(e.get('monto', 0)) for e in this_month)
                yearly_expenses = sum(float(e.get('monto', 0)) for e in this_year)
                
                # Proyección anual basada en el mes actual
                projected = monthly_expenses * 12 if this_month else 0
                
                period_window.destroy()
                self._show_report_window(
                    f"Reporte Consolidado - {period_name}",
                    self._format_consolidated_report(
                        total_expenses, monthly_expenses, yearly_expenses, len(filtered), 
                        avg_expense, monthly_expenses, projected, this_month, this_year, period_name
                    ),
                    "consolidated"
                )
            
            self._create_period_selection_window("Seleccionar Período - Consolidado", on_generate, button_color="#F44336")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte consolidado: {str(e)}")
    
    def _generate_trends_report(self):
        """Genera reporte de tendencias de gastos"""
        try:
            self._reload_all_data()
            
            expenses = self.expense_service.get_all_expenses()
            
            if not expenses:
                messagebox.showinfo("Sin datos", "No hay gastos registrados para generar el reporte.")
                return
            
            # Agrupar por mes
            monthly_data = {}
            for expense in expenses:
                try:
                    date_str = expense.get('fecha', '')
                    if date_str:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        month_key = f"{date_obj.year}-{date_obj.month:02d}"
                        if month_key not in monthly_data:
                            monthly_data[month_key] = {
                                'name': date_obj.strftime("%B %Y"),
                                'total': 0,
                                'count': 0
                            }
                        monthly_data[month_key]['total'] += float(expense.get('monto', 0))
                        monthly_data[month_key]['count'] += 1
                except Exception:
                    pass
            
            # Ordenar por fecha
            sorted_monthly = sorted(monthly_data.items())
            
            self._show_report_window(
                "Análisis de Tendencias de Gastos",
                self._format_trends_report(sorted_monthly, expenses),
                "trends"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de tendencias: {str(e)}")
    
    def _generate_subtype_report(self):
        """Genera reporte de gastos por subtipo"""
        try:
            self._reload_all_data()
            
            expenses = self.expense_service.get_all_expenses()
            
            if not expenses:
                messagebox.showinfo("Sin datos", "No hay gastos registrados para generar el reporte.")
                return
            
            def on_generate(period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry, period_window):
                filtered, period_name = self._filter_expenses_by_period(
                    expenses, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry
                )
                
                if filtered is None:
                    messagebox.showerror("Error", "Por favor complete todos los campos requeridos.")
                    return
                
                if not filtered:
                    messagebox.showinfo("Sin datos", f"No hay gastos registrados para el período seleccionado.")
                    period_window.destroy()
                    return
                
                # Agrupar por categoría y subtipo
                subtype_dict = {}
                for expense in filtered:
                    category = expense.get('categoria', 'Sin categoría')
                    subtype = expense.get('subtipo', 'Sin subtipo')
                    key = f"{category} - {subtype}"
                    
                    if key not in subtype_dict:
                        subtype_dict[key] = {
                            'category': category,
                            'subtype': subtype,
                            'count': 0,
                            'total': 0,
                            'expenses': []
                        }
                    subtype_dict[key]['count'] += 1
                    subtype_dict[key]['total'] += float(expense.get('monto', 0))
                    subtype_dict[key]['expenses'].append(expense)
                
                period_window.destroy()
                self._show_report_window(
                    f"Reporte por Subtipo - {period_name}",
                    self._format_subtype_report(subtype_dict, len(filtered), period_name),
                    "subtype"
                )
            
            self._create_period_selection_window("Seleccionar Período - Subtipo", on_generate, button_color="#00BCD4")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte por subtipo: {str(e)}")
    
    def _generate_year_comparison_report(self):
        """Genera reporte comparativo anual"""
        try:
            self._reload_all_data()
            
            expenses = self.expense_service.get_all_expenses()
            
            if not expenses:
                messagebox.showinfo("Sin datos", "No hay gastos registrados para generar el reporte.")
                return
            
            # Ventana para seleccionar años
            year_window = tk.Toplevel(self)
            year_window.title("Seleccionar Años para Comparar")
            year_window.geometry("500x400")
            year_window.transient(self)
            year_window.grab_set()
            
            tk.Label(
                year_window,
                text="Seleccione los años a comparar:",
                font=("Segoe UI", 13, "bold"),
                pady=20
            ).pack()
            
            main_frame = tk.Frame(year_window)
            main_frame.pack(fill="both", expand=True, padx=25, pady=15)
            
            current_year = datetime.now().year
            years = [str(y) for y in range(current_year - 9, current_year + 1)]
            years.reverse()
            
            tk.Label(main_frame, text="Año 1:", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 5))
            year1_combo = ttk.Combobox(main_frame, values=years, width=15, state="readonly")
            year1_combo.set(str(current_year))
            year1_combo.pack(anchor="w", pady=(0, 15))
            
            tk.Label(main_frame, text="Año 2:", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 5))
            year2_combo = ttk.Combobox(main_frame, values=years, width=15, state="readonly")
            if current_year > int(years[0]):
                year2_combo.set(str(current_year - 1))
            else:
                year2_combo.set(str(current_year))
            year2_combo.pack(anchor="w", pady=(0, 15))
            
            def generate():
                year1 = year1_combo.get()
                year2 = year2_combo.get()
                
                if not year1 or not year2:
                    messagebox.showerror("Error", "Por favor seleccione ambos años.")
                    return
                
                if year1 == year2:
                    messagebox.showerror("Error", "Por favor seleccione años diferentes.")
                    return
                
                # Filtrar gastos por año
                year1_expenses = [e for e in expenses if self._is_year(e.get('fecha', ''), int(year1))]
                year2_expenses = [e for e in expenses if self._is_year(e.get('fecha', ''), int(year2))]
                
                if not year1_expenses and not year2_expenses:
                    messagebox.showinfo("Sin datos", "No hay gastos registrados para los años seleccionados.")
                    year_window.destroy()
                    return
                
                year_window.destroy()
                self._show_report_window(
                    f"Comparativa Anual - {year1} vs {year2}",
                    self._format_year_comparison_report(year1, year2, year1_expenses, year2_expenses),
                    "year_comparison"
                )
            
            button_frame = tk.Frame(year_window)
            button_frame.pack(fill="x", pady=(10, 20))
            
            tk.Button(
                button_frame,
                text="Generar Reporte",
                font=("Segoe UI", 11, "bold"),
                bg="#FF5722",
                fg="white",
                relief="flat",
                padx=30,
                pady=10,
                cursor="hand2",
                command=generate
            ).pack()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte comparativo: {str(e)}")
    
    def _generate_recurring_expenses_report(self):
        """Genera reporte de gastos recurrentes"""
        try:
            self._reload_all_data()
            
            expenses = self.expense_service.get_all_expenses()
            
            if not expenses:
                messagebox.showinfo("Sin datos", "No hay gastos registrados para generar el reporte.")
                return
            
            # Identificar gastos recurrentes (mismo subtipo, similar monto, en diferentes meses)
            recurring = {}
            for expense in expenses:
                subtype = expense.get('subtipo', '')
                monto = float(expense.get('monto', 0))
                categoria = expense.get('categoria', '')
                
                if not subtype:
                    continue
                
                key = f"{categoria} - {subtype}"
                if key not in recurring:
                    recurring[key] = {
                        'category': categoria,
                        'subtype': subtype,
                        'count': 0,
                        'total': 0,
                        'amounts': [],
                        'expenses': []
                    }
                
                recurring[key]['count'] += 1
                recurring[key]['total'] += monto
                recurring[key]['amounts'].append(monto)
                recurring[key]['expenses'].append(expense)
            
            # Filtrar solo los que aparecen 3 o más veces (recurrentes)
            recurring_filtered = {k: v for k, v in recurring.items() if v['count'] >= 3}
            
            if not recurring_filtered:
                messagebox.showinfo("Sin datos", "No se encontraron gastos recurrentes (3 o más ocurrencias).")
                return
            
            self._show_report_window(
                "Reporte de Gastos Recurrentes",
                self._format_recurring_expenses_report(recurring_filtered),
                "recurring"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de gastos recurrentes: {str(e)}")
    
    # ==================== FORMATO DE REPORTES ====================
    
    def _format_period_report(self, expenses, period_name):
        """Formatea el reporte por período"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE GASTOS POR PERÍODO")
        report.append(f"Período: {period_name}")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append(f"PERÍODO SELECCIONADO: {period_name}")
        report.append("")
        report.append("RESUMEN:")
        report.append(f"  • Total de gastos: {len(expenses)}")
        report.append(f"  • Total gastado: ${sum(float(e.get('monto', 0)) for e in expenses):,.2f}")
        report.append(f"  • Promedio por gasto: ${sum(float(e.get('monto', 0)) for e in expenses) / len(expenses):,.2f}" if expenses else "  • Promedio por gasto: $0.00")
        report.append("")
        report.append("DETALLE DE GASTOS:")
        report.append("-" * 60)
        
        # Ordenar por fecha
        sorted_expenses = sorted(expenses, key=lambda x: x.get('fecha', ''), reverse=True)
        
        for expense in sorted_expenses:
            fecha_str = expense.get('fecha', '')
            try:
                fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d")
                fecha_display = fecha_obj.strftime("%d/%m/%Y")
            except:
                fecha_display = fecha_str
            
            report.append(f"Fecha: {fecha_display}")
            report.append(f"  • Categoría: {expense.get('categoria', 'N/A')}")
            report.append(f"  • Subtipo: {expense.get('subtipo', 'N/A')}")
            report.append(f"  • Apartamento: {expense.get('apartamento', 'General')}")
            report.append(f"  • Monto: ${float(expense.get('monto', 0)):,.2f}")
            report.append(f"  • Descripción: {expense.get('descripcion', 'N/A')}")
            report.append("")
        
        return "\n".join(report)
    
    def _format_category_report(self, categories_dict, total_expenses, period_name=None):
        """Formatea el reporte por categoría"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE GASTOS POR CATEGORÍA")
        if period_name:
            report.append(f"Período: {period_name}")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        if period_name:
            report.append(f"PERÍODO SELECCIONADO: {period_name}")
            report.append("")
        report.append("RESUMEN GENERAL:")
        report.append(f"  • Total de gastos: {total_expenses}")
        report.append(f"  • Total gastado: ${sum(c['total'] for c in categories_dict.values()):,.2f}")
        report.append("")
        report.append("ANÁLISIS POR CATEGORÍA:")
        report.append("-" * 60)
        
        # Ordenar por total (mayor a menor)
        sorted_categories = sorted(categories_dict.items(), key=lambda x: x[1]['total'], reverse=True)
        
        for category, data in sorted_categories:
            percentage = (data['total'] / sum(c['total'] for c in categories_dict.values()) * 100) if categories_dict else 0
            report.append(f"Categoría: {category}")
            report.append(f"  • Cantidad de gastos: {data['count']}")
            report.append(f"  • Total gastado: ${data['total']:,.2f}")
            report.append(f"  • Porcentaje del total: {percentage:.2f}%")
            report.append(f"  • Promedio por gasto: ${data['total']/data['count']:,.2f}")
            report.append("")
        
        return "\n".join(report)
    
    def _format_apartment_report(self, apt_expenses, period_name=None, selected_apartment=None):
        """Formatea el reporte de gastos por apartamento"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE GASTOS POR APARTAMENTO")
        if period_name:
            report.append(f"Período: {period_name}")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        if selected_apartment:
            report.append(f"APARTAMENTO SELECCIONADO: {selected_apartment}")
            report.append("")
        if period_name:
            report.append(f"PERÍODO SELECCIONADO: {period_name}")
            report.append("")
        report.append(f"Total de apartamentos con gastos: {len(apt_expenses)}")
        report.append("")
        report.append("DETALLE POR APARTAMENTO:")
        report.append("-" * 60)
        
        # Ordenar por número de apartamento
        def sort_key(item):
            apt_num = item[0]
            if apt_num == 'General':
                return 'ZZZ'  # General al final
            try:
                return f"{int(apt_num):04d}"  # Ordenar numéricamente
            except:
                return apt_num
        
        sorted_apts = sorted(apt_expenses.items(), key=sort_key)
        
        for apt_num, data in sorted_apts:
            report.append(f"Apartamento {apt_num}:")
            report.append(f"  • Total de gastos: {data['count']}")
            report.append(f"  • Total gastado: ${data['total']:,.2f}")
            report.append(f"  • Promedio por gasto: ${data['total']/data['count']:,.2f}" if data['count'] > 0 else "  • Promedio por gasto: $0.00")
            report.append("")
            report.append("  Historial de gastos:")
            # Ordenar gastos por fecha
            sorted_expenses = sorted(data['expenses'], key=lambda x: x.get('fecha', ''), reverse=True)
            for expense in sorted_expenses[:5]:  # Mostrar últimos 5
                fecha_str = expense.get('fecha', '')
                try:
                    fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d")
                    fecha_display = fecha_obj.strftime("%d/%m/%Y")
                except:
                    fecha_display = fecha_str
                report.append(f"    - {fecha_display}: ${float(expense.get('monto', 0)):,.2f} ({expense.get('categoria', 'N/A')})")
            if len(sorted_expenses) > 5:
                report.append(f"    ... y {len(sorted_expenses) - 5} gasto(s) más")
            report.append("")
        
        return "\n".join(report)
    
    def _format_consolidated_report(self, total, monthly, yearly, count, avg_expense, avg_monthly, projected, this_month, this_year, period_name=None):
        """Formatea el reporte consolidado"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE CONSOLIDADO DE GASTOS")
        if period_name:
            report.append(f"Período: {period_name}")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        if period_name:
            report.append(f"PERÍODO SELECCIONADO: {period_name}")
            report.append("")
        report.append("RESUMEN FINANCIERO:")
        report.append(f"  • Gastos totales (histórico): ${total:,.2f}")
        report.append(f"  • Gastos del mes actual: ${monthly:,.2f}")
        report.append(f"  • Gastos del año actual: ${yearly:,.2f}")
        report.append(f"  • Total de gastos procesados: {count}")
        report.append("")
        report.append("ESTADÍSTICAS:")
        report.append(f"  • Promedio por gasto: ${avg_expense:,.2f}")
        report.append(f"  • Promedio mensual (mes actual): ${avg_monthly:,.2f}")
        if projected > 0:
            report.append(f"  • Proyección anual (basada en mes actual): ${projected:,.2f}")
        report.append("")
        report.append("DETALLE POR PERÍODO:")
        report.append("-" * 60)
        report.append(f"  • Gastos en el mes actual: {len(this_month)}")
        report.append(f"  • Gastos en el año actual: {len(this_year)}")
        
        return "\n".join(report)
    
    def _format_trends_report(self, monthly_data, all_expenses):
        """Formatea el reporte de tendencias"""
        report = []
        report.append("=" * 60)
        report.append("ANÁLISIS DE TENDENCIAS DE GASTOS")
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
            report.append(f"  • Total gastado: ${data['total']:,.2f}")
            report.append(f"  • Cantidad de gastos: {data['count']}")
            report.append(f"  • Promedio por gasto: ${data['total']/data['count']:,.2f}" if data['count'] > 0 else "  • Promedio por gasto: $0.00")
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
    
    def _format_subtype_report(self, subtype_dict, total_expenses, period_name=None):
        """Formatea el reporte por subtipo"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE GASTOS POR SUBTIPO")
        if period_name:
            report.append(f"Período: {period_name}")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        if period_name:
            report.append(f"PERÍODO SELECCIONADO: {period_name}")
            report.append("")
        report.append("RESUMEN GENERAL:")
        report.append(f"  • Total de gastos: {total_expenses}")
        report.append(f"  • Total gastado: ${sum(s['total'] for s in subtype_dict.values()):,.2f}")
        report.append("")
        report.append("ANÁLISIS POR SUBTIPO:")
        report.append("-" * 60)
        
        # Ordenar por total (mayor a menor)
        sorted_subtypes = sorted(subtype_dict.items(), key=lambda x: x[1]['total'], reverse=True)
        
        for key, data in sorted_subtypes:
            percentage = (data['total'] / sum(s['total'] for s in subtype_dict.values()) * 100) if subtype_dict else 0
            report.append(f"Categoría: {data['category']}")
            report.append(f"Subtipo: {data['subtype']}")
            report.append(f"  • Cantidad de gastos: {data['count']}")
            report.append(f"  • Total gastado: ${data['total']:,.2f}")
            report.append(f"  • Porcentaje del total: {percentage:.2f}%")
            report.append(f"  • Promedio por gasto: ${data['total']/data['count']:,.2f}")
            report.append("")
        
        return "\n".join(report)
    
    def _format_year_comparison_report(self, year1, year2, year1_expenses, year2_expenses):
        """Formatea el reporte comparativo anual"""
        report = []
        report.append("=" * 60)
        report.append("COMPARATIVA ANUAL DE GASTOS")
        report.append(f"{year1} vs {year2}")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        
        total1 = sum(float(e.get('monto', 0)) for e in year1_expenses)
        total2 = sum(float(e.get('monto', 0)) for e in year2_expenses)
        
        report.append(f"AÑO {year1}:")
        report.append(f"  • Total de gastos: {len(year1_expenses)}")
        report.append(f"  • Total gastado: ${total1:,.2f}")
        report.append(f"  • Promedio por gasto: ${total1/len(year1_expenses):,.2f}" if year1_expenses else "  • Promedio por gasto: $0.00")
        report.append("")
        
        report.append(f"AÑO {year2}:")
        report.append(f"  • Total de gastos: {len(year2_expenses)}")
        report.append(f"  • Total gastado: ${total2:,.2f}")
        report.append(f"  • Promedio por gasto: ${total2/len(year2_expenses):,.2f}" if year2_expenses else "  • Promedio por gasto: $0.00")
        report.append("")
        
        report.append("ANÁLISIS COMPARATIVO:")
        report.append("-" * 60)
        difference = total1 - total2
        difference_percent = (difference / total2 * 100) if total2 > 0 else 0
        report.append(f"  • Diferencia absoluta: ${difference:,.2f}")
        report.append(f"  • Variación porcentual: {difference_percent:+.2f}%")
        
        if total1 > total2:
            report.append(f"  • El año {year1} tuvo un {abs(difference_percent):.2f}% más de gastos que {year2}")
        elif total1 < total2:
            report.append(f"  • El año {year1} tuvo un {abs(difference_percent):.2f}% menos de gastos que {year2}")
        else:
            report.append(f"  • Ambos años tuvieron el mismo total de gastos")
        
        return "\n".join(report)
    
    def _format_recurring_expenses_report(self, recurring_dict):
        """Formatea el reporte de gastos recurrentes"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE GASTOS RECURRENTES")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append("RESUMEN:")
        report.append(f"  • Total de tipos de gastos recurrentes: {len(recurring_dict)}")
        report.append(f"  • Total gastado en gastos recurrentes: ${sum(r['total'] for r in recurring_dict.values()):,.2f}")
        report.append("")
        report.append("DETALLE DE GASTOS RECURRENTES:")
        report.append("-" * 60)
        
        # Ordenar por frecuencia (mayor a menor)
        sorted_recurring = sorted(recurring_dict.items(), key=lambda x: x[1]['count'], reverse=True)
        
        for key, data in sorted_recurring:
            avg_amount = sum(data['amounts']) / len(data['amounts']) if data['amounts'] else 0
            min_amount = min(data['amounts']) if data['amounts'] else 0
            max_amount = max(data['amounts']) if data['amounts'] else 0
            
            report.append(f"Categoría: {data['category']}")
            report.append(f"Subtipo: {data['subtype']}")
            report.append(f"  • Frecuencia: {data['count']} veces")
            report.append(f"  • Total gastado: ${data['total']:,.2f}")
            report.append(f"  • Promedio por ocurrencia: ${avg_amount:,.2f}")
            report.append(f"  • Rango: ${min_amount:,.2f} - ${max_amount:,.2f}")
            report.append("")
        
        return "\n".join(report)
    
    # ==================== VENTANA DE REPORTE ====================
    
    def _show_report_window(self, title, content, report_type):
        """Muestra una ventana con el reporte generado"""
        report_window = tk.Toplevel(self)
        report_window.title(title)
        report_window.geometry("800x600")
        report_window.transient(self)
        
        # Header
        header = tk.Frame(report_window, bg="#f8f9fa", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        ).pack(side="left", padx=15, pady=12)
        
        # Botones de acción
        buttons_frame = tk.Frame(header, bg="#f8f9fa")
        buttons_frame.pack(side="right", padx=15, pady=8)
        
        def save_report():
            file_path = tk.filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    messagebox.showinfo("Éxito", f"Reporte guardado en: {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al guardar el reporte: {str(e)}")
        
        tk.Button(
            buttons_frame,
            text="Guardar",
            font=("Segoe UI", 10),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2",
            command=save_report
        ).pack(side="left", padx=(0, 5))
        
        tk.Button(
            buttons_frame,
            text="Cerrar",
            font=("Segoe UI", 10),
            bg="#757575",
            fg="white",
            relief="flat",
            padx=15,
            pady=5,
            cursor="hand2",
            command=report_window.destroy
        ).pack(side="left")
        
        # Contenido del reporte
        text_frame = tk.Frame(report_window)
        text_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        text_widget = scrolledtext.ScrolledText(
            text_frame,
            font=("Consolas", 10),
            wrap=tk.WORD,
            bg="#ffffff",
            fg="#000000"
        )
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", content)
        text_widget.config(state=tk.DISABLED)
    
    # ==================== HELPERS ====================
    
    def _is_this_month(self, date_str):
        """Verifica si una fecha corresponde al mes actual"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            now = datetime.now()
            return date.year == now.year and date.month == now.month
        except:
            return False
    
    def _is_this_year(self, date_str):
        """Verifica si una fecha corresponde al año actual"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return date.year == datetime.now().year
        except:
            return False
    
    def _is_year(self, date_str, year):
        """Verifica si una fecha corresponde a un año específico"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return date.year == year
        except:
            return False
    
    def _is_in_range(self, date_str, date_from, date_to):
        """Verifica si una fecha está en un rango"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return date_from <= date <= date_to
        except:
            return False
