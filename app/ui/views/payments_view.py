"""
Vista hub principal del módulo de Ingresos (Pagos).
Layout: barra de tabs anclada + panel de contenido.
Lazy load: cada sub-vista se instancia la primera vez que se selecciona su tab.

Tabs:
  - Editar / Eliminar  → EditDeletePaymentsView
  - Registrar ingreso  → _RegisterPaymentTab (inline)
  - Reportes           → PaymentReportsView
"""
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

if sys.platform == "win32":
    import winsound

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import (
    create_rounded_button, get_module_colors,
    ModernButton, bind_combobox_dropdown_on_click,
)
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.tenant_autocomplete import TenantAutocompleteEntry
from manager.app.services.payment_service import payment_service
from manager.app.services.tenant_service import tenant_service
from manager.app.services.apartment_service import apartment_service
from manager.app.services.building_service import building_service
from manager.app.ui.views.register_expense_view import DatePickerWidget
from manager.app.logger import logger

_TABS = [
    ("editar",    "✏️",  "Editar / Eliminar"),
    ("registrar", "➕", "Registrar ingreso"),
    ("reportes",  "📊", "Reportes"),
]

_MODULE         = "pagos"
_TAB_BAR_BG     = "#e8ecf0"
_TAB_BAR_BORDER = "#c5cdd6"


class PaymentsView(tk.Frame):
    """Hub principal del módulo de Ingresos con tabs de navegación."""

    def __init__(self, parent, on_back=None, preselected_tenant=None, on_payment_saved=None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._bg)
        self.on_back = on_back
        self.on_payment_saved = on_payment_saved
        self.preselected_tenant = preselected_tenant

        self._active_tab = None
        self._tab_buttons = {}
        self._loaded_views = {}

        self._build_layout()
        self.after(0, lambda: self._select_tab("editar"))

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self):
        colors = get_module_colors(_MODULE)
        theme = theme_manager.themes[theme_manager.current_theme]

        # ── Barra de tabs con borde inferior ──────────────────────────
        tab_bar_outer = tk.Frame(self, bg=_TAB_BAR_BORDER)
        tab_bar_outer.pack(fill="x")

        self._tab_bar = tk.Frame(tab_bar_outer, bg=_TAB_BAR_BG)
        self._tab_bar.pack(fill="x", side="top", pady=(0, 1))

        tabs_left = tk.Frame(self._tab_bar, bg=_TAB_BAR_BG)
        tabs_left.pack(side="left", fill="y")

        for key, icon, label in _TABS:
            self._create_tab_button(tabs_left, key, icon, label)

        # Botones Volver + Inicio a la derecha
        btns_right = tk.Frame(self._tab_bar, bg=_TAB_BAR_BG)
        btns_right.pack(side="right", padx=Spacing.SM, pady=Spacing.XS)

        btn_inicio = create_rounded_button(
            btns_right,
            text="🏠 Inicio",
            bg_color=colors["primary"],
            fg_color="white",
            hover_bg=colors["hover"],
            hover_fg="white",
            command=self._go_to_dashboard,
            padx=14,
            pady=7,
            radius=4,
            border_color="#000000",
        )
        btn_inicio.pack(side="right", padx=(4, 0))

        btn_volver = create_rounded_button(
            btns_right,
            text="← Volver",
            bg_color=theme.get("btn_secondary_bg", "#e5e7eb"),
            fg_color=colors["primary"],
            hover_bg=colors["light"],
            hover_fg=colors["primary"],
            command=self._on_volver,
            padx=14,
            pady=7,
            radius=4,
            border_color=colors["light"],
        )
        btn_volver.pack(side="right")

        # ── Panel de contenido ─────────────────────────────────────────
        self._content_panel = tk.Frame(self, bg=self._bg)
        self._content_panel.pack(fill="both", expand=True, padx=Spacing.XS, pady=0)

    # ------------------------------------------------------------------
    # Tabs
    # ------------------------------------------------------------------

    def _create_tab_button(self, parent, key, icon, label):
        colors = get_module_colors(_MODULE)
        theme = theme_manager.themes[theme_manager.current_theme]

        btn = tk.Button(
            parent,
            text=f"{icon}  {label}",
            font=("Segoe UI", 12),
            bg=_TAB_BAR_BG,
            fg=theme["text_primary"],
            activebackground=colors["light"],
            activeforeground=theme["text_primary"],
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            command=lambda k=key: self._select_tab(k),
        )
        btn.pack(side="left")
        btn.bind("<Enter>", lambda e, b=btn, k=key: self._on_tab_enter(b, k))
        btn.bind("<Leave>", lambda e, b=btn, k=key: self._on_tab_leave(b, k))
        self._tab_buttons[key] = btn

    def _on_tab_enter(self, btn, key):
        if key == self._active_tab:
            return
        btn.config(bg=get_module_colors(_MODULE)["light"])

    def _on_tab_leave(self, btn, key):
        if key == self._active_tab:
            return
        btn.config(bg=_TAB_BAR_BG)

    def _select_tab(self, key):
        colors = get_module_colors(_MODULE)
        theme = theme_manager.themes[theme_manager.current_theme]

        for k, btn in self._tab_buttons.items():
            if k == key:
                btn.config(
                    bg=colors["primary"],
                    fg="white",
                    font=("Segoe UI", 12, "bold"),
                    activebackground=colors["primary"],
                    activeforeground="white",
                )
            else:
                btn.config(
                    bg=_TAB_BAR_BG,
                    fg=theme["text_primary"],
                    font=("Segoe UI", 12),
                    activebackground=colors["light"],
                    activeforeground=theme["text_primary"],
                )

        self._active_tab = key

        for child in self._content_panel.winfo_children():
            child.pack_forget()

        if key not in self._loaded_views:
            try:
                view = self._build_tab_view(key)
                if view:
                    self._loaded_views[key] = view
            except Exception as exc:
                logger.exception("Error al cargar tab '%s': %s", key, exc)
                return

        view = self._loaded_views.get(key)
        if view:
            view.pack(fill="both", expand=True)

    # ------------------------------------------------------------------
    # Sub-vistas por tab
    # ------------------------------------------------------------------

    def _build_tab_view(self, key):
        parent = self._content_panel

        if key == "editar":
            from manager.app.ui.views.edit_delete_payments_view import EditDeletePaymentsView
            return EditDeletePaymentsView(
                parent,
                on_back=None,
                on_payment_saved=self.on_payment_saved,
                on_navigate_to_dashboard=self._go_to_dashboard,
            )

        if key == "registrar":
            return _RegisterPaymentTab(
                parent,
                on_navigate_to_dashboard=self._go_to_dashboard,
                on_cancel=self._on_cancel_registrar,
                on_payment_saved=self.on_payment_saved,
                preselected_tenant=self.preselected_tenant,
            )

        if key == "reportes":
            from manager.app.ui.views.payment_reports_view import PaymentReportsView
            return PaymentReportsView(
                parent,
                on_back=None,
                on_navigate_to_dashboard=self._go_to_dashboard,
            )

        return None

    # ------------------------------------------------------------------
    # Navegación
    # ------------------------------------------------------------------

    def _on_volver(self):
        """Recarga el tab activo descartando la vista cacheada."""
        if self._active_tab:
            self._loaded_views.pop(self._active_tab, None)
            self._select_tab(self._active_tab)

    def _on_cancel_registrar(self):
        """Cancela el registro: descarta la vista cacheada y vuelve al tab editar."""
        self._loaded_views.pop("registrar", None)
        self._select_tab("editar")

    def _go_to_dashboard(self):
        if self.on_back:
            self.on_back()


# ---------------------------------------------------------------------------
# Tab de registro de ingreso (formulario inline, sin header propio)
# ---------------------------------------------------------------------------


class _RegisterPaymentTab(tk.Frame):
    """Formulario de registro de ingreso/pago dentro del hub de tabs."""

    def __init__(self, parent, on_navigate_to_dashboard=None, on_cancel=None,
                 on_payment_saved=None, preselected_tenant=None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._bg)
        self.on_navigate_to_dashboard = on_navigate_to_dashboard
        self.on_cancel = on_cancel
        self.on_payment_saved = on_payment_saved
        self.preselected_tenant = preselected_tenant
        self.selected_tenant = None
        self._build()

    def _build(self):
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._bg

        self.tenants = tenant_service.get_all_tenants()

        # ── Búsqueda de inquilino ──────────────────────────────────────
        search_row = tk.Frame(self, bg=cb)
        search_row.pack(fill="x", padx=Spacing.LG, pady=(Spacing.MD, 4))

        tk.Label(search_row, text="Buscar inquilino:", font=("Segoe UI", 12, "bold"),
                 bg=cb, fg=theme["text_primary"]).pack(side="left")

        self.tenant_autocomplete = TenantAutocompleteEntry(
            search_row, self.tenants,
            on_select=self._on_tenant_selected,
            width=35, entry_pady=8, entry_font=("Segoe UI", 12), bg=cb,
        )
        self.tenant_autocomplete.pack(side="left", fill="x", expand=True, padx=(8, 0))

        btn_clear = ModernButton(search_row, text="Limpiar", icon=Icons.CANCEL,
                                 style="warning", command=self._clear_search,
                                 small=True, fg="#000000")
        btn_clear.pack(side="left", padx=(8, 0))

        # ── Formulario ────────────────────────────────────────────────
        self.fecha_var = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.monto_var = tk.StringVar()
        self.metodo_var = tk.StringVar(value="Efectivo")
        self.obs_var = tk.StringVar()

        self.form_frame = tk.Frame(self, bg=cb)
        self.form_frame.pack(fill="x", padx=Spacing.LG, pady=(0, Spacing.LG))
        self._build_form()

        # Preseleccionar inquilino si viene del hub
        if self.preselected_tenant:
            self.tenant_autocomplete._select_tenant(self.preselected_tenant)

        self.after(150, self._focus_search)

    def _build_form(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._bg
        row_opts = {"padx": (0, 12), "pady": 2}

        tk.Label(self.form_frame, text="Datos del ingreso",
                 font=("Segoe UI", 12, "bold"), bg=cb,
                 fg=theme["text_primary"]).pack(anchor="w", pady=(0, Spacing.SM))

        border_color = "#c4bc8a"
        card_wrap = tk.Frame(self.form_frame, bg=border_color, padx=1, pady=1)
        card_wrap.pack(fill="x", pady=(0, Spacing.MD))
        card = tk.Frame(card_wrap, bg=cb, padx=Spacing.LG, pady=Spacing.LG)
        card.pack(fill="x")

        self._var_apt_display = tk.StringVar(value=self._apt_display(self.selected_tenant))
        self._var_tenant_name = tk.StringVar(
            value=self.selected_tenant.get("nombre", "—") if self.selected_tenant else "—")

        # Apartamento (solo lectura)
        row_apt = tk.Frame(card, bg=cb)
        row_apt.pack(fill="x", pady=(0, Spacing.SM))
        tk.Label(row_apt, text="Apartamento/Unidad:", width=24, anchor="w",
                 bg=cb, fg=theme["text_primary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        tk.Label(row_apt, textvariable=self._var_apt_display, anchor="w",
                 bg=cb, fg=theme["text_secondary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)

        # Nombre (solo lectura)
        row_name = tk.Frame(card, bg=cb)
        row_name.pack(fill="x", pady=(0, Spacing.SM))
        tk.Label(row_name, text="Nombre del inquilino:", width=24, anchor="w",
                 bg=cb, fg=theme["text_primary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        tk.Label(row_name, textvariable=self._var_tenant_name, anchor="w",
                 bg=cb, fg=theme["text_secondary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)

        # Fecha
        row1 = tk.Frame(card, bg=cb)
        row1.pack(fill="x", pady=(0, Spacing.SM))
        tk.Label(row1, text="Fecha de pago (DD/MM/YYYY):", width=24, anchor="w",
                 bg=cb, fg=theme["text_primary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        self.date_picker = DatePickerWidget(row1)
        self.date_picker.pack(side="left", **row_opts)
        self.date_picker.set(self.fecha_var.get())

        def _on_date_change(event=None):
            val = self.date_picker.get()
            if val:
                self.fecha_var.set(val)
        self.date_picker.date_entry.bind("<KeyRelease>", _on_date_change)
        self.date_picker.date_entry.bind("<FocusOut>", _on_date_change)
        _orig_sel = self.date_picker._select_date
        _orig_tod = self.date_picker._select_today
        def _ws(day): _orig_sel(day); self.fecha_var.set(self.date_picker.get())
        def _wt(): _orig_tod(); self.fecha_var.set(self.date_picker.get())
        self.date_picker._select_date = _ws
        self.date_picker._select_today = _wt

        # Monto
        row2 = tk.Frame(card, bg=cb)
        row2.pack(fill="x", pady=(0, Spacing.SM))
        tk.Label(row2, text="Monto:", width=24, anchor="w",
                 bg=cb, fg=theme["text_primary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        tk.Entry(row2, textvariable=self.monto_var, width=28,
                 font=("Segoe UI", 10)).pack(side="left", **row_opts)

        # Método
        row3 = tk.Frame(card, bg=cb)
        row3.pack(fill="x", pady=(0, Spacing.SM))
        tk.Label(row3, text="Método:", width=24, anchor="w",
                 bg=cb, fg=theme["text_primary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        metodo_combo = ttk.Combobox(row3, textvariable=self.metodo_var,
                                    values=["Efectivo", "Transferencia", "Cheque"],
                                    width=26, font=("Segoe UI", 10))
        metodo_combo.pack(side="left", **row_opts)
        bind_combobox_dropdown_on_click(metodo_combo)

        # Observaciones
        row4 = tk.Frame(card, bg=cb)
        row4.pack(fill="x", pady=(0, Spacing.MD))
        tk.Label(row4, text="Observaciones:", width=24, anchor="w",
                 bg=cb, fg=theme["text_primary"], font=("Segoe UI", 10)).pack(side="left", **row_opts)
        tk.Entry(row4, textvariable=self.obs_var, width=42,
                 font=("Segoe UI", 10)).pack(side="left", **row_opts)

        # Botones
        btns = tk.Frame(self.form_frame, bg=cb)
        btns.pack(anchor="w", pady=(0, 0))

        btn_save = tk.Button(btns, text="Registrar Ingreso",
                             command=self._save,
                             bg="#22c55e", fg="#000000",
                             font=("Segoe UI", 10, "bold"),
                             relief="flat", padx=20, pady=8, cursor="hand2")
        btn_save.pack(side="left", padx=(0, Spacing.SM))
        btn_save.bind("<Enter>", lambda e: btn_save.configure(bg="#16a34a"))
        btn_save.bind("<Leave>", lambda e: btn_save.configure(bg="#22c55e"))

        btn_clear_form = ModernButton(btns, text="Limpiar", icon=Icons.CANCEL,
                                      style="secondary", command=self._clear_form,
                                      fg="#000000", small=False)
        btn_clear_form.pack(side="left", padx=(0, Spacing.SM))

        btn_cancel = ModernButton(btns, text="Cancelar", icon=Icons.CANCEL,
                                  style="secondary", command=self._cancel,
                                  fg="#000000", small=False)
        btn_cancel.pack(side="left")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _apt_display(self, tenant):
        if not tenant:
            return "—"
        apt_id = tenant.get("apartamento")
        if apt_id is None:
            return "—"
        try:
            apt = apartment_service.get_apartment_by_id(apt_id)
        except Exception:
            return "—"
        if not apt:
            return "—"
        building = None
        try:
            all_buildings = building_service.get_all_buildings()
            building = next((b for b in all_buildings if b.get("id") == apt.get("building_id")), None)
        except Exception:
            pass
        building_name = building.get("name", "") if building else ""
        tipo = apt.get("unit_type", "Apartamento Estándar")
        numero = apt.get("number", "")
        if building_name:
            return f"{building_name} - {tipo} {numero}" if tipo != "Apartamento Estándar" else f"{building_name} - {numero}"
        return f"{tipo} {numero}" if tipo != "Apartamento Estándar" else str(numero)

    def _focus_search(self):
        if hasattr(self, "tenant_autocomplete") and hasattr(self.tenant_autocomplete, "entry"):
            if self.tenant_autocomplete.entry.winfo_exists():
                self.tenant_autocomplete.entry.focus_set()

    def _on_tenant_selected(self, tenant):
        self.selected_tenant = tenant
        if hasattr(self, "_var_apt_display"):
            self._var_apt_display.set(self._apt_display(tenant))
        if hasattr(self, "_var_tenant_name"):
            self._var_tenant_name.set(tenant.get("nombre", "—"))
        if hasattr(self, "monto_var"):
            self.monto_var.set(str(tenant.get("valor_arriendo", "")))

    def _clear_search(self):
        self.tenant_autocomplete.set_tenants(self.tenants)
        self.selected_tenant = None
        if hasattr(self, "_var_apt_display"):
            self._var_apt_display.set("—")
        if hasattr(self, "_var_tenant_name"):
            self._var_tenant_name.set("—")
        self.monto_var.set("")
        self.fecha_var.set(datetime.now().strftime("%d/%m/%Y"))
        if hasattr(self, "date_picker") and self.date_picker.winfo_exists():
            self.date_picker.set(self.fecha_var.get())
        self.metodo_var.set("Efectivo")
        self.obs_var.set("")

    def _clear_form(self):
        self._clear_search()

    def _cancel(self):
        if self.on_cancel:
            self.on_cancel()

    def _save(self):
        if not self.selected_tenant:
            messagebox.showerror("Error", "Debe seleccionar un inquilino.")
            return
        fecha_str = self.date_picker.get() if hasattr(self, "date_picker") and self.date_picker.winfo_exists() else self.fecha_var.get()
        if fecha_str:
            self.fecha_var.set(fecha_str)
        if not self.fecha_var.get():
            messagebox.showerror("Error", "Debe ingresar la fecha de pago.")
            return
        try:
            datetime.strptime(self.fecha_var.get(), "%d/%m/%Y")
        except Exception:
            messagebox.showerror("Error", "La fecha debe tener formato DD/MM/YYYY.")
            return
        try:
            monto = float(self.monto_var.get())
            if monto <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "El monto debe ser un número positivo.")
            return

        data = {
            "id_inquilino": self.selected_tenant["id"],
            "nombre_inquilino": self.selected_tenant["nombre"],
            "fecha_pago": self.fecha_var.get(),
            "monto": monto,
            "metodo": self.metodo_var.get(),
            "observaciones": self.obs_var.get(),
        }

        # Prevenir duplicados
        existing = payment_service.get_payments_by_tenant(data["id_inquilino"])
        for p in existing:
            if p.get("fecha_pago") == data["fecha_pago"] and p.get("monto") == data["monto"]:
                messagebox.showwarning("Advertencia", "Ya existe un pago con la misma fecha y monto para este inquilino.")
                return

        payment_service.add_payment(data)
        self._generate_receipt(data)

        if sys.platform == "win32":
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass

        if self.on_payment_saved:
            self.on_payment_saved()

        # Limpiar para el siguiente registro
        self.fecha_var.set(datetime.now().strftime("%d/%m/%Y"))
        if hasattr(self, "date_picker") and self.date_picker.winfo_exists():
            self.date_picker.set(self.fecha_var.get())
        self.monto_var.set(str(self.selected_tenant.get("valor_arriendo", "")))
        self.metodo_var.set("Efectivo")
        self.obs_var.set("")

    def _generate_receipt(self, pago):
        try:
            from manager.app.paths_config import DOCUMENTOS_INQUILINOS_DIR, ensure_dirs, get_tenant_document_folder_name
            from manager.app.receipt_pdf import generate_payment_receipt_pdf
            ensure_dirs()
            tenant = self.selected_tenant or {}
            folder_name = get_tenant_document_folder_name(tenant)
            tenant_dir = DOCUMENTOS_INQUILINOS_DIR / folder_name
            tenant_dir.mkdir(parents=True, exist_ok=True)
            fecha = pago.get("fecha_pago", "").replace("/", "-")
            filepath = str(tenant_dir / f"recibo_{fecha}.pdf")
            generate_payment_receipt_pdf(pago, tenant, filepath)
        except Exception as exc:
            logger.warning("Error al generar recibo PDF: %s", exc)


# ---------------------------------------------------------------------------
# Modal de pago (se mantiene para compatibilidad con EditDeletePaymentsView)
# ---------------------------------------------------------------------------

class PaymentModal(tk.Toplevel):
    def __init__(self, parent, tenants, payment=None, on_save=None, preselected_tenant=None, compact=False):
        super().__init__(parent)
        self.title("Registrar Pago" if payment is None else "Editar Pago")
        self.compact = compact
        if compact:
            self.geometry("420x440")
        else:
            self.geometry("400x400")
        self.payment_service = payment_service
        self.payment = payment
        self.on_save = on_save
        self.tenants = tenants
        self.preselected_tenant = preselected_tenant
        self._create_form()
        self._close_modal = self._make_close_modal()
        self.bind_all("<Escape>", self._close_modal)
        self.protocol("WM_DELETE_WINDOW", lambda: self._close_modal(None))
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _make_close_modal(self):
        def _close(event=None):
            self.unbind_all("<Escape>")
            self.destroy()
        return _close

    def _create_form(self):
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=cb)

        tk.Label(self, text="Registrar Pago" if not self.payment else "Editar Pago",
                 font=("Segoe UI", 13, "bold"), bg=cb,
                 fg=theme["text_primary"]).pack(pady=(14, 6))

        form = tk.Frame(self, bg=cb)
        form.pack(fill="x", padx=20)

        row_opts = {"padx": (0, 8), "pady": 3}

        # Inquilino
        row_t = tk.Frame(form, bg=cb)
        row_t.pack(fill="x")
        tk.Label(row_t, text="Inquilino:", width=18, anchor="w",
                 bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        self._tenant_var = tk.StringVar()
        self._tenant_combo = ttk.Combobox(row_t, textvariable=self._tenant_var,
                                          values=[t.get("nombre", "") for t in self.tenants],
                                          width=24, state="readonly")
        self._tenant_combo.pack(side="left", **row_opts)
        bind_combobox_dropdown_on_click(self._tenant_combo)
        if self.preselected_tenant:
            self._tenant_var.set(self.preselected_tenant.get("nombre", ""))
        elif self.payment:
            self._tenant_var.set(self.payment.get("nombre_inquilino", ""))

        # Fecha
        row1 = tk.Frame(form, bg=cb)
        row1.pack(fill="x")
        tk.Label(row1, text="Fecha (DD/MM/YYYY):", width=18, anchor="w",
                 bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        self._fecha_var = tk.StringVar(value=self.payment.get("fecha_pago", datetime.now().strftime("%d/%m/%Y")) if self.payment else datetime.now().strftime("%d/%m/%Y"))
        self._date_picker = DatePickerWidget(row1)
        self._date_picker.pack(side="left", **row_opts)
        self._date_picker.set(self._fecha_var.get())
        def _dc(event=None):
            v = self._date_picker.get()
            if v: self._fecha_var.set(v)
        self._date_picker.date_entry.bind("<KeyRelease>", _dc)
        self._date_picker.date_entry.bind("<FocusOut>", _dc)

        # Monto
        row2 = tk.Frame(form, bg=cb)
        row2.pack(fill="x")
        tk.Label(row2, text="Monto:", width=18, anchor="w",
                 bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        self._monto_var = tk.StringVar(value=str(self.payment.get("monto", "")) if self.payment else "")
        tk.Entry(row2, textvariable=self._monto_var, width=26).pack(side="left", **row_opts)

        # Método
        row3 = tk.Frame(form, bg=cb)
        row3.pack(fill="x")
        tk.Label(row3, text="Método:", width=18, anchor="w",
                 bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        self._metodo_var = tk.StringVar(value=self.payment.get("metodo", "Efectivo") if self.payment else "Efectivo")
        mc = ttk.Combobox(row3, textvariable=self._metodo_var,
                          values=["Efectivo", "Transferencia", "Cheque"], width=24)
        mc.pack(side="left", **row_opts)
        bind_combobox_dropdown_on_click(mc)

        # Observaciones
        row4 = tk.Frame(form, bg=cb)
        row4.pack(fill="x")
        tk.Label(row4, text="Observaciones:", width=18, anchor="w",
                 bg=cb, fg=theme["text_primary"]).pack(side="left", **row_opts)
        self._obs_var = tk.StringVar(value=self.payment.get("observaciones", "") if self.payment else "")
        tk.Entry(row4, textvariable=self._obs_var, width=26).pack(side="left", **row_opts)

        # Botón guardar
        tk.Button(self, text="Guardar", command=self._save,
                  bg="#22c55e", fg="#000000",
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=18, pady=6,
                  cursor="hand2").pack(pady=(14, 0))

    def _save(self):
        tenant_name = self._tenant_var.get()
        tenant = next((t for t in self.tenants if t.get("nombre") == tenant_name), None)
        fecha = self._date_picker.get() or self._fecha_var.get()
        try:
            monto = float(self._monto_var.get())
            if monto <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Monto inválido.")
            return
        if not tenant:
            messagebox.showerror("Error", "Seleccione un inquilino.")
            return
        data = {
            "id_inquilino": tenant["id"],
            "nombre_inquilino": tenant["nombre"],
            "fecha_pago": fecha,
            "monto": monto,
            "metodo": self._metodo_var.get(),
            "observaciones": self._obs_var.get(),
        }
        if self.payment:
            self.payment_service.update_payment(self.payment["id"], data)
        else:
            self.payment_service.add_payment(data)
        if sys.platform == "win32":
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception:
                pass
        if self.on_save:
            self.on_save(data)
        self._make_close_modal()()
