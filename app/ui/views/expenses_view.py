"""
Vista para gestión de gastos del edificio
"""
import tkinter as tk
from tkinter import messagebox
from typing import Callable
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton
from manager.app.services.expense_service import ExpenseService

class ExpensesView(tk.Frame):
    """Vista profesional para gestión de gastos del edificio"""
    
    def __init__(self, parent, on_back=None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.expense_service = ExpenseService()
        self.on_back = on_back
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout principal con cards de acción"""
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
        
        # Contenedor principal con padding
        main_container = tk.Frame(self, **theme_manager.get_style("frame"))
        main_container.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.XL)
        
        # Header
        header = tk.Frame(main_container, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.XL))
        
        btn_back = ModernButton(header, text="Volver", icon=Icons.ARROW_LEFT, 
                               style="secondary", command=self._on_back)
        btn_back.pack(side="left")
        
        title = tk.Label(header, text="Gestión de Gastos", 
                        **theme_manager.get_style("label_title"))
        title.pack(side="left", padx=(Spacing.LG, 0))
        
        # Cards principales - contenedor centrado
        cards_container = tk.Frame(main_container, **theme_manager.get_style("frame"))
        cards_container.pack(expand=True, pady=Spacing.XL)
        
        cards_frame = tk.Frame(cards_container, **theme_manager.get_style("frame"))
        cards_frame.pack()
        
        # Crear las 3 cards
        card1 = self._create_action_card(
            cards_frame,
            icon=Icons.EXPENSES,
            title="Registrar nuevo gasto",
            description="Registra un nuevo gasto del edificio (mantenimiento, servicios, etc.).",
            color="#1976d2",
            command=self._show_register_expense
        )
        card1.grid(row=0, column=0, padx=Spacing.LG, pady=Spacing.MD)
        
        card2 = self._create_action_card(
            cards_frame,
            icon=Icons.EDIT,
            title="Editar/Eliminar gasto",
            description="Consulta, edita o elimina gastos registrados previamente.",
            color="#388e3c",
            command=self._show_edit_delete_expenses
        )
        card2.grid(row=0, column=1, padx=Spacing.LG, pady=Spacing.MD)
        
        card3 = self._create_action_card(
            cards_frame,
            icon=Icons.REPORTS,
            title="Reportes",
            description="Visualiza reportes y estadísticas de gastos.",
            color="#fbc02d",
            command=self._show_reports
        )
        card3.grid(row=0, column=2, padx=Spacing.LG, pady=Spacing.MD)
    
    def _create_action_card(self, parent, icon, title, description, color, command):
        """Crea una tarjeta de acción"""
        card = tk.Frame(parent, bg="white", bd=2, relief="raised", 
                       padx=18, pady=18, width=260, height=220)
        card.pack_propagate(False)
        card.bind("<Button-1>", lambda e: command())
        card.configure(cursor="hand2")
        
        # Ícono
        icon_label = tk.Label(card, text=icon, font=("Segoe UI", 28), 
                             fg=color, bg="white")
        icon_label.pack()
        
        # Título
        title_label = tk.Label(card, text=title, font=("Segoe UI", 14, "bold"), 
                              fg=color, bg="white")
        title_label.pack(pady=(8, 2))
        
        # Descripción
        desc_label = tk.Label(card, text=description, font=("Segoe UI", 10), 
                             fg="#444", bg="white", wraplength=200, justify="center")
        desc_label.pack(pady=(0, 2))
        
        # Hover effect
        def on_enter(e):
            card.configure(bg="#e3f2fd")
            icon_label.configure(bg="#e3f2fd")
            title_label.configure(bg="#e3f2fd")
            desc_label.configure(bg="#e3f2fd")
        
        def on_leave(e):
            card.configure(bg="white")
            icon_label.configure(bg="white")
            title_label.configure(bg="white")
            desc_label.configure(bg="white")
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        for w in [icon_label, title_label, desc_label]:
            w.bind("<Button-1>", lambda e: command())
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.configure(cursor="hand2")
        
        return card
    
    def _show_register_expense(self):
        """Muestra el formulario para registrar un nuevo gasto"""
        try:
            from .register_expense_view import RegisterExpenseView
            # Limpiar vista
            for widget in self.winfo_children():
                widget.destroy()
            
            form = RegisterExpenseView(self, on_back=self._create_layout)
            form.pack(fill="both", expand=True)
        except ImportError:
            messagebox.showinfo("En desarrollo", 
                              "El formulario de registro de gastos está en desarrollo.")
    
    def _show_edit_delete_expenses(self):
        """Muestra la vista para editar/eliminar gastos"""
        try:
            from .edit_delete_expenses_view import EditDeleteExpensesView
            # Limpiar vista
            for widget in self.winfo_children():
                widget.destroy()
            
            edit_delete_view = EditDeleteExpensesView(self, on_back=self._create_layout)
            edit_delete_view.pack(fill="both", expand=True)
        except ImportError as e:
            messagebox.showerror("Error", f"Error al cargar la vista: {str(e)}")
    
    def _show_reports(self):
        """Muestra reportes de gastos"""
        try:
            from .expense_reports_view import ExpenseReportsView
            # Limpiar vista
            for widget in self.winfo_children():
                widget.destroy()
            
            reports_view = ExpenseReportsView(self, on_back=self._create_layout)
            reports_view.pack(fill="both", expand=True)
        except ImportError as e:
            messagebox.showerror("Error", f"Error al cargar la vista de reportes: {str(e)}")
    
    def _on_back(self):
        """Maneja el botón de volver"""
        if self.on_back:
            self.on_back()

