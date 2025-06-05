import tkinter as tk
from tkinter import ttk
import json
import os

def load_colors():
    """Carga los colores desde el archivo de configuración"""
    try:
        with open('config/colors.json', 'r') as f:
            return json.load(f)
    except:
        # Colores por defecto si no se puede cargar el archivo
        return {
            'primary': '#1a73e8',
            'primary_dark': '#1557b0',
            'secondary': '#34a853',
            'danger': '#ea4335',
            'warning': '#fbbc05',
            'success': '#0f9d58',
            'background': '#ffffff',
            'surface': '#f8f9fa',
            'text': '#202124',
            'text_secondary': '#5f6368'
        }

def create_styled_button(parent, text, command):
    """Crea un botón estilizado"""
    btn = tk.Button(parent,
                    text=text,
                    command=command,
                    font=("Segoe UI", 10),
                    bg="#1a73e8",
                    fg="white",
                    bd=0,
                    padx=15,
                    pady=5,
                    cursor="hand2")
    
    def on_enter(e):
        btn.configure(bg="#1557b0")
    
    def on_leave(e):
        btn.configure(bg="#1a73e8")
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn

def create_card(parent, title, value, icon):
    """Crea una tarjeta de estadísticas"""
    card = ttk.Frame(parent, style="Card.TFrame")
    
    # Contenido de la tarjeta
    content = ttk.Frame(card)
    content.pack(fill="both", expand=True, padx=15, pady=10)
    
    # Icono
    icon_label = ttk.Label(content,
                          text=icon,
                          font=("Segoe UI", 24),
                          foreground="#1a73e8")
    icon_label.pack(anchor="w")
    
    # Valor
    value_label = ttk.Label(content,
                           text=value,
                           font=("Segoe UI", 20, "bold"),
                           foreground="#202124")
    value_label.pack(anchor="w", pady=(5, 0))
    
    # Título
    title_label = ttk.Label(content,
                           text=title,
                           font=("Segoe UI", 12),
                           foreground="#5f6368")
    title_label.pack(anchor="w", pady=(5, 0))
    
    return card

def setup_styles(root):
    """Configura los estilos globales de la aplicación"""
    style = ttk.Style()
    
    # Configurar tema
    try:
        root.tk.call("source", "azure.tcl")
        style.theme_use("azure")
    except tk.TclError:
        style.theme_use("clam")
    
    # Estilos principales
    style.configure("Main.TFrame", background="#ffffff")
    style.configure("Card.TFrame",
                   background="#ffffff",
                   relief="solid",
                   borderwidth=1)
    style.configure("CardHover.TFrame",
                   background="#f8f9fa",
                   relief="solid",
                   borderwidth=1)
    
    # Configurar colores base
    root.configure(bg="#ffffff")
    style.configure("TFrame", background="#ffffff")
    style.configure("TLabel", background="#ffffff")
    style.configure("TNotebook", background="#ffffff", borderwidth=0)
    style.configure("TNotebook.Tab", padding=[12, 4], font=("Segoe UI", 10))

    # Estilo para etiquetas
    style.configure('Title.TLabel',
                   font=('Segoe UI', 24, 'bold'),
                   foreground='#202124')
    
    style.configure('Subtitle.TLabel',
                   font=('Segoe UI', 18),
                   foreground='#5f6368')
    
    # Estilo para entradas
    style.configure('TEntry',
                   fieldbackground='#ffffff',
                   borderwidth=1)
    
    # Estilo para combobox
    style.configure('TCombobox',
                   fieldbackground='#ffffff',
                   borderwidth=1)
    
    # Estilos básicos para el calendario
    style.configure('Calendar.TFrame', background='white')
    style.configure('Calendar.TLabel', background='white')
    style.configure('Calendar.TButton', background='white') 