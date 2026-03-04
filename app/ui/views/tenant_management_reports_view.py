"""
Vista de reportes específicos para el módulo de Gestión de Inquilinos
Reportes enfocados en la gestión operativa de inquilinos
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
import csv
from pathlib import Path

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
from manager.app.services.tenant_service import tenant_service
from manager.app.services.payment_service import payment_service
from manager.app.services.apartment_service import apartment_service


class TenantManagementReportsView(tk.Frame):
    """Vista de reportes específicos para gestión de inquilinos"""
    
    def __init__(self, parent, on_back: Callable = None, on_navigate: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_back = on_back
        self.on_navigate = on_navigate
        
        # Recargar datos antes de generar reportes
        self._reload_all_data()
        
        self._create_layout()
    
    def _reload_all_data(self):
        """Recarga todos los datos necesarios para los reportes"""
        try:
            tenant_service._load_data()
            payment_service._load_data()
            apartment_service._load_data()
        except Exception as e:
            print(f"Error al recargar datos: {e}")
    
    def _create_layout(self):
        """Crea el layout principal de la vista de reportes"""
        theme = theme_manager.themes[theme_manager.current_theme]
        content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=content_bg)

        # Header
        header = tk.Frame(self, bg=content_bg)
        header.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)

        title = tk.Label(
            header,
            text="Reportes y Análisis",
            font=("Segoe UI", 16, "bold"),
            bg=content_bg,
            fg=theme["text_primary"]
        )
        title.pack(side="left")

        # Botones de navegación
        buttons_frame = tk.Frame(header, bg=content_bg)
        buttons_frame.pack(side="right")
        self._create_navigation_buttons(buttons_frame)

        # Contenedor principal: sin margen inferior para que el panel llegue al fondo y el centrado vertical sea correcto
        main_container = tk.Frame(self, bg=content_bg)
        main_container.pack(fill="both", expand=True, padx=Spacing.MD, pady=(0, 0))

        # Contenido de reportes
        self._create_reports_content(main_container)
    
    def _create_reports_content(self, parent):
        """Crea el contenido de los reportes"""
        theme = theme_manager.themes[theme_manager.current_theme]
        content_bg = theme.get("content_bg", theme["bg_primary"])
        border_light = theme.get("border_light", "#e5e7eb")

        # Subtítulo de sección
        tk.Label(
            parent,
            text="Seleccione el tipo de reporte que desea generar:",
            font=("Segoe UI", 12),
            bg=content_bg,
            fg="#000000"
        ).pack(anchor="w", pady=(0, Spacing.MD))

        # Panel que envuelve las tarjetas (sin marco/borde visible)
        panel = tk.Frame(parent, bg=content_bg)
        panel.pack(fill="both", expand=True, padx=0, pady=0)

        # Tres filas: espacio arriba (flexible), bloque de cards (fijo), espacio abajo (flexible) = centrado vertical
        grid_wrapper = tk.Frame(panel, bg=content_bg)
        grid_wrapper.pack(fill="both", expand=True)
        grid_wrapper.columnconfigure(0, weight=1)
        grid_wrapper.rowconfigure(0, weight=1)   # espacio arriba
        grid_wrapper.rowconfigure(1, weight=0)    # fila de los cards
        grid_wrapper.rowconfigure(2, weight=1)   # espacio abajo

        # Espaciador superior: ocupa el espacio sobrante arriba y empuja los cards hacia el centro
        spacer_top = tk.Frame(grid_wrapper, bg=content_bg)
        spacer_top.grid(row=0, column=0, sticky="nsew")

        # Bloque de tarjetas en la fila central (centrado horizontal y vertical)
        cards_holder = tk.Frame(grid_wrapper, bg=content_bg)
        cards_holder.grid(row=1, column=0, sticky="nsew")
        cards_holder.columnconfigure(0, weight=1)

        # Espaciador inferior: mismo peso que el de arriba para equilibrar
        spacer_bottom = tk.Frame(grid_wrapper, bg=content_bg)
        spacer_bottom.grid(row=2, column=0, sticky="nsew")

        cards_grid = tk.Frame(cards_holder, bg=content_bg, padx=Spacing.LG, pady=Spacing.LG)
        cards_grid.pack(anchor="center")

        # Grid de 2 columnas; tamaño de card igual que módulo Gastos (260x220)
        CARD_WIDTH = 260
        CARD_HEIGHT = 220
        cards_grid.columnconfigure(0, weight=1, uniform="cards", minsize=CARD_WIDTH)
        cards_grid.columnconfigure(1, weight=1, uniform="cards", minsize=CARD_WIDTH)

        # Colores del módulo inquilinos (azul distintivo) para cards, botones y acentos
        colors = get_module_colors("inquilinos")
        blue_primary = colors["primary"]
        blue_hover = colors["hover"]
        blue_light = colors["light"]
        blue_text = colors["text"]
        blue_border = "#93c5fd"  # blue-300 para borde de cards

        # Título/icono en azul oscuro (blue_text) para contraste; botón sigue con blue_primary
        title_icon_color = blue_text  # #1e40af blue-800
        reports = [
            ("👥 Reporte de Inquilinos",
             "Información consolidada de todos los inquilinos activos e inactivos.",
             title_icon_color,
             self._generate_tenants_consolidated_report),
            ("📞 Contactos de Emergencia",
             "Lista completa de contactos de emergencia de todos los inquilinos activos.",
             title_icon_color,
             self._generate_emergency_contacts_report),
        ]

        # Colocar cards en grid (2 columnas, centrados)
        self._report_cards = []
        row = 0
        col = 0
        # Hover más intenso que el fondo del card para que se note
        card_hover_bg = "#93c5fd"  # blue-300
        for title_text, description, color, command in reports:
            card = self._create_report_card(
                cards_grid,
                title_text,
                description,
                color,
                command,
                content_bg=content_bg,
                border_light=blue_border,
                btn_primary=blue_primary,
                btn_hover=blue_hover,
                btn_light=blue_light,
                btn_text=blue_text,
                text_primary=theme["text_primary"],
                text_secondary=theme["text_secondary"],
                bg_primary=blue_light,
                card_hover_bg=card_hover_bg,
            )
            card.grid(row=row, column=col, padx=Spacing.MD, pady=Spacing.SM, sticky="n")
            self._report_cards.append(card)

            col += 1
            if col >= 2:
                col = 0
                row += 1

        # Configurar fila(s) de cards con altura igual que módulo Gastos (220)
        row_minsize = CARD_HEIGHT + 2 * Spacing.MD
        for r in range(row + 1):
            cards_grid.rowconfigure(r, weight=0, minsize=row_minsize)
    
    def _create_report_card(self, parent, title_text, description, color, command,
                            content_bg=None, border_light=None,
                            btn_primary=None, btn_hover=None, btn_light=None, btn_text=None,
                            text_primary=None, text_secondary=None, bg_primary=None,
                            card_hover_bg=None):
        """Crea una tarjeta de reporte con borde visible y efecto hover (estilo estándar del app)."""
        theme = theme_manager.themes[theme_manager.current_theme]
        content_bg = content_bg or theme.get("content_bg", theme["bg_primary"])
        border_light = border_light or theme.get("border_light", "#e5e7eb")
        bg_card = bg_primary or theme["bg_primary"]
        text_primary = text_primary or theme["text_primary"]
        text_secondary = text_secondary or theme["text_secondary"]
        btn_primary = btn_primary or color
        btn_hover = btn_hover or color
        btn_light = btn_light or "#e0e7ff"
        btn_text = btn_text or "#1e293b"
        hover_bg = card_hover_bg if card_hover_bg is not None else (btn_light or "#93c5fd")

        # Mismo tamaño que cards del módulo Gastos: 260x220
        card = tk.Frame(
            parent,
            bg=bg_card,
            bd=2,
            relief="raised",
            highlightthickness=0,
            width=260,
            height=220,
        )
        card.pack_propagate(False)
        card.configure(cursor="hand2")

        content = tk.Frame(card, bg=bg_card, padx=Spacing.MD, pady=Spacing.MD)
        content.pack(fill="both", expand=True)

        title_label = tk.Label(
            content,
            text=title_text,
            font=("Segoe UI", 12, "bold"),
            bg=bg_card,
            fg=color,
            wraplength=240,
            justify="center"
        )
        title_label.pack(anchor="center", pady=(0, Spacing.SM))

        # Espaciador para empujar el botón al fondo y que quede a la misma altura en todos los cards
        spacer = tk.Frame(content, bg=bg_card, height=1)
        spacer.pack(fill="both", expand=True)

        btn_container = tk.Frame(content, bg=bg_card)
        btn_container.pack(side="bottom", fill="x")
        create_rounded_button(
            btn_container,
            "Generar Reporte",
            bg_color=btn_primary,
            fg_color="#ffffff",
            hover_bg=btn_hover,
            hover_fg="#ffffff",
            command=command,
            padx=14,
            pady=6,
            radius=0,
            border_color=btn_primary,
            outline_width=0,
        ).pack(anchor="center")

        def on_enter(e):
            card.configure(bg=hover_bg)
            content.configure(bg=hover_bg)
            title_label.configure(bg=hover_bg)
            spacer.configure(bg=hover_bg)
            btn_container.configure(bg=hover_bg)

        def on_leave(e):
            def _check_leave():
                try:
                    root = card.winfo_toplevel()
                    root.update_idletasks()
                    x, y = root.winfo_pointerx(), root.winfo_pointery()
                    w = root.winfo_containing(x, y)
                    cur = w
                    while cur:
                        if cur == card:
                            return
                        try:
                            cur = cur.master
                        except (tk.TclError, AttributeError):
                            break
                except (tk.TclError, AttributeError):
                    pass
                card.configure(bg=bg_card)
                content.configure(bg=bg_card)
                title_label.configure(bg=bg_card)
                spacer.configure(bg=bg_card)
                btn_container.configure(bg=bg_card)

            try:
                card.after(10, _check_leave)
            except tk.TclError:
                pass

        for widget in (card, content, title_label, spacer, btn_container):
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.configure(cursor="hand2")

        card._card_normal_bg = bg_card
        return card
    
    def _create_navigation_buttons(self, parent):
        """Crea los botones de navegación"""
        theme = theme_manager.themes[theme_manager.current_theme]
        hover_bg = theme.get("bg_tertiary", theme["btn_secondary_hover"])
        
        button_config = {
            "font": ("Segoe UI", 10, "bold"),
            "bg": theme["btn_secondary_bg"],
            "fg": theme["btn_secondary_fg"],
            "activebackground": hover_bg,
            "activeforeground": theme["btn_secondary_fg"],
            "bd": 1,
            "relief": "solid",
            "padx": 12,
            "pady": 5,
            "cursor": "hand2"
        }
        
        # Colores azules para módulo de inquilinos
        colors = get_module_colors("inquilinos")
        blue_primary = colors["primary"]
        blue_hover = colors["hover"]
        blue_light = colors["light"]
        blue_text = colors["text"]
        
        def go_back():
            if self.on_back:
                self.on_back()
        
        def go_to_dashboard():
            # Prioridad 1: Usar callback directo si está disponible
            if self.on_navigate:
                try:
                    self.on_navigate()  # El callback ya tiene "dashboard" hardcodeado
                    return
                except Exception as e:
                    print(f"Error en callback de navegación: {e}")
            
            # Prioridad 2: Buscar MainWindow a través de la jerarquía de widgets
            widget = self.master
            max_depth = 10
            depth = 0
            while widget and depth < max_depth:
                if (hasattr(widget, '_navigate_to') and 
                    hasattr(widget, '_load_view') and 
                    hasattr(widget, 'views_container')):
                    try:
                        widget._navigate_to("dashboard")
                        return
                    except Exception as e:
                        print(f"Error al navegar: {e}")
                        break
                widget = getattr(widget, 'master', None)
                depth += 1
            
            # Prioridad 3: Buscar desde el root window
            try:
                root = self.winfo_toplevel()
                # Buscar MainWindow entre los hijos del root
                for child in root.winfo_children():
                    if (hasattr(child, '_navigate_to') and 
                        hasattr(child, '_load_view') and 
                        hasattr(child, 'views_container')):
                        child._navigate_to("dashboard")
                        return
            except Exception as e:
                print(f"Error en búsqueda desde root: {e}")
            
            # Si todo falla, mostrar mensaje
            print("No se pudo encontrar MainWindow para navegar al dashboard")
        
        # Botón "Volver"
        btn_back = create_rounded_button(
            parent,
            text=f"{Icons.ARROW_LEFT} Volver",
            bg_color="white",
            fg_color=blue_primary,
            hover_bg=blue_light,
            hover_fg=blue_text,
            command=go_back,
            padx=16,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_back.pack(side="right", padx=(Spacing.MD, 0))
        
        # Botón "Dashboard"
        btn_dashboard = create_rounded_button(
            parent,
            text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=blue_primary,
            fg_color="white",
            hover_bg=blue_hover,
            hover_fg="white",
            command=go_to_dashboard,
            padx=18,
            pady=8,
            radius=4,
            border_color="#000000"
        )
        btn_dashboard.pack(side="right")
    
    # ==================== GENERADORES DE REPORTES ====================
    
    def _generate_tenants_consolidated_report(self):
        """Genera reporte consolidado de inquilinos (activos e inactivos)"""
        try:
            self._reload_all_data()
            
            tenants = tenant_service.get_all_tenants()
            active = [t for t in tenants if t.get('estado_pago') != 'inactivo']
            inactive = [t for t in tenants if t.get('estado_pago') == 'inactivo']
            
            report = []
            report.append("=" * 60)
            report.append("REPORTE DE INQUILINOS")
            report.append("=" * 60)
            report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            report.append("")
            report.append(f"RESUMEN:")
            report.append(f"  • Total de inquilinos: {len(tenants)}")
            report.append(f"  • Inquilinos activos: {len(active)}")
            report.append(f"  • Inquilinos inactivos: {len(inactive)}")
            report.append("")
            
            # Función auxiliar para formatear un inquilino
            def format_tenant(tenant):
                status = tenant.get('estado_pago', 'N/A')
                status_map = {
                    'al_dia': 'Al Día',
                    'pendiente_registro': 'Pendiente Registro',
                    'moroso': 'En Mora',
                    'inactivo': 'Inactivo'
                }
                status_text = status_map.get(status, status)
                
                # Obtener el número del apartamento
                apartment_display = self._get_apartment_display(tenant)
                
                lines = []
                lines.append(f"Nombre: {tenant.get('nombre', 'N/A')}")
                lines.append(f"  • Apartamento: {apartment_display}")
                lines.append(f"  • Documento: {tenant.get('numero_documento', 'N/A')}")
                lines.append(f"  • Teléfono: {tenant.get('telefono', 'N/A')}")
                lines.append(f"  • Estado: {status_text}")
                lines.append(f"  • Arriendo: ${float(tenant.get('valor_arriendo', 0)):,.2f}")
                
                # Si está inactivo, agregar información de desactivación
                if status == 'inactivo':
                    motivo = tenant.get('motivo_desactivacion', 'N/A')
                    fecha_desactivacion = tenant.get('fecha_desactivacion', 'N/A')
                    if fecha_desactivacion != 'N/A':
                        try:
                            fecha_dt = datetime.fromisoformat(fecha_desactivacion)
                            fecha_desactivacion = fecha_dt.strftime('%d/%m/%Y')
                        except:
                            pass
                    lines.append(f"  • Motivo de desactivación: {motivo}")
                    lines.append(f"  • Fecha de desactivación: {fecha_desactivacion}")
                
                lines.append("")
                return "\n".join(lines)
            
            # SECCIÓN 1: INQUILINOS ACTIVOS
            report.append("=" * 60)
            report.append("INQUILINOS ACTIVOS")
            report.append("=" * 60)
            report.append("")
            
            if active:
                for tenant in active:
                    report.append(format_tenant(tenant))
            else:
                report.append("No hay inquilinos activos.")
                report.append("")
            
            # SECCIÓN 2: INQUILINOS INACTIVOS
            if inactive:
                report.append("=" * 60)
                report.append("INQUILINOS INACTIVOS")
                report.append("=" * 60)
                report.append("")
                
                for tenant in inactive:
                    report.append(format_tenant(tenant))
            
            self._show_report_window(
                "Reporte de Inquilinos",
                "\n".join(report),
                "tenants_consolidated"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def _generate_occupation_history_report(self):
        """Genera reporte de historial de ocupación"""
        try:
            self._reload_all_data()
            
            tenants = tenant_service.get_all_tenants()
            apartments = apartment_service.get_all_apartments()
            
            report = []
            report.append("=" * 70)
            report.append("HISTORIAL DE OCUPACIÓN - GESTIÓN DE INQUILINOS")
            report.append("=" * 70)
            report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            report.append("")
            
            # Agrupar por apartamento
            apt_tenants = {}
            for tenant in tenants:
                apt_id = tenant.get('apartamento')
                if apt_id:
                    if apt_id not in apt_tenants:
                        apt_tenants[apt_id] = []
                    apt_tenants[apt_id].append(tenant)
            
            for apt in apartments:
                apt_id = apt.get('id')
                apt_display = f"{apt.get('unit_type', 'Apto')}: {apt.get('number', 'N/A')}"
                
                report.append("=" * 70)
                report.append(f"APARTAMENTO: {apt_display}")
                report.append("=" * 70)
                
                if apt_id in apt_tenants:
                    for tenant in apt_tenants[apt_id]:
                        report.append(f"Inquilino: {tenant.get('nombre', 'N/A')}")
                        fecha_ingreso = tenant.get('fecha_ingreso', 'N/A')
                        if fecha_ingreso and fecha_ingreso != 'N/A':
                            try:
                                fecha_dt = datetime.fromisoformat(fecha_ingreso)
                                fecha_ingreso = fecha_dt.strftime('%d/%m/%Y')
                            except:
                                pass
                        report.append(f"  Fecha de ingreso: {fecha_ingreso}")
                        
                        if tenant.get('estado_pago') == 'inactivo':
                            fecha_salida = tenant.get('fecha_desactivacion', 'N/A')
                            if fecha_salida and fecha_salida != 'N/A':
                                try:
                                    fecha_dt = datetime.fromisoformat(fecha_salida)
                                    fecha_salida = fecha_dt.strftime('%d/%m/%Y')
                                except:
                                    pass
                            report.append(f"  Fecha de salida: {fecha_salida}")
                            report.append(f"  Motivo: {tenant.get('motivo_desactivacion', 'N/A')}")
                        else:
                            report.append(f"  Estado: Activo")
                        report.append("")
                else:
                    report.append("Estado: Disponible")
                    report.append("")
            
            self._show_report_window(
                "Historial de Ocupación",
                "\n".join(report),
                "occupation_history"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def _generate_documents_report(self):
        """Genera reporte de documentos de inquilinos"""
        try:
            self._reload_all_data()
            
            tenants = tenant_service.get_all_tenants()
            active_tenants = [t for t in tenants if t.get('estado_pago') != 'inactivo']
            
            report = []
            report.append("=" * 70)
            report.append("REPORTE DE DOCUMENTOS - GESTIÓN DE INQUILINOS")
            report.append("=" * 70)
            report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            report.append("")
            report.append(f"Total de inquilinos activos: {len(active_tenants)}")
            report.append("")
            
            for tenant in active_tenants:
                apt = self._get_apartment_display(tenant)
                report.append(f"Inquilino: {tenant.get('nombre', 'N/A')} - {apt}")
                report.append(f"  Documento de identidad: {tenant.get('numero_documento', 'N/A')}")
                
                # Verificar documentos
                has_contract = tenant.get('contrato', '') != ''
                has_ficha = tenant.get('ficha', '') != ''
                
                report.append(f"  Contrato: {'✓ Presente' if has_contract else '✗ No registrado'}")
                report.append(f"  Ficha: {'✓ Presente' if has_ficha else '✗ No registrado'}")
                
                # Documentos adicionales
                documentos = tenant.get('documentos', [])
                if documentos:
                    report.append(f"  Documentos adicionales: {len(documentos)}")
                    for doc in documentos:
                        report.append(f"    - {doc.get('tipo', 'N/A')}: {doc.get('archivo', 'N/A')}")
                else:
                    report.append(f"  Documentos adicionales: Ninguno")
                
                report.append("")
            
            self._show_report_window(
                "Reporte de Documentos",
                "\n".join(report),
                "documents"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def _generate_emergency_contacts_report(self):
        """Genera reporte de contactos de emergencia"""
        try:
            self._reload_all_data()
            
            tenants = tenant_service.get_all_tenants()
            active_tenants = [t for t in tenants if t.get('estado_pago') != 'inactivo']
            
            report = []
            report.append("=" * 70)
            report.append("CONTACTOS DE EMERGENCIA - GESTIÓN DE INQUILINOS")
            report.append("=" * 70)
            report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            report.append("")
            report.append(f"Total de inquilinos activos: {len(active_tenants)}")
            report.append("")
            
            for tenant in active_tenants:
                apt = self._get_apartment_display(tenant)
                report.append(f"Inquilino: {tenant.get('nombre', 'N/A')} - {apt}")
                report.append(f"  Teléfono: {tenant.get('telefono', 'N/A')}")
                report.append(f"  Email: {tenant.get('email', 'N/A')}")
                
                # Contacto de emergencia (campos planos y/o anidados)
                contacto_emergencia = tenant.get('contacto_emergencia') or {}
                nombre_ec = (contacto_emergencia.get('nombre') if isinstance(contacto_emergencia, dict) else None) or tenant.get('contacto_emergencia_nombre', '').strip()
                telefono_ec = (contacto_emergencia.get('telefono') if isinstance(contacto_emergencia, dict) else None) or tenant.get('contacto_emergencia_telefono', '').strip()
                relacion_ec = (contacto_emergencia.get('relacion') if isinstance(contacto_emergencia, dict) else None) or tenant.get('contacto_emergencia_parentesco', '').strip()
                if nombre_ec or telefono_ec:
                    report.append(f"  Contacto de Emergencia:")
                    report.append(f"    Nombre: {nombre_ec or 'N/A'}")
                    report.append(f"    Teléfono: {telefono_ec or 'N/A'}")
                    if relacion_ec:
                        report.append(f"    Relación: {relacion_ec}")
                else:
                    report.append(f"  Contacto de Emergencia: No registrado")
                
                report.append("")
            
            self._show_report_window(
                "Contactos de Emergencia",
                "\n".join(report),
                "emergency_contacts"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def _generate_financial_summary_report(self):
        """Genera reporte de resumen financiero por inquilino"""
        try:
            self._reload_all_data()
            
            tenants = tenant_service.get_all_tenants()
            active_tenants = [t for t in tenants if t.get('estado_pago') != 'inactivo']
            
            report = []
            report.append("=" * 70)
            report.append("RESUMEN FINANCIERO POR INQUILINO - GESTIÓN DE INQUILINOS")
            report.append("=" * 70)
            report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            report.append("")
            
            total_arriendos = 0
            total_pagado = 0
            
            for tenant in active_tenants:
                apt = self._get_apartment_display(tenant)
                arriendo = float(tenant.get('valor_arriendo', 0))
                total_arriendos += arriendo
                
                report.append(f"Inquilino: {tenant.get('nombre', 'N/A')} - {apt}")
                report.append(f"  Arriendo mensual: ${arriendo:,.2f}")
                
                # Calcular total pagado
                payments = payment_service.get_payments_by_tenant(tenant.get('id'))
                total_tenant_paid = sum(float(p.get('monto', 0)) for p in payments)
                total_pagado += total_tenant_paid
                
                report.append(f"  Total pagado: ${total_tenant_paid:,.2f}")
                report.append(f"  Número de pagos: {len(payments)}")
                
                if payments:
                    last_payment = max(payments, key=lambda p: p.get('fecha', ''))
                    report.append(f"  Último pago: {last_payment.get('fecha', 'N/A')} - ${float(last_payment.get('monto', 0)):,.2f}")
                
                report.append("")
            
            report.append("=" * 70)
            report.append("RESUMEN GENERAL")
            report.append("=" * 70)
            report.append(f"Total de arriendos mensuales: ${total_arriendos:,.2f}")
            report.append(f"Total pagado (histórico): ${total_pagado:,.2f}")
            report.append(f"Inquilinos activos: {len(active_tenants)}")
            
            self._show_report_window(
                "Resumen Financiero por Inquilino",
                "\n".join(report),
                "financial_summary"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def _generate_availability_report(self):
        """Genera reporte de disponibilidad de apartamentos"""
        try:
            self._reload_all_data()
            
            apartments = apartment_service.get_all_apartments()
            tenants = tenant_service.get_all_tenants()
            
            # Crear mapa de ocupación
            occupied_apts = {}
            for tenant in tenants:
                if tenant.get('estado_pago') != 'inactivo':
                    apt_id = tenant.get('apartamento')
                    if apt_id:
                        occupied_apts[apt_id] = tenant
            
            report = []
            report.append("=" * 70)
            report.append("DISPONIBILIDAD DE APARTAMENTOS - GESTIÓN DE INQUILINOS")
            report.append("=" * 70)
            report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            report.append("")
            
            available = []
            occupied = []
            
            for apt in apartments:
                apt_id = apt.get('id')
                apt_display = f"{apt.get('unit_type', 'Apto')}: {apt.get('number', 'N/A')}"
                
                if apt_id in occupied_apts:
                    tenant = occupied_apts[apt_id]
                    occupied.append((apt_display, tenant))
                else:
                    available.append(apt_display)
            
            report.append("=" * 70)
            report.append("APARTAMENTOS DISPONIBLES")
            report.append("=" * 70)
            report.append(f"Total: {len(available)}")
            report.append("")
            for apt in available:
                report.append(f"  • {apt}")
            report.append("")
            
            report.append("=" * 70)
            report.append("APARTAMENTOS OCUPADOS")
            report.append("=" * 70)
            report.append(f"Total: {len(occupied)}")
            report.append("")
            for apt_display, tenant in occupied:
                report.append(f"  • {apt_display}")
                report.append(f"    Inquilino: {tenant.get('nombre', 'N/A')}")
                fecha_ingreso = tenant.get('fecha_ingreso', 'N/A')
                if fecha_ingreso and fecha_ingreso != 'N/A':
                    try:
                        fecha_dt = datetime.fromisoformat(fecha_ingreso)
                        fecha_ingreso = fecha_dt.strftime('%d/%m/%Y')
                    except:
                        pass
                report.append(f"    Fecha de ingreso: {fecha_ingreso}")
                report.append("")
            
            self._show_report_window(
                "Disponibilidad de Apartamentos",
                "\n".join(report),
                "availability"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")
    
    def _get_apartment_display(self, tenant):
        """Obtiene la representación del apartamento de un inquilino"""
        apartment_id = tenant.get('apartamento', None)
        if apartment_id is not None:
            try:
                apartment_id_int = int(apartment_id)
                apt = apartment_service.get_apartment_by_id(apartment_id_int) if hasattr(apartment_service, 'get_apartment_by_id') else None
                if not apt:
                    all_apts = apartment_service.get_all_apartments()
                    apt = next((a for a in all_apts if a.get('id') == apartment_id_int), None)
                if apt:
                    apt_number = apt.get('number', 'N/A')
                    apt_type = apt.get('unit_type', 'Apartamento Estándar')
                    if apt_type == "Apartamento Estándar":
                        return f"Apto: {apt_number}"
                    else:
                        return f"{apt_type}: {apt_number}"
            except:
                pass
        return "Sin apartamento asignado"
    
    def _reset_report_cards_appearance(self):
        """Restaura el color normal de los cards (por si el hover quedó pegado al cerrar la ventana del reporte)."""
        def set_bg_recursive(widget, bg):
            try:
                widget.configure(bg=bg)
            except (tk.TclError, Exception):
                pass
            for child in widget.winfo_children():
                set_bg_recursive(child, bg)
        for card in getattr(self, "_report_cards", []):
            try:
                if not card.winfo_exists():
                    continue
                bg = getattr(card, "_card_normal_bg", None)
                if bg is None:
                    continue
                set_bg_recursive(card, bg)
            except tk.TclError:
                pass

    def _show_report_window(self, title, content, report_type):
        """Muestra el reporte en una ventana con opciones de exportar"""
        window = tk.Toplevel(self)
        window.title(title)
        window.geometry("800x600")
        window.transient(self)
        window.grab_set()

        def on_report_window_closed():
            self.after(80, self._reset_report_cards_appearance)

        window.bind("<Destroy>", lambda e: on_report_window_closed())
        
        # Header - azul para mantener tonalidad azul del módulo
        header_bg = "#1e40af"  # blue-800 - azul oscuro para header
        header = tk.Frame(window, bg=header_bg, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg=header_bg,
            fg="white"
        ).pack(side="left", padx=15, pady=12)
        
        # Botones de acción - azul para mantener tonalidad azul
        btn_frame = tk.Frame(header, bg=header_bg)
        btn_frame.pack(side="right", padx=15)
        
        def export_csv():
            self._export_to_csv(content, title, report_type)
        
        def export_txt():
            self._export_to_txt(content, title, report_type)
        
        # Colores y hover (azul módulo inquilinos; Cerrar rojo con hover)
        colors = get_module_colors("inquilinos")
        btn_export_bg = colors.get("primary", "#2563eb")
        btn_export_hover = colors.get("hover", "#1e40af")
        btn_close_bg = "#dc2626"
        btn_close_hover = "#b91c1c"
        btn_opts = dict(font=("Segoe UI", 9), fg="white", relief="flat", padx=14, pady=6, cursor="hand2")

        btn_csv = tk.Button(btn_frame, text="💾 Exportar CSV", bg=btn_export_bg, **btn_opts, command=export_csv)
        btn_csv.pack(side="left", padx=5)
        btn_csv.bind("<Enter>", lambda e: btn_csv.config(bg=btn_export_hover))
        btn_csv.bind("<Leave>", lambda e: btn_csv.config(bg=btn_export_bg))

        btn_txt = tk.Button(btn_frame, text="📄 Exportar TXT", bg=btn_export_bg, **btn_opts, command=export_txt)
        btn_txt.pack(side="left", padx=5)
        btn_txt.bind("<Enter>", lambda e: btn_txt.config(bg=btn_export_hover))
        btn_txt.bind("<Leave>", lambda e: btn_txt.config(bg=btn_export_bg))

        btn_close = tk.Button(btn_frame, text="× Cerrar", bg=btn_close_bg, width=10, **btn_opts, command=window.destroy)
        btn_close.pack(side="left", padx=5)
        btn_close.bind("<Enter>", lambda e: btn_close.config(bg=btn_close_hover))
        btn_close.bind("<Leave>", lambda e: btn_close.config(bg=btn_close_bg))
        
        # Contenido con scroll
        text_frame = tk.Frame(window)
        text_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        text_widget = tk.Text(
            text_frame,
            font=("Consolas", 10),
            wrap="word",
            bg="#ffffff",
            fg="#000000"
        )
        text_widget.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.insert("1.0", content)
        text_widget.config(state="disabled")
    
    def _export_to_csv(self, content, title, report_type):
        """Exporta el reporte a CSV con el mismo contenido que el TXT: una fila por línea del informe."""
        try:
            from manager.app.paths_config import EXPORTS_DIR, ensure_dirs
            ensure_dirs()
            filename = f"tenant_management_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = EXPORTS_DIR / filename

            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                for line in content.split('\n'):
                    writer.writerow([line])

            self._show_export_success_dialog(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar CSV: {str(e)}")
    
    def _show_export_success_dialog(self, filepath):
        """Ventana de confirmación igual que en administración: ruta, Copiar, Abrir carpeta, Abrir archivo, Aceptar."""
        path = Path(filepath) if not isinstance(filepath, Path) else filepath
        win = tk.Toplevel(self.winfo_toplevel())
        win.title("Exportar")
        win.geometry("520x220")
        win.transient(self.winfo_toplevel())
        win.resizable(True, False)
        win.grab_set()
        content = tk.Frame(win, padx=24, pady=20)
        content.pack(fill="both", expand=True)
        top = tk.Frame(content)
        top.pack(fill="x")
        tk.Label(top, text="ℹ", font=("Segoe UI", 28), fg="#2563eb").pack(side="left", padx=(0, 12))
        msg = tk.Frame(top)
        msg.pack(side="left", fill="x", expand=True)
        tk.Label(msg, text="Exportación exitosa. Archivo guardado en:", font=("Segoe UI", 11)).pack(anchor="w")
        path_var = tk.StringVar(value=str(path))
        path_entry = tk.Entry(msg, textvariable=path_var, font=("Segoe UI", 10))
        path_entry.pack(fill="x", pady=(8, 0))
        path_entry.bind("<Key>", lambda e: "break")
        btns = tk.Frame(content)
        btns.pack(fill="x", pady=(20, 0))

        def copy_path():
            win.clipboard_clear()
            win.clipboard_append(str(path))

        def open_folder():
            folder = str(path.resolve().parent)
            if os.name == "nt":
                os.startfile(folder)
            else:
                import subprocess
                subprocess.run(["xdg-open", folder], check=False)

        def open_file():
            p = str(path.resolve())
            if os.name == "nt":
                os.startfile(p)
            else:
                import subprocess
                subprocess.run(["xdg-open", p], check=False)

        tk.Button(btns, text="📋 Copiar", font=("Segoe UI", 10), bg="#2563eb", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=copy_path).pack(side="left", padx=(0, 8))
        tk.Button(btns, text="📁 Abrir carpeta", font=("Segoe UI", 10), bg="#6b7280", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=open_folder).pack(side="left", padx=(0, 8))
        tk.Button(btns, text="📄 Abrir archivo", font=("Segoe UI", 10), bg="#059669", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=open_file).pack(side="left", padx=(0, 8))
        tk.Button(btns, text="Aceptar", font=("Segoe UI", 10), bg="#2563eb", fg="white", relief="flat", padx=14, pady=6, cursor="hand2", command=win.destroy).pack(side="right")

    def _export_to_txt(self, content, title, report_type):
        """Exporta el reporte a TXT"""
        try:
            from manager.app.paths_config import EXPORTS_DIR, ensure_dirs
            ensure_dirs()
            filename = f"tenant_management_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = EXPORTS_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                f.write(content)

            self._show_export_success_dialog(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar TXT: {str(e)}")
