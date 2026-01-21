"""
Vista completa de reportes para Building Manager Pro
Sistema escalable con múltiples tipos de reportes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
import csv
from pathlib import Path

from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import ModernButton, ModernCard
from manager.app.services.tenant_service import tenant_service
from manager.app.services.payment_service import payment_service
from manager.app.services.apartment_service import apartment_service
from manager.app.services.building_service import building_service


class ReportsView(tk.Frame):
    """Vista completa de reportes del sistema"""
    
    def __init__(self, parent, on_back: Callable = None):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_back = on_back
        
        # Recargar datos antes de generar reportes
        self._reload_all_data()
        
        self._create_layout()
    
    def _reload_all_data(self):
        """Recarga todos los datos necesarios para los reportes"""
        try:
            tenant_service._load_data()
            payment_service._load_data()
            apartment_service._load_data()
            building_service._load_buildings()
        except Exception as e:
            print(f"Error al recargar datos: {e}")
    
    def _create_layout(self):
        """Crea el layout principal de la vista de reportes"""
        # Header
        header = tk.Frame(self, bg="#f8f9fa", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg="#f8f9fa")
        title_frame.pack(side="left", padx=15, fill="y", expand=True)
        
        tk.Label(
            title_frame,
            text="📊 Reportes y Análisis",
            font=("Segoe UI", 18, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        ).pack(side="left", pady=15)
        
        if self.on_back:
            ModernButton(
                header,
                text="← Volver",
                style="secondary",
                command=self.on_back
            ).pack(side="right", padx=15, pady=15)
        
        # Contenedor principal sin scroll (ya no es necesario)
        main_container = tk.Frame(self, bg="#ffffff")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Contenido de reportes directamente en el contenedor principal
        self._create_reports_content(main_container)
    
    def _create_reports_content(self, parent):
        """Crea el contenido de los reportes"""
        # Título de sección
        tk.Label(
            parent,
            text="Seleccione el tipo de reporte que desea generar:",
            font=("Segoe UI", 12),
            bg="#ffffff",
            fg="#666"
        ).pack(anchor="w", pady=(0, 20))
        
        # Contenedor principal que usa todo el espacio disponible
        cards_container = tk.Frame(parent, bg="#ffffff")
        cards_container.pack(fill="both", expand=True)
        
        # Grid de cards - 3 columnas que se ajustan al espacio disponible
        cards_grid = tk.Frame(cards_container, bg="#ffffff")
        cards_grid.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Calcular y configurar el tamaño uniforme de las columnas
        # Configurar grid para que las columnas se distribuyan equitativamente
        # Reducir minsize para permitir más expansión horizontal
        cards_grid.columnconfigure(0, weight=1, uniform="cards", minsize=280)
        cards_grid.columnconfigure(1, weight=1, uniform="cards", minsize=280)
        cards_grid.columnconfigure(2, weight=1, uniform="cards", minsize=280)
        
        # Definir los reportes
        reports = [
            ("📈 Reporte de Ocupación", 
             "Muestra estadísticas de ocupación de apartamentos, porcentajes de ocupación y disponibilidad.",
             "#2196F3", 
             self._generate_occupation_report),
            ("💰 Reporte de Ingresos", 
             "Análisis de pagos recibidos, ingresos por período y proyecciones.",
             "#4CAF50", 
             self._generate_income_report),
            ("⚠️ Reporte de Mora", 
             "Lista de inquilinos con pagos pendientes o en mora con detalles.",
             "#FF9800", 
             self._generate_overdue_report),
            ("👥 Reporte de Inquilinos", 
             "Información consolidada de todos los inquilinos activos e inactivos.",
             "#9C27B0", 
             self._generate_tenants_report),
            ("📊 Reporte Financiero", 
             "Vista consolidada de ingresos, gastos y estado financiero general.",
             "#F44336", 
             self._generate_financial_report),
            ("🏢 Reporte de Apartamentos", 
             "Estado detallado de todos los apartamentos con sus características.",
             "#00BCD4", 
             self._generate_apartments_report)
        ]
        
        # Colocar cards en grid 3 columnas
        row = 0
        col = 0
        for title, description, color, command in reports:
            card = self._create_report_card(
                cards_grid,
                title,
                description,
                color,
                command
            )
            # Usar sticky="nsew" para que los cards se expandan uniformemente
            card.grid(row=row, column=col, padx=10, pady=8, sticky="nsew")
            
            # Avanzar a la siguiente posición
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # Configurar las filas para que se distribuyan equitativamente
        # Reducir minsize para que quepan sin scroll vertical
        for r in range(row + 1):
            cards_grid.rowconfigure(r, weight=1, uniform="rows", minsize=160)
    
    def _create_report_card(self, parent, title, description, color, command):
        """Crea una tarjeta de reporte que se ajusta uniformemente al espacio disponible"""
        card = tk.Frame(
            parent,
            bg="white",
            relief="raised",
            bd=2
        )
        # El card se expandirá uniformemente con sticky="nsew" en el grid
        
        content = tk.Frame(card, bg="white")
        # Reducir padding vertical para hacer los cards más compactos
        content.pack(fill="both", expand=True, padx=14, pady=10)
        
        # Contenedor para título con wraplength dinámico
        title_frame = tk.Frame(content, bg="white")
        title_frame.pack(anchor="w", pady=(0, 8), fill="x")
        
        # Icono y título - sin wraplength para que se ajuste al ancho disponible
        title_label = tk.Label(
            title_frame,
            text=title,
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg=color,
            anchor="w",
            justify="left",
            wraplength=1  # Se ajustará automáticamente al ancho del frame
        )
        title_label.pack(anchor="w", fill="x")
        
        # Descripción - se ajusta al ancho disponible, más compacta
        desc_label = tk.Label(
            content,
            text=description,
            font=("Segoe UI", 9),
            bg="white",
            fg="#666",
            justify="left",
            anchor="w",
            wraplength=1  # Se ajustará automáticamente
        )
        desc_label.pack(anchor="w", pady=(0, 10), fill="x", expand=True)
        
        # Botón generar - siempre al fondo con tamaño consistente, más compacto
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(fill="x", side="bottom")
        
        btn = tk.Button(
            btn_frame,
            text="Generar Reporte",
            font=("Segoe UI", 9, "bold"),
            bg=color,
            fg="white",
            relief="flat",
            padx=15,
            pady=6,
            cursor="hand2",
            command=command
        )
        btn.pack(fill="x")
        
        # Función para actualizar wraplength cuando el card cambie de tamaño
        def update_wraplength(event=None):
            if event:
                card_width = card.winfo_width()
                if card_width > 20:  # Solo actualizar si el card tiene un tamaño válido
                    # Calcular wraplength considerando el padding
                    available_width = card_width - 32  # 16px padding a cada lado
                    title_label.config(wraplength=max(available_width, 100))
                    desc_label.config(wraplength=max(available_width, 100))
        
        card.bind("<Configure>", update_wraplength)
        
        # Hover effect
        def on_enter(event):
            card.configure(bg="#f5f5f5")
            content.configure(bg="#f5f5f5")
            title_frame.configure(bg="#f5f5f5")
            title_label.configure(bg="#f5f5f5")
            desc_label.configure(bg="#f5f5f5")
            btn_frame.configure(bg="#f5f5f5")
        
        def on_leave(event):
            card.configure(bg="white")
            content.configure(bg="white")
            title_frame.configure(bg="white")
            title_label.configure(bg="white")
            desc_label.configure(bg="white")
            btn_frame.configure(bg="white")
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        content.bind("<Enter>", on_enter)
        content.bind("<Leave>", on_leave)
        
        return card
    
    # ==================== GENERADORES DE REPORTES ====================
    
    def _generate_occupation_report(self):
        """Genera reporte de ocupación"""
        try:
            self._reload_all_data()
            
            apartments = apartment_service.get_all_apartments()
            tenants = tenant_service.get_all_tenants()
            
            total_apartments = len(apartments)
            occupied = sum(1 for apt in apartments if apt.get('status') == 'Ocupado')
            available = sum(1 for apt in apartments if apt.get('status') == 'Disponible')
            maintenance = sum(1 for apt in apartments if apt.get('status') == 'En Mantenimiento')
            
            occupation_rate = (occupied / total_apartments * 100) if total_apartments > 0 else 0
            
            # Crear ventana de reporte
            self._show_report_window(
                "Reporte de Ocupación",
                self._format_occupation_report(
                    total_apartments, occupied, available, maintenance, occupation_rate, apartments, tenants
                ),
                "occupation"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de ocupación: {str(e)}")
    
    def _generate_income_report(self):
        """Genera reporte de ingresos"""
        try:
            self._reload_all_data()
            
            payments = payment_service.get_all_payments()
            
            if not payments:
                messagebox.showinfo("Sin datos", "No hay pagos registrados para generar el reporte.")
                return
            
            # Calcular totales
            total_income = sum(float(p.get('monto', 0)) for p in payments)
            
            # Filtrar por período
            now = datetime.now()
            this_month = [p for p in payments if self._is_this_month(p.get('fecha_pago', ''))]
            this_year = [p for p in payments if self._is_this_year(p.get('fecha_pago', ''))]
            
            monthly_income = sum(float(p.get('monto', 0)) for p in this_month)
            yearly_income = sum(float(p.get('monto', 0)) for p in this_year)
            
            # Métodos de pago
            payment_methods = {}
            for p in payments:
                method = p.get('metodo', 'No especificado')
                payment_methods[method] = payment_methods.get(method, 0) + float(p.get('monto', 0))
            
            self._show_report_window(
                "Reporte de Ingresos",
                self._format_income_report(
                    total_income, monthly_income, yearly_income, len(payments), payment_methods
                ),
                "income"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de ingresos: {str(e)}")
    
    def _generate_overdue_report(self):
        """Genera reporte de mora"""
        try:
            self._reload_all_data()
            
            tenants = tenant_service.get_all_tenants()
            tenant_service.recalculate_all_payment_statuses()
            tenant_service._load_data()
            tenants = tenant_service.get_all_tenants()
            
            overdue_tenants = [t for t in tenants if t.get('estado_pago') == 'moroso']
            pending_tenants = [t for t in tenants if t.get('estado_pago') == 'pendiente_registro']
            
            total_overdue = len(overdue_tenants)
            total_pending = len(pending_tenants)
            
            self._show_report_window(
                "Reporte de Mora",
                self._format_overdue_report(overdue_tenants, pending_tenants, total_overdue, total_pending),
                "overdue"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de mora: {str(e)}")
    
    def _generate_tenants_report(self):
        """Genera reporte de inquilinos"""
        try:
            self._reload_all_data()
            
            tenants = tenant_service.get_all_tenants()
            active = [t for t in tenants if t.get('estado_pago') != 'inactivo']
            inactive = [t for t in tenants if t.get('estado_pago') == 'inactivo']
            
            self._show_report_window(
                "Reporte de Inquilinos",
                self._format_tenants_report(tenants, active, inactive),
                "tenants"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de inquilinos: {str(e)}")
    
    def _generate_financial_report(self):
        """Genera reporte financiero consolidado"""
        try:
            self._reload_all_data()
            
            payments = payment_service.get_all_payments()
            total_income = sum(float(p.get('monto', 0)) for p in payments)
            
            # Intentar cargar gastos si existe el servicio
            total_expenses = 0
            try:
                from manager.app.services.expense_service import expense_service
                expenses = expense_service.get_all_expenses()
                total_expenses = sum(float(e.get('monto', 0)) for e in expenses)
            except:
                pass
            
            net_income = total_income - total_expenses
            
            self._show_report_window(
                "Reporte Financiero Consolidado",
                self._format_financial_report(total_income, total_expenses, net_income, len(payments)),
                "financial"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte financiero: {str(e)}")
    
    def _generate_apartments_report(self):
        """Genera reporte de apartamentos"""
        try:
            self._reload_all_data()
            
            apartments = apartment_service.get_all_apartments()
            tenants = tenant_service.get_all_tenants()
            
            self._show_report_window(
                "Reporte de Apartamentos",
                self._format_apartments_report(apartments, tenants),
                "apartments"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte de apartamentos: {str(e)}")
    
    # ==================== FORMATEADORES DE REPORTES ====================
    
    def _format_occupation_report(self, total, occupied, available, maintenance, rate, apartments, tenants):
        """Formatea el reporte de ocupación"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE OCUPACIÓN")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append("RESUMEN GENERAL:")
        report.append(f"  • Total de apartamentos: {total}")
        report.append(f"  • Ocupados: {occupied}")
        report.append(f"  • Disponibles: {available}")
        report.append(f"  • En mantenimiento: {maintenance}")
        report.append(f"  • Tasa de ocupación: {rate:.2f}%")
        report.append("")
        report.append("DETALLE POR APARTAMENTO:")
        report.append("-" * 60)
        
        for apt in apartments:
            status = apt.get('status', 'N/A')
            apt_num = apt.get('number', 'N/A')
            tenant_name = "Sin asignar"
            
            # Buscar inquilino asignado
            for tenant in tenants:
                if str(tenant.get('apartamento', '')) == str(apt.get('id', '')):
                    tenant_name = tenant.get('nombre', 'Sin asignar')
                    break
            
            report.append(f"Apartamento {apt_num}: {status} - Inquilino: {tenant_name}")
        
        return "\n".join(report)
    
    def _format_income_report(self, total, monthly, yearly, count, methods):
        """Formatea el reporte de ingresos"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE INGRESOS")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append("RESUMEN FINANCIERO:")
        report.append(f"  • Ingresos totales: ${total:,.2f}")
        report.append(f"  • Ingresos del mes actual: ${monthly:,.2f}")
        report.append(f"  • Ingresos del año actual: ${yearly:,.2f}")
        report.append(f"  • Total de pagos registrados: {count}")
        report.append("")
        report.append("INGRESOS POR MÉTODO DE PAGO:")
        report.append("-" * 60)
        for method, amount in methods.items():
            report.append(f"  • {method}: ${amount:,.2f}")
        
        return "\n".join(report)
    
    def _format_overdue_report(self, overdue, pending, total_overdue, total_pending):
        """Formatea el reporte de mora"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE MORA Y PAGOS PENDIENTES")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append(f"RESUMEN:")
        report.append(f"  • Inquilinos en mora: {total_overdue}")
        report.append(f"  • Inquilinos con pago pendiente: {total_pending}")
        report.append("")
        
        if overdue:
            report.append("INQUILINOS EN MORA:")
            report.append("-" * 60)
            for tenant in overdue:
                # Obtener el número del apartamento en lugar del ID
                apartment_display = 'N/A'
                apartment_id = tenant.get('apartamento', None)
                if apartment_id is not None:
                    try:
                        apartment_id_int = int(apartment_id)
                        apt = apartment_service.get_apartment_by_id(apartment_id_int) if hasattr(apartment_service, 'get_apartment_by_id') else None
                        if not apt:
                            all_apts = apartment_service.get_all_apartments()
                            apt = next((a for a in all_apts if a.get('id') == apartment_id_int), None)
                        if apt and 'number' in apt:
                            apartment_display = apt.get('number', 'N/A')
                        else:
                            apartment_display = str(apartment_id)
                    except Exception:
                        apartment_display = str(apartment_id)
                
                report.append(f"  • {tenant.get('nombre', 'N/A')} - Apartamento: {apartment_display}")
                report.append(f"    Arriendo: ${float(tenant.get('valor_arriendo', 0)):,.2f}")
            report.append("")
        
        if pending:
            report.append("INQUILINOS CON PAGO PENDIENTE:")
            report.append("-" * 60)
            for tenant in pending:
                # Obtener el número del apartamento en lugar del ID
                apartment_display = 'N/A'
                apartment_id = tenant.get('apartamento', None)
                if apartment_id is not None:
                    try:
                        apartment_id_int = int(apartment_id)
                        apt = apartment_service.get_apartment_by_id(apartment_id_int) if hasattr(apartment_service, 'get_apartment_by_id') else None
                        if not apt:
                            all_apts = apartment_service.get_all_apartments()
                            apt = next((a for a in all_apts if a.get('id') == apartment_id_int), None)
                        if apt and 'number' in apt:
                            apartment_display = apt.get('number', 'N/A')
                        else:
                            apartment_display = str(apartment_id)
                    except Exception:
                        apartment_display = str(apartment_id)
                
                report.append(f"  • {tenant.get('nombre', 'N/A')} - Apartamento: {apartment_display}")
        
        return "\n".join(report)
    
    def _format_tenants_report(self, all_tenants, active, inactive):
        """Formatea el reporte de inquilinos"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE INQUILINOS")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append(f"RESUMEN:")
        report.append(f"  • Total de inquilinos: {len(all_tenants)}")
        report.append(f"  • Inquilinos activos: {len(active)}")
        report.append(f"  • Inquilinos inactivos: {len(inactive)}")
        report.append("")
        report.append("DETALLE DE INQUILINOS:")
        report.append("-" * 60)
        
        for tenant in all_tenants:
            status = tenant.get('estado_pago', 'N/A')
            status_map = {
                'al_dia': 'Al Día',
                'pendiente_registro': 'Pendiente Registro',
                'moroso': 'En Mora',
                'inactivo': 'Inactivo'
            }
            status_text = status_map.get(status, status)
            
            # Obtener el número del apartamento en lugar del ID
            apartment_display = 'N/A'
            apartment_id = tenant.get('apartamento', None)
            if apartment_id is not None:
                try:
                    apartment_id_int = int(apartment_id)
                    apt = apartment_service.get_apartment_by_id(apartment_id_int) if hasattr(apartment_service, 'get_apartment_by_id') else None
                    if not apt:
                        all_apts = apartment_service.get_all_apartments()
                        apt = next((a for a in all_apts if a.get('id') == apartment_id_int), None)
                    if apt and 'number' in apt:
                        apartment_display = apt.get('number', 'N/A')
                    else:
                        apartment_display = str(apartment_id)
                except Exception:
                    apartment_display = str(apartment_id)
            
            report.append(f"Nombre: {tenant.get('nombre', 'N/A')}")
            report.append(f"  • Apartamento: {apartment_display}")
            report.append(f"  • Documento: {tenant.get('numero_documento', 'N/A')}")
            report.append(f"  • Teléfono: {tenant.get('telefono', 'N/A')}")
            report.append(f"  • Estado: {status_text}")
            report.append(f"  • Arriendo: ${float(tenant.get('valor_arriendo', 0)):,.2f}")
            report.append("")
        
        return "\n".join(report)
    
    def _format_financial_report(self, income, expenses, net, payment_count):
        """Formatea el reporte financiero"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE FINANCIERO CONSOLIDADO")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append("ESTADO FINANCIERO:")
        report.append(f"  • Total de ingresos: ${income:,.2f}")
        report.append(f"  • Total de gastos: ${expenses:,.2f}")
        report.append(f"  • Ingreso neto: ${net:,.2f}")
        report.append(f"  • Total de pagos procesados: {payment_count}")
        report.append("")
        
        if net < 0:
            report.append("⚠️  ADVERTENCIA: Los gastos superan los ingresos")
        elif net == 0:
            report.append("ℹ️  Los ingresos y gastos están equilibrados")
        else:
            report.append(f"✓ Balance positivo: ${net:,.2f}")
        
        return "\n".join(report)
    
    def _format_apartments_report(self, apartments, tenants):
        """Formatea el reporte de apartamentos con información detallada"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE APARTAMENTOS")
        report.append("=" * 60)
        report.append(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        report.append("")
        report.append(f"Total de apartamentos: {len(apartments)}")
        report.append("")
        report.append("DETALLE DE APARTAMENTOS:")
        report.append("-" * 60)
        
        for apt in apartments:
            apt_num = apt.get('number', 'N/A')
            status = apt.get('status', 'N/A')
            rent = apt.get('base_rent', '0')
            unit_type = apt.get('unit_type', 'Apartamento Estándar')
            rooms = apt.get('rooms', 'N/A')
            bathrooms = apt.get('bathrooms', 'N/A')
            area = apt.get('area', 'N/A')
            floor = apt.get('floor', 'N/A')
            tenant_name = "Sin asignar"
            
            # Buscar inquilino
            for tenant in tenants:
                if str(tenant.get('apartamento', '')) == str(apt.get('id', '')):
                    tenant_name = tenant.get('nombre', 'Sin asignar')
                    break
            
            report.append(f"Apartamento {apt_num}:")
            report.append(f"  • Tipo: {unit_type}")
            report.append(f"  • Estado: {status}")
            report.append(f"  • Piso: {floor}")
            report.append(f"  • Habitaciones: {rooms}")
            report.append(f"  • Baños: {bathrooms}")
            if area and str(area) != 'N/A' and str(area) != '0':
                try:
                    area_float = float(area)
                    report.append(f"  • Área: {area_float:,.0f} m²")
                except:
                    report.append(f"  • Área: {area} m²")
            else:
                report.append(f"  • Área: No especificada")
            report.append(f"  • Arriendo base: ${float(rent):,.2f}")
            report.append(f"  • Inquilino: {tenant_name}")
            report.append("")
        
        return "\n".join(report)
    
    # ==================== VENTANA DE VISUALIZACIÓN ====================
    
    def _show_report_window(self, title, content, report_type):
        """Muestra el reporte en una ventana con opciones de exportar"""
        window = tk.Toplevel(self)
        window.title(title)
        window.geometry("800x600")
        window.transient(self)
        window.grab_set()
        
        # Header
        header = tk.Frame(window, bg="#1976d2", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg="#1976d2",
            fg="white"
        ).pack(side="left", padx=15, pady=12)
        
        # Botones de acción
        btn_frame = tk.Frame(header, bg="#1976d2")
        btn_frame.pack(side="right", padx=15)
        
        def export_csv():
            self._export_to_csv(content, title, report_type)
        
        def export_txt():
            self._export_to_txt(content, title, report_type)
        
        tk.Button(
            btn_frame,
            text="💾 Exportar CSV",
            font=("Segoe UI", 9),
            bg="#4CAF50",
            fg="white",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=export_csv
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="📄 Exportar TXT",
            font=("Segoe UI", 9),
            bg="#2196F3",
            fg="white",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=export_txt
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="✖ Cerrar",
            font=("Segoe UI", 9),
            bg="#f44336",
            fg="white",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=window.destroy
        ).pack(side="left", padx=5)
        
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
        """Exporta el reporte a CSV"""
        try:
            export_dir = Path(__file__).resolve().parent.parent.parent.parent / "exports"
            export_dir.mkdir(exist_ok=True)
            
            filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = export_dir / filename
            
            # Para CSV, parseamos el contenido y lo convertimos a formato tabular cuando sea posible
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Escribir cada línea como una fila
                for line in content.split('\n'):
                    writer.writerow([line])
            
            messagebox.showinfo(
                "Exportación exitosa",
                f"Reporte exportado a:\n{filepath}\n\nPuedes copiar esta ruta para acceder al archivo."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar CSV: {str(e)}")
    
    def _export_to_txt(self, content, title, report_type):
        """Exporta el reporte a TXT"""
        try:
            export_dir = Path(__file__).resolve().parent.parent.parent.parent / "exports"
            export_dir.mkdir(exist_ok=True)
            
            filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = export_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo(
                "Exportación exitosa",
                f"Reporte exportado a:\n{filepath}\n\nPuedes copiar esta ruta para acceder al archivo."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar TXT: {str(e)}")
    
    # ==================== HELPERS ====================
    
    def _is_this_month(self, date_str):
        """Verifica si una fecha corresponde al mes actual"""
        try:
            date = datetime.strptime(date_str, "%d/%m/%Y")
            now = datetime.now()
            return date.year == now.year and date.month == now.month
        except:
            return False
    
    def _is_this_year(self, date_str):
        """Verifica si una fecha corresponde al año actual"""
        try:
            date = datetime.strptime(date_str, "%d/%m/%Y")
            return date.year == datetime.now().year
        except:
            return False
