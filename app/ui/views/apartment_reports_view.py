"""
Vista para mostrar reportes y estadísticas de los apartamentos.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import ModernButton

class ApartmentReportsView(tk.Frame):
    """Vista de reportes de apartamentos (actualmente un placeholder)."""

    def __init__(self, parent, on_back: Callable):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_back = on_back
        self._create_layout()

    def _create_layout(self):
        # Header
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)
        tk.Label(header, text="Reportes y Estadísticas de Apartamentos", **theme_manager.get_style("label_title")).pack(side="left")
        ModernButton(header, text="← Volver", style="secondary", command=self.on_back).pack(side="right")

        # Content
        content_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        content_frame.pack(fill="both", expand=True, padx=Spacing.XL, pady=Spacing.XL)

        tk.Label(
            content_frame,
            text="📈 Módulo en Desarrollo 📈",
            font=("Segoe UI", 24, "bold"),
            fg="#0078d4"
        ).pack(pady=Spacing.LG)

        tk.Label(
            content_frame,
            text="Esta sección está siendo construida para ofrecerte los mejores análisis.",
            font=("Segoe UI", 12),
            wraplength=500,
            justify="center"
        ).pack(pady=(0, Spacing.XL))
        
        # Upcoming features list
        features_frame = tk.Frame(content_frame, **theme_manager.get_style("card"))
        features_frame.pack(pady=Spacing.LG, padx=Spacing.LG)
        
        tk.Label(
            features_frame,
            text="Próximamente disponible:",
            font=("Segoe UI", 14, "bold"),
            **theme_manager.get_style("card_content")
        ).pack(anchor="w", padx=Spacing.LG, pady=(Spacing.MD, Spacing.SM))

        upcoming_features = [
            "📊 Reporte de ingresos por apartamento.",
            "🔧 Historial de mantenimiento y costos asociados.",
            "⏳ Reporte de vacancia (tiempo que un apartamento permanece desocupado).",
            "💰 Comparativa de rentabilidad entre unidades.",
            "📈 Gráficos interactivos y exportación a PDF/Excel."
        ]
        
        for feature in upcoming_features:
            tk.Label(
                features_frame,
                text=feature,
                font=("Segoe UI", 11),
                **theme_manager.get_style("card_content"),
                justify="left"
            ).pack(anchor="w", padx=Spacing.LG, pady=Spacing.XS)

        tk.Label(
            content_frame,
            text="¡Gracias por tu paciencia!",
            font=("Segoe UI", 12, "italic")
        ).pack(pady=(Spacing.XL, 0)) 