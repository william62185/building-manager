import tkinter as tk
from tkinter import messagebox
from ..components.theme_manager import theme_manager, Spacing
from ..components.icons import Icons
from manager.app.services.expense_service import ExpenseService

class ExpensesView(tk.Frame):
    """Vista profesional para gestión de gastos"""
    def __init__(self, parent, on_back=None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.expense_service = ExpenseService()
        self.on_back = on_back
        self._create_layout()

    def _create_layout(self):
        for widget in self.winfo_children():
            widget.destroy()
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG))
        btn_back = tk.Button(header, text="← Volver", command=self._on_back)
        btn_back.pack(side="left")
        title = tk.Label(header, text="Gestión de Gastos", **theme_manager.get_style("label_title"))
        title.pack(side="left", padx=(Spacing.LG, 0))
        cards_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        cards_frame.pack(pady=Spacing.XL)
        self._create_action_card(
            cards_frame,
            icon=Icons.PAYMENT_RECEIVED,
            title="Registrar gasto",
            description="Registra un nuevo gasto general o particular, adjunta documento de constancia.",
            color="#1976d2",
            command=self._show_register_expense
        ).pack(side="left", padx=Spacing.LG)
        self._create_action_card(
            cards_frame,
            icon=Icons.EDIT,
            title="Editar/Eliminar gasto",
            description="Consulta, edita o elimina gastos registrados y cambia el documento adjunto si es necesario.",
            color="#388e3c",
            command=self._show_edit_delete_expenses
        ).pack(side="left", padx=Spacing.LG)
        self._create_action_card(
            cards_frame,
            icon=Icons.REPORTS,
            title="Reportes",
            description="Visualiza y exporta reportes de gastos filtrando por año, mes, edificio o apartamento.",
            color="#fbc02d",
            command=self._show_reports
        ).pack(side="left", padx=Spacing.LG)

    def _create_action_card(self, parent, icon, title, description, color, command):
        card = tk.Frame(parent, bg="white", bd=2, relief="raised", padx=18, pady=18, width=260, height=220)
        card.pack_propagate(False)
        card.bind("<Button-1>", lambda e: command())
        card.configure(cursor="hand2")
        icon_label = tk.Label(card, text=icon, font=("Segoe UI", 28), fg=color, bg="white")
        icon_label.pack()
        title_label = tk.Label(card, text=title, font=("Segoe UI", 14, "bold"), fg=color, bg="white")
        title_label.pack(pady=(8, 2))
        desc_label = tk.Label(card, text=description, font=("Segoe UI", 10), fg="#444", bg="white", wraplength=200, justify="center")
        desc_label.pack(pady=(0, 2))
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
            w.configure(cursor="hand2")
        return card

    def _show_register_expense(self):
        from .register_expense_view import RegisterExpenseView
        for widget in self.winfo_children():
            widget.destroy()
        view = RegisterExpenseView(self, on_back=self._create_layout)
        view.pack(fill="both", expand=True)

    def _show_edit_delete_expenses(self):
        from .edit_delete_expenses_view import EditDeleteExpensesView
        for widget in self.winfo_children():
            widget.destroy()
        view = EditDeleteExpensesView(self, on_back=self._create_layout)
        view.pack(fill="both", expand=True)

    def _show_reports(self):
        from .expenses_reports_view import ExpensesReportsView
        for widget in self.winfo_children():
            widget.destroy()
        view = ExpensesReportsView(self, on_back=self._create_layout)
        view.pack(fill="both", expand=True)

    def _on_back(self):
        if self.on_back:
            self.on_back() 