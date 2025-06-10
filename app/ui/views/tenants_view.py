"""
Vista principal del módulo de inquilinos - Diseño rediseñado
Sistema simplificado con 4 opciones principales para el administrador
"""

import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional
from app.ui.components.theme_manager import theme_manager, Spacing
from app.ui.components.icons import Icons
from app.services.tenant_service import tenant_service
from app.ui.views.tenant_form_view import TenantFormView
from app.ui.views.tenant_details_view import TenantDetailsView

class TenantsView(tk.Frame):
    """Vista principal del módulo de inquilinos con diseño simplificado"""
    
    def __init__(self, parent, on_navigate: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        
        self.on_navigate = on_navigate
        self.current_view = "dashboard"
        self.selected_tenant = None
        
        # Crear layout principal
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout principal con 4 cards centrales"""
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
            
        # Título principal
        title_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        title_frame.pack(fill="x", pady=(0, Spacing.LG))
        
        # Botón volver
        btn_back = tk.Button(
            title_frame,
            text="← Volver al Menú",
            font=("Segoe UI", 10),
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            bd=1,
            relief="solid",
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._on_back_clicked
        )
        btn_back.pack(side="left")
        
        # Título
        title_label = tk.Label(
            title_frame,
            text="Gestión de Inquilinos",
            **theme_manager.get_style("label_title")
        )
        title_label.configure(font=("Segoe UI", 18, "bold"))
        title_label.pack(side="left", padx=(Spacing.LG, 0))
        
        # Pregunta principal
        question_label = tk.Label(
            self,
            text="¿Qué deseas hacer?",
            **theme_manager.get_style("label_subtitle")
        )
        question_label.configure(font=("Segoe UI", 14))
        question_label.pack(pady=(0, Spacing.XL))
        
        # Contenedor principal centrado
        main_container = tk.Frame(self, **theme_manager.get_style("frame"))
        main_container.pack(pady=Spacing.LG)
        
        # Grid de cards 2x2 con espaciado optimizado
        self._create_cards_grid(main_container)
    
    def _create_cards_grid(self, parent):
        """Crea el grid de 4 cards principales"""
        # Centrar todo el contenido
        grid_container = tk.Frame(parent, **theme_manager.get_style("frame"))
        grid_container.pack(anchor="center")
        
        # Fila 1
        row1 = tk.Frame(grid_container, **theme_manager.get_style("frame"))
        row1.pack(pady=(0, Spacing.LG))
        
        # Card 1: Agregar Inquilino
        self._create_action_card(
            row1, 
            "➕", 
            "Agregar Inquilino",
            "Registrar un nuevo inquilino en el sistema",
            "#1e40af",  # primary blue
            lambda: self._show_tenant_form()
        ).pack(side="left", padx=(0, Spacing.LG))
        
        # Card 2: Ver Inquilinos  
        self._create_action_card(
            row1,
            "👥",
            "Ver Inquilinos", 
            "Consultar lista completa de inquilinos",
            "#3b82f6",  # info blue
            lambda: self._show_tenants_list()
        ).pack(side="left")
        
        # Fila 2
        row2 = tk.Frame(grid_container, **theme_manager.get_style("frame"))
        row2.pack()
        
        # Card 3: Editar/Eliminar
        self._create_action_card(
            row2,
            "✏️", 
            "Editar/Eliminar",
            "Modificar o eliminar inquilinos existentes",
            "#f59e0b",  # warning orange
            lambda: self._show_edit_options()
        ).pack(side="left", padx=(0, Spacing.LG))
        
        # Card 4: Reportes
        self._create_action_card(
            row2,
            "📊",
            "Reportes", 
            "Generar reportes y estadísticas",
            "#10b981",  # success green
            lambda: self._show_reports()
        ).pack(side="left")
    
    def _create_action_card(self, parent, icon, title, description, color, command):
        """Crea una card de acción con hover effects"""
        # Frame principal de la card con dimensiones optimizadas
        card_frame = tk.Frame(
            parent,
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            relief="solid",
            bd=1,
            width=280,  # Ancho reducido
            height=180   # Alto reducido
        )
        card_frame.pack_propagate(False)  # Mantener dimensiones fijas
        
        # Contenido de la card
        content_frame = tk.Frame(card_frame, bg=card_frame["bg"])
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Icono grande
        icon_label = tk.Label(
            content_frame,
            text=icon,
            font=("Segoe UI", 24),
            bg=card_frame["bg"],
            fg=color
        )
        icon_label.pack(pady=(0, Spacing.MD))
        
        # Título
        title_label = tk.Label(
            content_frame,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg=card_frame["bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_primary"]
        )
        title_label.pack()
        
        # Descripción con wrap optimizado
        desc_label = tk.Label(
            content_frame,
            text=description,
            font=("Segoe UI", 9),
            bg=card_frame["bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"],
            wraplength=240,  # Ancho de wrap ajustado
            justify="center"
        )
        desc_label.pack(pady=(Spacing.XS, 0))
        
        # Efectos hover
        def on_enter(event):
            card_frame.configure(
                bg=color,
                relief="solid",
                bd=2
            )
            content_frame.configure(bg=color)
            icon_label.configure(bg=color, fg="white")
            title_label.configure(bg=color, fg="white")
            desc_label.configure(bg=color, fg="white")
            
        def on_leave(event):
            original_bg = theme_manager.themes[theme_manager.current_theme]["bg_primary"]
            card_frame.configure(
                bg=original_bg,
                relief="solid", 
                bd=1
            )
            content_frame.configure(bg=original_bg)
            icon_label.configure(bg=original_bg, fg=color)
            title_label.configure(bg=original_bg, fg=theme_manager.themes[theme_manager.current_theme]["text_primary"])
            desc_label.configure(bg=original_bg, fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"])
        
        def on_click(event):
            command()
            
        # Bind events a todos los elementos
        for widget in [card_frame, content_frame, icon_label, title_label, desc_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)
            widget.configure(cursor="hand2")
        
        return card_frame
    
    def _show_tenant_form(self):
        """Muestra el formulario de nuevo inquilino"""
        self.current_view = "form"
        
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
            
        # Crear formulario
        form_view = TenantFormView(
            self,
            on_back=self._back_to_dashboard
        )
        form_view.pack(fill="both", expand=True)
    
    def _show_tenants_list(self):
        """Muestra la lista de inquilinos"""
        self.current_view = "list"
        
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
            
        # Header
        header_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        header_frame.pack(fill="x", pady=(0, Spacing.LG))
        
        # Botón volver
        btn_back = tk.Button(
            header_frame,
            text="← Volver",
            font=("Segoe UI", 10),
            bg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_bg"],
            fg=theme_manager.themes[theme_manager.current_theme]["btn_secondary_fg"],
            bd=1,
            relief="solid",
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._back_to_dashboard
        )
        btn_back.pack(side="left")
        
        # Título
        title_label = tk.Label(
            header_frame,
            text="Lista de Inquilinos",
            **theme_manager.get_style("label_title")
        )
        title_label.configure(font=("Segoe UI", 16, "bold"))
        title_label.pack(side="left", padx=(Spacing.LG, 0))
        
        # Contenido
        self._create_tenants_list_content()
    
    def _create_tenants_list_content(self):
        """Crea el contenido de la lista de inquilinos"""
        # Obtener inquilinos
        tenants = tenant_service.get_all_tenants()
        
        if not tenants:
            # Mensaje sin inquilinos
            empty_frame = tk.Frame(self, **theme_manager.get_style("frame"))
            empty_frame.pack(fill="both", expand=True)
            
            message_label = tk.Label(
                empty_frame,
                text="No hay inquilinos registrados",
                font=("Segoe UI", 14),
                fg=theme_manager.themes[theme_manager.current_theme]["text_secondary"]
            )
            message_label.place(relx=0.5, rely=0.5, anchor="center")
            return
            
        # Lista de inquilinos
        list_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        list_frame.pack(fill="both", expand=True, padx=Spacing.LG)
        
        # Headers
        headers_frame = tk.Frame(list_frame, **theme_manager.get_style("frame"))
        headers_frame.pack(fill="x", pady=(0, Spacing.SM))
        
        headers = ["Nombre", "Apartamento", "Teléfono", "Estado", "Acciones"]
        weights = [3, 1, 2, 1, 2]
        
        for i, (header, weight) in enumerate(zip(headers, weights)):
            label = tk.Label(
                headers_frame,
                text=header,
                **theme_manager.get_style("label_body")
            )
            label.configure(font=("Segoe UI", 11, "bold"))
            label.pack(side="left", fill="x", expand=True, padx=2)
        
        # Inquilinos
        for tenant in tenants:
            self._create_tenant_row(list_frame, tenant)
    
    def _create_tenant_row(self, parent, tenant):
        """Crea una fila de inquilino"""
        row_frame = tk.Frame(
            parent,
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"],
            relief="solid",
            bd=1
        )
        row_frame.pack(fill="x", pady=1)
        
        # Nombre
        name_label = tk.Label(
            row_frame,
            text=tenant.get("nombre", ""),
            **theme_manager.get_style("label_body")
        )
        name_label.pack(side="left", fill="x", expand=True, padx=4, anchor="w")
        
        # Apartamento
        apt_label = tk.Label(
            row_frame,
            text=tenant.get("apartamento", ""),
            **theme_manager.get_style("label_body")
        )
        apt_label.pack(side="left", padx=4)
        
        # Teléfono
        phone_label = tk.Label(
            row_frame,
            text=tenant.get("telefono", ""),
            **theme_manager.get_style("label_body")
        )
        phone_label.pack(side="left", fill="x", expand=True, padx=4)
        
        # Estado
        status_text = tenant.get("estado_pago", "al_dia")
        status_colors = {
            "al_dia": "#10b981",
            "pendiente": "#f59e0b", 
            "moroso": "#ef4444"
        }
        
        status_label = tk.Label(
            row_frame,
            text=status_text.replace("_", " ").title(),
            fg=status_colors.get(status_text, "#6b7280"),
            **theme_manager.get_style("label_body")
        )
        status_label.pack(side="left", padx=4)
        
        # Botones de acción
        actions_frame = tk.Frame(row_frame, **theme_manager.get_style("frame"))
        actions_frame.pack(side="right", padx=4)
        
        # Botón ver
        btn_view = tk.Button(
            actions_frame,
            text="Ver",
            font=("Segoe UI", 9),
            bg="#3b82f6",
            fg="white",
            bd=0,
            relief="flat",
            padx=8,
            pady=2,
            cursor="hand2",
            command=lambda: self._show_tenant_details(tenant)
        )
        btn_view.pack(side="left", padx=(0, 2))
        
        # Botón editar
        btn_edit = tk.Button(
            actions_frame,
            text="Editar",
            font=("Segoe UI", 9),
            bg="#f59e0b",
            fg="white",
            bd=0,
            relief="flat",
            padx=8,
            pady=2,
            cursor="hand2",
            command=lambda: self._edit_tenant(tenant)
        )
        btn_edit.pack(side="left")
    
    def _show_tenant_details(self, tenant):
        """Muestra los detalles de un inquilino"""
        self.current_view = "details"
        self.selected_tenant = tenant
        
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
            
        # Crear vista de detalles
        details_view = TenantDetailsView(
            self,
            tenant_data=tenant,
            on_back=self._back_to_list,
            on_edit=self._edit_tenant
        )
        details_view.pack(fill="both", expand=True)
    
    def _edit_tenant(self, tenant):
        """Edita un inquilino"""
        self.current_view = "edit"
        self.selected_tenant = tenant
        
        # Limpiar vista
        for widget in self.winfo_children():
            widget.destroy()
            
        # Crear formulario de edición
        form_view = TenantFormView(
            self,
            on_back=self._back_to_list,
            tenant_data=tenant
        )
        form_view.pack(fill="both", expand=True)
    
    def _show_edit_options(self):
        """Muestra opciones de edición/eliminación"""
        messagebox.showinfo(
            "Información",
            "Para editar o eliminar inquilinos:\n\n" +
            "1. Ve a 'Ver Inquilinos'\n" +
            "2. Busca el inquilino deseado\n" +
            "3. Usa los botones 'Ver' o 'Editar'"
        )
    
    def _show_reports(self):
        """Muestra reportes"""
        messagebox.showinfo(
            "Reportes",
            "Módulo de reportes en desarrollo.\n\n" +
            "Próximamente disponible:\n" +
            "• Reporte de ocupación\n" +
            "• Reporte de pagos\n" +
            "• Estadísticas generales"
        )
    
    def _back_to_dashboard(self):
        """Vuelve al dashboard principal"""
        self.current_view = "dashboard"
        self._create_layout()
    
    def _back_to_list(self):
        """Vuelve a la lista de inquilinos"""
        self._show_tenants_list()
    
    def _on_back_clicked(self):
        """Maneja el clic en volver al menú principal"""
        if self.on_navigate:
            self.on_navigate("dashboard")