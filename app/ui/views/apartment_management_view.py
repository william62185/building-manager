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

        # Frame para botones de navegación (alineados a la derecha)
        buttons_frame = tk.Frame(header_frame, **theme_manager.get_style("frame"))
        buttons_frame.pack(side="right")
        
        # Agregar botones Volver y Dashboard
        self._create_navigation_buttons(buttons_frame, lambda: self.on_navigate("administration"))

        question_label = tk.Label(
            self, text="¿Qué deseas gestionar hoy?",
            **theme_manager.get_style("label_subtitle")
        )
        question_label.configure(font=("Segoe UI", 14))
        question_label.pack(pady=(0, Spacing.MD))

        main_container = tk.Frame(self, **theme_manager.get_style("frame"))
        main_container.pack(pady=Spacing.SM)

        self._create_cards_grid(main_container)

    def _create_cards_grid(self, parent):
        """Crea el grid de tarjetas de acción 2x2 con altura calculada dinámicamente"""
        cards_frame = tk.Frame(parent, **theme_manager.get_style("frame"))
        cards_frame.pack(pady=(0, Spacing.MD))  # Agregar padding inferior al contenedor
        
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
        
        def calculate_and_create_cards():
            """Calcula la altura y crea los cards después de que el layout esté renderizado"""
            # Obtener altura del contenedor principal
            self.update_idletasks()
            container_height = self.winfo_height()
            
            # Si aún no hay altura disponible, usar un valor por defecto
            if container_height <= 1:
                container_height = 600  # Altura por defecto
            
            # Obtener alturas reales de los elementos después del renderizado
            # Buscar el header_frame y question_label
            header_frame = None
            question_label = None
            for widget in self.winfo_children():
                if isinstance(widget, tk.Frame) and len(widget.winfo_children()) > 0:
                    # Verificar si es el header_frame (tiene el título)
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label) and "Gestión de Apartamentos" in child.cget("text"):
                            header_frame = widget
                            break
                elif isinstance(widget, tk.Label) and "¿Qué deseas gestionar hoy?" in widget.cget("text"):
                    question_label = widget
            
            # Calcular alturas reales o usar aproximaciones
            header_height = header_frame.winfo_height() if header_frame else 80
            question_height = question_label.winfo_height() if question_label else 40
            
            # Calcular espacio disponible para los cards con margen inferior muy generoso
            container_padding_top = Spacing.SM  # Padding superior del main_container
            padding_between_rows = Spacing.SM  # Padding entre las 2 filas
            bottom_margin = Spacing.XL * 2  # Margen inferior MUY generoso (doble)
            cards_frame_padding = Spacing.MD  # Padding inferior del cards_frame
            
            available_height = (container_height - header_height - question_height - 
                              container_padding_top - padding_between_rows - 
                              bottom_margin - cards_frame_padding)
            
            # Dividir entre 2 filas
            num_rows = 2
            calculated_height = int(available_height / num_rows)
            
            # Asegurar una altura mínima y máxima razonable (reducir max significativamente)
            min_height = 200
            max_height = 240  # Reducido aún más para dejar mucho más espacio inferior
            card_height = max(min_height, min(calculated_height, max_height))
            
            # Limpiar cards_frame si ya tiene widgets
            for widget in cards_frame.winfo_children():
                widget.destroy()
            
            # Crear los cards con la altura calculada
            for i, info in enumerate(cards_info):
                row = i // 2
                col = i % 2
                self._create_action_card(
                    cards_frame, info["icon"], info["title"], info["desc"],
                    info["color"], info["command"], card_height
                ).grid(row=row, column=col, padx=Spacing.MD, pady=Spacing.SM)
        
        # Calcular y crear después de que el layout esté renderizado
        self.after_idle(calculate_and_create_cards)

    def _create_action_card(self, parent, icon, title, description, color, command, card_height=220):
        """Crea una tarjeta de acción con altura calculada dinámicamente"""
        # Reducir tamaño en un 10% total (5% adicional)
        card_width = int(260 * 0.90)  # 234
        card_height_reduced = int(card_height * 0.90)
        
        card = tk.Frame(parent, bg="white", bd=2, relief="raised", 
                       padx=16, pady=16, width=card_width, height=card_height_reduced)
        card.pack_propagate(False)
        
        # Contenedor principal del card
        content_frame = tk.Frame(card, bg="white")
        content_frame.pack(fill="both", expand=True)
        
        # Ícono (más pequeño)
        icon_label = tk.Label(content_frame, text=icon, font=("Segoe UI", 24), 
                             fg=color, bg="white")
        icon_label.pack(pady=(0, 4))
        
        # Título (ajustar wraplength al nuevo ancho)
        title_wraplength = int(220 * 0.90)  # Reducir wraplength proporcionalmente
        title_label = tk.Label(content_frame, text=title, font=("Segoe UI", 13, "bold"), 
                              fg=color, bg="white", wraplength=title_wraplength, justify="center")
        title_label.pack(pady=(0, 2))
        
        # Descripción (ajustar wraplength al nuevo ancho)
        desc_wraplength = int(220 * 0.90)  # Reducir wraplength proporcionalmente
        desc_label = tk.Label(content_frame, text=description, font=("Segoe UI", 9), 
                             fg="#444", bg="white", wraplength=desc_wraplength, justify="center")
        desc_label.pack(pady=(0, 4))
        
        # Función para manejar clics - se ejecuta desde cualquier parte del card
        def on_card_click(e):
            # Prevenir propagación adicional si es necesario
            e.widget.focus_set()  # Asegurar que el widget tenga foco
            command()
            return "break"  # Detener propagación del evento
        
        # Hover effect
        def on_enter(e):
            card.configure(bg="#e3f2fd")
            content_frame.configure(bg="#e3f2fd")
            icon_label.configure(bg="#e3f2fd")
            title_label.configure(bg="#e3f2fd")
            desc_label.configure(bg="#e3f2fd")
        
        def on_leave(e):
            card.configure(bg="white")
            content_frame.configure(bg="white")
            icon_label.configure(bg="white")
            title_label.configure(bg="white")
            desc_label.configure(bg="white")
        
        # Hacer TODA el área clickeable: card, content_frame y todos los widgets hijos
        all_widgets = [card, content_frame, icon_label, title_label, desc_label]
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
        
        # Verificar que on_navigate esté disponible antes de pasarlo
        navigate_callback = self.on_navigate if hasattr(self, 'on_navigate') and self.on_navigate is not None else None
        if navigate_callback is None:
            print(f"DEBUG: on_navigate es None en ApartmentManagementView. Buscando en jerarquía...")
            # Buscar el callback desde el parent
            widget = self.master
            depth = 0
            while widget and depth < 10:
                if hasattr(widget, '_navigate_to'):
                    navigate_callback = widget._navigate_to
                    break
                widget = getattr(widget, 'master', None)
                depth += 1
        
        form_view = ApartmentFormView(
            self,
            on_back=self._back_to_dashboard,
            on_save_success=self._on_data_changed,
            apartment_data=None,  # Explicitly for new apartment
            on_navigate=navigate_callback  # Pasar el callback de navegación
        )
        form_view.pack(fill="both", expand=True)
        self.current_sub_view = form_view

    def _show_edit_form(self, apartment_data: dict, filter_state: dict):
        """Muestra el formulario para editar un apartamento existente."""
        self._last_list_filters = filter_state  # Guardar el estado del filtro
        
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
        
        form_view = ApartmentFormView(
            self,
            on_back=self._show_apartments_list, # Volver a la lista
            on_save_success=self._on_data_changed,
            apartment_data=apartment_data,
            on_navigate=navigate_callback  # Pasar el callback de navegación
        )
        form_view.pack(fill="both", expand=True)
        self.current_sub_view = form_view

    def _show_apartments_list(self):
        """Muestra la lista para ver y gestionar apartamentos."""
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
        
        list_view = ApartmentsListView(
            self,
            on_back=self._back_to_dashboard,
            on_edit=self._show_edit_form,
            initial_filters=self._last_list_filters, # Pasar el estado guardado
            on_navigate=navigate_callback  # Pasar el callback de navegación
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
        """Muestra la vista de reportes de apartamentos."""
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
        
        reports_view = ApartmentReportsView(
            self,
            on_back=self._back_to_dashboard,
            on_navigate=navigate_callback  # Pasar el callback de navegación
        )
        reports_view.pack(fill="both", expand=True)
        self.current_sub_view = reports_view

    def _back_to_dashboard(self):
        """Vuelve a renderizar el dashboard principal de este módulo."""
        self.current_sub_view = None
        self._create_layout()

    def _create_navigation_buttons(self, parent, on_back_command):
        """Crea los botones Volver y Dashboard con estilo consistente"""
        from manager.app.ui.components.icons import Icons
        
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
        
        # Botón "Volver"
        btn_back = tk.Button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            **button_config,
            command=on_back_command
        )
        btn_back.pack(side="right", padx=(Spacing.SM, 0))
        
        # Hover effect para botón "Volver"
        def on_enter_back(e):
            btn_back.configure(bg=hover_bg)
        
        def on_leave_back(e):
            btn_back.configure(bg=theme["btn_secondary_bg"])
        
        btn_back.bind("<Enter>", on_enter_back)
        btn_back.bind("<Leave>", on_leave_back)
        
        # Botón "Dashboard" con icono de casita
        btn_dashboard = tk.Button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            **button_config,
            command=lambda: self.on_navigate("dashboard")
        )
        btn_dashboard.pack(side="right")
        
        # Hover effect para botón "Dashboard"
        def on_enter_dashboard(e):
            btn_dashboard.configure(bg=hover_bg)
        
        def on_leave_dashboard(e):
            btn_dashboard.configure(bg=theme["btn_secondary_bg"])
        
        btn_dashboard.bind("<Enter>", on_enter_dashboard)
        btn_dashboard.bind("<Leave>", on_leave_dashboard)

    def _on_data_changed(self):
        """Callback para cuando los datos cambian (p.ej. se guarda un apto)."""
        # En lugar de solo refrescar, volvemos a la lista, que usará el filtro guardado.
        self._show_apartments_list() 