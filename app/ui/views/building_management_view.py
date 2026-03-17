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
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton, create_rounded_button, get_module_colors

class BuildingManagementView(tk.Frame):
    """Vista para la gestión de edificios."""

    def __init__(self, parent, on_back: Callable, main_window_ref=None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.on_back = on_back
        self.main_window_ref = main_window_ref
        self._create_layout()
        self._load_and_display_buildings()

    def _create_layout(self):
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg

        self.list_container = tk.Frame(self, bg=cb)
        self.list_container.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)

    def _load_and_display_buildings(self):
        """Carga y muestra la lista de edificios, con card para crear uno nuevo."""
        for widget in self.list_container.winfo_children():
            widget.destroy()

        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        buildings = building_service.get_all_buildings()
        has_building = bool(buildings)

        # ── Card "Crear Nuevo Edificio" ────────────────────────────────
        card_bg = "#f3e8ff" if not has_building else "#ede9fe"
        new_card = tk.Frame(self.list_container, bg=card_bg, relief="flat", bd=1)
        new_card.pack(fill="x", pady=(0, Spacing.MD), padx=Spacing.SM)

        inner = tk.Frame(new_card, bg=card_bg)
        inner.pack(fill="x", padx=Spacing.MD, pady=Spacing.MD)

        icon_color = "#7c3aed" if not has_building else "#a78bfa"
        text_color = theme["text_primary"] if not has_building else theme.get("text_secondary", "#6b7280")

        tk.Label(inner, text="🏗️  Crear Nuevo Edificio", font=("Segoe UI", 13, "bold"),
                 bg=card_bg, fg=icon_color, anchor="w").pack(side="left")

        if has_building:
            tk.Label(inner, text="(Ya existe un edificio registrado)", font=("Segoe UI", 9),
                     bg=card_bg, fg=text_color).pack(side="left", padx=(Spacing.SM, 0))
        else:
            def _go_create():
                from manager.app.ui.views.building_setup_view import BuildingSetupView
                for w in self.list_container.winfo_children():
                    w.destroy()
                setup = BuildingSetupView(self.list_container, on_back=self._load_and_display_buildings)
                setup.pack(fill="both", expand=True)

            hover_bg = "#e9d5ff"
            def _on_enter(e):
                new_card.configure(bg=hover_bg)
                inner.configure(bg=hover_bg)
                for w in inner.winfo_children():
                    w.configure(bg=hover_bg)
            def _on_leave(e):
                new_card.configure(bg=card_bg)
                inner.configure(bg=card_bg)
                for w in inner.winfo_children():
                    w.configure(bg=card_bg)

            for w in [new_card, inner] + list(inner.winfo_children()):
                w.bind("<Button-1>", lambda e: _go_create())
                w.bind("<Enter>", _on_enter)
                w.bind("<Leave>", _on_leave)
                w.configure(cursor="hand2")

        if not buildings:
            return

        for building in buildings:
            self._create_building_card(self.list_container, building)

    def _create_building_card(self, parent, building: dict):
        """Crea una tarjeta para un edificio con sus acciones y detalles."""
        theme = theme_manager.themes[theme_manager.current_theme]
        card_bg = "#f3e8ff"  # Morado claro, coherente con el módulo de administración (sin fondo blanco)
        card = tk.Frame(parent, bg=card_bg, relief="flat", bd=1)
        card.pack(fill="x", pady=(0, Spacing.MD), padx=Spacing.SM)

        main_content = tk.Frame(card, bg=card_bg)
        main_content.pack(fill="x", padx=Spacing.MD, pady=Spacing.MD)

        info_frame = tk.Frame(main_content, bg=card_bg)
        info_frame.pack(side="left", fill="x", expand=True)

        # Nombre del edificio
        building_name = building.get('name', 'Nombre no disponible')
        tk.Label(info_frame, text=f"🏢 {building_name}", font=("Segoe UI", 14, "bold"), anchor="w", bg=card_bg, fg=theme["text_primary"]).pack(fill="x")

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
                fg=theme.get("text_secondary", Colors.TEXT_SECONDARY),
                bg=card_bg,
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
            fg=theme.get("text_secondary", Colors.TEXT_SECONDARY),
            bg=card_bg,
            anchor="w"
        ).pack(fill="x", pady=(Spacing.XS, 0))

        actions_frame = tk.Frame(main_content, bg=card_bg)
        actions_frame.pack(side="right", anchor="e")

        ModernButton(
            actions_frame, 
            text="Editar Detalles", 
            icon="✏️",
            style="purple",  # Morado para mantener tonalidad morada del módulo de administración
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
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = theme.get("content_bg", theme["bg_primary"])
        dialog = tk.Toplevel(self)
        dialog.title("Editar Detalles del Edificio")
        dialog.geometry("500x450")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=cb)

        main_container = tk.Frame(dialog, bg=cb)
        main_container.pack(expand=True, fill="both", padx=Spacing.LG, pady=Spacing.LG)

        tk.Label(
            main_container, 
            text=f"Editar: {building.get('name', 'Edificio')}", 
            font=("Segoe UI", 14, "bold"),
            bg=cb,
            fg=theme["text_primary"]
        ).pack(pady=(0, Spacing.MD))

        form_frame = tk.Frame(main_container, bg=cb)
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
            row = tk.Frame(form_frame, bg=cb)
            row.pack(fill="x", pady=(0, Spacing.SM))
            
            label = tk.Label(row, text=label_text, width=18, anchor="w", bg=cb, fg=theme["text_primary"])
            label.pack(side="left", padx=(0, Spacing.SM))
            
            entry = ttk.Entry(row, textvariable=var, font=("Segoe UI", 10), width=30)
            entry.pack(side="left", fill="x", expand=True)
            
            if required:
                tk.Label(row, text="*", fg="red", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(Spacing.XS, 0))

        buttons_frame = tk.Frame(main_container, bg=cb)
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

        ModernButton(buttons_frame, text="Guardar", style="purple", command=save_and_close).pack(side="left", padx=(0, Spacing.SM))  # Morado para mantener tonalidad morada del módulo
        ModernButton(buttons_frame, text="Cancelar", style="secondary", command=dialog.destroy).pack(side="left")
        
        # Enfocar el primer campo al abrir
        dialog.after(100, lambda: form_frame.winfo_children()[0].winfo_children()[1].focus_set())

    def _create_navigation_buttons(self, parent, on_back_command):
        """Crea los botones Volver y Dashboard con estilo moderno y colores morados del módulo de administración"""
        # Colores morados para módulo de administración
        colors = get_module_colors("administración")
        purple_primary = colors["primary"]
        purple_hover = colors["hover"]
        purple_light = colors["light"]
        purple_text = colors["text"]
        
        theme = theme_manager.themes[theme_manager.current_theme]
        # Botón "Volver"
        btn_back = create_rounded_button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color=theme.get("btn_secondary_bg", "#f3f4f6"),
            fg_color=purple_primary,
            hover_bg=purple_light,
            hover_fg=purple_text,
            command=on_back_command,
            padx=16,
            pady=8,
            radius=4,
            border_color=theme.get("border_medium", "#d1d5db")
        )
        btn_back.pack(side="right", padx=(Spacing.MD, 0))
        
        # Botón "Dashboard" con icono de casita (siempre navega al dashboard)
        def go_to_dashboard():
            if self.main_window_ref and hasattr(self.main_window_ref, '_navigate_to'):
                self.main_window_ref._navigate_to("dashboard")
            else:
                # Fallback: buscar la ventana principal a través de la jerarquía
                widget = self.master
                while widget:
                    if hasattr(widget, '_navigate_to'):
                        widget._navigate_to("dashboard")
                        return
                    widget = getattr(widget, 'master', None)
        
        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=purple_primary,
            fg_color="white",
            hover_bg=purple_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_dashboard.pack(side="right")

    def _delete_building(self, building: dict):
        """Lógica para eliminar un edificio (futura implementación)."""
        # Aquí irá la comprobación de inquilinos, backup, etc.
        messagebox.showinfo("En desarrollo", "La funcionalidad para eliminar edificios se implementará próximamente con las medidas de seguridad necesarias.") 