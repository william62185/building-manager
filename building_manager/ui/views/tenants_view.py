import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime
import traceback
import csv
import json

from ...models.tenant import Tenant
from ...services.tenant_service import TenantService
from ..components import DataTable, BaseForm

class TenantsView(ttk.Frame):
    """Vista para gestionar inquilinos siguiendo el estilo Material Design del dashboard."""
    def __init__(self, master: Any):
        super().__init__(master)
        self.tenant_service = TenantService()
        self.current_tenant: Optional[Tenant] = None
        self.filtered_tenants: List[Tenant] = []
        
        self._setup_ui()
        self._load_data()  # Carga inicial de datos
        self._apply_filters()  # Aplicar filtros iniciales

    def _setup_ui(self):
        """Configura la interfaz siguiendo el estilo del dashboard."""
        self.configure(padding="4")

        # HEADER CON NAVEGACIÓN - MISMO ESTILO DEL DASHBOARD
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X)
        
        # Botón de retorno con estilo del dashboard
        back_btn = ttk.Button(
            header_frame,
            text="← Dashboard",
            command=self._go_back_to_dashboard,
            bootstyle="outline-secondary"
        )
        back_btn.pack(side=tk.RIGHT)

        # GESTIÓN DE INQUILINOS - SECCIÓN PRINCIPAL
        management_section = ttk.Frame(self)
        management_section.pack(fill=tk.BOTH, expand=True)

        # BARRA DE BÚSQUEDA Y FILTROS
        search_section = ttk.Frame(management_section)
        search_section.pack(fill=tk.X, pady=(0, 8))

        # Primera fila: búsqueda
        search_row = ttk.Frame(search_section)
        search_row.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(search_row, text="Buscar:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_change)
        self.search_entry = ttk.Entry(
            search_row,
            textvariable=self.search_var,
            width=35,
            font=("Segoe UI", 10)
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 8))

        clear_btn = ttk.Button(
            search_row,
            text="Limpiar",
            command=self._clear_search,
            bootstyle="outline-secondary"
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 15))

        # Label informativo
        ttk.Label(
            search_row, 
            text="(Buscar por nombre, apartamento, documento)", 
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(side=tk.LEFT)

        # Segunda fila: filtros
        filter_row = ttk.Frame(search_section)
        filter_row.pack(fill=tk.X)

        ttk.Label(filter_row, text="Estado:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_filter = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(
            filter_row,
            textvariable=self.status_filter,
            values=["Todos", "Activo", "Pendiente", "Moroso", "Suspendido"],
            state="readonly",
            width=12
        )
        status_combo.pack(side=tk.LEFT, padx=(0, 15))
        status_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        ttk.Label(filter_row, text="Ordenar por:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        self.sort_var = tk.StringVar(value="Nombre")
        sort_combo = ttk.Combobox(
            filter_row,
            textvariable=self.sort_var,
            values=["Nombre", "Apartamento", "Renta", "Fecha Ingreso", "Estado"],
            state="readonly",
            width=15
        )
        sort_combo.pack(side=tk.LEFT)
        sort_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        # TABLA DE INQUILINOS CON ESTILO MEJORADO
        table_section = ttk.Frame(management_section)
        table_section.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        # Contador de registros con estilo
        self.records_label = ttk.Label(
            table_section, 
            text="0 inquilinos encontrados",
            font=("Segoe UI", 10, "bold"),
            bootstyle="info"
        )
        self.records_label.pack(anchor=tk.W, pady=(0, 5))

        # Tabla con diseño mejorado
        self.table = DataTable(
            table_section,
            columns=[
                ("apartment", "Apartamento", 150),
                ("name", "Nombre Completo", 250),
                ("identification", "Documento", 150),
                ("rent", "Renta", 150),
                ("status", "Estado", 150),
                ("actions", "Acciones", 120)
            ],
            on_select=self._on_select_tenant,
            on_double_click=None  # Ya no necesitamos doble clic porque tenemos botones de acción
        )
        self.table.pack(fill=tk.BOTH, expand=True)

    def _create_action_card(self, parent, text, bg_color, fg_color, command):
        """Crea un card de acción con efecto de sombra siguiendo el estilo del dashboard."""
        # Frame contenedor para el efecto de sombra con altura mínima
        shadow_frame = ttk.Frame(parent, height=70)
        shadow_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4, pady=2)
        shadow_frame.pack_propagate(False)  # Mantener altura mínima
        
        # Frame de sombra (fondo gris desplazado)
        shadow = tk.Frame(
            shadow_frame,
            bg="#cccccc",
            relief="flat"
        )
        shadow.place(x=3, y=3, relwidth=1, relheight=1)
        
        # Frame principal del botón
        button_frame = tk.Frame(
            shadow_frame,
            bg=bg_color,
            relief="raised",
            bd=1
        )
        button_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Label del texto del botón
        button_label = tk.Label(
            button_frame,
            text=text,
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            justify=tk.CENTER
        )
        button_label.pack(expand=True, fill=tk.BOTH)
        
        # Eventos de interacción
        def on_enter(event):
            # Efecto hover - oscurecer color
            darker_color = self._darken_color(bg_color)
            button_frame.configure(bg=darker_color)
            button_label.configure(bg=darker_color)
        
        def on_leave(event):
            # Restaurar color original
            button_frame.configure(bg=bg_color)
            button_label.configure(bg=bg_color)
        
        def on_click(event):
            command()
        
        # Bind eventos a ambos elementos
        for widget in [button_frame, button_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

    def _darken_color(self, color):
        """Oscurece un color para efectos hover."""
        if color == "#28a745":  # Verde
            return "#218838"
        elif color == "#007bff":  # Azul
            return "#0056b3"
        elif color == "#dc3545":  # Rojo
            return "#c82333"
        elif color == "#17a2b8":  # Cyan
            return "#138496"
        else:
            return "#555555"

    def _focus_search(self):
        """Enfoca el campo de búsqueda."""
        self.search_entry.focus_set()

    def _load_data(self):
        """Carga todos los inquilinos desde el servicio."""
        try:
            # Obtener todos los inquilinos
            self.filtered_tenants = self.tenant_service.get_all()
            # Actualizar la tabla
            self._update_table()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar inquilinos: {str(e)}")
            print(f"Error al cargar datos: {e}")

    def _update_table(self):
        """Actualiza la tabla con los datos filtrados."""
        try:
            # Actualizar contador
            self.records_label.configure(text=f"{len(self.filtered_tenants)} inquilinos encontrados")
            
            # Preparar datos para la tabla
            table_data = []
            for tenant in self.filtered_tenants:
                # Crear frame para los botones de acción
                actions_frame = ttk.Frame(self.table)
                actions_frame.configure(padding="2")
                
                # Botón de ver detalles
                details_btn = ttk.Button(
                    actions_frame,
                    text="👁️",
                    bootstyle="info-link",
                    padding=3,
                    command=lambda t=tenant: self._show_tenant_details(t)
                )
                details_btn.pack(side=tk.LEFT, padx=5)
                
                # Botón de editar
                edit_btn = ttk.Button(
                    actions_frame,
                    text="✏️",
                    bootstyle="warning-link",
                    padding=3,
                    command=lambda t=tenant: self._edit_selected({"id": t.id})
                )
                edit_btn.pack(side=tk.LEFT, padx=5)
                
                # Botón de eliminar
                delete_btn = ttk.Button(
                    actions_frame,
                    text="🗑️",
                    bootstyle="danger-link",
                    padding=3,
                    command=lambda t=tenant: self._delete_tenant(t)
                )
                delete_btn.pack(side=tk.LEFT, padx=5)

                # Preparar fila de datos
                table_data.append({
                    "apartment": tenant.apartment,
                    "name": tenant.name,
                    "identification": tenant.identification,
                    "rent": f"${tenant.rent:,.2f}" if tenant.rent else "$0.00",
                    "status": tenant.status,
                    "actions": actions_frame
                })

            # Actualizar tabla
            self.table.set_data(table_data)

        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar tabla: {str(e)}")
            print(f"Error al actualizar tabla: {e}")

    def _show_tenant_details(self, tenant):
        """Muestra los detalles completos del inquilino."""
        dialog = ttk.Toplevel(self)
        dialog.title(f"Detalles del Inquilino - {tenant.name}")
        dialog.geometry("600x400")
        dialog.transient(self)
        dialog.grab_set()

        # Contenedor principal
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Datos del inquilino
        details = [
            ("Apartamento", tenant.apartment),
            ("Nombre Completo", tenant.name),
            ("Documento", tenant.identification),
            ("Email", tenant.email or "No especificado"),
            ("Teléfono", tenant.phone or "No especificado"),
            ("Profesión", tenant.profession or "No especificada"),
            ("Renta", f"${tenant.rent:,.2f}"),
            ("Depósito", f"${tenant.deposit:,.2f}"),
            ("Fecha de Ingreso", tenant.entry_date.strftime("%d/%m/%Y")),
            ("Estado", tenant.status),
            ("Contacto de Emergencia", tenant.emergency_contact_name or "No especificado"),
            ("Teléfono de Emergencia", tenant.emergency_contact_phone or "No especificado"),
            ("Relación", tenant.emergency_contact_relation or "No especificada"),
            ("Notas", tenant.notes or "Sin notas")
        ]

        for label, value in details:
            row = ttk.Frame(main_frame)
            row.pack(fill=tk.X, pady=2)
            
            ttk.Label(
                row,
                text=f"{label}:",
                font=("Segoe UI", 10, "bold"),
                width=20,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            ttk.Label(
                row,
                text=str(value),
                font=("Segoe UI", 10),
                wraplength=400,
                justify=tk.LEFT
            ).pack(side=tk.LEFT, fill=tk.X)

        # Botón de cerrar
        ttk.Button(
            main_frame,
            text="Cerrar",
            command=dialog.destroy,
            bootstyle="secondary"
        ).pack(pady=(20, 0))

    def _delete_tenant(self, tenant):
        """Elimina un inquilino específico."""
        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar al inquilino {tenant.name}?"
        ):
            try:
                self.tenant_service.delete(tenant.id)
                self._refresh_data()
                messagebox.showinfo("Éxito", "Inquilino eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar inquilino: {str(e)}")

    def _on_search_change(self, *args):
        """Maneja cambios en la búsqueda."""
        self._apply_filters()

    def _on_filter_change(self, event=None):
        """Maneja cambios en los filtros."""
        self._apply_filters()

    def _apply_filters(self):
        """Aplica los filtros actuales a los datos."""
        try:
            # Obtener valores de filtros
            search_term = self.search_var.get().lower()
            status_filter = self.status_filter.get()
            sort_by = self.sort_var.get()

            # Obtener todos los inquilinos
            all_tenants = self.tenant_service.get_all()
            
            # Aplicar filtro de búsqueda
            filtered = []
            for tenant in all_tenants:
                searchable_fields = [
                    str(tenant.apartment).lower(),
                    tenant.name.lower(),
                    str(tenant.identification).lower()
                ]
                if any(search_term in field for field in searchable_fields):
                    filtered.append(tenant)

            # Aplicar filtro de estado
            if status_filter != "Todos":
                filtered = [t for t in filtered if t.status == status_filter]

            # Aplicar ordenamiento
            if sort_by == "Nombre":
                filtered.sort(key=lambda x: x.name.lower())
            elif sort_by == "Apartamento":
                filtered.sort(key=lambda x: x.apartment)
            elif sort_by == "Renta":
                filtered.sort(key=lambda x: x.rent or 0, reverse=True)
            elif sort_by == "Estado":
                filtered.sort(key=lambda x: x.status)

            # Actualizar lista filtrada y tabla
            self.filtered_tenants = filtered
            self._update_table()

        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar filtros: {str(e)}")
            print(f"Error al aplicar filtros: {e}")
            traceback.print_exc()

    def _clear_search(self):
        """Limpia la búsqueda y filtros."""
        self.search_var.set("")
        self.status_filter.set("Todos")
        self.sort_var.set("Nombre")
        self._apply_filters()

    def _on_select_tenant(self, data: Dict[str, Any]):
        """Maneja la selección de un inquilino."""
        self.current_tenant = data

    def _edit_selected(self, data=None):
        """Edita el inquilino seleccionado."""
        # Si se llama desde doble clic, usar los datos proporcionados
        if data and isinstance(data, dict) and "id" in data:
            tenant_id = int(data["id"])
            self.current_tenant = self.tenant_service.get_by_id(tenant_id)
        
        if not self.current_tenant:
            messagebox.showwarning("Selección", "Por favor seleccione un inquilino para editar.")
            return
        
        # Crear datos para el formulario
        tenant_data = {
            "id": self.current_tenant.id,
            "apartment": self.current_tenant.apartment,
            "name": self.current_tenant.name,
            "identification": self.current_tenant.identification,
            "phone": self.current_tenant.phone,
            "email": self.current_tenant.email,
            "rent": str(self.current_tenant.rent) if self.current_tenant.rent else "",
            "status": self.current_tenant.status,
            "entry_date": self.current_tenant.entry_date.strftime("%d/%m/%Y") if self.current_tenant.entry_date else ""
        }
        
        self._show_form(tenant_data)

    def _delete_selected(self):
        """Elimina el inquilino seleccionado."""
        if not self.current_tenant:
            messagebox.showwarning("Selección", "Por favor seleccione un inquilino para eliminar.")
            return
        
        # Confirmar eliminación
        result = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar al inquilino {self.current_tenant.name} del apartamento {self.current_tenant.apartment}?\n\nEsta acción no se puede deshacer."
        )
        
        if result:
            try:
                self.tenant_service.delete(self.current_tenant.id)
                messagebox.showinfo("Éxito", "Inquilino eliminado correctamente.")
                self.current_tenant = None
                self._refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar inquilino: {e}")

    def _refresh_data(self):
        """Actualiza los datos de la tabla."""
        self._load_data()

    def _export_data(self):
        """Exporta los datos actuales a CSV."""
        if not self.filtered_tenants:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Guardar datos de inquilinos"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Escribir encabezados
                    headers = [
                        "Apartamento", "Nombre", "Documento", "Teléfono", 
                        "Email", "Renta", "Estado", "Fecha Ingreso"
                    ]
                    writer.writerow(headers)
                    
                    # Escribir datos
                    for tenant in self.filtered_tenants:
                        row = [
                            tenant.apartment,
                            tenant.name,
                            tenant.identification,
                            tenant.phone or "",
                            tenant.email or "",
                            f"${tenant.rent:,.2f}" if tenant.rent else "",
                            tenant.status,
                            tenant.entry_date.strftime("%d/%m/%Y") if tenant.entry_date else ""
                        ]
                        writer.writerow(row)
                
                messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar datos: {e}")

    def _go_back_to_dashboard(self):
        """Vuelve al dashboard de inquilinos."""
        main_window = self.winfo_toplevel()
        if hasattr(main_window, '_show_view'):
            main_window._show_view('tenants_dashboard')

    def _show_form(self, data: Optional[Dict[str, Any]] = None):
        """Muestra el formulario para crear/editar inquilino."""
        # Crear ventana modal
        dialog = ttk.Toplevel(self)
        dialog.title("Editar Inquilino" if data else "Nuevo Inquilino")
        dialog.geometry("800x700")
        dialog.transient(self)
        dialog.grab_set()

        # Determinar el inquilino a editar
        tenant = None
        if data and "id" in data:
            tenant = self.tenant_service.get_by_id(int(data["id"]))

        # Crear formulario usando BaseForm
        form = BaseForm(
            dialog,
            on_submit=lambda values: self._handle_submit(values, dialog),
            on_cancel=dialog.destroy
        )
        
        # Si hay datos, cargarlos en el formulario
        if tenant:
            try:
                form_data = {
                    "name": tenant.name,
                    "identification": tenant.identification,
                    "email": tenant.email or "",
                    "phone": tenant.phone or "",
                    "profession": getattr(tenant, 'profession', '') or "",
                    "apartment": tenant.apartment,
                    "rent": str(tenant.rent) if tenant.rent else "",
                    "deposit": str(getattr(tenant, 'deposit', '')) if getattr(tenant, 'deposit', None) else "",
                    "entry_date": tenant.entry_date.strftime("%d/%m/%Y") if tenant.entry_date else "",
                    "status": tenant.status,
                    "emergency_contact_name": getattr(tenant, 'emergency_contact_name', '') or "",
                    "emergency_contact_phone": getattr(tenant, 'emergency_contact_phone', '') or "",
                    "emergency_contact_relation": getattr(tenant, 'emergency_contact_relation', '') or "",
                    "notes": getattr(tenant, 'notes', '') or ""
                }
                form.set_data(form_data)
            except Exception as e:
                print(f"Error al cargar datos en el formulario: {e}")
        
        form.pack(fill=tk.BOTH, expand=True)

    def _handle_submit(self, values: Dict[str, Any], dialog: ttk.Toplevel):
        """Maneja el envío del formulario."""
        try:
            # Validaciones básicas
            required_fields = ["name", "identification", "apartment", "email", "status"]
            for field in required_fields:
                if not values.get(field, "").strip():
                    messagebox.showerror("Error", f"El campo {field} es obligatorio")
                    return

            # Convertir valores numéricos
            try:
                rent = Decimal(values.get("rent", "0") or "0")
                deposit = Decimal(values.get("deposit", "0") or "0")
            except:
                messagebox.showerror("Error", "Los valores de renta y depósito deben ser números válidos")
                return

            # Convertir fecha
            try:
                entry_date_str = values.get("entry_date", "").strip()
                if entry_date_str:
                    if '/' in entry_date_str:
                        entry_date = datetime.strptime(entry_date_str, "%d/%m/%Y").date()
                    else:
                        entry_date = datetime.strptime(entry_date_str, "%Y-%m-%d").date()
                else:
                    entry_date = None
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/YYYY")
                return

            # Crear objeto Tenant
            tenant_data = {
                "id": self.current_tenant.id if self.current_tenant else None,
                "name": values["name"].strip(),
                "identification": values["identification"].strip(),
                "email": values["email"].strip(),
                "phone": values.get("phone", "").strip() or None,
                "profession": values.get("profession", "").strip() or None,
                "apartment": values["apartment"].strip(),
                "rent": rent,
                "deposit": deposit,
                "entry_date": entry_date,
                "status": values["status"],
                "emergency_contact_name": values.get("emergency_contact_name", "").strip() or None,
                "emergency_contact_phone": values.get("emergency_contact_phone", "").strip() or None,
                "emergency_contact_relation": values.get("emergency_contact_relation", "").strip() or None,
                "notes": values.get("notes", "").strip() or None
            }

            # Filtrar campos None para evitar problemas con el constructor
            tenant_data = {k: v for k, v in tenant_data.items() if v is not None or k in ['id']}
            
            tenant = Tenant(**tenant_data)

            # Guardar en la base de datos
            if self.current_tenant:
                # Actualizar inquilino existente
                success = self.tenant_service.update(self.current_tenant.id, tenant)
                if success:
                    messagebox.showinfo("Éxito", "Inquilino actualizado correctamente")
                else:
                    raise Exception("Error al actualizar el inquilino")
            else:
                # Crear nuevo inquilino
                created_tenant = self.tenant_service.create(tenant)
                if created_tenant:
                    messagebox.showinfo("Éxito", f"Inquilino registrado correctamente (ID: {created_tenant.id})")
                else:
                    raise Exception("Error al registrar el inquilino")

            # Cerrar formulario y actualizar datos
            dialog.destroy()
            self.current_tenant = None
            self._refresh_data()

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al procesar el formulario: {str(e)}")

    def refresh(self):
        """Actualiza la vista."""
        self._load_data()
        self._apply_filters() 