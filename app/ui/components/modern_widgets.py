"""
Widgets modernos para Building Manager Pro
Componentes reutilizables con diseño profesional
"""

import tkinter as tk
from typing import Dict, Any, List, Optional, Callable
from .theme_manager import theme_manager, Spacing, Colors
from .icons import Icons


class ModernButton(tk.Frame):
    """Botón moderno con icono y estilo personalizable"""
    
    def __init__(self, parent, text: str = "", icon: str = "", style: str = "primary",
                 command: Callable = None, small: bool = False, fg: str = None, **kwargs):
        theme = theme_manager.themes[theme_manager.current_theme]
        
        # Determinar colores según estilo
        if style == "primary":
            bg = theme["btn_primary_bg"]
            fg = fg or theme["btn_primary_fg"]
            hover_bg = theme.get("btn_primary_hover", Colors.PRIMARY_DARK)
        elif style == "secondary":
            bg = theme["btn_secondary_bg"]
            fg = fg or theme["btn_secondary_fg"]
            hover_bg = theme.get("btn_secondary_hover", Colors.BG_TERTIARY)
        elif style == "warning":
            # Verde para módulo de pagos (antes era naranja)
            bg = "#22c55e"  # green-500 - verde para mantener tonalidad verde del módulo
            fg = fg or "#ffffff"
            hover_bg = "#16a34a"  # green-600 - verde más oscuro para hover
        elif style == "danger":
            bg = Colors.ERROR
            fg = fg or "#ffffff"
            hover_bg = "#dc2626"
        elif style == "purple" or style == "admin":
            # Morado para módulo de administración
            bg = "#8b5cf6"  # purple-500 - morado para mantener tonalidad morada del módulo
            fg = fg or "#ffffff"
            hover_bg = "#7c3aed"  # purple-600 - morado más oscuro para hover
        elif style == "pdf":
            bg = "#dc2626"
            fg = fg or "#ffffff"
            hover_bg = "#b91c1c"
        else:
            bg = theme["btn_primary_bg"]
            fg = fg or theme["btn_primary_fg"]
            hover_bg = theme.get("btn_primary_hover", Colors.PRIMARY_DARK)
        
        super().__init__(parent, bg=bg, relief="flat", bd=0, **kwargs)
        
        self.command = command
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        
        # Contenedor interno
        inner = tk.Frame(self, bg=bg)
        inner.pack(fill="both", expand=True, padx=Spacing.MD if not small else Spacing.SM, 
                   pady=Spacing.SM if not small else Spacing.XS)
        
        # Icono
        if icon:
            icon_label = tk.Label(inner, text=icon, bg=bg, fg=fg, 
                                 font=("Segoe UI Symbol", 12 if not small else 10))
            icon_label.pack(side="left", padx=(0, Spacing.XS if text else 0))
        
        # Texto
        if text:
            text_label = tk.Label(inner, text=text, bg=bg, fg=fg,
                                 font=("Segoe UI", 10 if small else 11, "bold"))
            text_label.pack(side="left")
        
        # Bind events - función auxiliar para vincular a todos los widgets recursivamente
        def bind_to_all_widgets(widget, event, handler):
            """Vincular evento a un widget y todos sus hijos recursivamente"""
            widget.bind(event, handler)
            widget.configure(cursor="hand2")
            for child in widget.winfo_children():
                bind_to_all_widgets(child, event, handler)
        
        def on_enter(e):
            self.configure(bg=self.hover_bg)
            inner.configure(bg=self.hover_bg)
            for widget in inner.winfo_children():
                widget.configure(bg=self.hover_bg)
        
        def on_leave(e):
            self.configure(bg=self.bg)
            inner.configure(bg=self.bg)
            for widget in inner.winfo_children():
                widget.configure(bg=self.bg)
        
        def on_click(e):
            if self.command:
                self.command()
            return "break"  # Prevenir propagación del evento
        
        # Vincular eventos a todo el botón y sus hijos
        bind_to_all_widgets(self, "<Enter>", on_enter)
        bind_to_all_widgets(self, "<Leave>", on_leave)
        bind_to_all_widgets(self, "<Button-1>", on_click)


class ModernCard(tk.Frame):
    """Tarjeta moderna con sombra y estilo profesional"""
    
    def __init__(self, parent, title=None, **kwargs):
        theme = theme_manager.themes[theme_manager.current_theme]
        bg = kwargs.pop("bg", theme["bg_primary"])
        super().__init__(parent, bg=bg, relief="flat", bd=1,
                        highlightbackground=theme["border_light"], **kwargs)
        
        # Contenedor interno para el contenido
        self.content_frame = tk.Frame(self, bg=bg)
        self.content_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)
        
        # Título opcional
        if title:
            title_label = tk.Label(
                self.content_frame,
                text=title,
                font=("Segoe UI", 12, "bold"),
                bg=bg,
                fg=theme["text_primary"]
            )
            title_label.pack(anchor="w", pady=(0, Spacing.MD))


class ModernEntry(tk.Entry):
    """Campo de entrada moderno"""
    
    def __init__(self, parent, placeholder: str = "", **kwargs):
        theme = theme_manager.themes[theme_manager.current_theme]
        default_kwargs = {
            "bg": theme["bg_primary"],
            "fg": theme["text_primary"],
            "font": ("Segoe UI", 11),
            "relief": "solid",
            "bd": 1,
            "highlightthickness": 0,
            "insertbackground": theme["text_primary"]
        }
        default_kwargs.update(kwargs)
        super().__init__(parent, **default_kwargs)
        
        if placeholder:
            self.insert(0, placeholder)
            self.configure(fg=theme["text_secondary"])
            self.bind("<FocusIn>", lambda e: self._on_focus_in(placeholder))
            self.bind("<FocusOut>", lambda e: self._on_focus_out(placeholder))
    
    def _on_focus_in(self, placeholder):
        theme = theme_manager.themes[theme_manager.current_theme]
        if self.get() == placeholder:
            self.delete(0, tk.END)
            self.configure(fg=theme["text_primary"])
    
    def _on_focus_out(self, placeholder):
        theme = theme_manager.themes[theme_manager.current_theme]
        if not self.get():
            self.insert(0, placeholder)
            self.configure(fg=theme["text_secondary"])


class ModernBadge(tk.Label):
    """Badge moderno para mostrar estados"""
    
    def __init__(self, parent, text: str, style: str = "neutral"):
        theme = theme_manager.themes[theme_manager.current_theme]
        
        # Colores según estilo
        if style == "success":
            bg = Colors.SUCCESS
            fg = "#ffffff"
        elif style == "danger":
            bg = Colors.ERROR
            fg = "#ffffff"
        elif style == "warning":
            # Verde para módulo de pagos (antes era naranja)
            bg = "#22c55e"  # green-500 - verde para mantener tonalidad verde del módulo
            fg = "#ffffff"
        elif style == "info":
            bg = Colors.INFO
            fg = "#ffffff"
        else:  # neutral
            bg = theme["bg_tertiary"]
            fg = theme["text_primary"]
        
        super().__init__(parent, text=text, bg=bg, fg=fg,
                        font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                        padx=Spacing.SM, pady=Spacing.XS)


class ModernSeparator(tk.Frame):
    """Separador moderno"""
    
    def __init__(self, parent, orientation: str = "vertical"):
        theme = theme_manager.themes[theme_manager.current_theme]
        if orientation == "vertical":
            super().__init__(parent, width=1, bg=theme["border_light"], relief="flat")
            self.pack(side="left", fill="y", padx=Spacing.MD)
        else:
            super().__init__(parent, height=1, bg=theme["border_light"], relief="flat")
            self.pack(fill="x", pady=Spacing.MD)


def create_rounded_button(parent, text, bg_color, fg_color, hover_bg, hover_fg, 
                          command=None, padx=18, pady=8, radius=4, border_color="#000000", outline_width=1):
    """Crea un botón con esquinas ligeramente redondeadas. outline_width=0 para sin borde."""
    btn_frame = tk.Frame(parent, bg=parent.cget("bg"))
    
    # Calcular ancho mínimo basado en el texto
    temp_label = tk.Label(parent, text=text, font=("Segoe UI", 10, "bold"))
    temp_label.update_idletasks()
    min_width = temp_label.winfo_reqwidth() + padx * 2
    temp_label.destroy()
    
    canvas = tk.Canvas(
        btn_frame,
        bg=parent.cget("bg"),
        highlightthickness=0,
        borderwidth=0,
        height=pady * 2 + 20,
        width=min_width
    )
    canvas.pack(fill="both", expand=True)
    
    # Variables para el estado del botón
    current_bg = bg_color
    current_fg = fg_color
    
    def draw_rounded_rect(canvas, x1, y1, x2, y2, radius, fill_color, outline_color, outline_w=1):
        """Dibuja un rectángulo redondeado; si outline_w es 0 no se dibuja borde."""
        # Rectángulo central
        canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill=fill_color, outline="", width=0)
        canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius, fill=fill_color, outline="", width=0)
        # Esquinas redondeadas (arcos)
        canvas.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, start=90, extent=90, fill=fill_color, outline="", style="pieslice", width=0)
        canvas.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2, start=0, extent=90, fill=fill_color, outline="", style="pieslice", width=0)
        canvas.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, start=180, extent=90, fill=fill_color, outline="", style="pieslice", width=0)
        canvas.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2, start=270, extent=90, fill=fill_color, outline="", style="pieslice", width=0)
        if outline_w <= 0:
            return
        # Bordes rectos y arcos del borde
        canvas.create_line(x1 + radius, y1, x2 - radius, y1, fill=outline_color, width=outline_w)
        canvas.create_line(x1 + radius, y2, x2 - radius, y2, fill=outline_color, width=outline_w)
        canvas.create_line(x1, y1 + radius, x1, y2 - radius, fill=outline_color, width=outline_w)
        canvas.create_line(x2, y1 + radius, x2, y2 - radius, fill=outline_color, width=outline_w)
        canvas.create_arc(x1, y1, x1 + radius * 2, y1 + radius * 2, start=90, extent=90, outline=outline_color, style="arc", width=outline_w)
        canvas.create_arc(x2 - radius * 2, y1, x2, y1 + radius * 2, start=0, extent=90, outline=outline_color, style="arc", width=outline_w)
        canvas.create_arc(x1, y2 - radius * 2, x1 + radius * 2, y2, start=180, extent=90, outline=outline_color, style="arc", width=outline_w)
        canvas.create_arc(x2 - radius * 2, y2 - radius * 2, x2, y2, start=270, extent=90, outline=outline_color, style="arc", width=outline_w)
    
    def draw_button(bg, fg):
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width > 1 and height > 1:
            draw_rounded_rect(canvas, 1, 1, width-1, height-1, radius, bg, border_color, outline_w=outline_width)
            
            # Dibujar texto centrado
            canvas.create_text(
                width // 2,
                height // 2,
                text=text,
                fill=fg,
                font=("Segoe UI", 10, "bold"),
                anchor="center"
            )
    
    def on_configure(event):
        draw_button(current_bg, current_fg)
    
    def on_enter(e):
        nonlocal current_bg, current_fg
        current_bg = hover_bg
        current_fg = hover_fg
        draw_button(current_bg, current_fg)
        canvas.configure(cursor="hand2")
    
    def on_leave(e):
        nonlocal current_bg, current_fg
        current_bg = bg_color
        current_fg = fg_color
        draw_button(current_bg, current_fg)
    
    def on_click(e):
        if command:
            command()
    
    canvas.bind("<Configure>", on_configure)
    canvas.bind("<Enter>", on_enter)
    canvas.bind("<Leave>", on_leave)
    canvas.bind("<Button-1>", on_click)
    canvas.configure(cursor="hand2")
    
    # Dibujar inicialmente después de que el widget esté configurado
    btn_frame.update_idletasks()
    draw_button(current_bg, current_fg)
    
    return btn_frame


def get_module_colors(module_name):
    """Obtiene los colores apropiados según el módulo (tonos con presencia, no pálidos)"""
    colors = {
        "inquilinos": {
            "primary": "#3b82f6",  # blue-500
            "hover": "#2563eb",    # blue-600
            "light": "#e0ecf7",    # tono azul suave (como segunda imagen)
            "text": "#1e40af"      # blue-800
        },
        "pagos": {
            "primary": "#22c55e",  # green-500
            "hover": "#16a34a",    # green-600
            "light": "#bbf7d0",    # green-200
            "text": "#166534"      # green-800
        },
        "gastos": {
            "primary": "#ef4444",   # red-500
            "hover": "#dc2626",    # red-600
            "light": "#fecaca",     # red-200
            "text": "#991b1b"      # red-800
        },
        "administración": {
            "primary": "#8b5cf6",  # purple-500
            "hover": "#7c3aed",    # purple-600
            "light": "#e9d5ff",     # purple-200
            "text": "#7c3aed"      # purple-600
        },
        "reportes": {
            "primary": "#f97316",   # orange-500
            "hover": "#ea580c",     # orange-600
            "light": "#fed7aa",     # orange-200
            "text": "#c2410c"      # orange-800
        }
    }
    return colors.get(module_name.lower(), colors["inquilinos"])


class ModernMetricCard(tk.Frame):
    """Tarjeta de métrica moderna"""
    
    def __init__(self, parent, title: str, value: str, icon: str = "", 
                 color_theme: str = "primary"):
        theme = theme_manager.themes[theme_manager.current_theme]
        # Usar bg_secondary para modo oscuro, blanco para modo claro
        card_bg = theme["bg_secondary"] if theme_manager.current_theme == "dark" else "white"
        # Card con borde más visible y fondo adaptado al tema
        super().__init__(parent, bg=card_bg, relief="flat", bd=1,
                        highlightbackground=theme["border_light"],
                        highlightthickness=1)
        
        # Contenedor interno con padding reducido (1/3 menos)
        inner = tk.Frame(self, bg=card_bg)
        inner.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
        
        # Header con icono y título en la misma línea
        header = tk.Frame(inner, bg=card_bg)
        header.pack(fill="x", pady=(0, Spacing.XS))
        
        if icon:
            icon_label = tk.Label(header, text=icon, bg=card_bg,
                                 fg="#000000",
                                 font=("Segoe UI Symbol", 12))
            icon_label.pack(side="left", padx=(0, Spacing.XS))
        
        title_label = tk.Label(header, text=title, bg=card_bg,
                              fg="#000000", font=("Segoe UI", 10))
        title_label.pack(side="left", fill="x", expand=True)
        
        # Valor destacado (reducido 1/3)
        value_label = tk.Label(inner, text=value, bg=card_bg,
                             fg=theme["text_primary"], font=("Segoe UI", 14, "bold"))
        value_label.pack(anchor="w")


class DetailedMetricCard(tk.Frame):
    """Tarjeta de métrica con detalles"""
    
    def __init__(self, parent, title: str, total_value: str, details: List[Dict[str, Any]],
                 icon: str = "", color_theme: str = "primary"):
        theme = theme_manager.themes[theme_manager.current_theme]
        # Usar bg_secondary para modo oscuro, blanco para modo claro
        card_bg = theme["bg_secondary"] if theme_manager.current_theme == "dark" else "white"
        # Card con borde más visible y fondo adaptado al tema
        super().__init__(parent, bg=card_bg, relief="flat", bd=1,
                        highlightbackground=theme["border_light"],
                        highlightthickness=1)
        
        # Contenedor interno con padding reducido (1/3 menos)
        inner = tk.Frame(self, bg=card_bg)
        inner.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)
        
        # Header con icono y título
        header = tk.Frame(inner, bg=card_bg)
        header.pack(fill="x", pady=(0, Spacing.XS))
        
        if icon:
            icon_label = tk.Label(header, text=icon, bg=card_bg,
                                 fg="#000000",
                                 font=("Segoe UI Symbol", 12))
            icon_label.pack(side="left", padx=(0, Spacing.XS))
        
        title_label = tk.Label(header, text=title, bg=card_bg,
                              fg="#000000", font=("Segoe UI", 10))
        title_label.pack(side="left", fill="x", expand=True)
        
        # Valor total destacado - aumentado para mejor visibilidad
        total_label = tk.Label(inner, text=total_value, bg=card_bg,
                             fg=theme["text_primary"], font=("Segoe UI", 18, "bold"))  # aumentado de 14 a 18
        total_label.pack(anchor="w", pady=(0, Spacing.XS))
        
        # Detalles con espaciado reducido - aumentado tamaño de fuente para mejor visibilidad
        details_frame = tk.Frame(inner, bg=card_bg)
        details_frame.pack(fill="x")
        
        for i, detail in enumerate(details):
            detail_row = tk.Frame(details_frame, bg=card_bg)
            detail_row.pack(fill="x", pady=(Spacing.XS if i > 0 else 0, 0))
            
            label = tk.Label(detail_row, text=detail.get("label", ""), 
                           bg=card_bg, fg=theme["text_secondary"],
                           font=("Segoe UI", 10))  # aumentado de 7 a 10 para mejor visibilidad
            label.pack(side="left")
            
            value = tk.Label(detail_row, text=str(detail.get("value", "")),
                           bg=card_bg, fg=detail.get("color", theme["text_primary"]),
                           font=("Segoe UI", 10, "bold"))  # aumentado de 7 a 10 para mejor visibilidad
            value.pack(side="right")


def bind_combobox_dropdown_on_click(combobox):
    """Hace que el listado del combobox se abra al hacer clic en el campo de texto (no solo en la flecha).
    En clic en la flecha no se interfiere para que el menú abra de forma nativa.
    Aplicar a todos los ttk.Combobox de la aplicación (ver ARCHITECTURE.md y reglas Cursor)."""
    def _on_click(event):
        widget = event.widget
        if not widget.winfo_exists():
            return
        try:
            w = widget.winfo_width()
            if w > 0 and event.x >= max(0, w - 28):
                return  # clic en la flecha: dejar comportamiento nativo
        except Exception:
            pass
        def _post():
            if widget.winfo_exists():
                widget.focus_set()
                widget.event_generate('<Down>')
        widget.after(30, _post)
    combobox.bind('<Button-1>', _on_click)

