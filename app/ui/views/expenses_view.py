"""
Vista para gestión de gastos del edificio
"""
import tkinter as tk
from tkinter import messagebox
from typing import Callable
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
from manager.app.ui.components.modern_widgets import ModernButton
from manager.app.services.expense_service import ExpenseService

class ExpensesView(tk.Frame):
    """Vista profesional para gestión de gastos del edificio"""
    
    def __init__(self, parent, on_back=None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        # Fondo igual al del área de contenido para que no se vea el recuadro blanco
        self.configure(bg=parent.cget("bg"))
        self.expense_service = ExpenseService()
        self.on_back = on_back
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout principal con cards de acción"""
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
        
        # Fondo de la vista (transparente respecto al área de contenido)
        bg_view = self.cget("bg")
        # Header
        header = tk.Frame(self, bg=bg_view)
        header.pack(fill="x", pady=(0, Spacing.LG))
        
        # Frame para botones de navegación (alineados a la derecha)
        buttons_frame = tk.Frame(header, bg=bg_view)
        buttons_frame.pack(side="right")
        
        # Agregar solo botón Dashboard (sin Volver porque es redundante)
        self._create_navigation_buttons(buttons_frame, self._on_back, show_back_button=False)
        
        # Pregunta principal
        theme = theme_manager.themes[theme_manager.current_theme]
        question_label = tk.Label(
            self,
            text="¿Qué deseas hacer?",
            font=("Segoe UI", 14),
            fg=theme["text_primary"],
            bg=bg_view
        )
        question_label.pack(pady=(0, Spacing.XL))
        
        # Cards principales (fondo igual al de la vista para que se vea transparente)
        cards_frame = tk.Frame(self, bg=bg_view)
        cards_frame.pack(pady=Spacing.LG)
        
        # Crear las 3 cards
        card1 = self._create_action_card(
            cards_frame,
            icon=Icons.EXPENSES,
            title="Registrar nuevo gasto",
            description="Registra un nuevo gasto del edificio (mantenimiento, servicios, etc.).",
            color="#991b1b",  # rojo oscuro - paleta roja armoniosa
            command=self._show_register_expense
        )
        card1.grid(row=0, column=0, padx=Spacing.LG)
        
        card2 = self._create_action_card(
            cards_frame,
            icon=Icons.EDIT,
            title="Editar/Eliminar gasto",
            description="Consulta, edita o elimina gastos registrados previamente.",
            color="#991b1b",  # mismo color que Registrar nuevo gasto para consistencia
            command=self._show_edit_delete_expenses
        )
        card2.grid(row=0, column=1, padx=Spacing.LG)
        
        card3 = self._create_action_card(
            cards_frame,
            icon=Icons.REPORTS,
            title="Reportes",
            description="Visualiza reportes y estadísticas de gastos.",
            color="#991b1b",  # mismo color que Registrar nuevo gasto para consistencia
            command=self._show_reports
        )
        card3.grid(row=0, column=2, padx=Spacing.LG)
    
    def _create_navigation_buttons(self, parent, on_back_command, show_back_button=True):
        """Crea los botones Volver y Dashboard con estilo moderno y colores rojos del módulo de gastos"""
        # Colores rojos para módulo de gastos
        colors = get_module_colors("gastos")
        red_primary = colors["primary"]
        red_hover = colors["hover"]
        red_light = colors["light"]
        red_text = colors["text"]
        
        # Botón "Volver" (solo si show_back_button es True)
        if show_back_button:
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
        
        # Botón "Dashboard" con icono de casita (siempre navega al dashboard)
        def go_to_dashboard():
            if self.on_back:
                self.on_back()  # on_back ya navega al dashboard desde main_window
        
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
    
    def _create_action_card(self, parent, icon, title, description, color, command):
        """Crea una card de acción con hover effects - mismo estilo que módulo inquilinos"""
        # Color rojo más intenso para el fondo base de las tarjetas (similar al hover)
        light_red_bg = "#fee2e2"  # red-100 - rojo claro más intenso para mejor contraste con iconos rojos
        
        card = tk.Frame(parent, bg=light_red_bg, bd=2, relief="raised", width=260, height=220)
        card.pack_propagate(False)  # Mantener tamaño fijo
        
        # Contenedor principal con padding uniforme para centrar verticalmente
        content_frame = tk.Frame(card, bg=light_red_bg)
        content_frame.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)
        
        # Frame espaciador superior para centrar el contenido
        top_spacer = tk.Frame(content_frame, bg=light_red_bg, height=1)
        top_spacer.pack(fill="x", expand=True)
        
        # Contenedor del contenido (icono, título)
        content_container = tk.Frame(content_frame, bg=light_red_bg)
        content_container.pack()
        
        # Ícono
        icon_label = tk.Label(content_container, text=icon, font=("Segoe UI", 28), 
                             fg=color, bg=light_red_bg)
        icon_label.pack(pady=(0, Spacing.MD))
        
        # Título
        title_label = tk.Label(content_container, text=title, font=("Segoe UI", 14, "bold"), 
                             fg="#000000", bg=light_red_bg)
        title_label.pack()
        
        # Textos descriptivos eliminados según solicitud del usuario
        
        # Frame espaciador inferior para centrar el contenido
        bottom_spacer = tk.Frame(content_frame, bg=light_red_bg, height=1)
        bottom_spacer.pack(fill="x", expand=True)
        
        # Función para manejar clics - se ejecuta desde cualquier parte del card
        def on_card_click(e):
            # Prevenir propagación adicional si es necesario
            e.widget.focus_set()  # Asegurar que el widget tenga foco
            command()
            return "break"  # Detener propagación del evento
        
        # Hover effect (más intenso que el fondo base)
        def on_enter(e):
            hover_color = "#fecaca"  # red-200 - rojo más intenso para hover
            card.configure(bg=hover_color)
            content_frame.configure(bg=hover_color)
            top_spacer.configure(bg=hover_color)
            content_container.configure(bg=hover_color)
            bottom_spacer.configure(bg=hover_color)
            icon_label.configure(bg=hover_color)
            title_label.configure(bg=hover_color)
        
        def on_leave(e):
            card.configure(bg=light_red_bg)
            content_frame.configure(bg=light_red_bg)
            top_spacer.configure(bg=light_red_bg)
            content_container.configure(bg=light_red_bg)
            bottom_spacer.configure(bg=light_red_bg)
            icon_label.configure(bg=light_red_bg)
            title_label.configure(bg=light_red_bg)
        
        # Hacer TODO el card clickeable - bind a todos los elementos
        # Esto asegura que cualquier parte del card responda al clic
        all_widgets = [card, content_frame, top_spacer, content_container, bottom_spacer, icon_label, title_label]
        for widget in all_widgets:
            widget.bind("<Button-1>", on_card_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.configure(cursor="hand2")
        
        return card
    
    def _show_register_expense(self):
        """Muestra el formulario para registrar un nuevo gasto"""
        try:
            from .register_expense_view import RegisterExpenseView
            # Limpiar vista
            for widget in self.winfo_children():
                widget.destroy()
            
            # Función para navegar al dashboard principal
            def go_to_dashboard():
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
                # Fallback: usar on_back si está disponible
                if self.on_back:
                    self.on_back()
            
            form = RegisterExpenseView(
                self, 
                on_back=self._create_layout,
                on_navigate_to_dashboard=go_to_dashboard
            )
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
            
            # Función para navegar al dashboard principal
            def go_to_dashboard():
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
                # Fallback: usar on_back si está disponible
                if self.on_back:
                    self.on_back()
            
            edit_delete_view = EditDeleteExpensesView(
                self, 
                on_back=self._create_layout,
                on_navigate_to_dashboard=go_to_dashboard
            )
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
            
            # Función para navegar al dashboard principal
            def go_to_dashboard():
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
                # Fallback: usar on_back si está disponible
                if self.on_back:
                    self.on_back()
            
            reports_view = ExpenseReportsView(
                self, 
                on_back=self._create_layout,
                on_navigate_to_dashboard=go_to_dashboard
            )
            reports_view.pack(fill="both", expand=True)
        except ImportError as e:
            messagebox.showerror("Error", f"Error al cargar la vista de reportes: {str(e)}")
    
    def _on_back(self):
        """Maneja el botón de volver"""
        if self.on_back:
            self.on_back()

