"""
Diálogo reutilizable de exportación exitosa.
Uso:
    from manager.app.ui.components.export_success_dialog import show_export_success_dialog
    show_export_success_dialog(parent_widget, filepath, module_color="#2563eb")
"""
import os
import subprocess
import tkinter as tk
from pathlib import Path


def show_export_success_dialog(parent: tk.Widget, filepath, module_color: str = "#2563eb"):
    """
    Muestra la ventana modal de exportación exitosa.

    Botones: Abrir carpeta | Abrir archivo | Aceptar
    (El botón Copiar fue eliminado intencionalmente.)

    Args:
        parent:        Widget padre (Toplevel o Frame).
        filepath:      Ruta del archivo exportado (str o Path).
        module_color:  Color primario del módulo para el ícono ℹ.
    """
    path = Path(filepath) if not isinstance(filepath, Path) else filepath

    win = tk.Toplevel(parent.winfo_toplevel())
    win.title("Exportación exitosa")
    win.geometry("460x170")
    win.resizable(False, False)
    win.transient(parent.winfo_toplevel())
    win.grab_set()

    # ── Contenido ──────────────────────────────────────────────
    content = tk.Frame(win, padx=20, pady=16)
    content.pack(fill="both", expand=True)

    # Fila superior: ícono + texto + ruta
    top = tk.Frame(content)
    top.pack(fill="x")

    tk.Label(
        top, text="ℹ", font=("Segoe UI", 26), fg=module_color
    ).pack(side="left", padx=(0, 12))

    msg = tk.Frame(top)
    msg.pack(side="left", fill="x", expand=True)

    tk.Label(
        msg,
        text="Exportación exitosa. Archivo guardado en:",
        font=("Segoe UI", 10),
        anchor="w",
    ).pack(fill="x")

    path_var = tk.StringVar(value=str(path))
    path_entry = tk.Entry(msg, textvariable=path_var, font=("Segoe UI", 9))
    path_entry.pack(fill="x", pady=(4, 0))
    path_entry.bind("<Key>", lambda e: "break")   # solo lectura

    # ── Botones ────────────────────────────────────────────────
    btns = tk.Frame(content)
    btns.pack(fill="x", pady=(14, 0))

    btn_cfg = dict(font=("Segoe UI", 10), relief="flat", pady=6, cursor="hand2")

    def open_folder():
        folder = str(path.resolve().parent)
        if os.name == "nt":
            os.startfile(folder)
        else:
            subprocess.run(["xdg-open", folder], check=False)

    def open_file():
        p = str(path.resolve())
        if os.name == "nt":
            os.startfile(p)
        else:
            subprocess.run(["xdg-open", p], check=False)

    tk.Button(
        btns, text="📁 Abrir carpeta",
        bg="#6b7280", fg="white", padx=14,
        command=open_folder, **btn_cfg
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        btns, text="📄 Abrir archivo",
        bg="#059669", fg="white", padx=14,
        command=open_file, **btn_cfg
    ).pack(side="left")

    tk.Button(
        btns, text="Aceptar",
        bg=module_color, fg="white", padx=18,
        command=win.destroy, **btn_cfg
    ).pack(side="right")
