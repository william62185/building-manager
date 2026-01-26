"""
Vista para listar, buscar, filtrar, editar y eliminar apartamentos.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, List, Dict, Any

from manager.app.services.apartment_service import apartment_service
from manager.app.services.building_service import building_service
from manager.app.services.tenant_service import tenant_service
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import ModernButton
from .apartment_form_view import ApartmentFormView

class ApartmentsListView(tk.Frame):
    """Vista para gestionar la lista de apartamentos"""

    def __init__(self, parent, on_back: Callable, on_edit: Callable, initial_filters: Dict[str, Any] = None, on_navigate: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_back = on_back
        self.on_edit = on_edit
        self.on_navigate = on_navigate  # Callback para navegar al dashboard principal
        self.all_apartments = []
        self._scroll_area_hover_count = 0 # Para un scroll robusto
        self.canvas = None
        
        self.bind("<Destroy>", self._on_destroy) # Bind the cleanup function
        self._create_layout()
        self._load_apartments_data()

        if initial_filters:
            self.building_var.set(initial_filters.get("building", "Todos"))
            self.status_var.set(initial_filters.get("status", "Todos"))
            self.search_var.set(initial_filters.get("search", ""))
        
        self._apply_filters()

    def _create_layout(self):
        # Header
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)
        tk.Label(header, text="Listado de Apartamentos", **theme_manager.get_style("label_title")).pack(side="left")
        
        # Frame para botones de navegación (alineados a la derecha)
        buttons_frame = tk.Frame(header, **theme_manager.get_style("frame"))
        buttons_frame.pack(side="right")
        
        # Agregar botones Volver y Dashboard
        self._create_navigation_buttons(buttons_frame, self.on_back)

        # Main container
        main_container = tk.Frame(self, **theme_manager.get_style("frame"))
        main_container.pack(fill="both", expand=True, padx=Spacing.MD)

        # Search Panel
        search_panel = self._create_search_panel(main_container)
        search_panel.pack(side="left", fill="y", padx=(0, Spacing.LG))

        # List Panel
        list_container = self._create_list_panel(main_container)
        list_container.pack(side="right", fill="both", expand=True)

    def _create_search_panel(self, parent):
        panel = tk.Frame(parent, **theme_manager.get_style("card"), width=250)
        panel.pack_propagate(False)
        
        tk.Label(panel, text="🔍 Filtros", **theme_manager.get_style("label_subtitle")).pack(pady=Spacing.MD)
        
        # General Search
        tk.Label(panel, text="Búsqueda General:", **theme_manager.get_style("label_body")).pack(anchor="w", padx=Spacing.MD)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_filters())
        ttk.Entry(panel, textvariable=self.search_var, font=("Segoe UI", 10)).pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.LG))

        # Building Filter
        tk.Label(panel, text="Edificio:", **theme_manager.get_style("label_body")).pack(anchor="w", padx=Spacing.MD)
        self.building_var = tk.StringVar(value="Todos")
        self.building_combo = ttk.Combobox(panel, textvariable=self.building_var, state="readonly", font=("Segoe UI", 10))
        
        self.buildings = building_service.get_all_buildings()
        building_names = ["Todos"] + [b.get('name', f"ID {b.get('id')}") for b in self.buildings]
        self.building_combo['values'] = building_names
        
        self.building_combo.pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.LG))
        self.building_combo.bind("<<ComboboxSelected>>", self._apply_filters)

        # Status Filter
        tk.Label(panel, text="Estado:", **theme_manager.get_style("label_body")).pack(anchor="w", padx=Spacing.MD)
        self.status_var = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(panel, textvariable=self.status_var, values=["Todos", "Disponible", "Ocupado", "En Mantenimiento"], state="readonly", font=("Segoe UI", 10))
        status_combo.pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.LG))
        status_combo.bind("<<ComboboxSelected>>", self._apply_filters)

        ModernButton(panel, text="Limpiar Filtros", command=self._clear_filters).pack(pady=Spacing.LG)
        return panel

    def _create_list_panel(self, parent):
        panel = tk.Frame(parent, **theme_manager.get_style("frame"))
        
        self.canvas = tk.Canvas(panel, **theme_manager.get_style("frame"), highlightthickness=0)
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=self.canvas.yview)
        self.list_panel = tk.Frame(self.canvas, **theme_manager.get_style("frame"))
        
        self.list_panel.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        list_window = self.canvas.create_window((0, 0), window=self.list_panel, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        def _on_canvas_configure(event):
            if self.canvas:
                self.canvas.itemconfig(list_window, width=event.width)
        self.canvas.bind("<Configure>", _on_canvas_configure)

        # Bind a los widgets principales para iniciar el seguimiento
        self.canvas.bind('<Enter>', self._bind_mousewheel)
        self.canvas.bind('<Leave>', self._unbind_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return panel

    def _load_apartments_data(self):
        self.all_apartments = apartment_service.get_all_apartments()
        self._display_apartments(self.all_apartments)

    def _sort_apartments(self, apartments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ordena los apartamentos según una lógica de negocio específica."""
        def get_sort_key(apt):
            unit_type = apt.get('unit_type', 'Apartamento Estándar')
            try:
                # Tratar sótanos o pisos negativos como prioritarios
                floor = int(apt.get('floor', 0))
            except (ValueError, TypeError):
                floor = 0

            # Prioridad basada en el tipo de unidad
            type_priority = {
                "Depósito": 0,
                "Local Comercial": 1,
                "Apartamento Estándar": 2,
                "Otro": 2, # Tratar como estándar
                "Penthouse": 99 # Un número alto para mandarlos al final
            }.get(unit_type, 2)

            # Lógica para el orden principal: Penthouses al final, luego por piso, luego por tipo.
            main_sort_group = 1
            if type_priority == 99: # Es un penthouse
                main_sort_group = 2
            elif floor <= 0: # Es un sótano/depósito
                main_sort_group = 0
            
            # Para el número/letra, intentar extraer un número para un ordenamiento más intuitivo
            try:
                number_str = str(apt.get('number', '0'))
                number_val = int(''.join(filter(str.isdigit, number_str)) or 0)
            except (ValueError, TypeError):
                number_val = 0

            return (main_sort_group, floor, type_priority, number_val, number_str)

        return sorted(apartments, key=get_sort_key)

    def _display_apartments(self, apartments: List[Dict[str, Any]]):
        for widget in self.list_panel.winfo_children():
            widget.destroy()

        if not apartments:
            tk.Label(self.list_panel, text="No se encontraron apartamentos.", **theme_manager.get_style("label_body")).pack(pady=Spacing.XL)
            return

        sorted_apartments = self._sort_apartments(apartments)

        for apt in sorted_apartments:
            self._create_apartment_card(self.list_panel, apt)

    def _create_apartment_card(self, parent, apt: Dict[str, Any]):
        card = tk.Frame(parent, **theme_manager.get_style("card"))
        card.pack(fill="x", pady=(0, Spacing.MD), padx=Spacing.SM)

        content = tk.Frame(card, **theme_manager.get_style("card_content"))
        content.pack(fill="x", padx=Spacing.MD, pady=Spacing.MD)

        # Main Info
        info_frame = tk.Frame(content, **theme_manager.get_style("card_content"))
        info_frame.pack(fill="x")
        
        # Determinar el tipo de unidad para mostrar el título correcto
        unit_type = apt.get('unit_type', 'Apartamento Estándar')
        unit_number = apt.get('number', 'N/A')
        
        # Crear el título según el tipo de unidad
        if unit_type == "Local Comercial":
            title_text = f"Local: {unit_number}"
        elif unit_type == "Penthouse":
            title_text = f"Penthouse: {unit_number}"
        elif unit_type == "Depósito":
            title_text = f"Depósito: {unit_number}"
        elif unit_type == "Apartamento Estándar":
            title_text = f"Apto: {unit_number}"
        else:
            # Para tipos personalizados (como "Otro")
            title_text = f"{unit_type}: {unit_number}"
        
        tk.Label(info_frame, text=title_text, font=("Segoe UI", 14, "bold")).pack(side="left")
        
        status_colors = {"Disponible": "green", "Ocupado": "orange", "En Mantenimiento": "blue"}
        status = apt.get("status", "N/A")
        tk.Label(info_frame, text=f"● {status}", fg=status_colors.get(status, "black"), font=("Segoe UI", 10, "bold")).pack(side="right")
        
        # Details
        details_frame = tk.Frame(content, **theme_manager.get_style("card_content"))
        details_frame.pack(fill="x", pady=(Spacing.SM, 0))
        details_text = f"Piso: {apt.get('floor')} | Habitaciones: {apt.get('rooms')} | Arriendo: ${float(apt.get('base_rent', 0)):,.0f}"
        details_label = tk.Label(details_frame, text=details_text, font=("Segoe UI", 10))
        details_label.pack(anchor="w")

        tenant_label = None
        if apt.get('status') == 'Ocupado':
            # Buscar el inquilino que tiene asignado este apartamento
            apartment_id = apt.get('id')
            tenant_name = "No asignado"
            
            # Buscar inquilino por ID del apartamento
            all_tenants = tenant_service.get_all_tenants()
            for tenant in all_tenants:
                if str(tenant.get('apartamento', '')) == str(apartment_id):
                    tenant_name = tenant.get('nombre', 'No asignado')
                    break
            
            tenant_label = tk.Label(details_frame, text=f"Inquilino: {tenant_name}", font=("Segoe UI", 10, "italic"))
            tenant_label.pack(anchor="w")

        # Actions
        actions_frame = tk.Frame(content, **theme_manager.get_style("card_content"))
        actions_frame.pack(fill="x", pady=(Spacing.MD, 0))
        edit_button = ModernButton(actions_frame, text="Editar", icon="✏️", style="info", small=True, command=lambda a=apt: self.on_edit(a, self.get_filter_state()))
        edit_button.pack(side="left")
        delete_button = ModernButton(actions_frame, text="Eliminar", icon="🗑️", style="danger", small=True, command=lambda a=apt: self._delete_apartment(a))
        delete_button.pack(side="left", padx=Spacing.SM)

        # --- Bind robusto para el scroll ---
        def bind_recursive(widget):
            widget.bind('<Enter>', self._bind_mousewheel)
            widget.bind('<Leave>', self._unbind_mousewheel)
            for child in widget.winfo_children():
                bind_recursive(child)
        
        bind_recursive(card)

    def get_filter_state(self) -> Dict[str, str]:
        """Devuelve el estado actual de los filtros."""
        if hasattr(self, 'building_var'): # Asegurarse de que los widgets existen
            return {
                'building': self.building_var.get(),
                'status': self.status_var.get(),
                'search': self.search_var.get()
            }
        return {} # Devuelve vacío si los filtros aún no se han creado

    def _apply_filters(self, event=None):
        search_term = self.search_var.get().lower()
        status_filter = self.status_var.get()
        building_filter = self.building_var.get()

        filtered = self.all_apartments

        # 1. Filter by building
        if building_filter != "Todos":
            selected_building_id = None
            for building in self.buildings:
                if building.get('name') == building_filter:
                    selected_building_id = building.get('id')
                    break
            if selected_building_id is not None:
                filtered = [apt for apt in filtered if apt.get('building_id') == selected_building_id]

        # 2. Filter by status
        if status_filter != "Todos":
            filtered = [apt for apt in filtered if apt.get('status') == status_filter]

        # 3. Filter by search term
        if search_term:
            # Obtener nombres de inquilinos para cada apartamento ocupado
            all_tenants = tenant_service.get_all_tenants()
            tenant_by_apt = {}
            for tenant in all_tenants:
                apt_id = str(tenant.get('apartamento', ''))
                if apt_id:
                    tenant_by_apt[apt_id] = tenant.get('nombre', '').lower()
            
            filtered = [apt for apt in filtered if 
                        search_term in str(apt.get('number', '')).lower() or
                        search_term in str(apt.get('floor', '')).lower() or
                        search_term in tenant_by_apt.get(str(apt.get('id', '')), '').lower()]

        self._display_apartments(filtered)

    def _clear_filters(self):
        self.search_var.set("")
        self.status_var.set("Todos")
        self.building_var.set("Todos")
        self._display_apartments(self.all_apartments)
        
    def _delete_apartment(self, apt: Dict[str, Any]):
        confirm = messagebox.askyesno("Confirmar Eliminación", f"¿Seguro que deseas eliminar el apartamento {apt.get('number')}? Esta acción no se puede deshacer.")
        if confirm:
            try:
                if apt.get("status") == "Ocupado":
                    messagebox.showwarning("Acción no permitida", "No se puede eliminar un apartamento que está ocupado. Primero debe desvincular al inquilino.")
                    return
                
                apartment_service.delete_apartment(apt['id'])
                messagebox.showinfo("Éxito", "Apartamento eliminado correctamente.")
                self.refresh_data() # Refresh list
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el apartamento: {e}")

    def refresh_data(self):
        """Public method to refresh data from outside"""
        self._load_apartments_data()
        self._apply_filters()

    def _on_destroy(self, event):
        """Cleanup hook to unbind global events when the widget is destroyed."""
        # Ensure the event is for this widget itself and not a child
        if event.widget == self and self._scroll_area_hover_count > 0:
            self.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        """Handles the mousewheel event, scrolling the canvas if it exists."""
        if self.canvas and self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(self, event):
        self._scroll_area_hover_count += 1
        if self._scroll_area_hover_count == 1:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        self._scroll_area_hover_count -= 1
        if self._scroll_area_hover_count <= 0:
            self._scroll_area_hover_count = 0
            # Use unbind_all on a root widget to be safe, e.g., self
            self.unbind_all("<MouseWheel>")
    
    def _create_navigation_buttons(self, parent, on_back_command):
        """Crea los botones Volver y Dashboard con estilo consistente"""
        from manager.app.ui.components.icons import Icons
        
        theme = theme_manager.themes[theme_manager.current_theme]
        hover_bg = theme.get("bg_tertiary", theme["btn_secondary_hover"])
        
        # Configuración común para ambos botones (misma altura)
        button_config = {
            "font": ("Segoe UI", 10, "bold"),
            "bg": theme["btn_secondary_bg"],
            "fg": theme["btn_secondary_fg"],
            "activebackground": hover_bg,
            "activeforeground": theme["btn_secondary_fg"],
            "bd": 1,
            "relief": "solid",
            "padx": 12,
            "pady": 5,
            "cursor": "hand2"
        }
        
        # Botón "Volver"
        btn_back = tk.Button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            **button_config,
            command=on_back_command
        )
        btn_back.pack(side="right", padx=(Spacing.SM, 0))
        
        # Hover effect para botón "Volver"
        def on_enter_back(e):
            btn_back.configure(bg=hover_bg)
        
        def on_leave_back(e):
            btn_back.configure(bg=theme["btn_secondary_bg"])
        
        btn_back.bind("<Enter>", on_enter_back)
        btn_back.bind("<Leave>", on_leave_back)
        
        # Botón "Dashboard" con icono de casita (siempre navega al dashboard principal)
        def go_to_dashboard():
            # Prioridad 1: Usar callback directo si está disponible
            if hasattr(self, 'on_navigate') and self.on_navigate is not None:
                try:
                    self.on_navigate("dashboard")
                    return
                except Exception as e:
                    print(f"Error en callback de navegación: {e}")
            
            # Prioridad 2: Buscar desde el root window (más confiable)
            try:
                root = self.winfo_toplevel()
                # Buscar MainWindow entre los hijos del root
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
            
            # Prioridad 3: Buscar MainWindow en la jerarquía de widgets
            # Empezar desde self.master y subir hasta encontrar MainWindow
            widget = self.master
            max_depth = 15
            depth = 0
            while widget and depth < max_depth:
                # Verificar si es MainWindow (tiene _navigate_to y views_container)
                if (hasattr(widget, '_navigate_to') and 
                    hasattr(widget, '_load_view') and 
                    hasattr(widget, 'views_container')):
                    try:
                        widget._navigate_to("dashboard")
                        return
                    except Exception as e:
                        print(f"Error al navegar: {e}")
                        break
                
                # Subir en la jerarquía
                widget = getattr(widget, 'master', None)
                depth += 1
            
            # Prioridad 4: Si no se encontró MainWindow, usar on_back como fallback
            if on_back_command:
                on_back_command()
        
        btn_dashboard = tk.Button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            **button_config,
            command=go_to_dashboard
        )
        btn_dashboard.pack(side="right")
        
        # Hover effect para botón "Dashboard"
        def on_enter_dashboard(e):
            btn_dashboard.configure(bg=hover_bg)
        
        def on_leave_dashboard(e):
            btn_dashboard.configure(bg=theme["btn_secondary_bg"])
        
        btn_dashboard.bind("<Enter>", on_enter_dashboard)
        btn_dashboard.bind("<Leave>", on_leave_dashboard) 