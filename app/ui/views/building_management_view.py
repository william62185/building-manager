"""
Vista para gestionar los edificios existentes (renombrar, eliminar).
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from collections import Counter

from manager.app.services.building_service import building_service
from manager.app.services.apartment_service import apartment_service
from manager.app.ui.components.theme_manager import theme_manager, Spacing, Colors
from manager.app.ui.components.modern_widgets import ModernButton

class BuildingManagementView(tk.Frame):
    """Vista para la gestión de edificios."""

    def __init__(self, parent, on_back: Callable):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_back = on_back
        self._create_layout()
        self._load_and_display_buildings()

    def _create_layout(self):
        # Header
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)
        
        # Título dinámico según si hay edificio o no
        building_count = building_service.get_building_count()
        title_text = "Gestión del Edificio" if building_count > 0 else "Gestión de Edificios"
        tk.Label(header, text=title_text, **theme_manager.get_style("label_title")).pack(side="left", padx=(0, Spacing.LG))
        
        # Frame para botones de navegación (alineados a la derecha)
        buttons_frame = tk.Frame(header, **theme_manager.get_style("frame"))
        buttons_frame.pack(side="right")
        
        # Agregar botones Volver y Dashboard
        self._create_navigation_buttons(buttons_frame, self.on_back)

        # List container
        self.list_container = tk.Frame(self, **theme_manager.get_style("frame"))
        self.list_container.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)

    def _load_and_display_buildings(self):
        """Carga y muestra la lista de edificios."""
        for widget in self.list_container.winfo_children():
            widget.destroy()

        buildings = building_service.get_all_buildings()

        if not buildings:
            tk.Label(self.list_container, text="No hay edificios registrados.", **theme_manager.get_style("label_body")).pack(pady=Spacing.XL)
            return

        for building in buildings:
            self._create_building_card(self.list_container, building)

    def _create_building_card(self, parent, building: dict):
        """Crea una tarjeta para un edificio con sus acciones y detalles."""
        card = tk.Frame(parent, **theme_manager.get_style("card"))
        card.pack(fill="x", pady=(0, Spacing.MD), padx=Spacing.SM)

        # Contenedor principal para alinear info a la izquierda y botones a la derecha
        main_content = tk.Frame(card, **theme_manager.get_style("card_content"))
        main_content.pack(fill="x", padx=Spacing.MD, pady=Spacing.MD)

        # Frame para la información (izquierda)
        info_frame = tk.Frame(main_content, **theme_manager.get_style("card_content"))
        info_frame.pack(side="left", fill="x", expand=True)

        # Nombre del edificio
        building_name = building.get('name', 'Nombre no disponible')
        tk.Label(info_frame, text=f"🏢 {building_name}", font=("Segoe UI", 14, "bold"), anchor="w").pack(fill="x")

        # Información de ubicación (si existe)
        address = building.get('address', '')
        city = building.get('city', '')
        country = building.get('country', '')
        
        location_parts = []
        if address:
            location_parts.append(address)
        if city:
            location_parts.append(city)
        if country:
            location_parts.append(country)
        
        if location_parts:
            location_text = " | ".join(location_parts)
            tk.Label(
                info_frame,
                text=f"📍 {location_text}",
                font=("Segoe UI", 9),
                fg=Colors.GRAY_600,
                anchor="w"
            ).pack(fill="x", pady=(Spacing.XS, 0))

        # --- Detalles dinámicos del edificio ---
        building_id = building.get('id')
        all_apartments = apartment_service.get_all_apartments()
        apartments_in_building = [apt for apt in all_apartments if apt.get('building_id') == building_id]
        
        # --- Lógica de conteo corregida ---
        # Contar pisos únicos en lugar de leer un valor fijo.
        unique_floors = {apt.get('floor') for apt in apartments_in_building if apt.get('floor')}
        floor_count = len(unique_floors)
        
        type_counts = Counter(apt.get('unit_type', 'Indefinido') for apt in apartments_in_building)
        
        # Crear la cadena de detalles
        details_parts = [f"{floor_count} Pisos"]
        for unit_type, count in sorted(type_counts.items()):
            type_name = unit_type if count == 1 else f"{unit_type}s"
            if unit_type == "Apartamento Estándar": # Caso especial para pluralización
                type_name = "Apartamento Estándar" if count == 1 else "Apartamentos Estándar"
            details_parts.append(f"{count} {type_name}")

        details_text = " | ".join(details_parts)

        tk.Label(
            info_frame, 
            text=details_text, 
            font=("Segoe UI", 9), 
            fg=Colors.GRAY_600,
            anchor="w"
        ).pack(fill="x", pady=(Spacing.XS, 0))

        # Frame para botones de acción (derecha)
        actions_frame = tk.Frame(main_content, **theme_manager.get_style("card_content"))
        actions_frame.pack(side="right", anchor="e")

        ModernButton(
            actions_frame, 
            text="Editar Detalles", 
            icon="✏️",
            style="info",
            small=True,
            command=lambda b=building: self._open_edit_dialog(b)
        ).pack(side="left", padx=Spacing.SM)
        
        # En la versión profesional, no permitimos eliminar el edificio
        # ya que es el único edificio de la instalación
        # ModernButton(
        #     actions_frame, 
        #     text="Eliminar", 
        #     icon="🗑️",
        #     style="danger",
        #     small=True,
        #     command=lambda b=building: self._delete_building(b)
        # ).pack(side="left", padx=Spacing.SM)

    def _open_edit_dialog(self, building: dict):
        """Abre un diálogo completo para editar los detalles de un edificio."""
        dialog = tk.Toplevel(self)
        dialog.title("Editar Detalles del Edificio")
        dialog.geometry("500x450")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=theme_manager.themes[theme_manager.current_theme]['bg_primary'])

        # Contenedor principal con scroll si es necesario
        main_container = tk.Frame(dialog, **theme_manager.get_style("frame"))
        main_container.pack(expand=True, fill="both", padx=Spacing.LG, pady=Spacing.LG)

        # Título
        title_style = theme_manager.get_style("label_title").copy()
        title_style['font'] = ("Segoe UI", 14, "bold")
        tk.Label(
            main_container, 
            text=f"Editar: {building.get('name', 'Edificio')}", 
            **title_style
        ).pack(pady=(0, Spacing.MD))

        # Formulario
        form_frame = tk.Frame(main_container, **theme_manager.get_style("frame"))
        form_frame.pack(fill="both", expand=True)

        # Variables del formulario
        name_var = tk.StringVar(value=building.get('name', ''))
        address_var = tk.StringVar(value=building.get('address', ''))
        city_var = tk.StringVar(value=building.get('city', ''))
        country_var = tk.StringVar(value=building.get('country', ''))
        phone_var = tk.StringVar(value=building.get('phone', ''))
        email_var = tk.StringVar(value=building.get('email', ''))

        # Campos del formulario
        fields = [
            ("Nombre del Edificio:", name_var, True),
            ("Dirección:", address_var, False),
            ("Ciudad:", city_var, False),
            ("País:", country_var, False),
            ("Teléfono:", phone_var, False),
            ("Email:", email_var, False),
        ]

        for label_text, var, required in fields:
            row = tk.Frame(form_frame, **theme_manager.get_style("frame"))
            row.pack(fill="x", pady=(0, Spacing.SM))
            
            label = tk.Label(row, text=label_text, width=18, anchor="w", **theme_manager.get_style("label_body"))
            label.pack(side="left", padx=(0, Spacing.SM))
            
            entry = ttk.Entry(row, textvariable=var, font=("Segoe UI", 10), width=30)
            entry.pack(side="left", fill="x", expand=True)
            
            if required:
                tk.Label(row, text="*", fg="red", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(Spacing.XS, 0))

        # Botones
        buttons_frame = tk.Frame(main_container, **theme_manager.get_style("frame"))
        buttons_frame.pack(pady=(Spacing.MD, 0))

        def save_and_close():
            # Validar nombre (requerido)
            new_name = name_var.get().strip()
            if not new_name:
                messagebox.showerror("Error", "El nombre del edificio es obligatorio.", parent=dialog)
                return
            
            # Preparar actualizaciones
            updates = {
                'name': new_name,
                'address': address_var.get().strip(),
                'city': city_var.get().strip(),
                'country': country_var.get().strip(),
                'phone': phone_var.get().strip(),
                'email': email_var.get().strip()
            }
            
            if building_service.update_building(building.get('id'), updates):
                messagebox.showinfo("Éxito", "Los detalles del edificio han sido actualizados.", parent=self)
                self._load_and_display_buildings()  # Refrescar la lista
                dialog.destroy()
            else:
                messagebox.showerror("Error", "No se pudieron actualizar los detalles del edificio.", parent=dialog)

        ModernButton(buttons_frame, text="Guardar", command=save_and_close).pack(side="left", padx=(0, Spacing.SM))
        ModernButton(buttons_frame, text="Cancelar", style="secondary", command=dialog.destroy).pack(side="left")
        
        # Enfocar el primer campo al abrir
        dialog.after(100, lambda: form_frame.winfo_children()[0].winfo_children()[1].focus_set())

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
            # Buscar la ventana principal a través de la jerarquía
            widget = self.master
            max_depth = 10
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

    def _delete_building(self, building: dict):
        """Lógica para eliminar un edificio (futura implementación)."""
        # Aquí irá la comprobación de inquilinos, backup, etc.
        messagebox.showinfo("En desarrollo", "La funcionalidad para eliminar edificios se implementará próximamente con las medidas de seguridad necesarias.") 