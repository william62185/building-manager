from typing import Optional, Dict, Any
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from decimal import Decimal

from ...services import TenantService
from ...models import Tenant

class TenantFormView(ttk.Frame):
    """Vista del formulario de inquilinos."""
    def __init__(self, master):
        super().__init__(master)
        self.tenant_service = TenantService()
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Contenedor principal con padding
        main_container = ttk.Frame(self, padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Título
        title = ttk.Label(
            main_container,
            text="Registro de Inquilino",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=(0, 20))

        # Formulario
        form_frame = ttk.Frame(main_container)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Campos del formulario
        fields = [
            ("name", "Nombre*:"),
            ("identification", "Identificación*:"),
            ("email", "Email*:"),
            ("phone", "Teléfono*:"),
            ("profession", "Profesión:"),
            ("apartment", "Apartamento*:"),
            ("rent", "Renta*:"),
            ("deposit", "Depósito*:"),
            ("entry_date", "Fecha de Ingreso*:"),
            ("emergency_contact_name", "Nombre Contacto Emergencia:"),
            ("emergency_contact_phone", "Teléfono Contacto Emergencia:"),
            ("emergency_contact_relation", "Relación Contacto Emergencia:"),
            ("notes", "Notas:")
        ]

        # Variables para almacenar los valores
        self.vars = {}
        
        # Crear campos
        for i, (field, label) in enumerate(fields):
            # Label
            ttk.Label(form_frame, text=label).grid(
                row=i, column=0, padx=5, pady=5, sticky="e"
            )
            
            # Entry/Text widget
            if field == "notes":
                widget = tk.Text(form_frame, height=4, width=40)
                self.vars[field] = widget
            else:
                var = tk.StringVar()
                widget = ttk.Entry(form_frame, textvariable=var)
                self.vars[field] = var
            
            widget.grid(row=i, column=1, padx=5, pady=5, sticky="ew")

        # Botones
        buttons_frame = ttk.Frame(main_container)
        buttons_frame.pack(pady=20)

        ttk.Button(
            buttons_frame,
            text="Guardar",
            command=self._save_tenant,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            buttons_frame,
            text="Cancelar",
            command=self._cancel,
            style="Secondary.TButton"
        ).pack(side=tk.LEFT, padx=5)

    def _save_tenant(self):
        """Guarda el inquilino."""
        try:
            # Validar campos requeridos
            required_fields = [
                "name", "identification", "email", "phone",
                "apartment", "rent", "deposit", "entry_date"
            ]
            
            data = {}
            for field in required_fields:
                value = self.vars[field].get() if field != "notes" else self.vars[field].get("1.0", tk.END).strip()
                if not value:
                    messagebox.showerror(
                        "Error",
                        f"El campo {field} es requerido"
                    )
                    return
                data[field] = value

            # Obtener campos opcionales
            optional_fields = [
                "profession", "emergency_contact_name",
                "emergency_contact_phone", "emergency_contact_relation",
                "notes"
            ]
            
            for field in optional_fields:
                value = self.vars[field].get() if field != "notes" else self.vars[field].get("1.0", tk.END).strip()
                if value:
                    data[field] = value

            # Convertir tipos de datos
            data["rent"] = Decimal(data["rent"])
            data["deposit"] = Decimal(data["deposit"])
            data["status"] = "active"  # Por defecto activo

            # Crear inquilino
            tenant = Tenant(**data)
            self.tenant_service.create(tenant)

            messagebox.showinfo(
                "Éxito",
                "Inquilino registrado correctamente"
            )
            self._go_back()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al guardar inquilino: {str(e)}"
            )

    def _cancel(self):
        """Cancela el registro y vuelve atrás."""
        self._go_back()

    def _go_back(self):
        """Vuelve al dashboard de inquilinos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('tenants_dashboard') 