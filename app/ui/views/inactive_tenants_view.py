"""
Vista de inquilinos inactivos.
Muestra la lista de inquilinos con estado 'inactivo', con búsqueda,
ver detalles y reactivar.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from datetime import datetime

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.services.tenant_service import tenant_service
from manager.app.services.apartment_service import apartment_service
from manager.app.logger import logger


class InactiveTenantsView(tk.Frame):
    """Lista de inquilinos inactivos con búsqueda y acciones."""

    _CARD_BG = "#f3e8ff"
    _CARD_BORDER = "#e9d5ff"
    _BTN_BG = "#8b5cf6"
    _BTN_HOVER = "#6d28d9"
    _PLACEHOLDER = "Buscar por nombre, apartamento, teléfono..."

    def __init__(self, parent, on_data_change: Callable = None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._bg)
        self.on_data_change = on_data_change
        self._all_tenants: list = []
        self._current_sub: Optional[tk.Widget] = None
        self._current_tenant: Optional[dict] = None
        self._build()

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _build(self):
        self._show_list()

    def _show_list(self):
        for w in self.winfo_children():
            w.destroy()
        self._current_sub = None

        theme = theme_manager.themes[theme_manager.current_theme]
        fg = theme.get("text_primary", "#1f2937")
        bg = self._bg

        # Title
        title_frame = tk.Frame(self, bg=bg)
        title_frame.pack(fill="x", padx=Spacing.MD, pady=(Spacing.SM, 0))
        tk.Label(
            title_frame,
            text="Inquilinos Inactivos",
            font=("Segoe UI", 15, "bold"),
            fg=fg, bg=bg,
        ).pack(side="left")

        # Subtitle
        tk.Label(
            self,
            text="Lista de inquilinos desactivados. Puedes reactivarlos si es necesario.",
            font=("Segoe UI", 10),
            fg="#374151", bg=bg,
        ).pack(anchor="w", padx=Spacing.MD, pady=(2, Spacing.SM))

        # Search bar
        search_frame = tk.Frame(self, bg=bg)
        search_frame.pack(fill="x", padx=Spacing.MD, pady=(0, Spacing.SM))

        tk.Label(search_frame, text="🔍 Buscar:", font=("Segoe UI", 10, "bold"),
                 fg=fg, bg=bg).pack(side="left", padx=(0, Spacing.SM))

        self._search_entry = tk.Entry(
            search_frame, font=("Segoe UI", 10),
            relief="solid", bd=1,
            highlightthickness=1,
            highlightbackground="#ccc",
            highlightcolor="#1976d2",
        )
        self._search_entry.pack(side="left", fill="x", expand=True, padx=(0, Spacing.SM))
        self._search_entry.insert(0, self._PLACEHOLDER)
        self._search_entry.config(fg="#999")
        self._search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self._search_entry.bind("<FocusOut>", self._on_search_focus_out)
        self._search_entry.bind("<KeyRelease>", lambda e: self.after_idle(self._apply_filter))

        btn_clear = tk.Button(
            search_frame, text=f"{Icons.CANCEL} Limpiar",
            font=("Segoe UI", 9, "bold"),
            bg=self._BTN_BG, fg="white",
            activebackground=self._BTN_HOVER, activeforeground="white",
            bd=0, relief="flat", padx=Spacing.SM, pady=4, cursor="hand2",
            command=self._clear_search,
        )
        btn_clear.pack(side="left")
        btn_clear.bind("<Enter>", lambda e: btn_clear.config(bg=self._BTN_HOVER))
        btn_clear.bind("<Leave>", lambda e: btn_clear.config(bg=self._BTN_BG))

        self._results_label = tk.Label(search_frame, text="", font=("Segoe UI", 9),
                                       fg="#374151", bg=bg)
        self._results_label.pack(side="right", padx=(Spacing.MD, 0))

        # Scrollable list
        container = tk.Frame(self, bg=bg)
        container.pack(fill="both", expand=True, padx=Spacing.MD, pady=(0, Spacing.MD))

        self._canvas = tk.Canvas(container, bg=bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self._canvas.yview)
        self._list_frame = tk.Frame(self._canvas, bg=bg)

        self._list_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        )
        self._canvas_win = self._canvas.create_window((0, 0), window=self._list_frame, anchor="nw")
        self._canvas.configure(yscrollcommand=scrollbar.set)
        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfig(self._canvas_win, width=e.width))

        self._canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _mw(event):
            try:
                if self._canvas.winfo_exists():
                    self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass
        self._canvas.bind_all("<MouseWheel>", _mw)

        # Load data
        self._reload_data()

    def _reload_data(self):
        tenant_service._load_data()
        tenants = tenant_service.get_all_tenants()
        self._all_tenants = [t for t in tenants if t.get("estado_pago") == "inactivo"]
        self._apply_filter()

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def _on_search_focus_in(self, event):
        if self._search_entry.get() == self._PLACEHOLDER:
            self._search_entry.delete(0, tk.END)
            self._search_entry.config(fg="#000")

    def _on_search_focus_out(self, event):
        if not self._search_entry.get().strip():
            self._search_entry.delete(0, tk.END)
            self._search_entry.insert(0, self._PLACEHOLDER)
            self._search_entry.config(fg="#999")

    def _clear_search(self):
        self._search_entry.delete(0, tk.END)
        self._search_entry.insert(0, self._PLACEHOLDER)
        self._search_entry.config(fg="#999")
        self._apply_filter()

    def _get_search_term(self) -> str:
        text = self._search_entry.get()
        if text == self._PLACEHOLDER:
            return ""
        return text.lower().strip()

    def _apply_filter(self):
        for w in self._list_frame.winfo_children():
            w.destroy()

        term = self._get_search_term()
        if term:
            filtered = [t for t in self._all_tenants if self._matches(t, term)]
        else:
            filtered = self._all_tenants

        total = len(self._all_tenants)
        shown = len(filtered)
        if term:
            self._results_label.config(text=f"Mostrando {shown} de {total}")
        else:
            self._results_label.config(
                text=f"{total} inquilino{'s' if total != 1 else ''} inactivo{'s' if total != 1 else ''}"
            )

        if not filtered:
            tk.Label(
                self._list_frame,
                text="No hay inquilinos inactivos." if not term else "Sin resultados.",
                font=("Segoe UI", 11), fg="#6b7280", bg=self._bg,
            ).pack(pady=Spacing.XL)
            return

        for tenant in filtered:
            self._create_card(self._list_frame, tenant)

    def _matches(self, tenant: dict, term: str) -> bool:
        if term in str(tenant.get("nombre", "")).lower():
            return True
        if term in str(tenant.get("telefono", "")).lower():
            return True
        if term in str(tenant.get("numero_documento", "")).lower():
            return True
        apt_id = tenant.get("apartamento")
        if apt_id is not None:
            try:
                apt = apartment_service.get_apartment_by_id(int(apt_id))
                if apt:
                    apt_text = f"{apt.get('unit_type','')} {apt.get('number','')}".lower()
                    if term in apt_text:
                        return True
            except Exception:
                pass
        return False

    # ------------------------------------------------------------------
    # Card
    # ------------------------------------------------------------------

    def _create_card(self, parent, tenant):
        card = tk.Frame(parent, bg=self._CARD_BG, relief="flat", bd=1,
                        highlightbackground=self._CARD_BORDER, highlightthickness=1)
        card.pack(fill="x", padx=Spacing.SM, pady=2)

        content = tk.Frame(card, bg=self._CARD_BG)
        content.pack(fill="x", padx=Spacing.SM, pady=Spacing.XS)

        info = tk.Frame(content, bg=self._CARD_BG)
        info.pack(side="left", fill="x", expand=True)

        # Row 1: name + apt + phone
        row1 = tk.Frame(info, bg=self._CARD_BG)
        row1.pack(fill="x", pady=(0, 2))
        tk.Label(row1, text=tenant.get("nombre", "N/A"),
                 font=("Segoe UI", 11, "bold"), fg="#4c1d95",
                 bg=self._CARD_BG).pack(side="left", padx=(0, Spacing.MD))

        apt_display = self._get_apt_display(tenant)
        tk.Label(row1, text=apt_display, font=("Segoe UI", 9),
                 fg="#374151", bg=self._CARD_BG).pack(side="left", padx=(0, Spacing.MD))
        tk.Label(row1, text=f"Tel: {tenant.get('telefono', 'N/A')}",
                 font=("Segoe UI", 9), fg="#374151",
                 bg=self._CARD_BG).pack(side="left")

        # Row 2: deactivation info
        row2 = tk.Frame(info, bg=self._CARD_BG)
        row2.pack(fill="x")
        fecha_raw = tenant.get("fecha_desactivacion", "")
        try:
            fecha_str = datetime.fromisoformat(fecha_raw).strftime("%d/%m/%Y") if fecha_raw else "N/A"
        except Exception:
            fecha_str = fecha_raw or "N/A"
        motivo = tenant.get("motivo_desactivacion", "N/A")
        tk.Label(row2, text=f"Desactivado: {fecha_str} | Razón: {motivo}",
                 font=("Segoe UI", 9), fg="#6b7280",
                 bg=self._CARD_BG).pack(anchor="w")

        # Buttons
        btns = tk.Frame(content, bg=self._CARD_BG)
        btns.pack(side="right", padx=(Spacing.SM, 0))
        self._make_btn(btns, f"{Icons.TENANT_PROFILE} Detalles",
                       lambda t=tenant: self._view_details(t))
        self._make_btn(btns, "🔄 Reactivar",
                       lambda t=tenant: self._reactivate(t))

    def _make_btn(self, parent, text, command):
        btn = tk.Button(parent, text=text, font=("Segoe UI", 9, "bold"),
                        bg=self._BTN_BG, fg="white",
                        activebackground=self._BTN_HOVER, activeforeground="white",
                        bd=0, relief="flat", padx=Spacing.SM, pady=4,
                        cursor="hand2", command=command)
        btn.pack(side="left", padx=(0, 3))
        btn.bind("<Enter>", lambda e: btn.config(bg=self._BTN_HOVER))
        btn.bind("<Leave>", lambda e: btn.config(bg=self._BTN_BG))

    def _get_apt_display(self, tenant) -> str:
        apt_id = tenant.get("apartamento")
        if apt_id is None:
            return "N/A"
        try:
            apt = apartment_service.get_apartment_by_id(int(apt_id))
            if apt:
                t = apt.get("unit_type", "Apartamento Estándar")
                n = apt.get("number", "N/A")
                return f"Apto: {n}" if t == "Apartamento Estándar" else f"{t}: {n}"
        except Exception:
            pass
        return f"Apto: {apt_id}"

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _view_details(self, tenant):
        from manager.app.ui.views.tenant_details_view import TenantDetailsView
        for w in self.winfo_children():
            w.destroy()
        self._current_sub = "details"
        self._current_tenant = tenant
        details = TenantDetailsView(
            self, tenant_data=tenant,
            on_back=self._show_list,
            on_edit=None,
            on_register_payment=None,
            read_only=True,
            on_reactivate=lambda: self._reactivate(tenant),
        )
        details.pack(fill="both", expand=True)

    def _reactivate(self, tenant):
        from manager.app.ui.views.tenant_form_view import TenantFormView
        for w in self.winfo_children():
            w.destroy()
        self._current_sub = "reactivate"
        self._current_tenant = tenant
        form = TenantFormView(
            self,
            on_back=lambda: self._view_details(tenant),
            tenant_data=tenant,
            on_save_success=self._on_reactivated,
            reactivate_mode=True,
        )
        form.pack(fill="both", expand=True)

    def _on_reactivated(self):
        if self.on_data_change:
            self.on_data_change()
        self._show_list()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def go_back(self) -> bool:
        """Protocolo de back para el hub. Retorna True si manejó el back internamente."""
        if self._current_sub == "reactivate" and self._current_tenant:
            self._view_details(self._current_tenant)
            return True
        if self._current_sub is not None:
            self._show_list()
            return True
        return False

    def refresh(self):
        """Recarga datos y vuelve a la lista."""
        self._show_list()
