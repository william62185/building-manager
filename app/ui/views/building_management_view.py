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
        tk.Label(header, text=title_text, **theme_manager.get_style("label_title")).pack(side="left")
        ModernButton(header, text="← Volver", style="secondary", command=self.on_back).pack(side="right")

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
            text="Renombrar", 
            icon="✏️",
            style="info",
            small=True,
            command=lambda b=building: self._open_rename_dialog(b)
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

    def _open_rename_dialog(self, building: dict):
        """Abre un diálogo para renombrar un edificio."""
        dialog = tk.Toplevel(self)
        dialog.title("Renombrar Edificio")
        dialog.geometry("350x150")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=theme_manager.themes[theme_manager.current_theme]['bg_primary'])

        container = tk.Frame(dialog, **theme_manager.get_style("frame"))
        container.pack(expand=True, fill="both", padx=Spacing.LG, pady=Spacing.LG)

        tk.Label(container, text=f"Nuevo nombre para '{building.get('name')}':", **theme_manager.get_style("label_body")).pack(pady=(0, Spacing.SM))

        name_var = tk.StringVar(value=building.get('name'))
        entry = ttk.Entry(container, textvariable=name_var, font=("Segoe UI", 12))
        entry.pack(fill="x")
        entry.focus_set()

        buttons_frame = tk.Frame(container, **theme_manager.get_style("frame"))
        buttons_frame.pack(pady=Spacing.LG)

        def save_and_close():
            new_name = name_var.get().strip()
            if not new_name:
                messagebox.showerror("Error", "El nombre no puede estar vacío.", parent=dialog)
                return
            
            if building_service.update_building_name(building.get('id'), new_name):
                messagebox.showinfo("Éxito", "El edificio ha sido renombrado.", parent=self)
                self._load_and_display_buildings() # Refrescar la lista
                dialog.destroy()
            else:
                messagebox.showerror("Error", "No se pudo renombrar el edificio.", parent=dialog)

        ModernButton(buttons_frame, text="Guardar", command=save_and_close).pack(side="left")
        ModernButton(buttons_frame, text="Cancelar", style="secondary", command=dialog.destroy).pack(side="left", padx=Spacing.SM)

    def _delete_building(self, building: dict):
        """Lógica para eliminar un edificio (futura implementación)."""
        # Aquí irá la comprobación de inquilinos, backup, etc.
        messagebox.showinfo("En desarrollo", "La funcionalidad para eliminar edificios se implementará próximamente con las medidas de seguridad necesarias.") 