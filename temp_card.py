def create_card(self, parent, icon_text, title, description, command):
    """Crea una card con estilo Material Design"""
    card = ttk.Frame(parent, style="Card.TFrame", cursor="hand2")
    
    # Contenido de la card
    content = ttk.Frame(card, cursor="hand2")
    content.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Icono y título
    header = ttk.Frame(content, cursor="hand2")
    header.pack(fill="x", pady=(0, 10))
    
    icon = ttk.Label(header,
                    text=icon_text,
                    font=("Segoe UI", 24),
                    foreground="#1a73e8",
                    cursor="hand2")
    icon.pack(side="left")
    
    title_label = ttk.Label(header,
                           text=title,
                           font=("Segoe UI", 16, "bold"),
                           foreground="#202124",
                           cursor="hand2")
    title_label.pack(side="left", padx=(10, 0))
    
    # Descripción
    desc_label = ttk.Label(content,
                          text=description,
                          font=("Segoe UI", 10),
                          foreground="#5f6368",
                          wraplength=300,
                          cursor="hand2")
    desc_label.pack(fill="x", pady=(0, 15))
    
    # Botón de acción
    btn = tk.Button(content,
                   text="Abrir →",
                   command=command,
                   font=("Segoe UI", 10),
                   bg="#1a73e8",
                   fg="white",
                   bd=0,
                   padx=15,
                   pady=5,
                   cursor="hand2")
    btn.pack(anchor="e")
    
    # Eventos hover y click
    def on_enter(e):
        card.configure(style="CardHover.TFrame")
        btn.configure(bg="#1557b0")
        
    def on_leave(e):
        card.configure(style="Card.TFrame")
        btn.configure(bg="#1a73e8")
        
    def on_click(e):
        command()
    
    # Vincular eventos a todos los widgets
    clickable_widgets = [card, content, header, icon, title_label, desc_label]
    for widget in clickable_widgets:
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        widget.bind("<Button-1>", on_click)
    
    # Eventos del botón
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return card
