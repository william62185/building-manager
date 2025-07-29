import tkinter as tk
from tkinter import ttk
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.services.apartment_service import apartment_service

class TenantAutocompleteEntry(tk.Frame):
    """Campo de búsqueda con autocomplete profesional para inquilinos"""
    def __init__(self, parent, tenants, on_select=None, width=40, placeholder="Buscar inquilino...", **kwargs):
        super().__init__(parent, **theme_manager.get_style("frame"), **kwargs)
        self.tenants = tenants
        self.on_select = on_select
        self.selected_tenant = None
        self.width = width
        self._build(placeholder)

    def _build(self, placeholder):
        self.var = tk.StringVar()
        entry_style = theme_manager.get_style("entry")
        self.entry = tk.Entry(self, textvariable=self.var, width=self.width, **entry_style)
        self.entry.pack(fill="x", padx=(0,0), pady=(0,0))
        self.entry.insert(0, placeholder)
        self.entry.configure(fg="#1976d2")
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)
        self.entry.bind("<KeyRelease>", self._on_keyrelease)
        self.entry.bind("<Down>", self._on_down)
        self.suggestions = None
        self.placeholder = placeholder

    def _clear_placeholder(self, event=None):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.configure(fg=theme_manager.themes[theme_manager.current_theme]["text_primary"])

    def _restore_placeholder(self, event=None):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.configure(fg="#1976d2")

    def _on_keyrelease(self, event=None):
        value = self.var.get().strip().lower()
        if not value or value == self.placeholder.lower():
            self._hide_suggestions()
            return
        matches = self._search_tenants(value)
        if matches:
            self._show_suggestions(matches)
        else:
            self._hide_suggestions()

    def _search_tenants(self, value):
        results = []
        for t in self.tenants:
            # Buscar por número real de apartamento
            apt_number = None
            apt_id = t.get("apartamento")
            if apt_id is not None:
                try:
                    apt = apartment_service.get_apartment_by_id(int(apt_id))
                    if apt and 'number' in apt:
                        apt_number = str(apt['number']).lower()
                except Exception:
                    pass
            if (
                value in str(t.get("nombre") or "").lower() or
                value in str(t.get("numero_documento") or "").lower() or
                value in str(t.get("apartamento") or "").lower() or
                value in str(t.get("email") or "").lower() or
                value in str(t.get("telefono") or "").lower() or
                (apt_number and value in apt_number)
            ):
                results.append(t)
        return results[:10]  # Máximo 10 sugerencias

    def _show_suggestions(self, matches):
        if self.suggestions:
            self.suggestions.destroy()
        self.suggestions = tk.Toplevel(self)
        self.suggestions.wm_overrideredirect(True)
        self.suggestions.configure(bg="#e3f2fd", bd=2, highlightbackground="#1976d2", highlightcolor="#1976d2")
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        self.suggestions.wm_geometry(f"{self.entry.winfo_width()}x{min(220, 22*len(matches))}+{x}+{y}")
        for i, t in enumerate(matches):
            apt_number = self._get_apartment_number(t)
            valor = t.get('valor_arriendo', 0)
            try:
                valor = float(valor)
            except Exception:
                valor = 0
            text = f"{t['nombre']} | Apt. {apt_number} | CC: {t['numero_documento']} | Día pago: {self._get_dia_pago(t)} | ${valor:,.0f}"
            label = tk.Label(self.suggestions, text=text, anchor="w", bg="#e3f2fd", fg="#1976d2", font=("Segoe UI", 10), padx=8, pady=2)
            label.pack(fill="x")
            label.bind("<Button-1>", lambda e, tenant=t: self._select_tenant(tenant))
            label.bind("<Enter>", lambda e, l=label: l.configure(bg="#1976d2", fg="white"))
            label.bind("<Leave>", lambda e, l=label: l.configure(bg="#e3f2fd", fg="#1976d2"))
        self.suggestions.lift()
        self.suggestions.update_idletasks()

    def _hide_suggestions(self):
        if self.suggestions:
            self.suggestions.destroy()
            self.suggestions = None

    def _on_down(self, event=None):
        if self.suggestions:
            self.suggestions.focus_set()

    def _select_tenant(self, tenant):
        self.selected_tenant = tenant
        apt_number = self._get_apartment_number(tenant)
        valor = tenant.get('valor_arriendo', 0)
        try:
            valor = float(valor)
        except Exception:
            valor = 0
        text = f"{tenant['nombre']} | Apt. {apt_number} | CC: {tenant['numero_documento']} | Día pago: {self._get_dia_pago(tenant)} | ${valor:,.0f}"
        self.var.set(text)
        self._hide_suggestions()
        if self.on_select:
            self.on_select(tenant)

    def _get_dia_pago(self, tenant):
        fecha = tenant.get('fecha_ingreso', '')
        try:
            return int(fecha.split('/')[0])
        except:
            return "-"

    def _get_apartment_number(self, tenant):
        apt_id = tenant.get('apartamento')
        if apt_id is not None:
            try:
                apt = apartment_service.get_apartment_by_id(int(apt_id))
                if apt and 'number' in apt:
                    return apt['number']
            except Exception:
                pass
        return apt_id if apt_id is not None else 'N/A'

    def get_selected_tenant(self):
        return self.selected_tenant

    def set_tenants(self, tenants):
        self.tenants = tenants
        self.selected_tenant = None
        self.var.set("") 