"""
Vista para mostrar reportes y estadísticas de los apartamentos.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors

class ApartmentReportsView(tk.Frame):
    """Vista de reportes de apartamentos con cards de acción."""

    def __init__(self, parent, on_back: Callable, on_navigate: Callable = None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.on_back = on_back
        self.on_navigate = on_navigate
        self._create_layout()

    def _create_layout(self):
        cb = self._content_bg
        fg = theme_manager.themes[theme_manager.current_theme].get("text_primary", "#1f2937")
        header_frame = tk.Frame(self, bg=cb)
        header_frame.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)
        title = tk.Label(header_frame, text="Gestión de Apartamentos", font=("Segoe UI", 16, "bold"), bg=cb, fg=fg)
        title.pack(side="left")
        buttons_frame = tk.Frame(header_frame, bg=cb)
        buttons_frame.pack(side="right")
        self._create_navigation_buttons(buttons_frame, self.on_back)
        subtitle_label = tk.Label(self, text="Reportes de Apartamentos", font=("Segoe UI", 14), bg=cb, fg=fg)
        subtitle_label.pack(pady=(0, Spacing.MD))
        main_container = tk.Frame(self, bg=cb)
        main_container.pack(pady=Spacing.SM, fill="both", expand=True)
        self._create_cards_grid(main_container)

    def _create_cards_grid(self, parent):
        cb = self._content_bg
        cards_frame = tk.Frame(parent, bg=cb)
        cards_frame.pack(pady=(0, Spacing.MD))
        
        cards_info = [
            {
                "icon": "📊",
                "title": "Ocupación y Vacancia",
                "desc": "",
                "icon_color": "#5b21b6",
                "title_fg": "#000000",
                "command": self._show_occupancy_report,
            },
        ]
        
        def calculate_and_create_cards():
            """Calcula la altura y crea los cards después de que el layout esté renderizado"""
            # Verificar que self y cards_frame todavía existen antes de continuar
            try:
                if not self.winfo_exists():
                    return
            except tk.TclError:
                return
            
            try:
                if not cards_frame.winfo_exists():
                    return
            except (tk.TclError, AttributeError):
                return
            
            try:
                self.update_idletasks()
                container_height = self.winfo_height()
            except tk.TclError:
                return
            
            if container_height <= 1:
                container_height = 600
            
            # Buscar el header_frame y subtitle_label
            header_frame = None
            subtitle_label = None
            try:
                for widget in self.winfo_children():
                    try:
                        if isinstance(widget, tk.Frame) and len(widget.winfo_children()) > 0:
                            for child in widget.winfo_children():
                                try:
                                    if isinstance(child, tk.Label) and "Gestión de Apartamentos" in child.cget("text"):
                                        header_frame = widget
                                        break
                                except tk.TclError:
                                    continue
                        elif isinstance(widget, tk.Label) and "Reportes de Apartamentos" in widget.cget("text"):
                            subtitle_label = widget
                    except tk.TclError:
                        continue
            except tk.TclError:
                return
            
            try:
                header_height = header_frame.winfo_height() if header_frame else 80
                subtitle_height = subtitle_label.winfo_height() if subtitle_label else 40
            except tk.TclError:
                header_height = 80
                subtitle_height = 40
            
            # Calcular espacio disponible para los cards
            container_padding_top = Spacing.SM
            padding_between_rows = Spacing.SM
            bottom_margin = Spacing.XL * 2
            cards_frame_padding = Spacing.MD
            
            available_height = (container_height - header_height - subtitle_height - 
                              container_padding_top - padding_between_rows - 
                              bottom_margin - cards_frame_padding)
            
            # Una sola fila (un card)
            num_rows = 1
            calculated_height = int(available_height / num_rows)
            
            min_height = 180
            max_height = 220
            card_height = max(min_height, min(calculated_height, max_height))
            
            # Limpiar cards_frame si ya tiene widgets
            try:
                for widget in cards_frame.winfo_children():
                    try:
                        widget.destroy()
                    except tk.TclError:
                        continue
            except tk.TclError:
                return
            
            # Crear los cards con la altura calculada
            try:
                for i, info in enumerate(cards_info):
                    row, col = i, 0
                    self._create_action_card(
                        cards_frame,
                        info["icon"],
                        info["title"],
                        info.get("desc", ""),
                        info.get("icon_color", info.get("color", "#6d28d9")),
                        info["command"],
                        card_height,
                        title_fg=info.get("title_fg"),
                    ).grid(row=row, column=col, padx=Spacing.MD, pady=Spacing.SM, sticky="nsew")
                
                # Configurar columna para que se distribuya uniformemente
                cards_frame.grid_columnconfigure(0, weight=1)
            except tk.TclError:
                return
        
        self.after_idle(calculate_and_create_cards)

    def _create_action_card(self, parent, icon, title, description, color, command, card_height=200, title_fg=None):
        """Crea una tarjeta de acción con altura calculada dinámicamente."""
        card_width = int(260 * 0.90)
        card_height_reduced = int(card_height * 0.90)
        card_bg = "#f3e8ff"
        hover_bg = "#e9d5ff"
        card = tk.Frame(parent, bg=card_bg, bd=2, relief="raised",
                        padx=16, pady=16, width=card_width, height=card_height_reduced)
        card.pack_propagate(False)
        content_frame = tk.Frame(card, bg=card_bg)
        content_frame.pack(fill="both", expand=True)
        icon_label = tk.Label(content_frame, text=icon, font=("Segoe UI", 24), fg=color, bg=card_bg)
        icon_label.pack(pady=(0, 4))
        title_wraplength = int(220 * 0.90)
        title_color = title_fg if title_fg is not None else color
        title_label = tk.Label(content_frame, text=title, font=("Segoe UI", 13, "bold"),
                              fg=title_color, bg=card_bg, wraplength=title_wraplength, justify="center")
        title_label.pack(pady=(0, 2))
        desc_wraplength = int(220 * 0.90)
        desc_label = tk.Label(content_frame, text=description, font=("Segoe UI", 9),
                              fg="#374151", bg=card_bg, wraplength=desc_wraplength, justify="center")
        if description:
            desc_label.pack(pady=(0, 4))

        def on_card_click(e):
            e.widget.focus_set()
            command()
            return "break"

        def on_enter(e):
            card.configure(bg=hover_bg)
            content_frame.configure(bg=hover_bg)
            icon_label.configure(bg=hover_bg)
            title_label.configure(bg=hover_bg)
            if description:
                desc_label.configure(bg=hover_bg)

        def on_leave(e):
            card.configure(bg=card_bg)
            content_frame.configure(bg=card_bg)
            icon_label.configure(bg=card_bg)
            title_label.configure(bg=card_bg)
            if description:
                desc_label.configure(bg=card_bg)

        all_widgets = [card, content_frame, icon_label, title_label]
        if description:
            all_widgets.append(desc_label)
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
        """Crea los botones Volver y Dashboard con estilo moderno y colores morados del módulo de administración"""
        from manager.app.ui.components.icons import Icons
        
        # Colores morados para módulo de administración
        colors = get_module_colors("administración")
        purple_primary = colors["primary"]
        purple_hover = colors["hover"]
        purple_light = colors["light"]
        purple_text = colors["text"]
        
        theme = theme_manager.themes[theme_manager.current_theme]
        btn_bg = theme.get("btn_secondary_bg", "#e5e7eb")
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
            border_color=purple_light
        )
        btn_back.pack(side="right", padx=(Spacing.MD, 0))

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
        
        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=purple_primary,
            fg_color="white",
            hover_bg=purple_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color=purple_hover
        )
        btn_dashboard.pack(side="right")
