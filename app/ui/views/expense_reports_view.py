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
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton, create_rounded_button, get_module_colors
from manager.app.services.expense_service import ExpenseService
from manager.app.services.apartment_service import apartment_service
from manager.app.paths_config import EXPORTS_DIR, ensure_dirs
from manager.app.ui.views.register_expense_view import DatePickerWidget

# Rojo más oscuro del módulo para iconos, títulos y botones (contraste)
DARK_RED = "#991b1b"
# Fondo sólido de las cards (rojo claro) para que no queden transparentes
CARD_BG = "#fee2e2"


class ExpenseReportsView(tk.Frame):
    """Vista completa de reportes de gastos del sistema"""
    
    def __init__(self, parent, on_back: Callable = None, on_navigate_to_dashboard: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.on_back = on_back
        self.on_navigate_to_dashboard = on_navigate_to_dashboard
        self.expense_service = ExpenseService()
        
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
        cb = self._content_bg
        theme = theme_manager.themes[theme_manager.current_theme]
        
        main_container = tk.Frame(self, bg=cb)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        header_frame = tk.Frame(main_container, bg=cb)
        header_frame.pack(fill="x", pady=(0, Spacing.MD))
        
        title_label = tk.Label(
            header_frame,
            text="📊 Reportes de Gastos",
            font=("Segoe UI", 18, "bold"),
            bg=cb,
            fg=theme["text_primary"]
        )
        title_label.pack(side="left", padx=(0, Spacing.LG))
        
        if self.on_back:
            self._create_navigation_buttons(header_frame, self.on_back)
        
        self._create_reports_content(main_container)
    
    def _create_reports_content(self, parent):
        """Crea el contenido de los reportes"""
        cb = self._content_bg
        
        cards_container = tk.Frame(parent, bg=cb)
        cards_container.pack(fill="both", expand=True, pady=(0, 10))
        
        cards_grid = tk.Frame(cards_container, bg=cb)
        cards_grid.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Tres columnas: Categoría y Subtipo, Apartamento, Comparativa Anual
        cards_grid.columnconfigure(0, weight=1, uniform="cards", minsize=200)
        cards_grid.columnconfigure(1, weight=1, uniform="cards", minsize=200)
        cards_grid.columnconfigure(2, weight=1, uniform="cards", minsize=200)
        
        reports = [
            ("📂 Reporte por Categoría y Subtipo",
             "Gastos agrupados por categoría y por subtipo con estadísticas.",
             self._generate_category_and_subtype_report),
            ("🏢 Reporte por Apartamento",
             "Análisis de gastos agrupados por apartamento.",
             self._generate_apartment_report),
            ("📊 Comparativa Anual",
             "Comparar gastos entre diferentes años.",
             self._generate_year_comparison_report),
        ]
        
        row = 0
        col = 0
        for title, description, command in reports:
            card = self._create_report_card(cards_grid, title, description, command)
            card.grid(row=row, column=col, padx=10, pady=8, sticky="nsew")
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        for r in range(row + 1):
            cards_grid.rowconfigure(r, weight=1, uniform="rows", minsize=200)
    
    def _create_report_card(self, parent, title, description, command):
        """Crea una tarjeta de reporte con fondo sólido (CARD_BG), rojo oscuro para icono, título y botón. Mismo estilo que reportes de pagos."""
        theme = theme_manager.themes[theme_manager.current_theme]
        card_bg = CARD_BG
        card = tk.Frame(parent, bg=card_bg, relief="raised", bd=2)
        
        content = tk.Frame(card, bg=card_bg)
        content.pack(fill="both", expand=True, padx=14, pady=12)
        
        title_frame = tk.Frame(content, bg=card_bg)
        title_frame.pack(anchor="w", pady=(0, 6), fill="x")
        
        title_label = tk.Label(
            title_frame,
            text=title,
            font=("Segoe UI", 13, "bold"),
            bg=card_bg,
            fg=DARK_RED,
            anchor="w",
            justify="left",
            wraplength=1
        )
        title_label.pack(anchor="w", fill="x")
        
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
        
        btn_frame = tk.Frame(content, bg=card_bg)
        btn_frame.pack(fill="x", side="bottom", pady=(4, 0))
        
        btn_red_hover = "#b91c1c"
        btn = tk.Button(
            btn_frame,
            text="Generar Reporte",
            font=("Segoe UI", 9, "bold"),
            bg=DARK_RED,
            fg="white",
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
            command=command
        )
        btn.pack(fill="x")
        btn.bind("<Enter>", lambda e: btn.config(bg=btn_red_hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=DARK_RED))
        
        def update_wraplength(event=None):
            if event:
                card_width = card.winfo_width()
                if card_width > 20:
                    available_width = card_width - 28
                    title_label.config(wraplength=max(available_width, 100))
                    desc_label.config(wraplength=max(available_width, 100))
        
        card.bind("<Configure>", update_wraplength)
        
        hover_bg = "#fecaca"
        def on_enter(event):
            card.configure(bg=hover_bg)
            content.configure(bg=hover_bg)
            title_frame.configure(bg=hover_bg)
            title_label.configure(bg=hover_bg)
            desc_label.configure(bg=hover_bg)
            btn_frame.configure(bg=hover_bg)
        
        def on_leave(event):
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
    
    def _create_period_selection_window(self, title="Seleccionar Período", on_generate=None, button_color="#dc2626"):
        """Ventana compacta para seleccionar período de reporte (sin opciones rápidas)."""
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

        # Selección por año y mes específicos
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
        
        # Años disponibles (últimos 10 años + año actual)
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

        # Año completo
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

        # Rango personalizado
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
    
    def _generate_apartment_report(self):
        """Genera reporte de gastos por apartamento"""
        try:
            self._reload_all_data()
            
            expenses = self.expense_service.get_all_expenses()
            apartments = apartment_service.get_all_apartments()
            
            if not expenses:
                messagebox.showinfo("Sin datos", "No hay gastos registrados para generar el reporte.")
                return
            
            period_window = tk.Toplevel(self)
            period_window.title("Seleccionar Apartamento y Período")
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
                # Filtrar por período
                filtered, period_name = self._filter_expenses_by_period(
                    expenses, period_type, year_combo, month_combo, year_only_combo, date_from_entry, date_to_entry
                )
                
                if filtered is None:
                    messagebox.showerror("Error", "Por favor complete todos los campos requeridos.")
                    return
                
                if not filtered:
                    messagebox.showinfo("Sin datos", f"No hay gastos registrados para el período seleccionado.")
                    return
                
                # Filtrar por apartamento si se seleccionó uno específico
                selected_apartment = None
                if apartment_type.get() == "specific":
                    selected_apartment = apartment_combo.get()
                    if selected_apartment and selected_apartment != "Todos":
                        filtered = [e for e in filtered if e.get('apartamento', '---') == selected_apartment]
                
                if not filtered:
                    messagebox.showinfo("Sin datos", f"No hay gastos registrados para los criterios seleccionados.")
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
                font=("Segoe UI", 10, "bold"),
                bg="#dc2626",
                fg="white",
                relief="flat",
                padx=22,
                pady=6,
                cursor="hand2",
                command=generate_wrapper
            ).pack()

            period_window.after(50, period_window.focus_force)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte por apartamento: {str(e)}")
    
    def _generate_category_and_subtype_report(self):
        """Genera reporte combinado por categoría y por subtipo"""
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
                    return
                # Agrupar por categoría
                categories_dict = {}
                for expense in filtered:
                    category = expense.get('categoria', 'Sin categoría')
                    if category not in categories_dict:
                        categories_dict[category] = {'count': 0, 'total': 0, 'expenses': []}
                    categories_dict[category]['count'] += 1
                    categories_dict[category]['total'] += float(expense.get('monto', 0))
                    categories_dict[category]['expenses'].append(expense)
                # Agrupar por categoría y subtipo
                subtype_dict = {}
                for expense in filtered:
                    category = expense.get('categoria', 'Sin categoría')
                    subtype = expense.get('subtipo', 'Sin subtipo')
                    key = f"{category} - {subtype}"
                    if key not in subtype_dict:
                        subtype_dict[key] = {
                            'category': category, 'subtype': subtype, 'count': 0, 'total': 0, 'expenses': []
                        }
                    subtype_dict[key]['count'] += 1
                    subtype_dict[key]['total'] += float(expense.get('monto', 0))
                    subtype_dict[key]['expenses'].append(expense)
                period_window.destroy()
                self._show_report_window(
                    f"Reporte por Categoría y Subtipo - {period_name}",
                    self._format_category_and_subtype_report(categories_dict, subtype_dict, len(filtered), period_name),
                    "category_subtype"
                )

            self._create_period_selection_window("Seleccionar Período - Categoría y Subtipo", on_generate, button_color="#dc2626")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")

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
            year_window.bind("<Escape>", lambda e: year_window.destroy())

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
                    return
                
                year_window.destroy()
                self._show_report_window(
                    f"Comparativa Anual - {year1} vs {year2}",
                    self._format_year_comparison_report(year1, year2, year1_expenses, year2_expenses),
                    "year_comparison"
                )
            
            button_frame = tk.Frame(year_window)
            button_frame.pack(fill="x", pady=(8, 12))
            tk.Button(
                button_frame,
                text="Generar Reporte",
                font=("Segoe UI", 10, "bold"),
                bg="#b91c1c",
                fg="white",
                relief="flat",
                padx=22,
                pady=6,
                cursor="hand2",
                command=generate
            ).pack()

            year_window.after(50, year_window.focus_force)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte comparativo: {str(e)}")
    
    # ==================== FORMATO DE REPORTES ====================
    
    def _format_category_and_subtype_report(self, categories_dict, subtype_dict, total_expenses, period_name=None):
        """Formatea el reporte combinado por categoría y por subtipo"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE GASTOS POR CATEGORÍA Y SUBTIPO")
        if period_name:
            report.append(f"Período: {period_name}")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        total_general = sum(c['total'] for c in categories_dict.values())
        report.append("RESUMEN GENERAL:")
        report.append(f"  • Total de gastos: {total_expenses}")
        report.append(f"  • Total gastado: ${total_general:,.2f}")
        report.append("")
        report.append("ANÁLISIS POR SUBTIPO:")
        report.append("-" * 60)
        total_sub = sum(s['total'] for s in subtype_dict.values())
        # Agrupar subtipos por categoría para mostrar cada grupo junto
        by_category = {}
        for key, data in subtype_dict.items():
            cat = data['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append((key, data))
        # Orden de categorías por total descendente; dentro de cada una, subtipos por total descendente
        category_order = sorted(categories_dict.items(), key=lambda x: x[1]['total'], reverse=True)
        for category, _ in category_order:
            if category not in by_category:
                continue
            items = sorted(by_category[category], key=lambda x: x[1]['total'], reverse=True)
            for key, data in items:
                percentage = (data['total'] / total_sub * 100) if total_sub else 0
                report.append(f"Categoría: {data['category']}")
                report.append(f"Subtipo: {data['subtype']}")
                report.append(f"  • Cantidad de gastos: {data['count']}")
                report.append(f"  • Total gastado: ${data['total']:,.2f}")
                report.append(f"  • Porcentaje del total: {percentage:.2f}%")
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
            label = self._get_unit_report_label(apt_num)
            report.append(f"{label}:")
            report.append(f"  • Total de gastos: {data['count']}")
            report.append(f"  • Total gastado: ${data['total']:,.2f}")
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

    def _get_unit_report_label(self, apt_num):
        """Devuelve la etiqueta correcta para el reporte: 'Local 1', 'Apartamento 2', 'Apartamento General', etc."""
        if apt_num == "General" or not apt_num:
            return "Apartamento General"
        apartments = apartment_service.get_all_apartments()
        for apt in apartments:
            if str(apt.get("number", "")) == str(apt_num):
                unit_type = apt.get("unit_type", "Apartamento Estándar")
                number = apt.get("number", apt_num)
                if unit_type in ("Local Comercial", "Local comercial"):
                    return f"Local {number}"
                if unit_type == "Penthouse":
                    return f"Penthouse {number}"
                if unit_type in ("Depósito", "Bodega") or "Depósito" in str(unit_type) or "Bodega" in str(unit_type):
                    return f"Depósito {number}"
                return f"Apartamento {number}"
        return f"Apartamento {apt_num}"
    
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
        report.append("")
        
        report.append(f"AÑO {year2}:")
        report.append(f"  • Total de gastos: {len(year2_expenses)}")
        report.append(f"  • Total gastado: ${total2:,.2f}")
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
    
    # ==================== VENTANA DE REPORTE ====================
    
    def _show_export_success_dialog(self, filepath: Path):
        """Ventana de confirmación tras exportar: Copiar, Abrir carpeta, Abrir archivo, Aceptar (reglas establecidas)."""
        colors = get_module_colors("gastos")
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
        tk.Label(top, text="ℹ", font=("Segoe UI", 28), fg=colors.get("primary", "#dc2626")).pack(side="left", padx=(0, Spacing.MD))
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
                import subprocess
                subprocess.run(["xdg-open", folder], check=False)

        def open_file():
            path = str(filepath.resolve())
            if os.name == "nt":
                os.startfile(path)
            else:
                import subprocess
                subprocess.run(["xdg-open", path], check=False)

        tk.Button(btns, text="📋 Copiar", font=("Segoe UI", 10), bg="#2563eb", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=copy_path).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btns, text="📁 Abrir carpeta", font=("Segoe UI", 10), bg="#6b7280", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=open_folder).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btns, text="📄 Abrir archivo", font=("Segoe UI", 10), bg="#059669", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=open_file).pack(side="left", padx=(0, Spacing.SM))
        tk.Button(btns, text="Aceptar", font=("Segoe UI", 10), bg="#2563eb", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=win.destroy).pack(side="right")

    def _show_report_window(self, title, content, report_type):
        """Muestra una ventana con el reporte generado (reglas: Exportar CSV, Exportar TXT, Cerrar; colores módulo gastos; utf-8-sig)."""
        colors = get_module_colors("gastos")
        header_bg = colors.get("hover", "#dc2626")
        btn_export_bg = colors.get("primary", "#dc2626")

        report_window = tk.Toplevel(self)
        report_window.title(title)
        report_window.geometry("800x600")
        report_window.transient(self)
        report_window.grab_set()

        header = tk.Frame(report_window, bg=header_bg, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        # Empaquetar botones primero (derecha) para que reserven espacio y Cerrar se vea completo
        buttons_frame = tk.Frame(header, bg=header_bg)
        buttons_frame.pack(side="right", padx=Spacing.LG, pady=8)
        title_label = tk.Label(
            header,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg=header_bg,
            fg="white"
        )
        title_label.pack(side="left", padx=Spacing.LG, pady=12, fill="x", expand=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_type = (report_type or "reporte").replace(" ", "_")

        def export_txt():
            try:
                ensure_dirs()
                filepath = EXPORTS_DIR / f"reporte_gastos_{safe_type}_{timestamp}.txt"
                with open(filepath, "w", encoding="utf-8-sig") as f:
                    f.write(content)
                self._show_export_success_dialog(filepath)
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")

        def export_csv():
            try:
                ensure_dirs()
                filepath = EXPORTS_DIR / f"reporte_gastos_{safe_type}_{timestamp}.csv"
                with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)
                    writer.writerow(["Reporte de gastos - Building Manager Pro", title])
                    writer.writerow([f"Fecha de exportación: {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
                    writer.writerow([])
                    writer.writerow(["Contenido"])
                    for line in content.splitlines():
                        writer.writerow([line])
                self._show_export_success_dialog(filepath)
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar CSV: {str(e)}")

        # Orden establecido: Exportar CSV, Exportar TXT, Cerrar (con hover suave y Cerrar corregido)
        btn_export_hover = colors.get("hover", "#b91c1c")
        btn_close_bg = "#dc2626"
        btn_close_hover = "#b91c1c"
        btn_opts = dict(font=("Segoe UI", 10), fg="white", relief="flat", padx=12, pady=6, cursor="hand2")

        btn_csv = tk.Button(buttons_frame, text="💾 Exportar CSV", bg=btn_export_bg, **btn_opts, command=export_csv)
        btn_csv.pack(side="left", padx=(0, 6))
        btn_csv.bind("<Enter>", lambda e: btn_csv.config(bg=btn_export_hover))
        btn_csv.bind("<Leave>", lambda e: btn_csv.config(bg=btn_export_bg))

        btn_txt = tk.Button(buttons_frame, text="📄 Exportar TXT", bg=btn_export_bg, **btn_opts, command=export_txt)
        btn_txt.pack(side="left", padx=(0, 6))
        btn_txt.bind("<Enter>", lambda e: btn_txt.config(bg=btn_export_hover))
        btn_txt.bind("<Leave>", lambda e: btn_txt.config(bg=btn_export_bg))

        btn_close = tk.Button(buttons_frame, text="× Cerrar", bg=btn_close_bg, width=9, **btn_opts, command=report_window.destroy)
        btn_close.pack(side="left")
        btn_close.bind("<Enter>", lambda e: btn_close.config(bg=btn_close_hover))
        btn_close.bind("<Leave>", lambda e: btn_close.config(bg=btn_close_bg))

        text_frame = tk.Frame(report_window, bg="#ffffff")
        text_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)
        tk.Label(
            text_frame,
            text="Vista previa (mismo contenido que al exportar a TXT/CSV)",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#6b7280"
        ).pack(anchor="w", pady=(0, 6))
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
        
        # Colores rojos para módulo de gastos
        colors = get_module_colors("gastos")
        red_primary = colors["primary"]
        red_hover = colors["hover"]
        red_light = colors["light"]
        red_text = colors["text"]
        
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
            fg_color=red_primary,
            hover_bg=red_light,
            hover_fg=red_text,
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
            bg_color=red_primary,
            fg_color="white",
            hover_bg=red_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_dashboard.pack(side="right")