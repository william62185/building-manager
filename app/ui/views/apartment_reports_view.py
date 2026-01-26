"""
Vista para mostrar reportes y estadísticas de los apartamentos.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from manager.app.ui.components.theme_manager import theme_manager, Spacing

class ApartmentReportsView(tk.Frame):
    """Vista de reportes de apartamentos con cards de acción."""

    def __init__(self, parent, on_back: Callable, on_navigate: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_back = on_back
        self.on_navigate = on_navigate  # Callback para navegar al dashboard principal
        self._create_layout()

    def _create_layout(self):
        """Crea el layout principal con cards de reportes en grid 2x3"""
        header_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)

        title = tk.Label(header_frame, text="Gestión de Apartamentos", **theme_manager.get_style("label_title"))
        title.pack(side="left")

        # Frame para botones de navegación (alineados a la derecha)
        buttons_frame = tk.Frame(header_frame, **theme_manager.get_style("frame"))
        buttons_frame.pack(side="right")
        
        # Agregar botones Volver y Dashboard
        self._create_navigation_buttons(buttons_frame, self.on_back)

        # Subtítulo
        subtitle_label = tk.Label(
            self, text="Reportes de Apartamentos",
            **theme_manager.get_style("label_subtitle")
        )
        subtitle_label.configure(font=("Segoe UI", 14))
        subtitle_label.pack(pady=(0, Spacing.MD))

        main_container = tk.Frame(self, **theme_manager.get_style("frame"))
        main_container.pack(pady=Spacing.SM, fill="both", expand=True)

        self._create_cards_grid(main_container)

    def _create_cards_grid(self, parent):
        """Crea el grid de tarjetas de reportes 2x3 con altura calculada dinámicamente"""
        cards_frame = tk.Frame(parent, **theme_manager.get_style("frame"))
        cards_frame.pack(pady=(0, Spacing.MD))
        
        cards_info = [
            {
                "icon": "📊", "title": "Ocupación y Vacancia",
                "desc": "Tasa de ocupación y tiempo de vacancia por apartamento",
                "color": "#10b981", "command": self._show_occupancy_report
            },
            {
                "icon": "⏳", "title": "Historial de Ocupación",
                "desc": "Análisis histórico de ocupación y rotación de inquilinos",
                "color": "#3b82f6", "command": self._show_occupation_history
            }
        ]
        
        def calculate_and_create_cards():
            """Calcula la altura y crea los cards después de que el layout esté renderizado"""
            self.update_idletasks()
            container_height = self.winfo_height()
            
            if container_height <= 1:
                container_height = 600
            
            # Buscar el header_frame y subtitle_label
            header_frame = None
            subtitle_label = None
            for widget in self.winfo_children():
                if isinstance(widget, tk.Frame) and len(widget.winfo_children()) > 0:
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label) and "Gestión de Apartamentos" in child.cget("text"):
                            header_frame = widget
                            break
                elif isinstance(widget, tk.Label) and "Reportes de Apartamentos" in widget.cget("text"):
                    subtitle_label = widget
            
            header_height = header_frame.winfo_height() if header_frame else 80
            subtitle_height = subtitle_label.winfo_height() if subtitle_label else 40
            
            # Calcular espacio disponible para los cards
            container_padding_top = Spacing.SM
            padding_between_rows = Spacing.SM
            bottom_margin = Spacing.XL * 2
            cards_frame_padding = Spacing.MD
            
            available_height = (container_height - header_height - subtitle_height - 
                              container_padding_top - padding_between_rows - 
                              bottom_margin - cards_frame_padding)
            
            # Dividir entre 2 filas (una columna)
            num_rows = 2
            calculated_height = int(available_height / num_rows)
            
            min_height = 180
            max_height = 220
            card_height = max(min_height, min(calculated_height, max_height))
            
            # Limpiar cards_frame si ya tiene widgets
            for widget in cards_frame.winfo_children():
                widget.destroy()
            
            # Crear los cards con la altura calculada (grid 2x1 - una columna, dos filas)
            for i, info in enumerate(cards_info):
                row = i  # Una fila por card
                col = 0  # Una sola columna
                self._create_action_card(
                    cards_frame, info["icon"], info["title"], info["desc"],
                    info["color"], info["command"], card_height
                ).grid(row=row, column=col, padx=Spacing.MD, pady=Spacing.SM, sticky="nsew")
            
            # Configurar columna para que se distribuya uniformemente
            cards_frame.grid_columnconfigure(0, weight=1)
        
        self.after_idle(calculate_and_create_cards)

    def _create_action_card(self, parent, icon, title, description, color, command, card_height=200):
        """Crea una tarjeta de acción con altura calculada dinámicamente"""
        card_width = int(260 * 0.90)  # 234
        card_height_reduced = int(card_height * 0.90)
        
        card = tk.Frame(parent, bg="white", bd=2, relief="raised", 
                       padx=16, pady=16, width=card_width, height=card_height_reduced)
        card.pack_propagate(False)
        
        content_frame = tk.Frame(card, bg="white")
        content_frame.pack(fill="both", expand=True)
        
        icon_label = tk.Label(content_frame, text=icon, font=("Segoe UI", 24), 
                             fg=color, bg="white")
        icon_label.pack(pady=(0, 4))
        
        title_wraplength = int(220 * 0.90)
        title_label = tk.Label(content_frame, text=title, font=("Segoe UI", 13, "bold"), 
                              fg=color, bg="white", wraplength=title_wraplength, justify="center")
        title_label.pack(pady=(0, 2))
        
        desc_wraplength = int(220 * 0.90)
        desc_label = tk.Label(content_frame, text=description, font=("Segoe UI", 9), 
                             fg="#444", bg="white", wraplength=desc_wraplength, justify="center")
        desc_label.pack(pady=(0, 4))
        
        def on_card_click(e):
            e.widget.focus_set()
            command()
            return "break"
        
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
        
        all_widgets = [card, content_frame, icon_label, title_label, desc_label]
        for widget in all_widgets:
            widget.bind("<Button-1>", on_card_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.configure(cursor="hand2")
        
        return card

    def _show_occupancy_report(self):
        """Muestra el reporte de ocupación y vacancia"""
        from .reports.occupancy_vacancy_report_view import OccupancyVacancyReportView
        
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
            on_back=self._back_to_reports_menu,
            on_navigate=navigate_callback
        )
        report_view.pack(fill="both", expand=True)

    def _show_occupation_history(self):
        """Muestra el historial de ocupación"""
        from .reports.occupation_history_report_view import OccupationHistoryReportView
        
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
        
        report_view = OccupationHistoryReportView(
            self,
            on_back=self._back_to_reports_menu,
            on_navigate=navigate_callback
        )
        report_view.pack(fill="both", expand=True)

    def _back_to_reports_menu(self):
        """Vuelve al menú principal de reportes"""
        for widget in self.winfo_children():
            widget.destroy()
        self._create_layout()

    def _create_navigation_buttons(self, parent, on_back_command):
        """Crea los botones Volver y Dashboard con estilo consistente"""
        from manager.app.ui.components.icons import Icons
        
        theme = theme_manager.themes[theme_manager.current_theme]
        hover_bg = theme.get("bg_tertiary", theme["btn_secondary_hover"])
        
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
        
        btn_back = tk.Button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            **button_config,
            command=on_back_command
        )
        btn_back.pack(side="right", padx=(Spacing.SM, 0))
        
        def on_enter_back(e):
            btn_back.configure(bg=hover_bg)
        
        def on_leave_back(e):
            btn_back.configure(bg=theme["btn_secondary_bg"])
        
        btn_back.bind("<Enter>", on_enter_back)
        btn_back.bind("<Leave>", on_leave_back)
        
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
            
            if on_back_command:
                on_back_command()
        
        btn_dashboard = tk.Button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            **button_config,
            command=go_to_dashboard
        )
        btn_dashboard.pack(side="right")
        
        def on_enter_dashboard(e):
            btn_dashboard.configure(bg=hover_bg)
        
        def on_leave_dashboard(e):
            btn_dashboard.configure(bg=theme["btn_secondary_bg"])
        
        btn_dashboard.bind("<Enter>", on_enter_dashboard)
        btn_dashboard.bind("<Leave>", on_leave_dashboard)
