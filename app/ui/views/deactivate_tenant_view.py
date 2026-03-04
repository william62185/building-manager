"""
Vista para desactivar inquilinos
Permite marcar un inquilino como inactivo y liberar su apartamento
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from datetime import datetime
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.tenant_autocomplete import TenantAutocompleteEntry
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
from manager.app.services.tenant_service import tenant_service
from manager.app.services.apartment_service import apartment_service

class DeactivateTenantView(tk.Frame):
    """Vista para desactivar un inquilino"""

    def __init__(self, parent, on_back: Callable = None, on_success: Callable = None, on_navigate: Callable = None, initial_tenant: Optional[dict] = None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.on_back = on_back
        self.on_success = on_success
        self.on_navigate = on_navigate
        self.selected_tenant = None
        self.current_view = "deactivate"
        self._create_layout()
        if initial_tenant:
            self._on_tenant_selected(initial_tenant)

    def _create_layout(self):
        """Crea el layout principal sin barra morada; navegación integrada en la parte superior."""
        theme = theme_manager.themes[theme_manager.current_theme]
        admin_colors = get_module_colors("administración")
        cb = self._content_bg
        fg = theme.get("text_primary", "#1f2937")
        fg_secondary = "#374151"
        # Fila superior solo con botones (sin barra morada ni texto "Administración")
        top_row = tk.Frame(self, bg=cb)
        top_row.pack(fill="x", pady=(0, Spacing.SM), padx=Spacing.MD)
        buttons_frame_main = tk.Frame(top_row, bg=cb)
        buttons_frame_main.pack(side="right")
        self._create_main_navigation_buttons(buttons_frame_main)
        header = tk.Frame(self, bg=cb)
        header.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)
        title = tk.Label(header, text="Desactivar Inquilino", font=("Segoe UI", 18, "bold"), fg=fg, bg=cb)
        title.pack(side="left")
        instructions_frame = tk.Frame(self, bg=cb)
        instructions_frame.pack(fill="x", pady=(0, Spacing.SM), padx=Spacing.MD)
        instructions = tk.Label(
            instructions_frame,
            text="Selecciona un inquilino para desactivarlo. Esto marcará su apartamento como disponible.",
            font=("Segoe UI", 11),
            fg=fg_secondary,
            bg=cb,
            wraplength=800,
            justify="left"
        )
        instructions.pack(anchor="w")
        search_frame = tk.Frame(self, bg=cb)
        search_frame.pack(fill="x", pady=(0, Spacing.MD), padx=Spacing.MD)
        tk.Label(search_frame, text="Buscar inquilino:", font=("Segoe UI", 11), fg=fg, bg=cb).pack(side="left", padx=(0, Spacing.SM))
        search_input_frame = tk.Frame(search_frame, bg=cb)
        search_input_frame.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
        
        self.tenants = tenant_service.get_all_tenants()
        self.tenant_autocomplete = TenantAutocompleteEntry(
            search_input_frame,
            self.tenants,
            on_select=self._on_tenant_selected,
            width=70,
            entry_pady=14,
            entry_font=("Segoe UI", 12),
            bg=cb,
        )
        self.tenant_autocomplete.pack(side="left", fill="x", expand=True)
        
        # Botón Limpiar con colores del módulo Administración
        admin_colors = get_module_colors("administración")
        btn_clear = tk.Button(
            search_frame,
            text=f"{Icons.CANCEL} Limpiar",
            font=("Segoe UI", 10, "bold"),
            bg=admin_colors["primary"],
            fg="white",
            activebackground=admin_colors["hover"],
            activeforeground="white",
            bd=0,
            relief="flat",
            highlightthickness=0,
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._clear_search
        )
        btn_clear.pack(side="left")
        btn_clear.bind("<Enter>", lambda e: btn_clear.configure(bg=admin_colors["hover"]))
        btn_clear.bind("<Leave>", lambda e: btn_clear.configure(bg=admin_colors["primary"]))
        # Posicionar cursor en el cuadro de búsqueda al abrir la vista
        self.after(150, self._focus_search_entry)
        
        self.info_frame = tk.Frame(self, bg=cb)
        self.info_frame.pack(fill="x", pady=(0, Spacing.MD), padx=Spacing.MD)
        self.motivo_frame = tk.Frame(self, bg=cb)
        self.motivo_frame.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)
        self.action_frame = tk.Frame(self, bg=cb)
        self.action_frame.pack(fill="x", padx=Spacing.MD, pady=Spacing.MD)
    
    def _create_main_navigation_buttons(self, parent, on_back_command=None):
        """Crea los botones de navegación del header principal (colores Administración)."""
        theme = theme_manager.themes[theme_manager.current_theme]
        # Colores del módulo Administración para botones de navegación
        admin_colors = get_module_colors("administración")
        admin_primary = admin_colors["primary"]
        admin_hover = admin_colors["hover"]
        admin_light = admin_colors["light"]
        admin_text = admin_colors["text"]

        # Botón "Dashboard"
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
            
            if self.on_back:
                self.on_back()
        
        back_command = on_back_command if on_back_command else self._on_back
        theme = theme_manager.themes[theme_manager.current_theme]
        btn_bg_sec = theme.get("btn_secondary_bg", "#e5e7eb")

        # Volver y Dashboard con el mismo formato que en Gestión de usuarios (create_rounded_button)
        btn_back = create_rounded_button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color=btn_bg_sec,
            fg_color=admin_primary,
            hover_bg=admin_light,
            hover_fg=admin_text,
            command=back_command,
            padx=16,
            pady=8,
            radius=4,
            border_color=admin_light,
        )
        btn_back.pack(side="right", padx=(Spacing.SM, 0))

        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=admin_primary,
            fg_color="white",
            hover_bg=admin_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color=admin_hover,
        )
        btn_dashboard.pack(side="right", padx=(Spacing.SM, 0))

        # Ver Inactivos a la izquierda (se empaqueta último con side="right")
        if self.current_view == "deactivate":
            btn_view_inactive = tk.Button(
                parent,
                text=f"{Icons.DELETE} Ver Inactivos",
                font=("Segoe UI", 10, "bold"),
                bg=admin_primary,
                fg="white",
                activebackground=admin_hover,
                activeforeground="white",
                bd=0,
                relief="flat",
                highlightthickness=0,
                padx=12,
                pady=5,
                cursor="hand2",
                command=self._view_inactive_tenants
            )
            btn_view_inactive.pack(side="right", padx=(Spacing.SM, 0))
            btn_view_inactive.bind("<Enter>", lambda e: btn_view_inactive.configure(bg=admin_hover))
            btn_view_inactive.bind("<Leave>", lambda e: btn_view_inactive.configure(bg=admin_primary))
    
    def _view_inactive_tenants(self):
        """Muestra la lista de inquilinos inactivos"""
        self.current_view = "inactive_list"
        # Limpiar vista actual (con verificación de que el widget existe)
        try:
            # Intentar obtener los hijos del widget
            children = self.winfo_children()
            for widget in children:
                try:
                    widget.destroy()
                except:
                    pass
        except (tk.TclError, AttributeError):
            # Si el widget ya fue destruido, simplemente continuar
            pass
        
        admin_colors = get_module_colors("administración")
        cb = self._content_bg
        fg = theme_manager.themes[theme_manager.current_theme].get("text_primary", "#1f2937")
        fg_sec = "#374151"
        top_row = tk.Frame(self, bg=cb)
        top_row.pack(fill="x", pady=(0, Spacing.SM), padx=Spacing.MD)
        buttons_frame_main = tk.Frame(top_row, bg=cb)
        buttons_frame_main.pack(side="right")
        self._create_main_navigation_buttons(buttons_frame_main, on_back_command=self._back_to_deactivate_form)
        title_frame = tk.Frame(self, bg=cb)
        title_frame.pack(fill="x", pady=(0, Spacing.SM), padx=Spacing.MD)
        title = tk.Label(title_frame, text="Inquilinos Inactivos", font=("Segoe UI", 18, "bold"), fg=fg, bg=cb)
        title.pack(side="left")
        instructions_frame = tk.Frame(self, bg=cb)
        instructions_frame.pack(fill="x", pady=(0, Spacing.MD), padx=Spacing.MD)
        instructions = tk.Label(
            instructions_frame,
            text="Lista de inquilinos desactivados. Puedes reactivarlos si es necesario.",
            font=("Segoe UI", 10),
            fg=fg_sec,
            bg=cb,
            wraplength=800,
            justify="left"
        )
        instructions.pack(anchor="w")
        search_frame = tk.Frame(self, bg=cb)
        search_frame.pack(fill="x", pady=(0, Spacing.MD), padx=Spacing.MD)
        tk.Label(search_frame, text="🔍 Buscar:", font=("Segoe UI", 10, "bold"), fg=fg, bg=cb).pack(side="left", padx=(0, Spacing.SM))
        
        self.search_var = tk.StringVar()
        self.search_placeholder = "Buscar por nombre, apartamento, teléfono..."
        self.search_entry = None  # Almacenar referencia al entry
        
        # Crear entry sin StringVar inicialmente para evitar que el placeholder active el trace
        search_entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground="#ccc",
            highlightcolor="#1976d2"
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
        self.search_entry = search_entry  # Guardar referencia
        
        # Insertar placeholder
        search_entry.insert(0, self.search_placeholder)
        search_entry.config(fg="#999")
        
        def on_search_focus_in(event):
            current_text = search_entry.get()
            if current_text == self.search_placeholder:
                search_entry.delete(0, tk.END)
                search_entry.config(fg="#000")
        
        def on_search_focus_out(event):
            current_text = search_entry.get()
            if not current_text or current_text.strip() == "":
                search_entry.delete(0, tk.END)
                search_entry.insert(0, self.search_placeholder)
                search_entry.config(fg="#999")
        
        def on_search_key_press(event):
            # Si el contenido es el placeholder, borrarlo antes de que se inserte la tecla
            if search_entry.get() == self.search_placeholder:
                search_entry.delete(0, tk.END)
                search_entry.config(fg="#000")
        
        def on_search_key_release(event):
            # Aplicar filtro directamente cuando se escribe
            # Usar after_idle para asegurar que el texto ya esté en el entry
            self.after_idle(lambda: self._apply_search_filter() if hasattr(self, 'scrollable_frame') and hasattr(self, 'all_inactive_tenants') else None)
        
        search_entry.bind("<FocusIn>", on_search_focus_in)
        search_entry.bind("<FocusOut>", on_search_focus_out)
        search_entry.bind("<KeyPress>", on_search_key_press)
        search_entry.bind("<KeyRelease>", on_search_key_release)
        
        # Configurar trace después de configurar el placeholder (como respaldo)
        self.search_var.trace_add("write", lambda *_: self._on_search_change())
        
        # Botón limpiar búsqueda (colores Administración)
        admin_colors = get_module_colors("administración")
        btn_clear_search = tk.Button(
            search_frame,
            text=f"{Icons.CANCEL} Limpiar",
            font=("Segoe UI", 9, "bold"),
            bg=admin_colors["primary"],
            fg="white",
            activebackground=admin_colors["hover"],
            activeforeground="white",
            bd=0,
            relief="flat",
            highlightthickness=0,
            padx=Spacing.SM,
            pady=4,
            cursor="hand2",
            command=self._clear_search_filter
        )
        btn_clear_search.pack(side="left")
        btn_clear_search.bind("<Enter>", lambda e: btn_clear_search.configure(bg=admin_colors["hover"]))
        btn_clear_search.bind("<Leave>", lambda e: btn_clear_search.configure(bg=admin_colors["primary"]))
        
        self.results_label = tk.Label(search_frame, text="", font=("Segoe UI", 9), fg=fg_sec, bg=cb)
        self.results_label.pack(side="right", padx=(Spacing.MD, 0))
        container = tk.Frame(self, bg=cb)
        container.pack(fill="both", expand=True, padx=Spacing.MD, pady=(0, Spacing.MD))
        self.canvas = tk.Canvas(container, bg=cb, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=cb)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configurar actualización del ancho del canvas
        def update_canvas_width(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.canvas.bind("<Configure>", update_canvas_width)
        
        # Almacenar referencia a los inquilinos inactivos para filtrado
        self.all_inactive_tenants = []
        
        # Cargar datos de inquilinos inactivos primero
        tenant_service._load_data()
        tenants = tenant_service.get_all_tenants()
        self.all_inactive_tenants = [
            t for t in tenants 
            if t.get('estado_pago') == 'inactivo'
        ]
        
        # Ahora aplicar el filtro (que mostrará los inquilinos)
        self._apply_search_filter()
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con mouse
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _load_inactive_tenants(self, parent):
        """Carga y muestra la lista de inquilinos inactivos (método legacy, ahora usa _apply_search_filter directamente)"""
        # Este método ya no se usa, pero se mantiene por compatibilidad
        # La carga de datos ahora se hace directamente en _view_inactive_tenants
        pass
    
    def _on_search_change(self):
        """Maneja cambios en el campo de búsqueda"""
        # Solo aplicar filtro si estamos en la vista de inactivos y el frame existe
        if not hasattr(self, 'current_view'):
            return
        
        # Verificar que estamos en la vista correcta
        if self.current_view != "inactive_list":
            return
        
        # Verificar que scrollable_frame existe
        if not hasattr(self, 'scrollable_frame'):
            return
        
        try:
            if self.scrollable_frame.winfo_exists():
                self._apply_search_filter()
        except (tk.TclError, AttributeError) as e:
            print(f"Error en _on_search_change: {e}")
            pass
    
    def _clear_search_filter(self):
        """Limpia el filtro de búsqueda"""
        if hasattr(self, 'search_entry') and self.search_entry:
            try:
                if self.search_entry.winfo_exists():
                    self.search_entry.delete(0, tk.END)
                    self.search_entry.insert(0, self.search_placeholder)
                    self.search_entry.config(fg="#999")
                    self.search_entry.icursor(0)  # Cursor al inicio para que al escribir se borre el placeholder
            except (tk.TclError, AttributeError):
                pass
        if hasattr(self, 'search_var'):
            self.search_var.set("")
        if hasattr(self, 'scrollable_frame') and self.current_view == "inactive_list":
            try:
                if self.scrollable_frame.winfo_exists():
                    self._apply_search_filter()
            except (tk.TclError, AttributeError):
                pass
    
    def _apply_search_filter(self):
        """Aplica el filtro de búsqueda y actualiza la lista"""
        # Verificar que scrollable_frame existe y está disponible
        if not hasattr(self, 'scrollable_frame'):
            return
        
        try:
            if not self.scrollable_frame.winfo_exists():
                return
        except (tk.TclError, AttributeError):
            return
        
        # Verificar que tenemos la lista de inquilinos cargada
        if not hasattr(self, 'all_inactive_tenants'):
            return
        
        # Limpiar lista actual
        try:
            children = self.scrollable_frame.winfo_children()
            for widget in children:
                try:
                    widget.destroy()
                except:
                    pass
        except (tk.TclError, AttributeError):
            return
        
        # Obtener término de búsqueda directamente del entry
        search_term = ""
        try:
            if hasattr(self, 'search_entry') and self.search_entry:
                if self.search_entry.winfo_exists():
                    entry_text = self.search_entry.get()
                    # Ignorar si es el placeholder o está vacío
                    if entry_text and entry_text.strip() and entry_text != self.search_placeholder:
                        search_term = entry_text.lower().strip()
        except (tk.TclError, AttributeError):
            # Si hay error, continuar sin filtro
            pass
        
        # Filtrar inquilinos
        if search_term:
            filtered_tenants = []
            for tenant in self.all_inactive_tenants:
                # Buscar en nombre
                nombre = str(tenant.get('nombre', '')).lower()
                # Buscar en apartamento
                apt_id = tenant.get('apartamento')
                apt_text = ''
                if apt_id is not None:
                    try:
                        apt_id_int = int(apt_id) if isinstance(apt_id, str) else apt_id
                        apt = apartment_service.get_apartment_by_id(apt_id_int)
                        if apt:
                            apt_number = apt.get('number', '')
                            apt_type = apt.get('unit_type', 'Apartamento Estándar')
                            if apt_type == "Apartamento Estándar":
                                apt_text = apt_number.lower()
                            else:
                                apt_text = f"{apt_type} {apt_number}".lower()
                    except:
                        apt_text = str(apt_id).lower()
                # Buscar en teléfono
                telefono = str(tenant.get('telefono', '')).lower()
                # Buscar en documento
                documento = str(tenant.get('numero_documento', '')).lower()
                
                if (search_term in nombre or 
                    search_term in apt_text or 
                    search_term in telefono or 
                    search_term in documento):
                    filtered_tenants.append(tenant)
        else:
            filtered_tenants = self.all_inactive_tenants
        
        # Actualizar contador (solo si existe)
        try:
            if hasattr(self, 'results_label') and self.results_label.winfo_exists():
                total = len(self.all_inactive_tenants)
                filtered = len(filtered_tenants)
                if search_term:
                    self.results_label.config(text=f"Mostrando {filtered} de {total} inquilinos")
                else:
                    self.results_label.config(text=f"{total} inquilino{'s' if total != 1 else ''} inactivo{'s' if total != 1 else ''}")
        except (tk.TclError, AttributeError):
            pass
        
        if not filtered_tenants:
            # Mostrar mensaje si no hay resultados
            try:
                if hasattr(self, 'scrollable_frame') and self.scrollable_frame.winfo_exists():
                    empty_label = tk.Label(
                        self.scrollable_frame,
                        text="No se encontraron inquilinos inactivos." if search_term else "No hay inquilinos inactivos.",
                        font=("Segoe UI", 11),
                        fg="#6b7280",
                        bg=self._content_bg
                    )
                    empty_label.pack(pady=Spacing.XL)
            except (tk.TclError, AttributeError):
                pass
            return
        
        # Mostrar cada inquilino inactivo filtrado
        try:
            if hasattr(self, 'scrollable_frame') and self.scrollable_frame.winfo_exists():
                for tenant in filtered_tenants:
                    self._create_inactive_tenant_card(self.scrollable_frame, tenant)
                
                # Actualizar scroll
                self.scrollable_frame.update_idletasks()
                if hasattr(self, 'canvas') and self.canvas.winfo_exists():
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except (tk.TclError, AttributeError):
            pass
    
    def _create_inactive_tenant_card(self, parent, tenant):
        """Crea una tarjeta compacta para un inquilino inactivo"""
        card_bg = "#f3e8ff"
        card_frame = tk.Frame(
            parent,
            bg=card_bg,
            relief="flat",
            bd=1,
            highlightbackground="#e9d5ff",
            highlightthickness=1
        )
        card_frame.pack(fill="x", padx=Spacing.SM, pady=2)
        content_frame = tk.Frame(card_frame, bg=card_bg)
        content_frame.pack(fill="x", padx=Spacing.SM, pady=Spacing.XS)
        info_frame = tk.Frame(content_frame, bg=card_bg)
        info_frame.pack(side="left", fill="x", expand=True)
        row1_frame = tk.Frame(info_frame, bg=card_bg)
        row1_frame.pack(fill="x", pady=(0, 2))
        name_label = tk.Label(
            row1_frame,
            text=tenant.get('nombre', 'N/A'),
            font=("Segoe UI", 11, "bold"),
            fg="#4c1d95",
            bg=card_bg,
            anchor="w"
        )
        name_label.pack(side="left", padx=(0, Spacing.MD))
        apt_id = tenant.get('apartamento')
        apt_display = 'N/A'
        if apt_id is not None:
            try:
                apt_id_int = int(apt_id) if isinstance(apt_id, str) else apt_id
                apt = apartment_service.get_apartment_by_id(apt_id_int)
                if apt:
                    apt_number = apt.get('number', 'N/A')
                    apt_type = apt.get('unit_type', 'Apartamento Estándar')
                    if apt_type == "Apartamento Estándar":
                        apt_display = f"Apto: {apt_number}"
                    else:
                        apt_display = f"{apt_type}: {apt_number}"
            except:
                apt_display = f"Apto: {apt_id}"
        apt_label = tk.Label(row1_frame, text=apt_display, font=("Segoe UI", 9), fg="#374151", bg=card_bg, anchor="w")
        apt_label.pack(side="left", padx=(0, Spacing.MD))
        phone = tenant.get('telefono', 'N/A')
        phone_label = tk.Label(row1_frame, text=f"Tel: {phone}", font=("Segoe UI", 9), fg="#374151", bg=card_bg, anchor="w")
        phone_label.pack(side="left")
        row2_frame = tk.Frame(info_frame, bg=card_bg)
        row2_frame.pack(fill="x")
        fecha_desactivacion = tenant.get('fecha_desactivacion', '')
        motivo = tenant.get('motivo_desactivacion', 'N/A')
        if fecha_desactivacion:
            try:
                fecha_dt = datetime.fromisoformat(fecha_desactivacion)
                fecha_str = fecha_dt.strftime('%d/%m/%Y')
            except:
                fecha_str = fecha_desactivacion
        else:
            fecha_str = 'N/A'
        deactivation_text = f"Desactivado: {fecha_str} | Razón: {motivo}"
        deactivation_label = tk.Label(row2_frame, text=deactivation_text, font=("Segoe UI", 9), fg="#6b7280", bg=card_bg, anchor="w")
        deactivation_label.pack(anchor="w")
        btn_frame = tk.Frame(content_frame, bg=card_bg)
        btn_frame.pack(side="right", padx=(Spacing.SM, 0))
        
        # Botón Ver Detalles (más compacto)
        btn_view_details = tk.Button(
            btn_frame,
            text=f"{Icons.TENANT_PROFILE} Detalles",
            font=("Segoe UI", 9, "bold"),
            bg="#8b5cf6",  # Morado para mantener tonalidad morada del módulo de administración
            fg="white",
            activebackground="#6d28d9",  # Morado oscuro para hover
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=Spacing.SM,
            pady=4,
            cursor="hand2",
            command=lambda: self._view_tenant_details(tenant)
        )
        btn_view_details.pack(side="left", padx=(0, 3))  # Horizontal con espacio entre botones
        
        def on_enter_view(e):
            btn_view_details.configure(bg="#6d28d9")  # Morado oscuro para hover - módulo administración
        def on_leave_view(e):
            btn_view_details.configure(bg="#8b5cf6")  # Morado para mantener tonalidad morada del módulo
        btn_view_details.bind("<Enter>", on_enter_view)
        btn_view_details.bind("<Leave>", on_leave_view)
        
        # Botón Reactivar (más compacto)
        btn_reactivate = tk.Button(
            btn_frame,
            text=f"🔄 Reactivar",
            font=("Segoe UI", 9, "bold"),
            bg="#8b5cf6",  # Morado para mantener tonalidad morada del módulo de administración
            fg="white",
            activebackground="#6d28d9",  # Morado oscuro para hover
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=Spacing.SM,
            pady=4,
            cursor="hand2",
            command=lambda: self._reactivate_tenant(tenant)
        )
        btn_reactivate.pack(side="left")  # Horizontal
        
        def on_enter_btn(e):
            btn_reactivate.configure(bg="#6d28d9")  # Morado oscuro para hover
        def on_leave_btn(e):
            btn_reactivate.configure(bg="#8b5cf6")  # Morado para mantener tonalidad morada del módulo
        btn_reactivate.bind("<Enter>", on_enter_btn)
        btn_reactivate.bind("<Leave>", on_leave_btn)
    
    def _view_tenant_details(self, tenant):
        """Muestra los detalles del inquilino en modo solo lectura"""
        from manager.app.ui.views.tenant_details_view import TenantDetailsView
        
        # Limpiar vista actual (con verificación de que el widget existe)
        try:
            children = self.winfo_children()
            for widget in children:
                try:
                    widget.destroy()
                except:
                    pass
        except (tk.TclError, AttributeError):
            pass
        
        # Crear vista de detalles en modo solo lectura (sin opción de editar)
        # Crear wrapper para on_navigate_to_dashboard que acepte argumento opcional
        def navigate_to_dashboard(view_name="dashboard"):
            if self.on_navigate:
                self.on_navigate(view_name)
        
        details_view = TenantDetailsView(
            self,
            tenant_data=tenant,
            on_back=self._view_inactive_tenants,
            on_edit=None,  # Sin opción de editar desde aquí
            on_register_payment=None,  # Sin opción de registrar pago para inactivos
            on_navigate_to_dashboard=navigate_to_dashboard,
            read_only=True  # Modo solo lectura
        )
        details_view.pack(fill="both", expand=True)
    
    def _reactivate_tenant(self, tenant):
        """Abre el formulario de reactivación para editar y reactivar el inquilino"""
        from manager.app.ui.views.tenant_form_view import TenantFormView
        
        # Limpiar vista actual (con verificación de que el widget existe)
        try:
            children = self.winfo_children()
            for widget in children:
                try:
                    widget.destroy()
                except:
                    pass
        except (tk.TclError, AttributeError):
            pass
        
        # Crear formulario en modo reactivación
        # Crear wrapper para on_navigate_to_dashboard que acepte argumento opcional
        def navigate_to_dashboard(view_name="dashboard"):
            if self.on_navigate:
                self.on_navigate(view_name)
        
        reactivate_view = TenantFormView(
            self,
            on_back=self._view_inactive_tenants,
            tenant_data=tenant,
            on_save_success=self._on_tenant_reactivated,
            on_navigate_to_dashboard=navigate_to_dashboard,
            reactivate_mode=True  # Modo especial de reactivación
        )
        reactivate_view.pack(fill="both", expand=True)
    
    def _on_tenant_reactivated(self):
        """Callback cuando se reactiva un inquilino exitosamente"""
        # Recargar la vista de inactivos
        self._view_inactive_tenants()
        
        # Llamar callback de éxito si existe
        if self.on_success:
            self.on_success()
    
    def _focus_search_entry(self):
        """Coloca el foco en el cuadro de búsqueda al abrir la vista Desactivar inquilino."""
        if hasattr(self, "tenant_autocomplete") and hasattr(self.tenant_autocomplete, "entry"):
            if self.tenant_autocomplete.entry.winfo_exists():
                self.tenant_autocomplete.entry.focus_set()
    
    def _on_tenant_selected(self, tenant):
        """Maneja la selección de un inquilino"""
        self.selected_tenant = tenant
        self._show_tenant_info()
    
    def _clear_search(self):
        """Limpia la búsqueda"""
        self.tenant_autocomplete.set_tenants(self.tenants)
        self.tenant_autocomplete.var.set("")
        self.selected_tenant = None
        
        # Limpiar información mostrada
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        for widget in self.motivo_frame.winfo_children():
            widget.destroy()
        for widget in self.action_frame.winfo_children():
            widget.destroy()
    
    def _show_tenant_info(self):
        """Muestra la información del inquilino seleccionado"""
        if not self.selected_tenant:
            return
        
        # Limpiar frames
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        for widget in self.motivo_frame.winfo_children():
            widget.destroy()
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        
        card_bg = "#f3e8ff"
        card = tk.Frame(
            self.info_frame,
            bg=card_bg,
            relief="solid",
            bd=1,
            padx=Spacing.LG,
            pady=Spacing.MD
        )
        card.pack(fill="x", pady=(0, Spacing.MD))
        row1 = tk.Frame(card, bg=card_bg)
        row1.pack(fill="x", pady=(0, Spacing.SM))
        name_label_bold = tk.Label(row1, text="Nombre:", font=("Segoe UI", 11, "bold"), fg="#1f2937", bg=card_bg)
        name_label_bold.pack(side="left", padx=(0, Spacing.XS))
        name_label = tk.Label(row1, text=self.selected_tenant.get('nombre', 'N/A'), font=("Segoe UI", 11), fg="#1f2937", bg=card_bg)
        name_label.pack(side="left", padx=(0, Spacing.LG))
        
        # Apartamento
        apt_id = self.selected_tenant.get('apartamento')
        apt_info = "N/A"
        if apt_id is not None:
            apt = apartment_service.get_apartment_by_id(apt_id)
            if apt:
                unit_type = apt.get('unit_type', 'Apartamento Estándar')
                unit_number = apt.get('number', 'N/A')
                if unit_type == "Local Comercial":
                    apt_info = f"Local: {unit_number}"
                elif unit_type == "Penthouse":
                    apt_info = f"Penthouse: {unit_number}"
                elif unit_type == "Depósito":
                    apt_info = f"Depósito: {unit_number}"
                elif unit_type == "Apartamento Estándar":
                    apt_info = f"Apto: {unit_number}"
                else:
                    apt_info = f"{unit_type}: {unit_number}"
        
        apt_label_text = tk.Label(row1, text="Apto:", font=("Segoe UI", 11), fg="#1f2937", bg=card_bg)
        apt_label_text.pack(side="left", padx=(0, Spacing.XS))
        apt_label = tk.Label(row1, text=apt_info, font=("Segoe UI", 11), fg="#1f2937", bg=card_bg)
        apt_label.pack(side="left")
        row2 = tk.Frame(card, bg=card_bg)
        row2.pack(fill="x")
        estado = self.selected_tenant.get('estado_pago', 'N/A')
        estado_text = {
            'al_dia': 'Al día',
            'moroso': 'En mora',
            'inactivo': 'Inactivo',
            'pendiente_registro': 'Pendiente Registro'
        }.get(estado, estado)
        estado_label_bold = tk.Label(row2, text="Estado:", font=("Segoe UI", 11, "bold"), fg="#1f2937", bg=card_bg)
        estado_label_bold.pack(side="left", padx=(0, Spacing.XS))
        estado_label = tk.Label(row2, text=estado_text, font=("Segoe UI", 11), fg="#1f2937", bg=card_bg)
        estado_label.pack(side="left", padx=(0, Spacing.LG))
        fecha_ingreso = self.selected_tenant.get('fecha_ingreso', '')
        if not fecha_ingreso:
            fecha_ingreso = "N/A"
        ingreso_label_text = tk.Label(row2, text="Ingreso:", font=("Segoe UI", 11), fg="#1f2937", bg=card_bg)
        ingreso_label_text.pack(side="left", padx=(0, Spacing.XS))
        ingreso_label = tk.Label(row2, text=fecha_ingreso, font=("Segoe UI", 11), fg="#1f2937", bg=card_bg)
        ingreso_label.pack(side="left")
        cb = self._content_bg
        motivo_label = tk.Label(self.motivo_frame, text="Motivo:", font=("Segoe UI", 11), fg=theme_manager.themes[theme_manager.current_theme].get("text_primary", "#1f2937"), bg=cb)
        motivo_label.pack(side="left", padx=(0, Spacing.SM))
        
        self.motivo_var = tk.StringVar()
        motivo_options = [
            "Finalización de contrato",
            "Incumplimiento de pago",
            "Mutuo acuerdo",
            "Vencimiento de contrato",
            "Otro"
        ]
        
        motivo_combo = ttk.Combobox(
            self.motivo_frame,
            textvariable=self.motivo_var,
            values=motivo_options,
            state="readonly",
            width=30,
            font=("Segoe UI", 10)
        )
        motivo_combo.pack(side="left", fill="x", expand=True)
        motivo_combo.current(0)  # Seleccionar el primero por defecto
        
        # Botones de acción
        btn_sec_bg = theme_manager.themes[theme_manager.current_theme].get("btn_secondary_bg", "#e5e7eb")
        btn_cancel = tk.Button(
            self.action_frame,
            text=f"{Icons.CANCEL} Cancelar",
            font=("Segoe UI", 11, "bold"),
            bg=btn_sec_bg,
            fg="#1f2937",
            activebackground="#d1d5db",
            activeforeground="#1f2937",
            bd=1,
            relief="solid",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._on_back
        )
        btn_cancel.pack(side="right", padx=(Spacing.SM, 0))

        def on_enter_cancel(e):
            btn_cancel.configure(bg="#d1d5db")
        def on_leave_cancel(e):
            btn_cancel.configure(bg=btn_sec_bg)
        btn_cancel.bind("<Enter>", on_enter_cancel)
        btn_cancel.bind("<Leave>", on_leave_cancel)
        
        # Botón Desactivar (rojo)
        btn_deactivate = tk.Button(
            self.action_frame,
            text=f"{Icons.DELETE} Desactivar Inquilino",
            font=("Segoe UI", 11, "bold"),
            bg="#F44336",
            fg="white",
            activebackground="#D32F2F",
            activeforeground="white",
            bd=0,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._deactivate_tenant
        )
        btn_deactivate.pack(side="right")
        
        def on_enter_deactivate(e):
            btn_deactivate.configure(bg="#D32F2F")
        def on_leave_deactivate(e):
            btn_deactivate.configure(bg="#F44336")
        btn_deactivate.bind("<Enter>", on_enter_deactivate)
        btn_deactivate.bind("<Leave>", on_leave_deactivate)
    
    def _deactivate_tenant(self):
        """Desactiva el inquilino seleccionado"""
        if not self.selected_tenant:
            messagebox.showwarning("Advertencia", "Por favor selecciona un inquilino.")
            return
        
        motivo = self.motivo_var.get()
        if not motivo:
            messagebox.showwarning("Advertencia", "Por favor selecciona un motivo de desactivación.")
            return
        
        tenant_id = self.selected_tenant.get('id')
        tenant_name = self.selected_tenant.get('nombre', 'Inquilino')
        apt_id = self.selected_tenant.get('apartamento')
        
        # Confirmar acción
        confirm = messagebox.askyesno(
            "Confirmar Desactivación",
            f"¿Estás seguro de que deseas desactivar a {tenant_name}?\n\n"
            f"Motivo: {motivo}\n\n"
            "Esto marcará el apartamento como disponible."
        )
        
        if not confirm:
            return
        
        try:
            # Actualizar estado del inquilino a inactivo
            tenant_service.update_tenant(tenant_id, {
                "estado_pago": "inactivo",
                "motivo_desactivacion": motivo,
                "fecha_desactivacion": datetime.now().isoformat()
            })
            
            # Marcar apartamento como disponible si existe
            if apt_id is not None:
                # Asegurar que apt_id sea un entero
                try:
                    apt_id_int = int(apt_id) if isinstance(apt_id, str) else apt_id
                    apt = apartment_service.get_apartment_by_id(apt_id_int)
                    if apt:
                        apartment_service.update_apartment(apt_id_int, {"status": "Disponible"})
                        print(f"✅ Apartamento {apt.get('number', apt_id_int)} marcado como Disponible")
                    else:
                        print(f"⚠️ No se encontró apartamento con ID: {apt_id_int}")
                except (ValueError, TypeError) as e:
                    print(f"⚠️ Error al procesar ID de apartamento {apt_id}: {str(e)}")
            
            messagebox.showinfo("Éxito", f"Inquilino {tenant_name} desactivado correctamente.")
            
            # Limpiar selección
            self._clear_search()
            
            # Llamar callback de éxito
            if self.on_success:
                self.on_success()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al desactivar inquilino: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _back_to_deactivate_form(self):
        """Regresa al formulario de desactivar inquilino"""
        # Actualizar estado de vista actual
        self.current_view = "deactivate"
        # Limpiar vista actual
        try:
            children = self.winfo_children()
            for widget in children:
                try:
                    widget.destroy()
                except:
                    pass
        except (tk.TclError, AttributeError):
            pass
        # Recrear el layout inicial
        self._create_layout()
    
    def _on_back(self):
        """Maneja el botón de volver"""
        if self.on_back:
            self.on_back()
