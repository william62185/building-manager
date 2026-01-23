"""
Vista para desactivar inquilinos
Permite marcar un inquilino como inactivo y liberar su apartamento
"""
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Optional
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import ModernButton, ModernCard
from manager.app.ui.components.tenant_autocomplete import TenantAutocompleteEntry
from manager.app.services.tenant_service import tenant_service
from manager.app.services.apartment_service import apartment_service

class DeactivateTenantView(tk.Frame):
    """Vista para desactivar un inquilino"""
    
    def __init__(self, parent, on_back: Callable = None, on_success: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_back = on_back
        self.on_success = on_success
        self.selected_tenant = None
        self._create_layout()
    
    def _create_layout(self):
        """Crea el layout principal"""
        # Header
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG))
        
        btn_back = ModernButton(header, text="Volver", icon=Icons.ARROW_LEFT, 
                               style="secondary", command=self._on_back)
        btn_back.pack(side="left")
        
        title = tk.Label(header, text="Desactivar Inquilino", 
                        **theme_manager.get_style("label_title"))
        title.pack(side="left", padx=(Spacing.LG, 0))
        
        # Instrucciones
        instructions_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        instructions_frame.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.LG)
        
        instructions = tk.Label(
            instructions_frame,
            text="Selecciona un inquilino para desactivarlo. Esto marcará su apartamento como disponible.",
            **theme_manager.get_style("label_body"),
            wraplength=800,
            justify="left"
        )
        instructions.pack(anchor="w")
        
        # Buscador de inquilino
        search_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        search_frame.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.LG)
        
        label_style = theme_manager.get_style("label_body").copy()
        label_style["font"] = ("Segoe UI", 12, "bold")
        tk.Label(search_frame, text="Buscar inquilino:", **label_style).pack(side="left")
        
        self.tenants = tenant_service.get_all_tenants()
        self.tenant_autocomplete = TenantAutocompleteEntry(
            search_frame,
            self.tenants,
            on_select=self._on_tenant_selected,
            width=70
        )
        self.tenant_autocomplete.pack(side="left", padx=(Spacing.MD, 0))
        
        btn_clear = ModernButton(search_frame, text="Limpiar", icon=Icons.CANCEL, 
                                style="warning", command=self._clear_search, small=True)
        btn_clear.pack(side="left", padx=(Spacing.MD, 0))
        
        # Información del inquilino seleccionado
        self.info_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        self.info_frame.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.LG)
        
        # Botón de desactivar
        self.action_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        self.action_frame.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)
    
    def _on_tenant_selected(self, tenant):
        """Maneja la selección de un inquilino"""
        self.selected_tenant = tenant
        self._show_tenant_info()
    
    def _clear_search(self):
        """Limpia la búsqueda"""
        self.tenant_autocomplete.set_tenants(self.tenants)
        self.selected_tenant = None
        
        # Limpiar información mostrada
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        for widget in self.action_frame.winfo_children():
            widget.destroy()
    
    def _show_tenant_info(self):
        """Muestra la información del inquilino seleccionado"""
        if not self.selected_tenant:
            return
        
        # Limpiar frame de información
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        
        # Card con información del inquilino
        card = ModernCard(self.info_frame)
        card.pack(fill="x", pady=(0, Spacing.MD))
        
        info_inner = tk.Frame(card, **theme_manager.get_style("frame"))
        info_inner.pack(fill="x", padx=Spacing.LG, pady=Spacing.LG)
        
        # Nombre
        name_label = tk.Label(
            info_inner,
            text=f"Nombre: {self.selected_tenant.get('nombre', 'N/A')}",
            **theme_manager.get_style("label_title")
        )
        name_label.pack(anchor="w", pady=(0, Spacing.SM))
        
        # Apartamento
        apt_id = self.selected_tenant.get('apartamento')
        apt_info = "N/A"
        if apt_id is not None:
            apt = apartment_service.get_apartment_by_id(apt_id)
            if apt:
                apt_info = f"Apartamento: {apt.get('number', 'N/A')}"
        
        apt_label = tk.Label(
            info_inner,
            text=apt_info,
            **theme_manager.get_style("label_body")
        )
        apt_label.pack(anchor="w", pady=(0, Spacing.SM))
        
        # Estado actual
        estado = self.selected_tenant.get('estado_pago', 'N/A')
        estado_text = {
            'al_dia': 'Al día',
            'moroso': 'En mora',
            'inactivo': 'Inactivo',
            'pendiente_registro': 'Pendiente Registro'
        }.get(estado, estado)
        
        estado_label = tk.Label(
            info_inner,
            text=f"Estado actual: {estado_text}",
            **theme_manager.get_style("label_body")
        )
        estado_label.pack(anchor="w")
        
        # Botón de desactivar
        btn_deactivate = ModernButton(
            self.action_frame,
            text="Desactivar Inquilino",
            icon=Icons.DELETE,
            style="danger",
            command=self._deactivate_tenant
        )
        btn_deactivate.pack(side="left")
    
    def _deactivate_tenant(self):
        """Desactiva el inquilino seleccionado"""
        if not self.selected_tenant:
            messagebox.showwarning("Advertencia", "Por favor selecciona un inquilino.")
            return
        
        tenant_id = self.selected_tenant.get('id')
        tenant_name = self.selected_tenant.get('nombre', 'Inquilino')
        apt_id = self.selected_tenant.get('apartamento')
        
        # Confirmar acción
        confirm = messagebox.askyesno(
            "Confirmar Desactivación",
            f"¿Estás seguro de que deseas desactivar a {tenant_name}?\n\n"
            "Esto marcará el apartamento como disponible."
        )
        
        if not confirm:
            return
        
        try:
            # Actualizar estado del inquilino a inactivo
            tenant_service.update_tenant(tenant_id, {"estado_pago": "inactivo"})
            
            # Marcar apartamento como disponible si existe
            if apt_id is not None:
                apt = apartment_service.get_apartment_by_id(apt_id)
                if apt:
                    apartment_service.update_apartment(apt_id, {"status": "Disponible"})
            
            messagebox.showinfo("Éxito", f"Inquilino {tenant_name} desactivado correctamente.")
            
            # Limpiar selección
            self._clear_search()
            
            # Llamar callback de éxito
            if self.on_success:
                self.on_success()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al desactivar inquilino: {str(e)}")
    
    def _on_back(self):
        """Maneja el botón de volver"""
        if self.on_back:
            self.on_back()

