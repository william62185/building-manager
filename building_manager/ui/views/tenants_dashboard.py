import tkinter as tk
from ttkbootstrap import ttk

class TenantsDashboard(ttk.Frame):
    """Dashboard para la gestión de inquilinos."""
    def __init__(self, master):
        super().__init__(master)
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Contenedor principal
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título del dashboard
        title = ttk.Label(
            main_container,
            text="Gestión de Inquilinos",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=(0, 20))

        # Grid de tarjetas
        cards_frame = ttk.Frame(main_container)
        cards_frame.pack(fill=tk.BOTH, expand=True)

        # Configurar grid
        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.rowconfigure(0, weight=1)

        # Tarjeta: Registrar nuevo inquilino
        register_card = ttk.Frame(cards_frame, style="Card.TFrame")
        register_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        register_title = ttk.Label(
            register_card,
            text="Registrar Nuevo Inquilino",
            font=("Helvetica", 16, "bold")
        )
        register_title.pack(pady=10)
        
        register_desc = ttk.Label(
            register_card,
            text="Registra un nuevo inquilino en el sistema",
            wraplength=200
        )
        register_desc.pack(pady=5)
        
        register_btn = ttk.Button(
            register_card,
            text="Registrar",
            command=self._register_tenant,
            style="Accent.TButton"
        )
        register_btn.pack(pady=10)

        # Tarjeta: Buscar inquilinos
        search_card = ttk.Frame(cards_frame, style="Card.TFrame")
        search_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        search_title = ttk.Label(
            search_card,
            text="Buscar Inquilinos",
            font=("Helvetica", 16, "bold")
        )
        search_title.pack(pady=10)
        
        search_desc = ttk.Label(
            search_card,
            text="Busca y gestiona inquilinos existentes",
            wraplength=200
        )
        search_desc.pack(pady=5)
        
        search_btn = ttk.Button(
            search_card,
            text="Buscar",
            command=self._search_tenants,
            style="Accent.TButton"
        )
        search_btn.pack(pady=10)

        # Botón para volver al dashboard principal
        back_btn = ttk.Button(
            main_container,
            text="Volver al Dashboard",
            command=self._go_back_to_main,
            style="Link.TButton"
        )
        back_btn.pack(pady=20)

    def _go_back_to_main(self):
        """Vuelve al dashboard principal."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('dashboard')

    def _register_tenant(self):
        """Abre directamente el formulario de registro de nuevo inquilino."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('tenant_form')

    def _search_tenants(self):
        """Navega a la vista de búsqueda de inquilinos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('tenants') 