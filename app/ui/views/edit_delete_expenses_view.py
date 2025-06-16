import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from manager.app.services.expense_service import ExpenseService
from manager.app.services.tenant_service import tenant_service
from ..components.theme_manager import theme_manager, Spacing
from ..components.icons import Icons
from datetime import datetime, timedelta
import os
import shutil

class EditDeleteExpensesView(tk.Frame):
    def __init__(self, parent, on_back=None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_back = on_back
        self.expense_service = ExpenseService()
        self._create_layout()

    def _create_layout(self):
        for widget in self.winfo_children():
            widget.destroy()
        # Botón volver y título
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(Spacing.LG, 0), padx=Spacing.LG)
        btn_back = tk.Button(header, text="← Volver", font=("Segoe UI", 11, "bold"), command=self.on_back, bg="#1976d2", fg="white", relief="flat", padx=14, pady=4)
        btn_back.pack(side="right")
        title = tk.Label(header, text="Gestión de Gastos", font=("Segoe UI", 18, "bold"), fg="#222", bg=header["bg"])
        title.pack(side="left")
        # Frame de filtros
        filtros = tk.Frame(self, **theme_manager.get_style("card"))
        filtros.pack(fill="x", padx=Spacing.LG, pady=(Spacing.MD, Spacing.MD))
        label_font = ("Segoe UI", 10, "bold")
        entry_font = ("Segoe UI", 10)
        # Apartamento
        tk.Label(filtros, text="Apartamento:", font=label_font).grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.apto_var = tk.StringVar(value="---")
        self.apto_combo = ttk.Combobox(filtros, textvariable=self.apto_var, width=14, state="normal", font=entry_font)
        self._update_apto_combo()
        self.apto_combo.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        # Categoría
        tk.Label(filtros, text="Categoría:", font=label_font).grid(row=0, column=2, sticky="w", padx=2, pady=2)
        self.categoria_var = tk.StringVar(value="---")
        categorias = ["---", "Servicios públicos", "Reparaciones", "Mantenimiento", "Otros"]
        self.categoria_combo = ttk.Combobox(filtros, textvariable=self.categoria_var, values=categorias, width=16, state="normal", font=entry_font)
        self.categoria_combo.grid(row=0, column=3, sticky="ew", padx=2, pady=2)
        self.categoria_combo.bind('<<ComboboxSelected>>', self._on_categoria_change)
        # Subtipo
        tk.Label(filtros, text="Subtipo:", font=label_font).grid(row=0, column=4, sticky="w", padx=2, pady=2)
        self.subtipo_var = tk.StringVar(value="---")
        self.subtipo_combo = ttk.Combobox(filtros, textvariable=self.subtipo_var, width=16, state="normal", font=entry_font)
        self._update_subtipo_combo()
        self.subtipo_combo.grid(row=0, column=5, sticky="ew", padx=2, pady=2)
        # Fechas
        today = datetime.now()
        first_day = today.replace(day=1)
        if today.month == 12:
            last_day = today.replace(day=31)
        else:
            next_month = today.replace(day=28) + timedelta(days=4)
            last_day = next_month - timedelta(days=next_month.day)
        tk.Label(filtros, text="Desde:", font=label_font).grid(row=1, column=0, sticky="w", padx=2, pady=2)
        self.fecha_desde = DateEntry(filtros, width=14, date_pattern="yyyy-mm-dd", font=entry_font)
        self.fecha_desde.set_date(first_day)
        self.fecha_desde.grid(row=1, column=1, sticky="ew", padx=2, pady=2)
        tk.Label(filtros, text="Hasta:", font=label_font).grid(row=1, column=2, sticky="w", padx=2, pady=2)
        self.fecha_hasta = DateEntry(filtros, width=14, date_pattern="yyyy-mm-dd", font=entry_font)
        self.fecha_hasta.set_date(last_day)
        self.fecha_hasta.grid(row=1, column=3, sticky="ew", padx=2, pady=2)
        # Botones
        btn_filtrar = tk.Button(filtros, text="Filtrar", font=label_font, bg="#388e3c", fg="white", relief="flat", padx=10, pady=2, command=self._filtrar)
        btn_filtrar.grid(row=1, column=4, sticky="ew", padx=2, pady=2)
        btn_limpiar = tk.Button(filtros, text="Limpiar", font=label_font, bg="#ff9800", fg="white", relief="flat", padx=10, pady=2, command=self._limpiar_filtros)
        btn_limpiar.grid(row=1, column=5, sticky="ew", padx=2, pady=2)
        # Expandir columnas para ocupar espacio
        for i in range(6):
            filtros.grid_columnconfigure(i, weight=1)
        # Frame de listado
        self.list_frame = tk.Frame(self, **theme_manager.get_style("card"))
        self.list_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))
        self._display_expenses_list()

    def _update_apto_combo(self):
        tenants = tenant_service.get_all_tenants()
        aptos = sorted(set(t["apartamento"] for t in tenants if t.get("apartamento")))
        aptos = ["---"] + aptos
        self.apto_combo["values"] = aptos
        self.apto_combo.set("---")

    def _on_categoria_change(self, event=None):
        categoria = self.categoria_var.get()
        subtipos = {
            "Servicios públicos": ["---", "Energía eléctrica", "Gas domiciliario", "Acueducto y alcantarillado", "Aseo/Residuos"],
            "Reparaciones": ["---", "Locativas", "Eléctricas", "Plomería", "Techo", "Generales apartamento"],
            "Mantenimiento": ["---", "Ascensor", "Zonas comunes", "Jardinería"],
            "Otros": ["---", "Honorarios administración", "Papelería y suministros", "Otros (especificar)"]
        }
        self.subtipo_combo["values"] = subtipos.get(categoria, ["---"])
        self.subtipo_var.set("---")

    def _update_subtipo_combo(self):
        self._on_categoria_change()

    def _filtrar(self):
        self._display_expenses_list()

    def _limpiar_filtros(self):
        self.apto_var.set("---")
        self.categoria_var.set("---")
        self.subtipo_var.set("---")
        # Restaurar fechas a primer y último día del mes actual
        today = datetime.now()
        first_day = today.replace(day=1)
        if today.month == 12:
            last_day = today.replace(day=31)
        else:
            next_month = today.replace(day=28) + timedelta(days=4)
            last_day = next_month - timedelta(days=next_month.day)
        self.fecha_desde.set_date(first_day)
        self.fecha_hasta.set_date(last_day)
        self._display_expenses_list()

    def _get_filtered_expenses(self):
        expenses = self.expense_service.get_all_expenses()
        # Filtros
        apto = self.apto_var.get()
        cat = self.categoria_var.get()
        sub = self.subtipo_var.get()
        f_desde = self.fecha_desde.get_date()
        f_hasta = self.fecha_hasta.get_date()
        filtered = []
        for e in expenses:
            if apto != "---" and e.get("apartamento") != apto:
                continue
            if cat != "---" and e.get("categoria") != cat:
                continue
            if sub != "---" and e.get("subtipo") != sub:
                continue
            try:
                fecha = datetime.strptime(e.get("fecha", ""), "%Y-%m-%d").date()
            except Exception:
                continue
            if fecha < f_desde or fecha > f_hasta:
                continue
            filtered.append(e)
        return filtered

    def _display_expenses_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        expenses = self._get_filtered_expenses()
        columns = [
            ("Fecha", 12),
            ("Categoría", 18),
            ("Subtipo", 20),
            ("Apartamento", 12),
            ("Monto", 14),
            ("Descripción", 32),
            ("Documento", 24),
            ("Acciones", 10)
        ]
        # Scroll profesional
        canvas = tk.Canvas(self.list_frame, borderwidth=0, highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(self.list_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        table_frame = tk.Frame(canvas)
        table_window = canvas.create_window((0, 0), window=table_frame, anchor="nw")
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        table_frame.bind("<Configure>", _on_frame_configure)
        def _on_canvas_configure(event):
            canvas.itemconfig(table_window, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)
        # Encabezado
        for idx, (col, width) in enumerate(columns):
            tk.Label(table_frame, text=col, font=("Segoe UI", 10, "bold"), width=width, anchor="w", bg="#f5f5f5").grid(row=0, column=idx, padx=(0, 1), sticky="nsew")
            table_frame.grid_columnconfigure(idx, weight=1)
        if not expenses:
            tk.Label(table_frame, text="No hay gastos registrados.", font=("Segoe UI", 11), fg="#666").grid(row=1, column=0, columnspan=len(columns), pady=10, sticky="w")
            return
        zebra_colors = ("#ffffff", "#f0f4fa")
        for row_idx, exp in enumerate(reversed(expenses), start=1):
            bg_color = zebra_colors[row_idx % 2]
            for col_idx, (key, (_, width)) in enumerate(zip([
                "fecha", "categoria", "subtipo", "apartamento", "monto", "descripcion", "documento"
            ], columns)):
                if key == "monto":
                    val = f"${exp.get('monto', 0):,.2f}"
                elif key == "documento":
                    val = os.path.basename(exp.get("documento", "")) if exp.get("documento") else "-"
                else:
                    val = exp.get(key, "") or "-"
                tk.Label(table_frame, text=val, font=("Segoe UI", 10), width=width, anchor="w", bg=bg_color).grid(row=row_idx, column=col_idx, padx=(0, 1), sticky="nsew")
            # Acciones: editar y eliminar
            actions_frame = tk.Frame(table_frame, bg=bg_color)
            actions_frame.grid(row=row_idx, column=len(columns)-1, padx=(0, 1), sticky="nsew")
            btn_edit = tk.Button(actions_frame, text=Icons.EDIT, font=("Segoe UI", 12), fg="#1976d2", bg=bg_color, bd=0, relief="flat", cursor="hand2", command=lambda e=exp: self._edit_expense(e))
            btn_edit.pack(side="left", padx=(0, 6))
            btn_delete = tk.Button(actions_frame, text=Icons.DELETE, font=("Segoe UI", 12), fg="#d32f2f", bg=bg_color, bd=0, relief="flat", cursor="hand2", command=lambda e=exp: self._delete_expense(e))
            btn_delete.pack(side="left")
            table_frame.grid_columnconfigure(len(columns)-1, weight=1)
        # Scroll con mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)
        table_frame.bind('<Enter>', _bind_mousewheel)
        table_frame.bind('<Leave>', _unbind_mousewheel)

    def _edit_expense(self, expense):
        from .register_expense_view import RegisterExpenseView
        modal = tk.Toplevel(self)
        modal.title("Editar Gasto")
        modal.transient(self)
        modal.grab_set()
        def cerrar_modal():
            modal.destroy()
            self._display_expenses_list()
        form = RegisterExpenseView(modal, on_back=cerrar_modal, expense=expense)
        form.pack(fill="both", expand=True)
        # Precargar datos en el formulario
        form.fecha_var.set(expense.get("fecha", ""))
        form.categoria_var.set(expense.get("categoria", ""))
        form._on_categoria_change()
        form.subtipo_var.set(expense.get("subtipo", ""))
        form.apto_combo.set(expense.get("apartamento", "---"))
        form.monto_var.set(str(expense.get("monto", "")))
        form.desc_var.set(expense.get("descripcion", ""))
        # Eliminar el frame de listado inferior
        if hasattr(form, 'list_frame'):
            form.list_frame.destroy()
        # Eliminar el botón 'Volver' si existe
        for child in form.winfo_children():
            if isinstance(child, tk.Frame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, tk.Button) and subchild.cget("text").startswith("← Volver"):
                        subchild.destroy()
        # Reemplazar el botón de guardar por uno que actualiza el gasto
        for child in form.winfo_children():
            if isinstance(child, tk.Button) and child.cget("text") == "Registrar Gasto":
                child.config(text="Guardar cambios", command=lambda: guardar_edicion())
        def guardar_edicion():
            # Validaciones igual que en _guardar_gasto
            if not form.fecha_var.get():
                messagebox.showerror("Error", "Debe ingresar la fecha del gasto.")
                return
            if not form.monto_var.get():
                messagebox.showerror("Error", "Debe ingresar el monto del gasto.")
                return
            try:
                monto = float(form.monto_var.get())
                if monto <= 0:
                    raise ValueError
            except Exception:
                messagebox.showerror("Error", "El monto debe ser un número positivo.")
                return
            if not form.desc_var.get():
                messagebox.showerror("Error", "Debe ingresar una descripción.")
                return
            # Guardar documento adjunto si se cambió
            doc_dest = expense.get("documento", None)
            if form.selected_file:
                docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../gastos_docs'))
                os.makedirs(docs_dir, exist_ok=True)
                doc_dest = os.path.join(docs_dir, f"gasto_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(form.selected_file)}")
                shutil.copy2(form.selected_file, doc_dest)
            # Construir datos
            data = {
                "fecha": form.fecha_var.get(),
                "categoria": form.categoria_var.get(),
                "subtipo": form.subtipo_var.get(),
                "apartamento": form.apto_combo.get() or "---",
                "monto": monto,
                "descripcion": form.desc_var.get(),
                "documento": doc_dest
            }
            self.expense_service.update_expense(expense["id"], data)
            messagebox.showinfo("Éxito", "Gasto actualizado correctamente.")
            cerrar_modal()

    def _delete_expense(self, expense):
        if messagebox.askyesno("Confirmar eliminación", "¿Seguro que deseas eliminar este gasto?"):
            self.expense_service.delete_expense(expense["id"])
            messagebox.showinfo("Eliminado", "Gasto eliminado correctamente.")
            self._display_expenses_list() 