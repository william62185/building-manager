"""
Vista principal del módulo de Gestión de Apartamentos
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
from manager.app.services.apartment_service import apartment_service
from .apartment_form_view import ApartmentFormView
from .apartments_list_view import ApartmentsListView
from .occupation_status_view import OccupationStatusView
from .reports.occupancy_vacancy_report_view import OccupancyVacancyReportView

class ApartmentManagementView(tk.Frame):
    """Dashboard para la gestión de apartamentos"""

    def __init__(self, parent, on_navigate: Callable):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.on_navigate = on_navigate
        self.current_sub_view = None
        self._last_list_filters = None  # Para guardar el estado del filtro
        self._create_layout()

    def _create_layout(self):
        """Abre directamente el listado de apartamentos."""
        self.current_sub_view = None
        for widget in self.winfo_children():
            widget.destroy()
        self._show_apartments_list()

    def _create_cards_grid(self, parent):
        pass  # Ya no se usa

    def _create_cards_grid(self, parent):
        """Crea el grid de tarjetas de acción 2x2 con altura calculada dinámicamente"""
        cb = self._content_bg
        cards_frame = tk.Frame(parent, bg=cb)
        cards_frame.pack(pady=(0, Spacing.MD))
        
        # Color oscuro para iconos (más contraste); sin texto descriptivo
        icon_color = "#4c1d95"  # purple-900
        cards_info = [
            {"icon": "🏢", "title": "Registrar Apartamento", "command": self._show_register_form},
            {"icon": "🔍", "title": "Ver/Gestionar Apartamentos", "command": self._show_apartments_list},
        ]
        card_height = 220

        def calculate_and_create_cards():
            """Crea los cards después de que el layout esté renderizado"""
            try:
                if not self.winfo_exists() or not cards_frame.winfo_exists():
                    return
            except tk.TclError:
                return
            
            # Limpiar cards_frame si ya tiene widgets
            try:
                for widget in cards_frame.winfo_children():
                    try:
                        widget.destroy()
                    except tk.TclError:
                        continue
            except tk.TclError:
                return
            
            # Crear los cards
            try:
                for i, info in enumerate(cards_info):
                    col = i % 2
                    self._create_action_card(
                        cards_frame, info["icon"], info["title"], icon_color, info["command"], card_height
                    ).grid(row=0, column=col, padx=Spacing.MD, pady=Spacing.SM)
            except tk.TclError:
                return
        
        # Calcular y crear después de que el layout esté renderizado
        self.after_idle(calculate_and_create_cards)

    def _create_action_card(self, parent, icon, title, icon_color, command, card_height=220):
        """Crea una tarjeta de acción: icono oscuro, título negro, sin texto descriptivo."""
        card_bg = "#f3e8ff"  # Morado claro para módulo administración
        card_width = int(260 * 0.90)
        card_height_reduced = int(card_height * 0.90)
        
        card = tk.Frame(parent, bg=card_bg, bd=2, relief="raised", 
                       padx=16, pady=16, width=card_width, height=card_height_reduced)
        card.pack_propagate(False)
        
        content_frame = tk.Frame(card, bg=card_bg)
        content_frame.pack(fill="both", expand=True)
        
        icon_label = tk.Label(content_frame, text=icon, font=("Segoe UI", 24), fg=icon_color, bg=card_bg)
        icon_label.pack(pady=(0, 6))
        
        title_wraplength = int(220 * 0.90)
        title_label = tk.Label(content_frame, text=title, font=("Segoe UI", 13, "bold"), 
                              fg="#000000", bg=card_bg, wraplength=title_wraplength, justify="center")
        title_label.pack(pady=(0, 4))
        
        def on_card_click(e):
            e.widget.focus_set()
            command()
            return "break"
        
        hover_bg = "#e9d5ff"
        def on_enter(e):
            card.configure(bg=hover_bg)
            content_frame.configure(bg=hover_bg)
            icon_label.configure(bg=hover_bg)
            title_label.configure(bg=hover_bg)
        
        def on_leave(e):
            card.configure(bg=card_bg)
            content_frame.configure(bg=card_bg)
            icon_label.configure(bg=card_bg)
            title_label.configure(bg=card_bg)
        
        all_widgets = [card, content_frame, icon_label, title_label]
        for widget in all_widgets:
            widget.bind("<Button-1>", on_card_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.configure(cursor="hand2")
        
        return card

    def _show_register_form(self):
        """Muestra el formulario para registrar un nuevo apartamento."""
        for widget in self.winfo_children():
            widget.destroy()

        form_view = ApartmentFormView(
            self,
            on_back=self._show_apartments_list,
            on_save_success=self._on_data_changed,
            apartment_data=None,
            on_navigate=self.on_navigate,
        )
        form_view.pack(fill="both", expand=True)
        self.current_sub_view = form_view

    def _show_edit_form(self, apartment_data: dict, filter_state: dict):
        """Muestra el formulario para editar un apartamento existente."""
        self._last_list_filters = filter_state

        for widget in self.winfo_children():
            widget.destroy()

        form_view = ApartmentFormView(
            self,
            on_back=self._show_apartments_list,
            on_save_success=self._on_data_changed,
            apartment_data=apartment_data,
            on_navigate=self.on_navigate,
        )
        form_view.pack(fill="both", expand=True)
        self.current_sub_view = form_view

    def _show_apartments_list(self):
        """Muestra la lista para ver y gestionar apartamentos."""
        for widget in self.winfo_children():
            widget.destroy()

        list_view = ApartmentsListView(
            self,
            on_back=self._back_to_dashboard,
            on_edit=self._show_edit_form,
            initial_filters=self._last_list_filters,
            on_navigate=self.on_navigate,
            on_new=self._show_register_form,
        )
        list_view.pack(fill="both", expand=True)
        self.current_sub_view = list_view

    def _show_occupation_status(self):
        """Muestra la vista de estado de ocupación."""
        for widget in self.winfo_children():
            widget.destroy()
        
        # Verificar que on_navigate esté disponible antes de pasarlo
        navigate_callback = self.on_navigate if hasattr(self, 'on_navigate') and self.on_navigate is not None else None
        if navigate_callback is None:
            # Buscar el callback desde el parent
            widget = self.master
            depth = 0
            while widget and depth < 10:
                if hasattr(widget, '_navigate_to'):
                    navigate_callback = widget._navigate_to
                    break
                widget = getattr(widget, 'master', None)
                depth += 1
        
        status_view = OccupationStatusView(
            self,
            on_back=self._back_to_dashboard,
            on_navigate=navigate_callback  # Pasar el callback de navegación
        )
        status_view.pack(fill="both", expand=True)
        self.current_sub_view = status_view

    def _show_reports(self):
        """Abre directamente la vista de Ocupación y Vacancia (sin pantalla intermedia)."""
        for widget in self.winfo_children():
            widget.destroy()

        navigate_callback = self.on_navigate if hasattr(self, 'on_navigate') and self.on_navigate is not None else None
        if navigate_callback is None:
            widget = self.master
            depth = 0
            while widget and depth < 10:
                if hasattr(widget, '_navigate_to'):
                    navigate_callback = widget._navigate_to
                    break
                widget = getattr(widget, 'master', None)
                depth += 1

        report_view = OccupancyVacancyReportView(
            self,
            on_back=self._back_to_dashboard,
            on_navigate=navigate_callback,
        )
        report_view.pack(fill="both", expand=True)
        self.current_sub_view = report_view

    def _create_navigation_buttons(self, parent, on_back_command):
        """Crea los botones Volver y Dashboard con estilo moderno y colores morados del módulo de administración"""
        # Colores morados para módulo de administración
        colors = get_module_colors("administración")
        purple_primary = colors["primary"]
        purple_hover = colors["hover"]
        purple_light = colors["light"]
        purple_text = colors["text"]
        
        theme = theme_manager.themes[theme_manager.current_theme]
        btn_bg = theme.get("btn_secondary_bg", "#f9fafb")
        # Botón "Volver"
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
            border_color="#000000"
        )
        btn_back.pack(side="right", padx=(Spacing.MD, 0))
        
        # Botón "Dashboard" con icono de casita
        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=purple_primary,
            fg_color="white",
            hover_bg=purple_hover,
            hover_fg="white",
            command=lambda: self.on_navigate("dashboard"),
            padx=18,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_dashboard.pack(side="right")

    def _back_to_dashboard(self):
        """Vuelve a renderizar el dashboard principal de este módulo."""
        self.current_sub_view = None
        self._create_layout()

    def _on_data_changed(self):
        """Callback para cuando los datos cambian (p.ej. se guarda un apto)."""
        # En lugar de solo refrescar, volvemos a la lista, que usará el filtro guardado.
        self._show_apartments_list() 