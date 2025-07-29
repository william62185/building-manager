"""
Vista principal del módulo de Gestión de Apartamentos
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.services.apartment_service import apartment_service
from .apartment_form_view import ApartmentFormView
from .apartments_list_view import ApartmentsListView
from .occupation_status_view import OccupationStatusView
from .apartment_reports_view import ApartmentReportsView

class ApartmentManagementView(tk.Frame):
    """Dashboard para la gestión de apartamentos"""

    def __init__(self, parent, on_navigate: Callable):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_navigate = on_navigate
        self.current_sub_view = None
        self._last_list_filters = None  # Para guardar el estado del filtro
        self._create_layout()

    def _create_layout(self):
        """Crea el layout principal con cards de acción"""
        self.current_sub_view = None
        for widget in self.winfo_children():
            widget.destroy()

        header_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", pady=(0, Spacing.LG))

        title = tk.Label(header_frame, text="Gestión de Apartamentos", **theme_manager.get_style("label_title"))
        title.pack(side="left")

        btn_back = tk.Button(
            header_frame,
            text="← Volver a Administración",
            font=("Segoe UI", 10),
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            bd=1, relief="solid", padx=8, pady=4, cursor="hand2",
            command=lambda: self.on_navigate("administration")
        )
        btn_back.pack(side="right")

        question_label = tk.Label(
            self, text="¿Qué deseas gestionar hoy?",
            **theme_manager.get_style("label_subtitle")
        )
        question_label.configure(font=("Segoe UI", 14))
        question_label.pack(pady=(0, Spacing.XL))

        main_container = tk.Frame(self, **theme_manager.get_style("frame"))
        main_container.pack(pady=Spacing.LG)

        self._create_cards_grid(main_container)

    def _create_cards_grid(self, parent):
        """Crea el grid de tarjetas de acción 2x2"""
        grid_container = tk.Frame(parent, **theme_manager.get_style("frame"))
        grid_container.pack(anchor="center")

        cards_info = [
            {
                "icon": "🏢", "title": "Registrar Apartamento",
                "desc": "Añadir una nueva unidad al sistema.",
                "color": "#1e40af", "command": self._show_register_form
            },
            {
                "icon": "🔍", "title": "Ver/Gestionar Apartamentos",
                "desc": "Editar, eliminar o ver detalles de los apartamentos.",
                "color": "#3b82f6", "command": self._show_apartments_list
            },
            {
                "icon": "📊", "title": "Estado de Ocupación",
                "desc": "Visualizar apartamentos disponibles y ocupados.",
                "color": "#10b981", "command": self._show_occupation_status
            },
            {
                "icon": "📈", "title": "Reportes",
                "desc": "Generar reportes financieros y de mantenimiento.",
                "color": "#f59e0b", "command": self._show_reports
            }
        ]

        row1 = tk.Frame(grid_container, **theme_manager.get_style("frame"))
        row1.pack(pady=(0, Spacing.LG))
        row2 = tk.Frame(grid_container, **theme_manager.get_style("frame"))
        row2.pack()

        for i, info in enumerate(cards_info):
            parent_row = row1 if i < 2 else row2
            self._create_action_card(
                parent_row, info["icon"], info["title"], info["desc"],
                info["color"], info["command"]
            ).pack(side="left", padx=(0, Spacing.LG) if i % 2 == 0 else 0)

    def _create_action_card(self, parent, icon, title, description, color, command):
        card_frame = tk.Frame(
            parent, bg="white", relief="raised", bd=2, width=280, height=240
        )
        card_frame.pack_propagate(False)
        content_frame = tk.Frame(card_frame, bg="white")
        content_frame.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.LG)

        icon_label = tk.Label(content_frame, text=icon, font=("Segoe UI Symbol", 32), bg="white", fg=color)
        icon_label.pack(pady=(0, Spacing.MD))
        title_label = tk.Label(content_frame, text=title, font=("Segoe UI", 15, "bold"), bg="white", fg=color)
        title_label.pack()
        desc_label = tk.Label(
            content_frame, text=description, font=("Segoe UI", 10),
            bg="white", fg="#444", wraplength=220, justify="center"
        )
        desc_label.pack(pady=(Spacing.XS, 0))

        def on_enter(event):
            for w in [card_frame, content_frame, icon_label, title_label, desc_label]:
                w.configure(bg="#e3f2fd")
        
        def on_leave(event):
            for w in [card_frame, content_frame, icon_label, title_label, desc_label]:
                w.configure(bg="white")

        for widget in [card_frame, content_frame, icon_label, title_label, desc_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e: command())
            widget.configure(cursor="hand2")
            
        return card_frame

    def _show_register_form(self):
        """Muestra el formulario para registrar un nuevo apartamento."""
        for widget in self.winfo_children():
            widget.destroy()
        
        form_view = ApartmentFormView(
            self,
            on_back=self._back_to_dashboard,
            on_save_success=self._on_data_changed,
            apartment_data=None  # Explicitly for new apartment
        )
        form_view.pack(fill="both", expand=True)
        self.current_sub_view = form_view

    def _show_edit_form(self, apartment_data: dict, filter_state: dict):
        """Muestra el formulario para editar un apartamento existente."""
        self._last_list_filters = filter_state  # Guardar el estado del filtro
        
        for widget in self.winfo_children():
            widget.destroy()
        
        form_view = ApartmentFormView(
            self,
            on_back=self._show_apartments_list, # Volver a la lista
            on_save_success=self._on_data_changed,
            apartment_data=apartment_data
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
            initial_filters=self._last_list_filters # Pasar el estado guardado
        )
        list_view.pack(fill="both", expand=True)
        self.current_sub_view = list_view

    def _show_occupation_status(self):
        """Muestra la vista de estado de ocupación."""
        for widget in self.winfo_children():
            widget.destroy()
        
        status_view = OccupationStatusView(
            self,
            on_back=self._back_to_dashboard
        )
        status_view.pack(fill="both", expand=True)
        self.current_sub_view = status_view

    def _show_reports(self):
        """Muestra la vista de reportes de apartamentos."""
        for widget in self.winfo_children():
            widget.destroy()
        
        reports_view = ApartmentReportsView(
            self,
            on_back=self._back_to_dashboard
        )
        reports_view.pack(fill="both", expand=True)
        self.current_sub_view = reports_view

    def _back_to_dashboard(self):
        """Vuelve a renderizar el dashboard principal de este módulo."""
        self.current_sub_view = None
        self._create_layout()

    def _on_data_changed(self):
        """Callback para cuando los datos cambian (p.ej. se guarda un apto)."""
        # En lugar de solo refrescar, volvemos a la lista, que usará el filtro guardado.
        self._show_apartments_list() 