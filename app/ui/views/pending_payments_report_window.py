"""
Ventana de reporte de pagos pendientes (Toplevel).
Muestra el contenido del reporte con opciones Exportar CSV, Exportar TXT y Cerrar.
"""

import csv
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from pathlib import Path
from typing import Callable

from manager.app.paths_config import EXPORTS_DIR, ensure_dirs
from manager.app.ui.components.theme_manager import Spacing
from manager.app.ui.components.modern_widgets import get_module_colors


def show_pending_payments_report(
    parent: tk.Tk,
    content: str,
    on_export_success: Callable[[Path], None],
) -> None:
    """
    Muestra una ventana modal con el reporte de pagos pendientes.
    Reglas: orden Exportar CSV, TXT, Cerrar; colores reportes; on_export_success
    se invoca al exportar correctamente (el caller puede mostrar el diálogo de éxito).
    """
    colors = get_module_colors("reportes")
    header_bg = colors.get("hover", "#ea580c")
    btn_export_bg = colors.get("primary", "#f97316")

    window = tk.Toplevel(parent)
    window.title("Reporte de Pagos Pendientes")
    window.geometry("800x600")
    window.transient(parent)
    window.grab_set()

    header = tk.Frame(window, bg=header_bg, height=50)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(
        header,
        text="Reporte de Pagos Pendientes",
        font=("Segoe UI", 14, "bold"),
        bg=header_bg,
        fg="white",
    ).pack(side="left", padx=Spacing.LG, pady=12)
    btn_frame = tk.Frame(header, bg=header_bg)
    btn_frame.pack(side="right", padx=Spacing.LG)

    def export_csv() -> None:
        try:
            ensure_dirs()
            filename = (
                f"pending_payments_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            filepath = EXPORTS_DIR / filename
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                for line in content.split("\n"):
                    writer.writerow([line])
            on_export_success(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar CSV: {str(e)}")

    def export_txt() -> None:
        try:
            ensure_dirs()
            filename = (
                f"pending_payments_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            filepath = EXPORTS_DIR / filename
            with open(filepath, "w", encoding="utf-8-sig") as f:
                f.write(content)
            on_export_success(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar TXT: {str(e)}")

    btn_export_hover = colors.get("hover", "#ea580c")
    btn_close_bg = "#dc2626"
    btn_close_hover = "#b91c1c"
    btn_opts = dict(
        font=("Segoe UI", 9),
        fg="white",
        relief="flat",
        padx=14,
        pady=6,
        cursor="hand2",
    )

    btn_csv = tk.Button(
        btn_frame,
        text="💾 Exportar CSV",
        bg=btn_export_bg,
        **btn_opts,
        command=export_csv,
    )
    btn_csv.pack(side="left", padx=Spacing.SM)
    btn_csv.bind("<Enter>", lambda e: btn_csv.config(bg=btn_export_hover))
    btn_csv.bind("<Leave>", lambda e: btn_csv.config(bg=btn_export_bg))

    btn_txt = tk.Button(
        btn_frame,
        text="📄 Exportar TXT",
        bg=btn_export_bg,
        **btn_opts,
        command=export_txt,
    )
    btn_txt.pack(side="left", padx=Spacing.SM)
    btn_txt.bind("<Enter>", lambda e: btn_txt.config(bg=btn_export_hover))
    btn_txt.bind("<Leave>", lambda e: btn_txt.config(bg=btn_export_bg))

    btn_close = tk.Button(
        btn_frame,
        text="× Cerrar",
        bg=btn_close_bg,
        width=10,
        **btn_opts,
        command=window.destroy,
    )
    btn_close.pack(side="left", padx=Spacing.SM)
    btn_close.bind("<Enter>", lambda e: btn_close.config(bg=btn_close_hover))
    btn_close.bind("<Leave>", lambda e: btn_close.config(bg=btn_close_bg))

    text_frame = tk.Frame(window)
    text_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=Spacing.LG)

    text_widget = tk.Text(
        text_frame,
        font=("Consolas", 10),
        wrap="word",
        bg="#ffffff",
        fg="#000000",
    )
    text_widget.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
    scrollbar.pack(side="right", fill="y")
    text_widget.config(yscrollcommand=scrollbar.set)

    text_widget.insert("1.0", content)
    text_widget.tag_configure("bold", font=("Consolas", 10, "bold"))
    num_lines = int(text_widget.index("end-1c").split(".")[0])
    for i in range(1, num_lines + 1):
        line_text = text_widget.get(f"{i}.0", f"{i}.0 lineend")
        if line_text.strip().startswith("Inquilino:") or "• Apartamento:" in line_text:
            text_widget.tag_add("bold", f"{i}.0", f"{i}.0 lineend")
    text_widget.config(state="disabled")
