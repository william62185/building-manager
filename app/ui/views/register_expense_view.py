import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ..components.theme_manager import theme_manager, Spacing
from ..components.icons import Icons
from manager.app.services.expense_service import ExpenseService
from manager.app.services.tenant_service import tenant_service
import shutil
import os
from datetime import datetime
from tkcalendar import DateEntry

class RegisterExpenseView(tk.Frame):
    """Vista para registrar o editar un gasto"""
    def __init__(self, parent, on_back=None, expense=None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.expense_service = ExpenseService()
        self.on_back = on_back
        self.selected_file = None
        self.expense = expense  # Nuevo: gasto a editar (o None)
        self._create_layout()

    def _create_layout(self):
        for widget in self.winfo_children():
            widget.destroy()
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG))
        btn_back = tk.Button(header, text="← Volver", command=self._on_back)
        btn_back.pack(side="left")
        title_text = "Editar Gasto" if self.expense else "Registrar Gasto"
        title = tk.Label(header, text=title_text, **theme_manager.get_style("label_title"))
        title.pack(side="left", padx=(Spacing.LG, 0))
        form = tk.Frame(self, **theme_manager.get_style("card"))
        form.pack(padx=Spacing.LG, pady=Spacing.LG, fill="x")
        # Fecha
        tk.Label(form, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", pady=4)
        self.fecha_var = tk.StringVar(value=self.expense.get("fecha") if self.expense else datetime.now().strftime("%Y-%m-%d"))
        self.fecha_entry = DateEntry(form, textvariable=self.fecha_var, date_pattern="yyyy-mm-dd", width=22)
        self.fecha_entry.grid(row=0, column=1, sticky="w", pady=4)
        # Categoría
        tk.Label(form, text="Categoría:").grid(row=1, column=0, sticky="w", pady=4)
        self.categoria_var = tk.StringVar(value=self.expense.get("categoria") if self.expense else "Servicios públicos")
        categorias = ["Servicios públicos", "Reparaciones", "Mantenimiento", "Otros"]
        categoria_combo = ttk.Combobox(form, textvariable=self.categoria_var, values=categorias, width=22, state="normal")
        categoria_combo.grid(row=1, column=1, sticky="w", pady=4)
        categoria_combo.bind('<<ComboboxSelected>>', self._on_categoria_change)
        # Apartamento
        tk.Label(form, text="Apartamento:").grid(row=3, column=0, sticky="w", pady=4)
        self.apto_combo = ttk.Combobox(form, width=22, state="normal")
        self._update_apto_combo()
        self.apto_combo.grid(row=3, column=1, sticky="w", pady=4)
        if self.expense:
            self.apto_combo.set(self.expense.get("apartamento", "---"))
        # Subtipo
        tk.Label(form, text="Subtipo:").grid(row=2, column=0, sticky="w", pady=4)
        self.subtipo_var = tk.StringVar()
        self.subtipo_combo = ttk.Combobox(form, textvariable=self.subtipo_var, width=22, state="normal")
        self._update_subtipo_combo()
        self.subtipo_combo.grid(row=2, column=1, sticky="w", pady=4)
        if self.expense:
            self.subtipo_var.set(self.expense.get("subtipo", ""))
        # Monto
        tk.Label(form, text="Monto:").grid(row=4, column=0, sticky="w", pady=4)
        self.monto_var = tk.StringVar(value=str(self.expense.get("monto")) if self.expense else "")
        tk.Entry(form, textvariable=self.monto_var, width=25).grid(row=4, column=1, sticky="w", pady=4)
        # Descripción
        tk.Label(form, text="Descripción:").grid(row=5, column=0, sticky="w", pady=4)
        self.desc_var = tk.StringVar(value=self.expense.get("descripcion") if self.expense else "")
        tk.Entry(form, textvariable=self.desc_var, width=60).grid(row=5, column=1, columnspan=2, sticky="we", pady=4)
        # Documento adjunto
        tk.Label(form, text="Documento de constancia:").grid(row=6, column=0, sticky="w", pady=4)
        doc_text = os.path.basename(self.expense.get("documento", "")) if self.expense and self.expense.get("documento") else "Ningún archivo seleccionado"
        self.doc_label = tk.Label(form, text=doc_text, fg="#1976d2" if self.expense and self.expense.get("documento") else "#888")
        self.doc_label.grid(row=6, column=1, sticky="w", pady=4)
        btn_adjuntar = tk.Button(form, text="Adjuntar archivo", command=self._adjuntar_documento)
        btn_adjuntar.grid(row=6, column=2, sticky="e", padx=4)
        # Botón guardar único
        btn_text = "Guardar cambios" if self.expense else "Registrar Gasto"
        btn_guardar = tk.Button(form, text=btn_text, command=self._guardar)
        btn_guardar.grid(row=7, column=0, columnspan=3, pady=Spacing.LG)
        # Solo mostrar lista si es modo registro
        if not self.expense:
            self.list_frame = tk.Frame(self, **theme_manager.get_style("card"))
            self.list_frame.pack(fill="both", expand=True, padx=Spacing.LG, pady=(0, Spacing.LG))
            self._display_expenses_list()
        self._on_categoria_change()

    def _on_categoria_change(self, event=None):
        categoria = self.categoria_var.get()
        subtipos = {
            "Servicios públicos": ["Energía eléctrica", "Gas domiciliario", "Acueducto y alcantarillado", "Aseo/Residuos"],
            "Reparaciones": ["Locativas", "Eléctricas", "Plomería", "Techo", "Generales apartamento"],
            "Mantenimiento": ["Ascensor", "Zonas comunes", "Jardinería"],
            "Otros": ["Honorarios administración", "Papelería y suministros", "Otros (especificar)"]
        }
        self.subtipo_combo["values"] = subtipos.get(categoria, [])
        self.subtipo_var.set(subtipos.get(categoria, [""])[0])
        # El combobox de apartamento siempre debe estar visible, así que no se oculta nunca.

    def _update_subtipo_combo(self):
        self._on_categoria_change()

    def _update_apto_combo(self):
        tenants = tenant_service.get_all_tenants()
        aptos = sorted(set(t["apartamento"] for t in tenants if t.get("apartamento")))
        aptos = ["---"] + aptos  # Opción para gasto general
        self.apto_combo["values"] = aptos
        self.apto_combo.set("---")

    def _adjuntar_documento(self):
        file_path = filedialog.askopenfilename(title="Seleccionar documento", filetypes=[("PDFs", "*.pdf"), ("Imágenes", "*.jpg;*.jpeg;*.png"), ("Todos", "*.*")])
        if file_path:
            self.selected_file = file_path
            self.doc_label.config(text=os.path.basename(file_path), fg="#1976d2")

    def _guardar(self):
        # Validaciones
        if not self.fecha_var.get():
            messagebox.showerror("Error", "Debe ingresar la fecha del gasto.")
            return
        if not self.monto_var.get():
            messagebox.showerror("Error", "Debe ingresar el monto del gasto.")
            return
        try:
            monto = float(self.monto_var.get())
            if monto <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "El monto debe ser un número positivo.")
            return
        if not self.desc_var.get():
            messagebox.showerror("Error", "Debe ingresar una descripción.")
            return
        # Guardar documento adjunto
        doc_dest = self.expense.get("documento", None) if self.expense else None
        if self.selected_file:
            docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../gastos_docs'))
            os.makedirs(docs_dir, exist_ok=True)
            doc_dest = os.path.join(docs_dir, f"gasto_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.path.basename(self.selected_file)}")
            shutil.copy2(self.selected_file, doc_dest)
        # Construir datos
        data = {
            "fecha": self.fecha_var.get(),
            "categoria": self.categoria_var.get(),
            "subtipo": self.subtipo_var.get(),
            "apartamento": self.apto_combo.get() or "---",
            "monto": monto,
            "descripcion": self.desc_var.get(),
            "documento": doc_dest
        }
        if self.expense:
            self.expense_service.update_expense(self.expense["id"], data)
            messagebox.showinfo("Éxito", "Gasto actualizado correctamente.")
            if self.on_back:
                self.on_back()
        else:
            self.expense_service.add_expense(data)
            messagebox.showinfo("Éxito", "Gasto registrado correctamente.")
            self._create_layout()

    def _display_expenses_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        expenses = self.expense_service.get_all_expenses()
        columns = [
            ("Fecha", 12),
            ("Categoría", 18),
            ("Subtipo", 20),
            ("Apartamento", 12),
            ("Monto", 14),
            ("Descripción", 32),
            ("Documento", 24)
        ]
        # --- SCROLL PROFESIONAL ---
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
            for idx in range(len(columns)):
                table_frame.grid_columnconfigure(idx, weight=1)
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

    def _on_back(self):
        if self.on_back:
            self.on_back() 