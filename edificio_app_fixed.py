import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, StringVar, filedialog
import sqlite3
import datetime
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import shutil
import zipfile
import json
from pathlib import Path
from tkcalendar import DateEntry
import logging
from tkinter import filedialog
from utils.style_utils import setup_styles, create_styled_button, create_card
import platform

# Importar módulo de sonido según el sistema operativo
if platform.system() == 'Windows':
    import winsound
    def play_notification_sound():
        try:
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
        except:
            pass
elif platform.system() in ['Linux', 'Darwin']:  # Linux o macOS
    try:
        import pygame
        pygame.mixer.init()
        def play_notification_sound():
            try:
                pygame.mixer.music.load("notification.wav")  # Asegúrate de tener este archivo
                pygame.mixer.music.play()
            except:
                pass
    except ImportError:
        def play_notification_sound():
            pass  # Si no hay sistema de sonido disponible, no hacer nada
else:
    def play_notification_sound():
        pass  # Sistema operativo no reconocido, no hacer nada

# === IMPORTACIÓN DE CALENDARIO ===
CALENDAR_AVAILABLE = False
try:
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
except ImportError:
    pass

# Define la clase TenantModule primero

class TenantModule:
    def __init__(self, manager):
        self.manager = manager
        self.frame = None
        self._listado_modal_active = False
        self._add_modal_active = False
        
    def setup_ui(self, parent):
        """Configura la interfaz del módulo de inquilinos"""
        self.frame = ttk.Frame(parent)
        
        # Crear contenedor principal con scroll
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill="both", expand=True)
        
        # Frame para el contenido
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Crear tarjetas de estadísticas
        self.create_stat_cards(content_frame)
        
        # Programar la primera actualización de estadísticas para 100ms después de iniciar
        self.frame.after(100, self.actualizar_estadisticas)
        
        return self.frame
        
    def create_stat_cards(self, container):
        """Crea tarjetas de estadísticas con el nuevo estilo"""
        # Frame para estadísticas
        stats_frame = ttk.Frame(container, style='Main.TFrame')
        stats_frame.pack(fill="x", pady=5)

        # Crear 5 tarjetas en una fila
        cards_data = [
            ("Total Inquilinos", "0", "👥", "total_label"),
            ("Activos", "0", "✅", "active_label"),
            ("Pendientes", "0", "⚠️", "pending_label"),
            ("Gastos/Mes", "$0", "💰", "expenses_label"),
            ("Saldo Neto", "$0", "📈", "balance_label")
        ]

        for title, value, icon, label_name in cards_data:
            card = create_card(stats_frame, title, value, icon)
            card.pack(side="left", fill="x", expand=True, padx=5)
            
            # Guardar referencia al label de valor
            for child in card.winfo_children():
                if isinstance(child, ttk.Frame):  # El frame interno
                    for subchild in child.winfo_children():
                        if isinstance(subchild, ttk.Label):
                            if subchild.cget("text") == value:  # El label del valor
                                setattr(self, label_name, subchild)
                                break
            
            # Configurar eventos para la tarjeta
            self.setup_add_card_events(card, None, None, None)  # Por ahora no necesitamos los eventos

    def setup_add_card_events(self, card_content, icon_label, title_label, subtitle_label):
        """Configura los eventos de hover y click para las tarjetas"""
        def on_enter(event):
            """Efecto al pasar el mouse por encima"""
            card_content.configure(style='Card.Hover.TFrame')

        def on_leave(event):
            """Efecto al quitar el mouse"""
            card_content.configure(style='Card.TFrame')

        # Vincular eventos
        card_content.bind('<Enter>', on_enter)
        card_content.bind('<Leave>', on_leave)

    def setup_view_card_events(self, card_content, icon_label, title_label, subtitle_label):
        """Configura los eventos del card de ver inquilinos"""

        def on_enter(event):
            hover_bg = "#c8f7c5"
            self.view_tenant_card.config(bg=hover_bg, relief="solid", bd=2)
            card_content.config(bg=hover_bg)
            icon_label.config(bg=hover_bg, fg="#2e7d32")
            title_label.config(bg=hover_bg, fg="#2e7d32")
            subtitle_label.config(bg=hover_bg, fg="#495057")

        def on_leave(event):
            original_bg = "#f0f8e8"
            self.view_tenant_card.config(bg=original_bg, relief="raised", bd=2)
            card_content.config(bg=original_bg)
            icon_label.config(bg=original_bg, fg="#2c3e50")
            title_label.config(bg=original_bg, fg="#2c3e50")
            subtitle_label.config(bg=original_bg, fg="#5a6c7d")

        def on_click(event):
            self.abrir_ventana_listado_inquilinos()

        # Bind eventos
        for widget in [self.view_tenant_card, card_content, icon_label, title_label, subtitle_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

    def abrir_ventana_listado_inquilinos(self):
        """Abre una ventana modal con el listado completo de inquilinos"""
        # Actualizar estadísticas antes de abrir la ventana
        self.actualizar_estadisticas()
        
        # Crear ventana modal
        listado_window = tk.Toplevel()
        listado_window.title("📋 Listado Completo de Inquilinos")
        listado_window.geometry("1200x700")  # Aumentamos un poco la altura
        listado_window.resizable(True, True)
        listado_window.transient(self.manager.root)
        listado_window.grab_set()

        # Variables para control
        self._listado_modal_active = True

        # Configurar actualización periódica de estadísticas
        def actualizar_periodicamente():
            if self._listado_modal_active and listado_window.winfo_exists():
                self.actualizar_estadisticas()
                listado_window.after(5000, actualizar_periodicamente)  # Actualizar cada 5 segundos

        # Iniciar actualización periódica
        actualizar_periodicamente()

        # Frame principal con padding
        main_frame = ttk.Frame(listado_window, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0, 15))

        title_label = ttk.Label(title_frame,
                             text="📋 Gestión Completa de Inquilinos",
                             font=("Segoe UI", 16, "bold"),
                             foreground="#2c3e50")
        title_label.pack()

        # Frame de búsqueda avanzada
        search_frame = ttk.LabelFrame(main_frame, text="🔍 Búsqueda y Filtros Avanzados", padding="10")
        search_frame.pack(fill="x", pady=(0, 10))

        # Contenedor para la tabla y botones
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)

        # Frame para la tabla con scrollbar
        table_frame = ttk.Frame(content_frame)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Crear Treeview
        columns = ("id", "nombre", "apto", "identificacion", "email", "celular", "estado", "renta")
        self.tree_inquilinos = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Configurar columnas
        self.tree_inquilinos.heading("id", text="ID")
        self.tree_inquilinos.heading("nombre", text="Nombre")
        self.tree_inquilinos.heading("apto", text="Apto")
        self.tree_inquilinos.heading("identificacion", text="Identificación")
        self.tree_inquilinos.heading("email", text="Email")
        self.tree_inquilinos.heading("celular", text="Celular")
        self.tree_inquilinos.heading("estado", text="Estado")
        self.tree_inquilinos.heading("renta", text="Renta")

        # Ajustar anchos de columna
        self.tree_inquilinos.column("id", width=50)
        self.tree_inquilinos.column("nombre", width=200)
        self.tree_inquilinos.column("apto", width=80)
        self.tree_inquilinos.column("identificacion", width=120)
        self.tree_inquilinos.column("email", width=180)
        self.tree_inquilinos.column("celular", width=120)
        self.tree_inquilinos.column("estado", width=100)
        self.tree_inquilinos.column("renta", width=100)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_inquilinos.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree_inquilinos.xview)
        self.tree_inquilinos.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid para la tabla y scrollbars
        self.tree_inquilinos.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Frame para botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(0, 5))

        # Botones de acción
        btn_agregar = create_styled_button(button_frame, "➕ Agregar Inquilino", self.mostrar_formulario_agregar)
        btn_agregar.pack(side="left", padx=5)

        btn_ver = create_styled_button(button_frame, "👁️ Ver Detalles", self.ver_detalles_inquilino_listado)
        btn_ver.pack(side="left", padx=5)

        btn_editar = create_styled_button(button_frame, "✏️ Editar", self.editar_inquilino_listado)
        btn_editar.pack(side="left", padx=5)

        btn_eliminar = create_styled_button(button_frame, "🗑️ Eliminar", self.eliminar_inquilino_listado)
        btn_eliminar.pack(side="left", padx=5)

        btn_cerrar = create_styled_button(button_frame, "❌ Cerrar", lambda: self.cerrar_listado_window(listado_window))
        btn_cerrar.pack(side="right", padx=5)

        # Texto de ayuda
        help_text = ttk.Label(main_frame, 
                           text="✨ Seleccione un inquilino de la lista y use los botones de acción",
                           font=("Segoe UI", 10),
                           foreground="#666666")
        help_text.pack(pady=5)

        # Cargar datos
        self.cargar_inquilinos_listado()

        # Configurar cleanup al cerrar
        listado_window.protocol("WM_DELETE_WINDOW", lambda: self.cerrar_listado_window(listado_window))

    def cerrar_listado_window(self, window):
        """Cierra la ventana de listado de forma segura"""
        try:
            self._listado_modal_active = False
            window.destroy()
            # Actualizar estadísticas en el dashboard principal
            self.actualizar_estadisticas()
        except Exception as e:
            logging.error(f"Error cerrando ventana listado: {e}")

    def cargar_inquilinos_listado(self):
        """Carga la lista de inquilinos en el treeview"""
        # Limpiar treeview
        for item in self.tree_inquilinos.get_children():
            self.tree_inquilinos.delete(item)

        try:
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            # Obtener todos los inquilinos
            cursor.execute("""
                SELECT id, nombre, apartamento, identificacion, 
                       email, celular, estado, renta 
                FROM inquilinos 
                ORDER BY nombre
            """)

            # Insertar datos en el treeview
            for row in cursor.fetchall():
                self.tree_inquilinos.insert("", "end", values=row)

            conn.close()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar inquilinos: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")

    def on_listado_search_key_release(self, event):
        """Realiza búsqueda al escribir en el listado"""
        self.aplicar_filtros_listado()

    def on_listado_filter_change(self, event=None):
        """Aplica filtros automáticamente cuando cambian en el listado"""
        if hasattr(self, '_listado_filter_after'):
            self.manager.root.after_cancel(self._listado_filter_after)
        self._listado_filter_after = self.manager.root.after(300, self.aplicar_filtros_listado)

    def clear_placeholder_listado(self, event):
        """Limpia los placeholders de los campos de renta en el listado"""
        if event.widget.get() in ["Min", "Max"]:
            event.widget.delete(0, tk.END)

    def aplicar_filtros_listado(self):
        """Aplica todos los filtros combinados en el listado"""
        if not hasattr(self, 'listado_tree'):
            return

        try:
            # Limpiar treeview
            for item in self.listado_tree.get_children():
                self.listado_tree.delete(item)

            # Obtener valores de filtros
            termino_busqueda = self.listado_entry_buscar.get().lower().strip()
            estado_filtro = self.listado_filtro_estado.get()
            apartamento_filtro = self.listado_filtro_apartamento.get().strip()

            # Filtros de renta
            renta_min = self.listado_filtro_renta_min.get().strip()
            renta_max = self.listado_filtro_renta_max.get().strip()

            # Convertir renta a números
            try:
                renta_min_val = float(renta_min) if renta_min and renta_min != "Min" else 0
            except ValueError:
                renta_min_val = 0

            try:
                renta_max_val = float(renta_max) if renta_max and renta_max != "Max" else float('inf')
            except ValueError:
                renta_max_val = float('inf')

            # Construir consulta SQL
            query = """
                SELECT id, nombre, apartamento, identificacion, email, celular, estado, renta 
                FROM inquilinos WHERE 1=1
            """
            params = []

            # Filtro de búsqueda general
            if termino_busqueda:
                query += """ AND (
                    LOWER(nombre) LIKE ? OR 
                    LOWER(apartamento) LIKE ? OR 
                    LOWER(identificacion) LIKE ? OR 
                    LOWER(email) LIKE ? OR 
                    LOWER(celular) LIKE ?
                )"""
                search_pattern = f"%{termino_busqueda}%"
                params.extend([search_pattern] * 5)

            # Filtro por estado
            if estado_filtro and estado_filtro != "Todos":
                query += " AND estado = ?"
                params.append(estado_filtro)

            # Filtro por apartamento
            if apartamento_filtro:
                query += " AND LOWER(apartamento) LIKE ?"
                params.append(f"%{apartamento_filtro.lower()}%")

            # Filtro por renta
            if renta_min_val > 0:
                query += " AND renta >= ?"
                params.append(renta_min_val)

            if renta_max_val < float('inf'):
                query += " AND renta <= ?"
                params.append(renta_max_val)

            query += """ ORDER BY 
                CASE 
                    WHEN estado = 'Activo' THEN 1
                    WHEN estado = 'Pendiente' THEN 2
                    WHEN estado = 'Moroso' THEN 3
                    WHEN estado = 'Suspendido' THEN 4
                    ELSE 5
                END,
                apartamento"""

            # Ejecutar consulta
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            conn.close()

            # Mostrar resultados
            for row in resultados:
                # Convertir None a string vacío
                row_display = []
                for item in row:
                    if item is None:
                        row_display.append("")
                    else:
                        row_display.append(item)

                self.listado_tree.insert("", "end", values=row_display)

            # Actualizar contador
            total_resultados = len(resultados)
            if hasattr(self, 'listado_results_label'):
                self.listado_results_label.config(text=f"📊 Resultados: {total_resultados}")

        except Exception as e:
            logging.error(f"Error aplicando filtros en listado: {e}")
            messagebox.showerror("Error", f"Error en filtros: {e}")

    def limpiar_filtros_listado(self):
        """Limpia todos los filtros del listado"""
        if not hasattr(self, 'listado_entry_buscar'):
            return

        self.listado_entry_buscar.delete(0, tk.END)
        self.listado_filtro_estado.set("Todos")
        self.listado_filtro_apartamento.delete(0, tk.END)

        # Restaurar placeholders
        self.listado_filtro_renta_min.delete(0, tk.END)
        self.listado_filtro_renta_min.insert(0, "Min")
        self.listado_filtro_renta_max.delete(0, tk.END)
        self.listado_filtro_renta_max.insert(0, "Max")

        # Cargar todos los inquilinos
        self.cargar_inquilinos_listado()

    def ver_detalles_inquilino_listado(self):
        """Muestra los detalles del inquilino seleccionado"""
        # Obtener selección
        selected_items = self.tree_inquilinos.selection()
        if not selected_items:
            messagebox.showwarning("Selección requerida", "Por favor, seleccione un inquilino de la lista.")
            return

        # Obtener ID del inquilino seleccionado
        inquilino_id = self.tree_inquilinos.item(selected_items[0])['values'][0]

        try:
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            # Obtener datos del inquilino
            cursor.execute("""
                SELECT i.*, 
                       COALESCE(SUM(p.monto), 0) as total_pagado,
                       COUNT(p.id) as num_pagos,
                       MAX(p.fecha) as ultimo_pago_fecha,
                       (SELECT monto FROM pagos WHERE inquilino_id = i.id ORDER BY fecha DESC LIMIT 1) as ultimo_pago_monto
                FROM inquilinos i
                LEFT JOIN pagos p ON i.id = p.inquilino_id
                WHERE i.id = ?
                GROUP BY i.id
            """, (inquilino_id,))
            
            row = cursor.fetchone()
            if row:
                # Separar los datos en las diferentes partes que necesitamos
                datos_inquilino = row[:-4]  # Todos los campos excepto los últimos 4 que son de pagos
                total_pagado = row[-4] or 0  # COALESCE ya maneja el caso NULL
                num_pagos = row[-3] or 0
                ultimo_pago = (row[-2], row[-1]) if row[-2] and row[-1] else None
                
                # Mostrar la ventana de detalles
                self.mostrar_ventana_detalles_inquilino(
                    inquilino_id=inquilino_id,
                    datos=datos_inquilino,
                    total_pagado=float(total_pagado),
                    num_pagos=int(num_pagos),
                    ultimo_pago=ultimo_pago
                )
            else:
                messagebox.showerror("Error", "No se encontró el inquilino seleccionado.")

            conn.close()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")
            logging.error(f"Error en ver_detalles_inquilino_listado: {str(e)}")
            if 'conn' in locals():
                conn.close()

    def editar_inquilino_listado(self):
        """Abre el formulario de edición para el inquilino seleccionado"""
        # Obtener selección
        selected_items = self.tree_inquilinos.selection()
        if not selected_items:
            messagebox.showwarning("Selección requerida", "Por favor, seleccione un inquilino de la lista.")
            return

        # Obtener ID del inquilino seleccionado
        inquilino_id = self.tree_inquilinos.item(selected_items[0])['values'][0]

        try:
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            # Obtener datos del inquilino en el orden correcto
            cursor.execute("""
                SELECT nombre, apartamento, renta, identificacion, email, celular, profesion,
                       fecha_ingreso, deposito, estado, contacto_emergencia, telefono_emergencia,
                       relacion_emergencia, notas, archivo_identificacion, archivo_contrato
                FROM inquilinos WHERE id = ?
            """, (inquilino_id,))
            
            datos = cursor.fetchone()
            conn.close()

            if datos:
                self.mostrar_formulario_editar(inquilino_id, datos)
            else:
                messagebox.showerror("Error", "No se encontró el inquilino seleccionado.")

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos para edición: {str(e)}")

    def eliminar_inquilino_listado(self):
        """Elimina el inquilino seleccionado"""
        # Obtener selección
        selected_items = self.tree_inquilinos.selection()
        if not selected_items:
            messagebox.showwarning("Selección requerida", "Por favor, seleccione un inquilino de la lista.")
            return

        # Obtener datos del inquilino seleccionado
        item_values = self.tree_inquilinos.item(selected_items[0])['values']
        inquilino_id = item_values[0]
        nombre = item_values[1]
        apartamento = item_values[2]

        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar eliminación", 
                                 f"¿Está seguro de eliminar al inquilino {nombre} del apartamento {apartamento}?\n\n" +
                                 "Esta acción también eliminará todos los pagos asociados y no se puede deshacer."):
            return

        try:
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            # Eliminar pagos asociados primero
            cursor.execute("DELETE FROM pagos WHERE inquilino_id = ?", (inquilino_id,))
            
            # Eliminar inquilino
            cursor.execute("DELETE FROM inquilinos WHERE id = ?", (inquilino_id,))
            
            conn.commit()
            conn.close()

            # Actualizar lista
            self.cargar_inquilinos_listado()
            
            # Actualizar combo box de inquilinos en la pestaña de pagos
            self.manager.payment_module.cargar_inquilinos_combo()
            
            messagebox.showinfo("Éxito", f"Inquilino {nombre} eliminado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar inquilino: {str(e)}")

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas del dashboard - VERSIÓN MEJORADA"""
        try:
            # Verificar que los labels existen
            required_labels = ['total_label', 'active_label', 'pending_label', 'expenses_label', 'balance_label']
            for label in required_labels:
                if not hasattr(self, label):
                    logging.warning(f"Label {label} no encontrado, inicializando estadísticas...")
                    self.create_stat_cards(self.frame.winfo_children()[0])
                    return

            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            # Total de inquilinos
            cursor.execute("SELECT COUNT(*) FROM inquilinos")
            total = cursor.fetchone()[0] or 0

            # Inquilinos activos
            cursor.execute("SELECT COUNT(*) FROM inquilinos WHERE estado = 'Activo'")
            activos = cursor.fetchone()[0] or 0

            # Inquilinos pendientes/problemáticos
            cursor.execute("""
                SELECT COUNT(*) FROM inquilinos 
                WHERE estado IN ('Pendiente', 'Moroso', 'Suspendido')
            """)
            pendientes = cursor.fetchone()[0] or 0

            # Gastos del mes actual
            fecha_actual = datetime.date.today()
            mes_actual = fecha_actual.month
            año_actual = fecha_actual.year

            # Ingresos del mes (pagos)
            cursor.execute("""
                SELECT COALESCE(SUM(monto), 0) FROM pagos 
                WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
            """, (str(año_actual), f"{mes_actual:02d}"))
            ingresos_mes = cursor.fetchone()[0] or 0

            # Gastos del mes
            cursor.execute("""
                SELECT COALESCE(SUM(monto), 0) FROM gastos 
                WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
            """, (str(año_actual), f"{mes_actual:02d}"))
            gastos_mes = cursor.fetchone()[0] or 0

            conn.close()

            # Actualizar labels con formato de moneda
            self.total_label.config(text=str(total))
            self.active_label.config(text=str(activos))
            self.pending_label.config(text=str(pendientes))
            self.expenses_label.config(text=f"${gastos_mes:,.2f}")
            self.balance_label.config(text=f"${ingresos_mes - gastos_mes:,.2f}")

            # Cambiar colores según valores
            if pendientes > 0:
                self.pending_label.config(foreground="#e74c3c")  # Rojo si hay problemas
            else:
                self.pending_label.config(foreground="#27ae60")  # Verde si todo bien

            if ingresos_mes - gastos_mes >= 0:
                self.balance_label.config(foreground="#27ae60")  # Verde
            else:
                self.balance_label.config(foreground="#e74c3c")  # Rojo

            # Forzar actualización visual
            self.frame.update_idletasks()

        except Exception as e:
            logging.error(f"Error actualizando estadísticas: {e}")
            messagebox.showerror("Error", f"Error actualizando estadísticas: {e}")

    def mostrar_formulario_agregar(self):
        """Abre ventana modal para agregar nuevo inquilino"""
        # DESHABILITAR SCROLL PRINCIPAL GLOBALMENTE
        self.manager.root.unbind_all("<MouseWheel>")
        self.manager.root.unbind("<MouseWheel>")
        for child in self.manager.root.winfo_children():
            try:
                child.unbind_all("<MouseWheel>")
                child.unbind("<MouseWheel>")
            except:
                pass
        # Crear ventana modal
        add_window = tk.Toplevel()
        add_window.title("➕ Agregar Nuevo Inquilino")
        add_window.geometry("750x650")
        add_window.resizable(True, True)
        add_window.transient(self.manager.root)
        add_window.grab_set()
        self._add_modal_active = True
        add_window.attributes('-topmost', True)  # Mantener siempre arriba
        add_window.focus_force()
        add_window.lift()

        # Función de limpieza
        def cleanup_and_close():
            try:
                self._add_modal_active = False

                # REACTIVAR SCROLL PRINCIPAL (versión simple)
                def _on_mousewheel(event):
                    # Intentar encontrar y hacer scroll en el canvas principal
                    try:
                        canvas = self.manager.root.winfo_children()[0].winfo_children()[1].winfo_children()[0].winfo_children()[0]
                        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    except:
                        pass

                self.manager.root.bind_all("<MouseWheel>", _on_mousewheel)

                add_window.destroy()
            except Exception as e:
                logging.error(f"Error en cleanup: {e}")

        self.manager.root.bind_all("<MouseWheel>", lambda e: "break")

        # Frame principal SIN scroll
        main_frame = ttk.Frame(add_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configurar weight para que maneje bien el resize
        add_window.columnconfigure(0, weight=1)
        add_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Centrar ventana
        add_window.update_idletasks()
        width = 750
        height = 650
        screen_width = add_window.winfo_screenwidth()
        screen_height = add_window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        add_window.geometry(f'{width}x{height}+{x}+{y}')

        # Crear formulario en main_frame
        self.setup_add_form_modal(main_frame, add_window, cleanup_and_close)

        # FORZAR UPDATE después de crear el formulario:
        add_window.update_idletasks()
        main_frame.update_idletasks()
        add_window.minsize(750, 650)

        # Configurar protocolo de cierre
        add_window.protocol("WM_DELETE_WINDOW", cleanup_and_close)

        # Dar foco
        add_window.focus_force()
        logging.info("Ventana de agregar inquilino abierta")

    def generar_reporte_inquilinos(self):
        """Genera un reporte de todos los inquilinos"""
        try:
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            cursor.execute("""
                SELECT nombre, apartamento, identificacion, email, celular, estado, renta,
                       fecha_ingreso, deposito, profesion
                FROM inquilinos 
                ORDER BY apartamento
            """)

            inquilinos = cursor.fetchall()
            conn.close()

            if not inquilinos:
                messagebox.showinfo("Sin datos", "No hay inquilinos registrados para generar reporte.")
                return

            # Crear archivo de reporte
            fecha_actual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"reporte_inquilinos_{fecha_actual}.txt"

            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("                    REPORTE DE INQUILINOS\n")
                f.write("=" * 80 + "\n")
                f.write(f"Fecha de generación: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total de inquilinos: {len(inquilinos)}\n")
                f.write("=" * 80 + "\n\n")

                for inquilino in inquilinos:
                    f.write(f"Nombre: {inquilino[0] or 'N/A'}\n")
                    f.write(f"Apartamento: {inquilino[1] or 'N/A'}\n")
                    f.write(f"Identificación: {inquilino[2] or 'N/A'}\n")
                    f.write(f"Email: {inquilino[3] or 'N/A'}\n")
                    f.write(f"Celular: {inquilino[4] or 'N/A'}\n")
                    f.write(f"Estado: {inquilino[5] or 'N/A'}\n")
                    f.write(f"Renta: ${inquilino[6] or 0:,.0f}\n")
                    f.write(f"Fecha ingreso: {inquilino[7] or 'N/A'}\n")
                    f.write(f"Depósito: ${inquilino[8] or 0:,.0f}\n")
                    f.write(f"Profesión: {inquilino[9] or 'N/A'}\n")
                    f.write("-" * 80 + "\n\n")

            messagebox.showinfo("Reporte generado", f"Reporte guardado como: {nombre_archivo}")

            # Intentar abrir el archivo
            try:
                os.startfile(nombre_archivo)
            except:
                pass

        except Exception as e:
            logging.error(f"Error generando reporte: {e}")
            messagebox.showerror("Error", f"Error generando reporte: {e}")

    def exportar_datos_inquilinos(self):
        """Exporta los datos de inquilinos a CSV"""
        try:
            import csv

            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM inquilinos ORDER BY apartamento
            """)

            inquilinos = cursor.fetchall()

            # Obtener nombres de columnas
            cursor.execute("PRAGMA table_info(inquilinos)")
            columnas = [columna[1] for columna in cursor.fetchall()]

            conn.close()

            if not inquilinos:
                messagebox.showinfo("Sin datos", "No hay inquilinos para exportar.")
                return

            # Seleccionar ubicación del archivo
            archivo = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
                title="Guardar datos de inquilinos"
            )

            if archivo:
                with open(archivo, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(columnas)  # Encabezados
                    writer.writerows(inquilinos)  # Datos

                messagebox.showinfo("Exportación exitosa", f"Datos exportados a: {archivo}")

        except Exception as e:
            logging.error(f"Error exportando datos: {e}")
            messagebox.showerror("Error", f"Error exportando datos: {e}")

    def importar_datos_inquilinos(self):
        """Importa datos de inquilinos desde CSV"""
        try:
            import csv

            archivo = filedialog.askopenfilename(
                filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")],
                title="Seleccionar archivo de inquilinos"
            )

            if not archivo:
                return

            # Leer archivo CSV
            inquilinos_importados = []
            with open(archivo, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    inquilinos_importados.append(row)

            if not inquilinos_importados:
                messagebox.showwarning("Archivo vacío", "El archivo no contiene datos válidos.")
                return

            # Confirmar importación
            if not messagebox.askyesno("Confirmar importación",
                                       f"¿Deseas importar {len(inquilinos_importados)} inquilinos?\n"
                                       f"Los datos duplicados serán omitidos."):
                return

            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            importados = 0
            omitidos = 0

            for inquilino in inquilinos_importados:
                try:
                    # Verificar si ya existe (por nombre y apartamento)
                    cursor.execute("""
                        SELECT id FROM inquilinos 
                        WHERE nombre = ? AND apartamento = ?
                    """, (inquilino.get('nombre', ''), inquilino.get('apartamento', '')))

                    if cursor.fetchone():
                        omitidos += 1
                        continue

                    # Insertar nuevo inquilino
                    cursor.execute("""
                        INSERT INTO inquilinos (
                            nombre, apartamento, renta, identificacion, email, celular,
                            profesion, fecha_ingreso, deposito, estado, contacto_emergencia,
                            telefono_emergencia, relacion_emergencia, notas
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        inquilino.get('nombre', ''),
                        inquilino.get('apartamento', ''),
                        float(inquilino.get('renta', 0)) if inquilino.get('renta') else 0,
                        inquilino.get('identificacion', ''),
                        inquilino.get('email', ''),
                        inquilino.get('celular', ''),
                        inquilino.get('profesion', ''),
                        inquilino.get('fecha_ingreso', ''),
                        float(inquilino.get('deposito', 0)) if inquilino.get('deposito') else 0,
                        inquilino.get('estado', 'Activo'),
                        inquilino.get('contacto_emergencia', ''),
                        inquilino.get('telefono_emergencia', ''),
                        inquilino.get('relacion_emergencia', ''),
                        inquilino.get('notas', '')
                    ))

                    importados += 1

                except Exception as e:
                    logging.error(f"Error importando inquilino: {e}")
                    omitidos += 1

            conn.commit()
            conn.close()

            messagebox.showinfo("Importación completada",
                                f"Importación finalizada:\n"
                                f"• Importados: {importados}\n"
                                f"• Omitidos: {omitidos}")

            # Actualizar estadísticas
            self.actualizar_estadisticas()

        except Exception as e:
            logging.error(f"Error importando datos: {e}")
            messagebox.showerror("Error", f"Error importando datos: {e}")

    def ver_detalles_inquilino_por_id(self, inquilino_id):
        """Muestra detalles del inquilino por ID"""
        try:
            # Obtener datos completos de la base de datos
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT nombre, apartamento, renta, identificacion, email, celular, profesion,
                       fecha_ingreso, deposito, estado, contacto_emergencia, telefono_emergencia,
                       relacion_emergencia, notas, archivo_identificacion, archivo_contrato
                FROM inquilinos WHERE id = ?
            """, (inquilino_id,))

            datos = cursor.fetchone()

            if not datos:
                conn.close()
                messagebox.showerror("Error", "No se pudieron cargar los datos del inquilino.")
                return

            # Obtener información financiera
            cursor.execute("SELECT SUM(monto), COUNT(*) FROM pagos WHERE inquilino_id = ?", (inquilino_id,))
            pago_info = cursor.fetchone()
            total_pagado = pago_info[0] if pago_info[0] else 0
            num_pagos = pago_info[1] if pago_info[1] else 0

            # Último pago
            cursor.execute("SELECT fecha, monto FROM pagos WHERE inquilino_id = ? ORDER BY fecha DESC LIMIT 1",
                           (inquilino_id,))
            ultimo_pago = cursor.fetchone()
            conn.close()

            # Mostrar ventana de detalles
            self.mostrar_ventana_detalles_inquilino(
                inquilino_id=inquilino_id,
                datos=datos,
                total_pagado=float(total_pagado),
                num_pagos=int(num_pagos),
                ultimo_pago=ultimo_pago
            )

        except Exception as e:
            logging.error(f"Error obteniendo detalles por ID: {e}")
            messagebox.showerror("Error", f"Error obteniendo detalles: {e}")

    def editar_inquilino_por_id(self, inquilino_id):
        """Edita el inquilino por ID"""
        try:
            # Obtener datos completos de la base de datos
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT nombre, apartamento, renta, identificacion, email, celular, profesion,
                       fecha_ingreso, deposito, estado, contacto_emergencia, telefono_emergencia,
                       relacion_emergencia, notas, archivo_identificacion, archivo_contrato
                FROM inquilinos WHERE id = ?
            """, (inquilino_id,))

            datos = cursor.fetchone()
            conn.close()

            if not datos:
                messagebox.showerror("Error", "No se pudieron cargar los datos del inquilino.")
                return

            # Abrir ventana modal de edición
            self.mostrar_formulario_editar(inquilino_id, datos)

        except Exception as e:
            logging.error(f"Error obteniendo datos para edición: {e}")
            messagebox.showerror("Error", f"Error obteniendo datos: {e}")

    def abrir_archivo(self, ruta_archivo):
        """Abre un archivo usando el programa predeterminado del sistema"""
        try:
            # Asegurarse de que el archivo existe
            if not os.path.exists(ruta_archivo):
                messagebox.showerror("Error", f"El archivo no existe: {ruta_archivo}")
                return

            # En Windows, usar os.startfile
            if os.name == 'nt':
                os.startfile(ruta_archivo)
            # En Linux o Mac
            else:
                import subprocess
                # Usar xdg-open en Linux o open en Mac
                opener = 'xdg-open' if os.name == 'posix' else 'open'
                subprocess.run([opener, ruta_archivo])

        except Exception as e:
            logging.error(f"Error abriendo archivo: {e}")
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

    def setup_add_form_modal(self, parent, window, cleanup_function):
        """Configura el formulario en ventana modal - VERSIÓN CON CALENDARIO MEJORADO"""

        # Canvas para scroll interno del formulario
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        # Configurar el scroll
        canvas.configure(yscrollcommand=scrollbar.set)
        scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=canvas.winfo_width())

        # Ajustar el ancho del contenido cuando se redimensiona el canvas
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind('<Configure>', on_canvas_configure)

        canvas.pack(side="left", fill="both", expand=True, padx=(5, 0))
        scrollbar.pack(side="right", fill="y")

        # Scroll con mouse en todo el formulario
        def scroll_form(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"  # Prevenir propagación del evento

        # Vincular el evento de scroll a todos los widgets
        canvas.bind_all("<MouseWheel>", scroll_form)
        window.bind("<MouseWheel>", scroll_form)
        scroll_frame.bind("<MouseWheel>", scroll_form)

        # Título
        title_frame = ttk.Frame(scroll_frame)
        title_frame.pack(fill="x", pady=(0, 20))

        title_label = tk.Label(title_frame,
                             text="📝 Registrar Nuevo Inquilino",
                             font=("Segoe UI", 16, "bold"),
                             fg="#2c3e50")
        title_label.pack()

        # Contenedor principal para los frames
        content_frame = ttk.Frame(scroll_frame)
        content_frame.pack(fill="both", expand=True, padx=20)

        # === INFORMACIÓN PERSONAL ===
        personal_frame = ttk.LabelFrame(content_frame, text="👤 Información Personal", padding="15")
        personal_frame.pack(fill="x", pady=(0, 15))

        # Fila 1
        row1 = ttk.Frame(personal_frame)
        row1.pack(fill="x", pady=5)

        ttk.Label(row1, text="Nombre completo:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_nombre = ttk.Entry(row1, width=30)
        self.modal_nombre.grid(row=0, column=1, sticky="ew", padx=(0, 20))

        ttk.Label(row1, text="Identificación:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.modal_identificacion = ttk.Entry(row1, width=20)
        self.modal_identificacion.grid(row=0, column=3, sticky="ew")

        row1.columnconfigure(1, weight=2)
        row1.columnconfigure(3, weight=1)

        # Fila 2
        row2 = ttk.Frame(personal_frame)
        row2.pack(fill="x", pady=5)

        ttk.Label(row2, text="Email:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_email = ttk.Entry(row2, width=30)
        self.modal_email.grid(row=0, column=1, sticky="ew", padx=(0, 20))

        ttk.Label(row2, text="Celular:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.modal_celular = ttk.Entry(row2, width=20)
        self.modal_celular.grid(row=0, column=3, sticky="ew")

        row2.columnconfigure(1, weight=2)
        row2.columnconfigure(3, weight=1)

        # Profesión
        row3 = ttk.Frame(personal_frame)
        row3.pack(fill="x", pady=5)

        ttk.Label(row3, text="Profesión:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_profesion = ttk.Entry(row3)
        self.modal_profesion.grid(row=0, column=1, sticky="ew")

        row3.columnconfigure(1, weight=1)

        # === INFORMACIÓN DEL ARRENDAMIENTO ===
        rental_frame = ttk.LabelFrame(content_frame, text="🏠 Información del Arrendamiento", padding="15")
        rental_frame.pack(fill="x", pady=(0, 15))

        # Fila arrendamiento 1
        rent_row1 = ttk.Frame(rental_frame)
        rent_row1.pack(fill="x", pady=5)

        ttk.Label(rent_row1, text="Apartamento:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_apto = ttk.Entry(rent_row1, width=10)
        self.modal_apto.grid(row=0, column=1, sticky="w", padx=(0, 20))

        ttk.Label(rent_row1, text="Renta mensual:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.modal_renta = ttk.Entry(rent_row1, width=15)
        self.modal_renta.grid(row=0, column=3, sticky="w", padx=(0, 20))

        ttk.Label(rent_row1, text="Estado:").grid(row=0, column=4, sticky="w", padx=(0, 10))
        self.modal_estado = ttk.Combobox(rent_row1, width=12,
                                       values=["Activo", "Pendiente", "Inactivo", "Moroso", "Suspendido"],
                                       state="readonly")
        self.modal_estado.set("Activo")
        self.modal_estado.grid(row=0, column=5, sticky="w")

        # Fila arrendamiento 2
        rent_row2 = ttk.Frame(rental_frame)
        rent_row2.pack(fill="x", pady=5)

        ttk.Label(rent_row2, text="Fecha ingreso:").grid(row=0, column=0, sticky="w", padx=(0, 10))

        # === SELECTOR DE FECHA MEJORADO ===
        if CALENDAR_AVAILABLE:
            today = datetime.date.today()
            self.modal_fecha = DateEntry(rent_row2,
                                       width=12,
                                       background='#007acc',
                                       foreground='white',
                                       borderwidth=1,
                                       date_pattern='yyyy-mm-dd',
                                       showweeknumbers=False,
                                       locale='es_ES',
                                       font=('Segoe UI', 9))
            
            # Configurar el estilo del calendario emergente
            self.modal_fecha._top_cal.configure(background='white')
            
            # Prevenir que el calendario se cierre automáticamente
            def prevent_calendar_close(event=None):
                return 'break'
            
            # Mantener el calendario funcional
            def setup_calendar_controls():
                if hasattr(self.modal_fecha, '_top_cal'):
                    # Vincular a todos los elementos del calendario
                    for widget in self.modal_fecha._top_cal.winfo_children():
                        if isinstance(widget, (ttk.Button, tk.Button)):
                            widget.bind('<Button-1>', prevent_calendar_close, add="+")
                        elif isinstance(widget, tk.Canvas):
                            # El canvas contiene los números del calendario
                            widget.bind('<Button-1>', prevent_calendar_close, add="+")
                    
                    # Configurar el calendario para mantenerse visible
                    self.modal_fecha._top_cal.lift()
                    
                    # Permitir cerrar solo cuando se hace clic fuera
                    def close_on_focusout(event):
                        if event.widget == self.modal_fecha._top_cal:
                            return
                        if not any(child.winfo_containing(event.x_root, event.y_root) == child 
                                 for child in self.modal_fecha._top_cal.winfo_children()):
                            self.modal_fecha._top_cal.withdraw()
                    
                    self.modal_fecha._top_cal.bind('<FocusOut>', close_on_focusout)
            
            # Vincular eventos
            self.modal_fecha.bind('<<DateEntryPopup>>', lambda e: self.modal_fecha.after(10, setup_calendar_controls))
            self.modal_fecha.bind('<<CalendarSelected>>', prevent_calendar_close)
        else:
            self.modal_fecha = ttk.Entry(rent_row2, width=12)
            self.modal_fecha.insert(0, datetime.date.today().isoformat())
            info_label = ttk.Label(rent_row2, text="(YYYY-MM-DD)",
                                 font=("Segoe UI", 8), foreground="gray")
            info_label.grid(row=0, column=2, sticky="w", padx=(5, 0))

        self.modal_fecha.grid(row=0, column=1, sticky="w", padx=(0, 20))

        ttk.Label(rent_row2, text="Depósito:").grid(row=0, column=2 if not CALENDAR_AVAILABLE else 2,
                                                  sticky="w", padx=(0, 10))
        self.modal_deposito = ttk.Entry(rent_row2, width=15)
        self.modal_deposito.grid(row=0, column=3 if not CALENDAR_AVAILABLE else 3, sticky="w")

        # === CONTACTO DE EMERGENCIA ===
        emergency_frame = ttk.LabelFrame(content_frame, text="🚨 Contacto de Emergencia", padding="15")
        emergency_frame.pack(fill="x", pady=(0, 15))

        emerg_row1 = ttk.Frame(emergency_frame)
        emerg_row1.pack(fill="x", pady=5)

        ttk.Label(emerg_row1, text="Nombre contacto:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_contacto = ttk.Entry(emerg_row1, width=30)
        self.modal_contacto.grid(row=0, column=1, sticky="ew", padx=(0, 20))

        ttk.Label(emerg_row1, text="Teléfono:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.modal_tel_emergencia = ttk.Entry(emerg_row1, width=20)
        self.modal_tel_emergencia.grid(row=0, column=3, sticky="ew")

        emerg_row1.columnconfigure(1, weight=2)
        emerg_row1.columnconfigure(3, weight=1)

        emerg_row2 = ttk.Frame(emergency_frame)
        emerg_row2.pack(fill="x", pady=5)

        ttk.Label(emerg_row2, text="Relación:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_relacion = ttk.Combobox(emerg_row2, width=15,
                                         values=["Padre", "Madre", "Esposo/a", "Hermano/a", "Hijo/a", "Amigo/a", "Otro"],
                                         state="readonly")
        self.modal_relacion.grid(row=0, column=1, sticky="w")

        # === NOTAS ===
        notes_frame = ttk.LabelFrame(content_frame, text="📝 Notas Adicionales", padding="15")
        notes_frame.pack(fill="x", pady=(0, 15))

        self.modal_notas = tk.Text(notes_frame, height=4, width=60, wrap="word")
        self.modal_notas.pack(fill="x")

        # === ARCHIVOS ADJUNTOS ===
        files_frame = ttk.LabelFrame(content_frame, text="📎 Archivos Adjuntos", padding="15")
        files_frame.pack(fill="x", pady=(0, 15))

        # Fila para archivo de identificación
        files_row1 = ttk.Frame(files_frame)
        files_row1.pack(fill="x", pady=5)

        ttk.Label(files_row1, text="📄 Identificación:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_id_file_label = ttk.Label(files_row1, text="No seleccionado", foreground="gray")
        self.modal_id_file_label.grid(row=0, column=1, sticky="w", padx=(0, 10))

        ttk.Button(files_row1, text="📁 Seleccionar",
                  command=lambda: self.seleccionar_archivo_id_modal()).grid(row=0, column=2, padx=(0, 5))

        # Fila para archivo de contrato
        files_row2 = ttk.Frame(files_frame)
        files_row2.pack(fill="x", pady=5)

        ttk.Label(files_row2, text="📄 Contrato:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.modal_contract_file_label = ttk.Label(files_row2, text="No seleccionado", foreground="gray")
        self.modal_contract_file_label.grid(row=0, column=1, sticky="w", padx=(0, 10))

        ttk.Button(files_row2, text="📁 Seleccionar",
                  command=lambda: self.seleccionar_archivo_contrato_modal()).grid(row=0, column=2, padx=(0, 5))

        # === BOTONES ===
        btn_frame = ttk.Frame(content_frame)
        btn_frame.pack(fill="x", pady=20)

        ttk.Button(btn_frame, text="💾 Guardar",
                  command=lambda: self.guardar_inquilino_modal(window, cleanup_function)).pack(
            side="right", padx=(10, 0))
        ttk.Button(btn_frame, text="❌ Cancelar",
                  command=cleanup_function).pack(side="right")

    def guardar_inquilino_modal(self, window, cleanup_function):
        """Guarda un nuevo inquilino desde la ventana modal - VERSIÓN CON ARCHIVOS"""
        conn = None
        try:
            # Obtener valores de todos los campos MODALES
            nombre = self.modal_nombre.get().strip()
            identificacion = self.modal_identificacion.get().strip()
            email = self.modal_email.get().strip()
            celular = self.modal_celular.get().strip()
            profesion = self.modal_profesion.get().strip()
            apto = self.modal_apto.get().strip()
            renta = self.modal_renta.get().strip()
            estado = self.modal_estado.get()
            fecha_ingreso = self.modal_fecha.get().strip()
            deposito = self.modal_deposito.get().strip()
            contacto_emergencia = self.modal_contacto.get().strip()
            telefono_emergencia = self.modal_tel_emergencia.get().strip()
            relacion_emergencia = self.modal_relacion.get()
            notas = self.modal_notas.get(1.0, tk.END).strip()

            # Validaciones básicas obligatorias
            if not nombre:
                messagebox.showwarning("Campo requerido", "El nombre es obligatorio.")
                self.modal_nombre.focus()
                return

            if not apto:
                messagebox.showwarning("Campo requerido", "El apartamento es obligatorio.")
                self.modal_apto.focus()
                return

            if not renta:
                messagebox.showwarning("Campo requerido", "La renta es obligatoria.")
                self.modal_renta.focus()
                return

            # Validación de renta
            try:
                renta = float(renta)
                if renta <= 0:
                    messagebox.showerror("Error", "La renta debe ser un número positivo.")
                    self.modal_renta.focus()
                    return
            except ValueError:
                messagebox.showerror("Error", "La renta debe ser un número válido.")
                self.modal_renta.focus()
                return

            # Validación de depósito
            deposito_valor = 0
            if deposito:
                try:
                    deposito_valor = float(deposito)
                    if deposito_valor < 0:
                        messagebox.showerror("Error", "El depósito no puede ser negativo.")
                        self.modal_deposito.focus()
                        return
                except ValueError:
                    messagebox.showerror("Error", "El depósito debe ser un número válido.")
                    self.modal_deposito.focus()
                    return

            # Validación de email
            if email and '@' not in email:
                messagebox.showwarning("Email inválido", "Por favor ingresa un email válido.")
                self.modal_email.focus()
                return

            # Iniciar conexión a la base de datos
            conn = sqlite3.connect('edificio.db', timeout=20)
            cursor = conn.cursor()

            # Verificar que no existe otro inquilino con la misma identificación
            if identificacion:
                cursor.execute("SELECT nombre FROM inquilinos WHERE identificacion = ? AND identificacion != ''",
                           (identificacion,))
                resultado = cursor.fetchone()
                if resultado:
                    messagebox.showerror("Identificación duplicada",
                                     f"Ya existe un inquilino con la identificación {identificacion}: {resultado[0]}")
                    self.modal_identificacion.focus()
                    return

            # Verificar que no existe otro inquilino en el mismo apartamento activo
            cursor.execute("SELECT nombre FROM inquilinos WHERE apartamento = ? AND estado = 'Activo'", (apto,))
            resultado = cursor.fetchone()
            if resultado:
                if not messagebox.askyesno("Apartamento ocupado",
                                       f"El apartamento {apto} ya tiene un inquilino activo: {resultado[0]}\n"
                                       f"¿Deseas continuar de todas formas?"):
                    self.modal_apto.focus()
                    return

            # Guardar en la base de datos
            cursor.execute("""
                INSERT INTO inquilinos (
                    nombre, identificacion, email, celular, profesion,
                    apartamento, renta, estado, fecha_ingreso, deposito,
                    contacto_emergencia, telefono_emergencia, relacion_emergencia, notas
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nombre, identificacion, email, celular, profesion,
                  apto, renta, estado, fecha_ingreso, deposito_valor,
                  contacto_emergencia, telefono_emergencia, relacion_emergencia, notas))

            # Obtener el ID del inquilino recién creado
            inquilino_id = cursor.lastrowid

            # Copiar archivos adjuntos si existen
            archivos_copiados = self.copiar_archivos_inquilino_modal(inquilino_id, nombre)

            # Actualizar rutas de archivos en la base de datos
            if archivos_copiados:
                archivo_id_final = archivos_copiados.get('identificacion', None)
                archivo_contrato_final = archivos_copiados.get('contrato', None)
                fecha_actual = datetime.datetime.now().isoformat()

                cursor.execute("""
                    UPDATE inquilinos 
                    SET archivo_identificacion = ?, archivo_contrato = ?,
                        fecha_archivo_id = ?, fecha_archivo_contrato = ?
                    WHERE id = ?
                """, (archivo_id_final, archivo_contrato_final,
                      fecha_actual if archivo_id_final else None,
                      fecha_actual if archivo_contrato_final else None,
                      inquilino_id))

            # Confirmar transacción
            conn.commit()

            # Mensaje de éxito con información de archivos
            mensaje_exito = f"Inquilino {nombre} registrado exitosamente en el apartamento {apto}."
            if archivos_copiados:
                archivos_info = []
                if 'identificacion' in archivos_copiados:
                    archivos_info.append("identificación")
                if 'contrato' in archivos_copiados:
                    archivos_info.append("contrato")
                mensaje_exito += f"\n\nArchivos adjuntados: {', '.join(archivos_info)}"

            # Mostrar mensaje de éxito
            messagebox.showinfo("✅ Éxito", mensaje_exito)
            play_notification_sound()

            # Actualizar estadísticas
            self.actualizar_estadisticas()

            # Actualizar combo box de inquilinos en la pestaña de pagos
            self.manager.payment_module.cargar_inquilinos_combo()

            # Actualizar lista de inquilinos si la ventana está abierta
            if hasattr(self, 'tree_inquilinos'):
                self.cargar_inquilinos_listado()

            # Cerrar ventana modal
            cleanup_function()

        except sqlite3.Error as e:
            if "database is locked" in str(e):
                messagebox.showerror("Error de base de datos", 
                                   "La base de datos está ocupada. Por favor, espere un momento y vuelva a intentarlo.")
            else:
                messagebox.showerror("Error de base de datos", f"Error al guardar: {e}")
            if conn:
                conn.rollback()
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    def seleccionar_archivo_id_modal(self):
        """Selecciona archivo de identificación"""
        try:
            # Temporalmente desactivar topmost para el diálogo
            for window in self.manager.root.winfo_children():
                if hasattr(window, 'attributes'):
                    try:
                        window.attributes('-topmost', False)
                    except:
                        pass

            file_path = filedialog.askopenfilename(
                title="Seleccionar archivo de identificación",
                filetypes=[
                    ("Archivos de imagen", "*.jpg *.jpeg *.png *.pdf"),
                    ("Archivos PDF", "*.pdf"),
                    ("Archivos de imagen", "*.jpg *.jpeg *.png"),
                    ("Todos los archivos", "*.*")
                ]
            )

            # Reactivar topmost después del diálogo
            for window in self.manager.root.winfo_children():
                if hasattr(window, 'attributes') and 'Agregar' in str(window.title):
                    try:
                        window.attributes('-topmost', True)
                        window.lift()
                    except:
                        pass

            if file_path:
                self.modal_id_file_path = file_path
                filename = os.path.basename(file_path)
                self.modal_id_file_label.config(text=filename, foreground="green")

        except Exception as e:
            logging.error(f"Error seleccionando archivo ID: {e}")
            messagebox.showerror("Error", f"Error seleccionando archivo: {e}")

    def seleccionar_archivo_contrato_modal(self):
        """Selecciona archivo de contrato"""
        try:
            # Temporalmente desactivar topmost
            for window in self.manager.root.winfo_children():
                if hasattr(window, 'attributes'):
                    try:
                        window.attributes('-topmost', False)
                    except:
                        pass

            file_path = filedialog.askopenfilename(
                title="Seleccionar contrato de arrendamiento",
                filetypes=[
                    ("Archivos PDF", "*.pdf"),
                    ("Archivos de imagen", "*.jpg *.jpeg *.png"),
                    ("Documentos Word", "*.doc *.docx"),
                    ("Todos los archivos", "*.*")
                ]
            )

            # Reactivar topmost
            for window in self.manager.root.winfo_children():
                if hasattr(window, 'attributes') and 'Agregar' in str(window.title):
                    try:
                        window.attributes('-topmost', True)
                        window.lift()
                    except:
                        pass

            if file_path:
                self.modal_contract_file_path = file_path
                filename = os.path.basename(file_path)
                self.modal_contract_file_label.config(text=filename, foreground="green")

        except Exception as e:
            logging.error(f"Error seleccionando archivo contrato: {e}")
            messagebox.showerror("Error", f"Error seleccionando archivo: {e}")

    def copiar_archivos_inquilino_modal(self, inquilino_id, nombre_inquilino):
        """Copia los archivos adjuntos a la carpeta del inquilino"""
        try:
            # Crear carpeta para archivos del inquilino
            carpeta_inquilino = f"Archivos_Inquilinos/{inquilino_id}_{nombre_inquilino.replace(' ', '_')}"

            if not os.path.exists(carpeta_inquilino):
                os.makedirs(carpeta_inquilino)

            archivos_copiados = {}

            # Copiar archivo de identificación
            if hasattr(self, 'modal_id_file_path') and self.modal_id_file_path:
                extension = os.path.splitext(self.modal_id_file_path)[1]
                nuevo_nombre = f"identificacion_{inquilino_id}{extension}"
                ruta_destino = os.path.join(carpeta_inquilino, nuevo_nombre)

                shutil.copy2(self.modal_id_file_path, ruta_destino)
                archivos_copiados['identificacion'] = ruta_destino

            # Copiar archivo de contrato
            if hasattr(self, 'modal_contract_file_path') and self.modal_contract_file_path:
                extension = os.path.splitext(self.modal_contract_file_path)[1]
                nuevo_nombre = f"contrato_{inquilino_id}{extension}"
                ruta_destino = os.path.join(carpeta_inquilino, nuevo_nombre)

                shutil.copy2(self.modal_contract_file_path, ruta_destino)
                archivos_copiados['contrato'] = ruta_destino

            return archivos_copiados

        except Exception as e:
            logging.error(f"Error copiando archivos: {e}")
            return {}

    def mostrar_ventana_detalles_inquilino(self, inquilino_id, datos, total_pagado, num_pagos, ultimo_pago):
        """Muestra una ventana con los detalles completos del inquilino"""
        # Crear ventana modal
        detalles_window = tk.Toplevel()
        detalles_window.title(f"📋 Detalles Completos - {datos[1]}")  # datos[1] es el nombre
        detalles_window.geometry("800x600")
        detalles_window.transient(self.root)
        detalles_window.grab_set()

        # Frame principal con scroll
        main_frame = ttk.Frame(detalles_window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Canvas y scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Título
        title_frame = ttk.Frame(scrollable_frame)
        title_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(title_frame,
                text="ℹ️ Información Completa del Inquilino",
                font=("Segoe UI", 16, "bold"),
                foreground="#2c3e50").pack()

        # Información Personal
        self.create_info_section(scrollable_frame, "👤 Información Personal", [
            ("Nombre completo:", datos[1]),
            ("Identificación:", datos[4] or "No especificado"),
            ("Email:", datos[5] or "No especificado"),
            ("Celular:", datos[6] or "No especificado"),
            ("Profesión:", datos[7] or "No especificado")
        ])

        # Información del Arrendamiento
        self.create_info_section(scrollable_frame, "🏠 Información del Arrendamiento", [
            ("Apartamento:", datos[2]),
            ("Renta mensual:", f"${datos[3]:,.2f}" if datos[3] else "No especificado"),
            ("Estado:", datos[10] or "Activo"),
            ("Fecha de ingreso:", datos[8] or "No especificado"),
            ("Depósito:", f"${datos[9]:,.2f}" if datos[9] else "No especificado")
        ])

        # Contacto de Emergencia
        self.create_info_section(scrollable_frame, "🚨 Contacto de Emergencia", [
            ("Nombre:", datos[11] or "No especificado"),
            ("Teléfono:", datos[12] or "No especificado"),
            ("Relación:", datos[13] or "No especificado")
        ])

        # Información de Pagos
        pagos_info = [
            ("Total pagado:", f"${total_pagado:,.2f}"),
            ("Número de pagos:", str(num_pagos)),
        ]
        if ultimo_pago:
            pagos_info.append(("Último pago:", f"${ultimo_pago[1]:,.2f} ({ultimo_pago[0]})"))
        else:
            pagos_info.append(("Último pago:", "No hay pagos registrados"))

        self.create_info_section(scrollable_frame, "💰 Información de Pagos", pagos_info)

        # Documentos
        docs_info = []
        if datos[15]:  # archivo_identificacion
            docs_info.append(("ID:", datos[15]))
            if datos[17]:  # fecha_archivo_id
                docs_info.append(("Fecha ID:", datos[17]))
        if datos[16]:  # archivo_contrato
            docs_info.append(("Contrato:", datos[16]))
            if datos[18]:  # fecha_archivo_contrato
                docs_info.append(("Fecha contrato:", datos[18]))

        if docs_info:
            self.create_info_section(scrollable_frame, "📄 Documentos", docs_info)

        # Notas
        if datos[14]:  # notas
            self.create_info_section(scrollable_frame, "📝 Notas", [
                ("Notas:", datos[14])
            ])

        # Botones de acción
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill="x", pady=10)

        ttk.Button(button_frame, text="✏️ Editar",
                  command=lambda: self.editar_inquilino_por_id(inquilino_id)).pack(side="left", padx=5)

        ttk.Button(button_frame, text="📄 Generar PDF",
                  command=lambda: self.generar_ficha_inquilino(inquilino_id)).pack(side="left", padx=5)

        ttk.Button(button_frame, text="❌ Cerrar",
                  command=detalles_window.destroy).pack(side="right", padx=5)

        # Configurar scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Agregar evento de scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        canvas.bind("<MouseWheel>", _on_mousewheel)
        detalles_window.bind("<MouseWheel>", _on_mousewheel)

    def create_info_section(self, parent, title, data_pairs):
        """Crea una sección de información con título y pares de datos"""
        section = ttk.LabelFrame(parent, text=title, padding=10)
        section.pack(fill="x", pady=5, padx=5)

        for label, value in data_pairs:
            row = ttk.Frame(section)
            row.pack(fill="x", pady=2)

            ttk.Label(row, text=label, width=20, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
            
            # Si es un documento (ID o Contrato), agregar un botón para abrirlo
            if "Archivos_Inquilinos" in str(value):
                btn_frame = ttk.Frame(row)
                btn_frame.pack(side="left", fill="x", expand=True)
                
                # Label con el nombre del archivo
                ttk.Label(btn_frame, text=os.path.basename(str(value)), wraplength=300).pack(side="left", padx=(0, 10))
                
                # Botón para abrir el archivo
                ttk.Button(btn_frame, 
                          text="📄 Ver documento",
                          command=lambda v=value: self.abrir_archivo(v)).pack(side="left")
            else:
                ttk.Label(row, text=str(value), wraplength=400).pack(side="left", fill="x", expand=True)

    def mostrar_formulario_editar(self, inquilino_id, datos):
        """Abre ventana modal para editar inquilino con datos pre-cargados"""

        # Marcar que hay ventana modal activa
        self._add_modal_active = True

        # Crear ventana modal
        edit_window = tk.Toplevel()
        edit_window.title(f"✏️ Editar Inquilino - {datos[0]}")
        edit_window.geometry("750x650")
        edit_window.resizable(True, True)
        edit_window.transient(self.manager.root)
        edit_window.grab_set()

        # === SISTEMA DE SCROLL ===
        main_frame = ttk.Frame(edit_window)
        main_frame.pack(fill="both", expand=True, padx=15, pady=5)

        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Scroll con rueda del mouse
        def modal_scroll(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"

        edit_window.bind("<MouseWheel>", modal_scroll)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Función de cleanup
        def cleanup_and_close():
            try:
                self._add_modal_active = False
                edit_window.unbind("<MouseWheel>")
                edit_window.destroy()
            except Exception as e:
                logging.error(f"Error en cleanup: {e}")

        # Centrar ventana
        edit_window.update_idletasks()
        width = 750
        height = 680
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = 5
        edit_window.geometry(f'{width}x{height}+{x}+{y}')

        # Crear formulario con datos pre-cargados
        self.setup_edit_form_modal(scrollable_frame, edit_window, cleanup_and_close, inquilino_id, datos)

        # Protocolo de cierre
        edit_window.protocol("WM_DELETE_WINDOW", cleanup_and_close)

        # Foco
        edit_window.focus_force()

        logging.info(f"Ventana de edición abierta para inquilino: {datos[0]}")

    def setup_edit_form_modal(self, parent, window, cleanup_function, inquilino_id, datos):
        """Configura el formulario de edición con calendario mejorado"""

        # Título
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill="x", pady=(0, 20))

        title_label = tk.Label(title_frame,
                               text=f"✏️ Editar Información del Inquilino",
                               font=("Segoe UI", 16, "bold"),
                               fg="#2c3e50")
        title_label.pack()

        subtitle_label = tk.Label(title_frame,
                                  text=f"Modificando datos de: {inquilino_id}",
                                  font=("Segoe UI", 12),
                                  fg="#6c757d")
        subtitle_label.pack()

        # === INFORMACIÓN PERSONAL ===
        personal_frame = ttk.LabelFrame(parent, text="👤 Información Personal", padding="15")
        personal_frame.pack(fill="x", pady=(0, 10))

        # Fila 1
        row1 = ttk.Frame(personal_frame)
        row1.pack(fill="x", pady=5)

        ttk.Label(row1, text="Nombre completo:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_nombre = ttk.Entry(row1, width=25)
        self.edit_nombre.insert(0, datos[0] or "")  # nombre
        self.edit_nombre.grid(row=0, column=1, sticky="ew", padx=(0, 20))

        ttk.Label(row1, text="Identificación:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.edit_identificacion = ttk.Entry(row1, width=15)
        self.edit_identificacion.insert(0, datos[3] or "")  # identificacion
        self.edit_identificacion.grid(row=0, column=3, sticky="ew")

        row1.columnconfigure(1, weight=1)
        row1.columnconfigure(3, weight=1)

        # Fila 2
        row2 = ttk.Frame(personal_frame)
        row2.pack(fill="x", pady=5)

        ttk.Label(row2, text="Email:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_email = ttk.Entry(row2, width=25)
        self.edit_email.insert(0, datos[4] or "")  # email
        self.edit_email.grid(row=0, column=1, sticky="ew", padx=(0, 20))

        ttk.Label(row2, text="Celular:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.edit_celular = ttk.Entry(row2, width=15)
        self.edit_celular.insert(0, datos[5] or "")  # celular
        self.edit_celular.grid(row=0, column=3, sticky="ew")

        row2.columnconfigure(1, weight=1)
        row2.columnconfigure(3, weight=1)

        # Profesión
        row3 = ttk.Frame(personal_frame)
        row3.pack(fill="x", pady=5)

        ttk.Label(row3, text="Profesión:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_profesion = ttk.Entry(row3, width=40)
        self.edit_profesion.insert(0, datos[6] or "")  # profesion
        self.edit_profesion.grid(row=0, column=1, sticky="ew")

        row3.columnconfigure(1, weight=1)

        # === INFORMACIÓN DEL ARRENDAMIENTO ===
        rental_frame = ttk.LabelFrame(parent, text="🏠 Información del Arrendamiento", padding="15")
        rental_frame.pack(fill="x", pady=(0, 10))

        # Fila arrendamiento 1
        rent_row1 = ttk.Frame(rental_frame)
        rent_row1.pack(fill="x", pady=5)

        ttk.Label(rent_row1, text="Apartamento:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_apto = ttk.Entry(rent_row1, width=10)
        self.edit_apto.insert(0, datos[1] or "")  # apartamento
        self.edit_apto.grid(row=0, column=1, sticky="w", padx=(0, 20))

        ttk.Label(rent_row1, text="Renta mensual:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.edit_renta = ttk.Entry(rent_row1, width=15)
        self.edit_renta.insert(0, str(datos[2]) if datos[2] else "")  # renta
        self.edit_renta.grid(row=0, column=3, sticky="w", padx=(0, 20))

        ttk.Label(rent_row1, text="Estado:").grid(row=0, column=4, sticky="w", padx=(0, 10))
        self.edit_estado = ttk.Combobox(rent_row1, width=12,
                                        values=["Activo", "Pendiente", "Inactivo", "Moroso", "Suspendido"])
        self.edit_estado.set(datos[9] or "Activo")  # estado
        self.edit_estado.grid(row=0, column=5, sticky="w")

        # Fila arrendamiento 2
        rent_row2 = ttk.Frame(rental_frame)
        rent_row2.pack(fill="x", pady=5)

        ttk.Label(rent_row2, text="Fecha ingreso:").grid(row=0, column=0, sticky="w", padx=(0, 10))

        # === SELECTOR DE FECHA MEJORADO PARA EDITAR ===
        if CALENDAR_AVAILABLE:
            # Usar DateEntry con calendario visual
            self.edit_fecha = DateEntry(rent_row2,
                                        width=12,
                                        background='#007acc',
                                        foreground='white',
                                        borderwidth=2,
                                        date_pattern='yyyy-mm-dd',
                                        state='readonly',
                                        showweeknumbers=False,
                                        locale='es_ES',
                                        selectbackground='#0078d4',
                                        selectforeground='white',
                                        normalbackground='white',
                                        normalforeground='black',
                                        font=('Segoe UI', 9))

            # Cargar fecha existente o fecha actual
            if datos[7]:  # Si hay fecha, cargarla
                try:
                    fecha_obj = datetime.datetime.fromisoformat(datos[7]).date()
                    self.edit_fecha.set_date(fecha_obj)
                except:
                    self.edit_fecha.set_date(datetime.date.today())
            else:
                self.edit_fecha.set_date(datetime.date.today())
        else:
            # Fallback a Entry normal
            self.edit_fecha = ttk.Entry(rent_row2, width=12)
            self.edit_fecha.insert(0, datos[7] or datetime.date.today().isoformat())

        self.edit_fecha.grid(row=0, column=1, sticky="w", padx=(0, 20))

        ttk.Label(rent_row2, text="Depósito:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.edit_deposito = ttk.Entry(rent_row2, width=15)
        self.edit_deposito.insert(0, str(datos[8]) if datos[8] else "")  # deposito
        self.edit_deposito.grid(row=0, column=3, sticky="w")

        # === CONTACTO DE EMERGENCIA ===
        emergency_frame = ttk.LabelFrame(parent, text="🚨 Contacto de Emergencia", padding="15")
        emergency_frame.pack(fill="x", pady=(0, 10))

        emerg_row1 = ttk.Frame(emergency_frame)
        emerg_row1.pack(fill="x", pady=5)

        ttk.Label(emerg_row1, text="Nombre contacto:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_contacto = ttk.Entry(emerg_row1, width=25)
        self.edit_contacto.insert(0, datos[10] or "")  # contacto_emergencia
        self.edit_contacto.grid(row=0, column=1, sticky="ew", padx=(0, 20))

        ttk.Label(emerg_row1, text="Teléfono:").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.edit_tel_emergencia = ttk.Entry(emerg_row1, width=15)
        self.edit_tel_emergencia.insert(0, datos[11] or "")  # telefono_emergencia
        self.edit_tel_emergencia.grid(row=0, column=3, sticky="ew")

        emerg_row1.columnconfigure(1, weight=1)
        emerg_row1.columnconfigure(3, weight=1)

        emerg_row2 = ttk.Frame(emergency_frame)
        emerg_row2.pack(fill="x", pady=5)

        ttk.Label(emerg_row2, text="Relación:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_relacion = ttk.Combobox(emerg_row2, width=15,
                                          values=["Padre", "Madre", "Esposo/a", "Hermano/a", "Hijo/a", "Amigo/a",
                                                  "Otro"])
        self.edit_relacion.set(datos[12] or "")  # relacion_emergencia
        self.edit_relacion.grid(row=0, column=1, sticky="w")

        # === NOTAS ===
        notes_frame = ttk.LabelFrame(parent, text="📝 Notas Adicionales", padding="15")
        notes_frame.pack(fill="x", pady=(0, 10))

        self.edit_notas = tk.Text(notes_frame, height=4, width=60)
        self.edit_notas.insert(1.0, datos[13] or "")  # notas
        self.edit_notas.pack(fill="x")

        # === ARCHIVOS ADJUNTOS ===
        files_frame = ttk.LabelFrame(parent, text="📎 Archivos Adjuntos", padding="15")
        files_frame.pack(fill="x", pady=(0, 10))

        files_row1 = ttk.Frame(files_frame)
        files_row1.pack(fill="x", pady=5)

        # Archivo de Identificación
        ttk.Label(files_row1, text="🪪 Identificación:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_id_file_label = ttk.Label(files_row1,
                                            text=os.path.basename(datos[14]) if datos[14] else "No seleccionado",
                                            foreground="blue" if datos[14] else "gray")
        self.edit_id_file_label.grid(row=0, column=1, sticky="w", padx=(0, 10))

        ttk.Button(files_row1, text="📁 Cambiar",
                   command=lambda: self.seleccionar_archivo_edit_id()).grid(row=0, column=2, padx=(0, 5))

        files_row2 = ttk.Frame(files_frame)
        files_row2.pack(fill="x", pady=5)

        # Archivo de Contrato
        ttk.Label(files_row2, text="📄 Contrato:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.edit_contract_file_label = ttk.Label(files_row2,
                                                  text=os.path.basename(datos[15]) if datos[15] else "No seleccionado",
                                                  foreground="blue" if datos[15] else "gray")
        self.edit_contract_file_label.grid(row=0, column=1, sticky="w", padx=(0, 10))

        ttk.Button(files_row2, text="📁 Cambiar",
                   command=lambda: self.seleccionar_archivo_edit_contrato()).grid(row=0, column=2, padx=(0, 5))

        # === BOTONES ===
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x", pady=20)

        ttk.Button(btn_frame, text="💾 Guardar Cambios",
                   command=lambda: self.actualizar_inquilino_modal(window, cleanup_function, inquilino_id)).pack(
            side="right", padx=(10, 0))
        ttk.Button(btn_frame, text="❌ Cancelar",
                   command=cleanup_function).pack(side="right")

    def seleccionar_archivo_edit_id(self):
        """Selecciona archivo de identificación"""
        try:
            # Temporalmente desactivar topmost para el diálogo
            for window in self.manager.root.winfo_children():
                if hasattr(window, 'attributes'):
                    try:
                        window.attributes('-topmost', False)
                    except:
                        pass

            file_path = filedialog.askopenfilename(
                title="Seleccionar archivo de identificación",
                filetypes=[
                    ("Archivos de imagen", "*.jpg *.jpeg *.png *.pdf"),
                    ("Archivos PDF", "*.pdf"),
                    ("Archivos de imagen", "*.jpg *.jpeg *.png"),
                    ("Todos los archivos", "*.*")
                ]
            )

            # Reactivar topmost después del diálogo
            for window in self.manager.root.winfo_children():
                if hasattr(window, 'attributes') and 'Agregar' in str(window.title):
                    try:
                        window.attributes('-topmost', True)
                        window.lift()
                    except:
                        pass

            if file_path:
                self.edit_id_file_path = file_path
                filename = os.path.basename(file_path)
                self.edit_id_file_label.config(text=filename, foreground="blue")

        except Exception as e:
            logging.error(f"Error seleccionando archivo ID en edición: {e}")
            messagebox.showerror("Error", f"Error seleccionando archivo: {e}")

    def seleccionar_archivo_edit_contrato(self):
        """Selecciona nuevo archivo de contrato para edición"""
        try:
            file_path = filedialog.askopenfilename(
                title="Cambiar contrato de arrendamiento",
                filetypes=[
                    ("Archivos PDF", "*.pdf"),
                    ("Archivos de imagen", "*.jpg *.jpeg *.png"),
                    ("Documentos Word", "*.doc *.docx"),
                    ("Todos los archivos", "*.*")
                ]
            )

            if file_path:
                self.edit_contract_file_path = file_path
                filename = os.path.basename(file_path)
                self.edit_contract_file_label.config(text=filename, foreground="blue")

        except Exception as e:
            logging.error(f"Error seleccionando archivo contrato en edición: {e}")
            messagebox.showerror("Error", f"Error seleccionando archivo: {e}")

    def actualizar_inquilino_modal(self, window, cleanup_function, inquilino_id):
        """Actualiza los datos del inquilino editado"""
        conn = None
        try:
            # Obtener valores del formulario de edición
            nombre = self.edit_nombre.get().strip()
            identificacion = self.edit_identificacion.get().strip()
            email = self.edit_email.get().strip()
            celular = self.edit_celular.get().strip()
            profesion = self.edit_profesion.get().strip()
            apto = self.edit_apto.get().strip()
            renta = self.edit_renta.get().strip()
            estado = self.edit_estado.get()
            fecha_ingreso = self.edit_fecha.get().strip()
            deposito = self.edit_deposito.get().strip()
            contacto_emergencia = self.edit_contacto.get().strip()
            telefono_emergencia = self.edit_tel_emergencia.get().strip()
            relacion_emergencia = self.edit_relacion.get()
            notas = self.edit_notas.get(1.0, tk.END).strip()

            # Validaciones básicas
            if not nombre:
                messagebox.showwarning("Campo requerido", "El nombre es obligatorio.")
                self.edit_nombre.focus()
                return

            if not apto:
                messagebox.showwarning("Campo requerido", "El apartamento es obligatorio.")
                self.edit_apto.focus()
                return

            if not renta:
                messagebox.showwarning("Campo requerido", "La renta es obligatoria.")
                self.edit_renta.focus()
                return

            # Validación de renta
            try:
                renta = float(renta)
                if renta <= 0:
                    messagebox.showerror("Error", "La renta debe ser un número positivo.")
                    self.edit_renta.focus()
                    return
            except ValueError:
                messagebox.showerror("Error", "La renta debe ser un número válido.")
                self.edit_renta.focus()
                return

            # Validación de depósito
            deposito_valor = 0
            if deposito:
                try:
                    deposito_valor = float(deposito)
                    if deposito_valor < 0:
                        messagebox.showerror("Error", "El depósito no puede ser negativo.")
                        self.edit_deposito.focus()
                        return
                except ValueError:
                    messagebox.showerror("Error", "El depósito debe ser un número válido.")
                    self.edit_deposito.focus()
                    return

            # Validación de email
            if email and '@' not in email:
                messagebox.showwarning("Email inválido", "Por favor ingresa un email válido.")
                self.edit_email.focus()
                return

            # Iniciar conexión a la base de datos con timeout extendido
            conn = sqlite3.connect('edificio.db', timeout=20)
            cursor = conn.cursor()

            # Query base de actualización
            cursor.execute("""
                UPDATE inquilinos 
                SET nombre = ?, apartamento = ?, renta = ?, identificacion = ?, email = ?, 
                    celular = ?, profesion = ?, fecha_ingreso = ?, deposito = ?, estado = ?,
                    contacto_emergencia = ?, telefono_emergencia = ?, relacion_emergencia = ?, notas = ?
                WHERE id = ?
            """, (nombre, apto, renta, identificacion, email, celular, profesion,
                  fecha_ingreso, deposito_valor, estado, contacto_emergencia,
                  telefono_emergencia, relacion_emergencia, notas, inquilino_id))

            # PROCESAR ARCHIVOS ADJUNTOS EN EDICIÓN
            archivos_actualizados = self.procesar_archivos_edicion(inquilino_id, nombre)

            # Actualizar rutas de archivos en la base de datos si hay cambios
            if archivos_actualizados:
                archivo_id_final = archivos_actualizados.get('identificacion', None)
                archivo_contrato_final = archivos_actualizados.get('contrato', None)
                fecha_actual = datetime.datetime.now().isoformat()

                cursor.execute("""
                    UPDATE inquilinos 
                    SET archivo_identificacion = COALESCE(?, archivo_identificacion),
                        archivo_contrato = COALESCE(?, archivo_contrato),
                        fecha_archivo_id = CASE WHEN ? IS NOT NULL THEN ? ELSE fecha_archivo_id END,
                        fecha_archivo_contrato = CASE WHEN ? IS NOT NULL THEN ? ELSE fecha_archivo_contrato END
                    WHERE id = ?
                """, (archivo_id_final, archivo_contrato_final,
                      archivo_id_final, fecha_actual if archivo_id_final else None,
                      archivo_contrato_final, fecha_actual if archivo_contrato_final else None,
                      inquilino_id))

            # Confirmar transacción
            conn.commit()

            # Mensaje de éxito
            messagebox.showinfo("✅ Éxito", f"Inquilino {nombre} actualizado exitosamente.")
            play_notification_sound()

            # Actualizar estadísticas
            self.actualizar_estadisticas()

            # Recargar lista si existe
            if hasattr(self, 'cargar_inquilinos_listado'):
                self.cargar_inquilinos_listado()

            # Cerrar ventana modal
            cleanup_function()

        except sqlite3.Error as e:
            if "database is locked" in str(e):
                messagebox.showerror("Error de base de datos", 
                                   "La base de datos está ocupada. Por favor, espere un momento y vuelva a intentarlo.")
            else:
                messagebox.showerror("Error de base de datos", f"Error actualizando inquilino: {e}")
            if conn:
                conn.rollback()
        except Exception as e:
            logging.error(f"Error actualizando inquilino: {e}")
            messagebox.showerror("Error", f"Error actualizando inquilino: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass

    def procesar_archivos_edicion(self, inquilino_id, nombre_inquilino):
        """Procesa archivos adjuntos durante la edición"""
        try:
            archivos_procesados = {}

            # Crear carpeta si no existe
            carpeta_inquilino = f"Archivos_Inquilinos/{inquilino_id}_{nombre_inquilino.replace(' ', '_')}"
            if not os.path.exists(carpeta_inquilino):
                os.makedirs(carpeta_inquilino)

            # Procesar archivo de identificación si cambió
            if hasattr(self, 'edit_id_file_path') and self.edit_id_file_path:
                # Verificar si es un archivo nuevo (no es la ruta existente)
                if not self.edit_id_file_path.startswith("Archivos_Inquilinos"):
                    extension = os.path.splitext(self.edit_id_file_path)[1]
                    nuevo_nombre = f"identificacion_{inquilino_id}{extension}"
                    ruta_destino = os.path.join(carpeta_inquilino, nuevo_nombre)

                    shutil.copy2(self.edit_id_file_path, ruta_destino)
                    archivos_procesados['identificacion'] = ruta_destino

            # Procesar archivo de contrato si cambió
            if hasattr(self, 'edit_contract_file_path') and self.edit_contract_file_path:
                # Verificar si es un archivo nuevo
                if not self.edit_contract_file_path.startswith("Archivos_Inquilinos"):
                    extension = os.path.splitext(self.edit_contract_file_path)[1]
                    nuevo_nombre = f"contrato_{inquilino_id}{extension}"
                    ruta_destino = os.path.join(carpeta_inquilino, nuevo_nombre)

                    shutil.copy2(self.edit_contract_file_path, ruta_destino)
                    archivos_procesados['contrato'] = ruta_destino

            return archivos_procesados

        except Exception as e:
            logging.error(f"Error procesando archivos en edición: {e}")
            return {}

    def actualizar_grafico_estados(self):
        """Actualiza el gráfico de distribución por estados"""
        try:
            # Limpiar canvas
            self.chart_canvas.delete("all")

            # Obtener datos de estados
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            cursor.execute("""
                SELECT estado, COUNT(*) FROM inquilinos 
                GROUP BY estado
                ORDER BY COUNT(*) DESC
            """)

            datos = cursor.fetchall()
            conn.close()

            if not datos:
                self.chart_canvas.create_text(125, 100, text="Sin datos", font=("Segoe UI", 12))
                return

            # Colores para cada estado
            colores = {
                'Activo': '#27ae60',
                'Pendiente': '#f39c12',
                'Moroso': '#e74c3c',
                'Suspendido': '#8e44ad',
                'Inactivo': '#95a5a6'
            }

            # Calcular total
            total = sum(cantidad for _, cantidad in datos)

            # Dibujar gráfico de barras horizontal simple
            y_offset = 20
            bar_height = 25
            max_width = 180

            for i, (estado, cantidad) in enumerate(datos):
                # Calcular ancho de barra
                bar_width = (cantidad / total) * max_width if total > 0 else 0

                # Color de la barra
                color = colores.get(estado, '#95a5a6')

                # Dibujar barra
                self.chart_canvas.create_rectangle(
                    50, y_offset + i * (bar_height + 5),
                        50 + bar_width, y_offset + i * (bar_height + 5) + bar_height,
                    fill=color, outline=color
                )

                # Etiqueta del estado
                self.chart_canvas.create_text(
                    45, y_offset + i * (bar_height + 5) + bar_height // 2,
                    text=estado[:8], anchor="e", font=("Segoe UI", 8)
                )

                # Cantidad
                self.chart_canvas.create_text(
                    55 + bar_width, y_offset + i * (bar_height + 5) + bar_height // 2,
                    text=str(cantidad), anchor="w", font=("Segoe UI", 8, "bold")
                )

        except Exception as e:
            logging.error(f"Error actualizando gráfico: {e}")
            self.chart_canvas.create_text(125, 100, text="Error cargando gráfico", font=("Segoe UI", 10))

    def actualizar_actividad_reciente(self):
        """Actualiza la actividad reciente"""
        try:
            self.activity_text.config(state=tk.NORMAL)
            self.activity_text.delete(1.0, tk.END)

            # Obtener actividad reciente de pagos
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            cursor.execute("""
                SELECT p.fecha, i.nombre, i.apartamento, p.monto
                FROM pagos p
                JOIN inquilinos i ON p.inquilino_id = i.id
                ORDER BY p.fecha DESC
                LIMIT 10
            """)

            pagos_recientes = cursor.fetchall()

            # Obtener inquilinos agregados recientemente
            cursor.execute("""
                SELECT nombre, apartamento, fecha_ingreso, estado
                FROM inquilinos
                WHERE fecha_ingreso IS NOT NULL
                ORDER BY fecha_ingreso DESC
                LIMIT 5
            """)

            nuevos_inquilinos = cursor.fetchall()
            conn.close()

            # Mostrar actividad
            self.activity_text.insert(tk.END, "💰 PAGOS RECIENTES:\n", "header")

            if pagos_recientes:
                for fecha, nombre, apto, monto in pagos_recientes[:5]:
                    fecha_formato = datetime.datetime.fromisoformat(fecha).strftime("%d/%m")
                    self.activity_text.insert(tk.END, f"• {fecha_formato} - {nombre} (Apto {apto}): ${monto:,.0f}\n")
            else:
                self.activity_text.insert(tk.END, "• No hay pagos registrados\n")

            self.activity_text.insert(tk.END, f"\n👥 NUEVOS INQUILINOS:\n", "header")

            if nuevos_inquilinos:
                for nombre, apto, fecha_ingreso, estado in nuevos_inquilinos[:3]:
                    if fecha_ingreso:
                        try:
                            fecha_formato = datetime.datetime.fromisoformat(fecha_ingreso).strftime("%d/%m/%Y")
                        except:
                            fecha_formato = fecha_ingreso
                        self.activity_text.insert(tk.END, f"• {nombre} - Apto {apto} ({fecha_formato})\n")
            else:
                self.activity_text.insert(tk.END, "• No hay nuevos inquilinos\n")

            # Configurar tags para headers
            self.activity_text.tag_configure("header", font=("Segoe UI", 9, "bold"))

            self.activity_text.config(state=tk.DISABLED)

        except Exception as e:
            logging.error(f"Error actualizando actividad: {e}")
            self.activity_text.config(state=tk.NORMAL)
            self.activity_text.delete(1.0, tk.END)
            self.activity_text.insert(tk.END, "Error cargando actividad reciente")
            self.activity_text.config(state=tk.DISABLED)

    def actualizar_metricas_adicionales(self):
        """Actualiza las métricas adicionales"""
        try:
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            # Calcular ocupación (asumiendo 20 apartamentos totales, ajusta según tu edificio)
            cursor.execute("SELECT COUNT(*) FROM inquilinos WHERE estado = 'Activo'")
            activos = cursor.fetchone()[0] or 0

            total_apartamentos = 20  # Ajusta este número según tu edificio
            ocupacion = (activos / total_apartamentos) * 100 if total_apartamentos > 0 else 0

            # Renta promedio
            cursor.execute("SELECT AVG(renta) FROM inquilinos WHERE estado = 'Activo' AND renta > 0")
            promedio_renta = cursor.fetchone()[0] or 0

            # Último inquilino que ingresó
            cursor.execute("""
                SELECT nombre, fecha_ingreso FROM inquilinos 
                WHERE fecha_ingreso IS NOT NULL 
                ORDER BY fecha_ingreso DESC 
                LIMIT 1
            """)
            ultimo_ingreso = cursor.fetchone()

            conn.close()

            # Actualizar labels
            self.ocupacion_label.config(text=f"🏠 Ocupación: {ocupacion:.1f}%")
            self.promedio_renta_label.config(text=f"💰 Renta Promedio: ${promedio_renta:,.0f}")

            if ultimo_ingreso and ultimo_ingreso[1]:
                try:
                    fecha_formato = datetime.datetime.fromisoformat(ultimo_ingreso[1]).strftime("%d/%m/%Y")
                    self.ultimo_ingreso_label.config(text=f"📅 Último Ingreso: {ultimo_ingreso[0]} ({fecha_formato})")
                except:
                    self.ultimo_ingreso_label.config(text=f"📅 Último Ingreso: {ultimo_ingreso[0]}")
            else:
                self.ultimo_ingreso_label.config(text="📅 Último Ingreso: N/A")

        except Exception as e:
            logging.error(f"Error actualizando métricas: {e}")

    def obtener_fecha_modal(self):
        """Obtiene la fecha del campo modal de forma segura"""
        try:
            if CALENDAR_AVAILABLE and hasattr(self.modal_fecha, 'get_date'):
                # Es un DateEntry
                return self.modal_fecha.get_date().isoformat()
            else:
                # Es un Entry normal
                return self.modal_fecha.get().strip()
        except:
            return datetime.date.today().isoformat()

    def obtener_fecha_edit(self):
        """Obtiene la fecha del campo de edición de forma segura"""
        try:
            if CALENDAR_AVAILABLE and hasattr(self.edit_fecha, 'get_date'):
                # Es un DateEntry
                return self.edit_fecha.get_date().isoformat()
            else:
                # Es un Entry normal
                return self.edit_fecha.get().strip()
        except:
            return datetime.date.today().isoformat()

    def generar_ficha_inquilino(self, inquilino_id):
        """Genera una ficha en PDF con los detalles del inquilino"""
        try:
            # Obtener datos del inquilino
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()
            
            # Consulta para obtener todos los datos del inquilino
            cursor.execute("""
                SELECT i.*, 
                       COALESCE(SUM(p.monto), 0) as total_pagado,
                       COUNT(p.id) as num_pagos,
                       MAX(p.fecha) as ultimo_pago_fecha,
                       (SELECT monto FROM pagos WHERE inquilino_id = i.id ORDER BY fecha DESC LIMIT 1) as ultimo_pago_monto
                FROM inquilinos i
                LEFT JOIN pagos p ON i.id = p.inquilino_id
                WHERE i.id = ?
                GROUP BY i.id
            """, (inquilino_id,))
            
            datos = cursor.fetchone()
            conn.close()

            if not datos:
                messagebox.showerror("Error", "No se encontraron los datos del inquilino.")
                return

            # Generar nombre del archivo
            nombre_archivo = f"ficha_inquilino_{datos[1].replace(' ', '_')}_{datos[2]}.pdf"

            # Crear PDF
            c = canvas.Canvas(nombre_archivo, pagesize=letter)
            ancho, alto = letter
            margen = 50
            y = alto - margen

            # Título
            c.setFont("Helvetica-Bold", 16)
            c.drawString(margen, y, "FICHA DE INQUILINO")
            y -= 30

            # Fecha de generación
            c.setFont("Helvetica", 10)
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.drawString(margen, y, f"Fecha de generación: {fecha_actual}")
            y -= 40

            # Información Personal
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margen, y, "Información Personal")
            y -= 20
            c.setFont("Helvetica", 12)
            info_personal = [
                ("Nombre completo:", datos[1]),
                ("Identificación:", datos[4] or "No especificado"),
                ("Email:", datos[5] or "No especificado"),
                ("Celular:", datos[6] or "No especificado"),
                ("Profesión:", datos[7] or "No especificado")
            ]
            for label, value in info_personal:
                c.drawString(margen, y, f"{label} {value}")
                y -= 20
            y -= 20

            # Información del Arrendamiento
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margen, y, "Información del Arrendamiento")
            y -= 20
            c.setFont("Helvetica", 12)
            info_arriendo = [
                ("Apartamento:", datos[2]),
                ("Renta mensual:", f"${datos[3]:,.2f}" if datos[3] else "No especificado"),
                ("Estado:", datos[10] or "Activo"),
                ("Fecha de ingreso:", datos[8] or "No especificado"),
                ("Depósito:", f"${datos[9]:,.2f}" if datos[9] else "No especificado")
            ]
            for label, value in info_arriendo:
                c.drawString(margen, y, f"{label} {value}")
                y -= 20
            y -= 20

            # Contacto de Emergencia
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margen, y, "Contacto de Emergencia")
            y -= 20
            c.setFont("Helvetica", 12)
            info_emergencia = [
                ("Nombre:", datos[11] or "No especificado"),
                ("Teléfono:", datos[12] or "No especificado"),
                ("Relación:", datos[13] or "No especificado")
            ]
            for label, value in info_emergencia:
                c.drawString(margen, y, f"{label} {value}")
                y -= 20
            y -= 20

            # Información de Pagos
            c.setFont("Helvetica-Bold", 14)
            c.drawString(margen, y, "Información de Pagos")
            y -= 20
            c.setFont("Helvetica", 12)
            total_pagado = datos[-4] if datos[-4] else 0
            num_pagos = datos[-3] if datos[-3] else 0
            info_pagos = [
                ("Total pagado:", f"${total_pagado:,.2f}"),
                ("Número de pagos:", str(num_pagos))
            ]
            if datos[-2] and datos[-1]:  # Si hay último pago
                info_pagos.append(("Último pago:", f"${datos[-1]:,.2f} ({datos[-2]})"))
            else:
                info_pagos.append(("Último pago:", "No hay pagos registrados"))

            for label, value in info_pagos:
                c.drawString(margen, y, f"{label} {value}")
                y -= 20
            y -= 20

            # Notas
            if datos[14]:  # Si hay notas
                c.setFont("Helvetica-Bold", 14)
                c.drawString(margen, y, "Notas")
                y -= 20
                c.setFont("Helvetica", 12)
                # Dividir las notas en líneas si son muy largas
                notas = datos[14]
                palabras = notas.split()
                linea = ""
                for palabra in palabras:
                    if len(linea + " " + palabra) < 80:  # Límite de caracteres por línea
                        linea += " " + palabra if linea else palabra
                    else:
                        c.drawString(margen, y, linea)
                        y -= 20
                        linea = palabra
                if linea:  # Imprimir última línea
                    c.drawString(margen, y, linea)

            # Guardar PDF
            c.save()
            messagebox.showinfo("PDF Generado", f"La ficha se ha guardado como: {nombre_archivo}")

            # Abrir el PDF
            try:
                os.startfile(nombre_archivo)
            except:
                pass

        except Exception as e:
            logging.error(f"Error generando ficha PDF: {e}")
            messagebox.showerror("Error", f"Error generando ficha PDF: {e}")

class PaymentModule:
    def __init__(self, manager):
        self.manager = manager

    def setup_ui(self, parent):
        """Configura la interfaz de gestión de pagos"""
        # Frame principal
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text=" 💰 Pagos ")
        
        # Botón para volver al dashboard
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill="x", padx=20, pady=(20,10))
        
        back_btn = tk.Button(header_frame,
                           text="← Volver al Dashboard",
                           command=lambda: self.manager.notebook.select(0),
                           font=("Segoe UI", 10),
                           bg="#f0f0f0",
                           fg="#1a73e8",
                           bd=0,
                           padx=15,
                           pady=5,
                           cursor="hand2")
        back_btn.pack(side="left")

        # Frame para registrar pagos
        register_frame = ttk.LabelFrame(self.frame, text="Registrar Nuevo Pago", padding="10")
        register_frame.pack(fill="x", pady=10)

        # Seleccionar inquilino
        row1 = ttk.Frame(register_frame)
        row1.pack(fill="x", pady=5)

        ttk.Label(row1, text="Inquilino:").pack(side="left", padx=(0, 5))

        # Dropdown de inquilinos
        self.inquilino_var = StringVar()
        self.combo_inquilinos = ttk.Combobox(row1, textvariable=self.inquilino_var, width=40)
        self.combo_inquilinos.pack(side="left", fill="x", expand=True)
        self.combo_inquilinos.bind("<<ComboboxSelected>>", self.actualizar_monto)

        # Monto
        row2 = ttk.Frame(register_frame)
        row2.pack(fill="x", pady=5)

        ttk.Label(row2, text="Monto:").pack(side="left", padx=(0, 5))
        self.entry_monto = ttk.Entry(row2, width=15)
        self.entry_monto.pack(side="left")

        # Fecha
        ttk.Label(row2, text="Fecha:").pack(side="left", padx=(15, 5))

        self.entry_fecha = ttk.Entry(row2, width=15)
        # Fecha actual por defecto
        self.entry_fecha.insert(0, datetime.date.today().isoformat())
        self.entry_fecha.pack(side="left")

        # Botón de registrar
        btn_frame = ttk.Frame(register_frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Registrar Pago",
                   command=self.registrar_pago).pack(side="right")

        # Frame para historial de pagos
        history_frame = ttk.LabelFrame(self.frame, text="Historial de Pagos", padding="10")
        history_frame.pack(fill="both", expand=True, pady=10)

        # Filtro de historial
        filter_frame = ttk.Frame(history_frame)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="Filtrar por inquilino:").pack(side="left", padx=(0, 5))

        # Dropdown para filtro
        self.filtro_var = StringVar()
        self.combo_filtro = ttk.Combobox(filter_frame, textvariable=self.filtro_var, width=40)
        self.combo_filtro.pack(side="left", padx=(0, 5))

        ttk.Button(filter_frame, text="Filtrar",
                   command=self.filtrar_pagos).pack(side="left")
        ttk.Button(filter_frame, text="Mostrar Todos",
                   command=self.cargar_pagos).pack(side="left", padx=(5, 0))

        # Treeview para historial
        columns = ("id", "fecha", "inquilino", "apartamento", "monto")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings")

        # Definir encabezados
        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("inquilino", text="Inquilino")
        self.tree.heading("apartamento", text="Apartamento")
        self.tree.heading("monto", text="Monto")

        # Ajustar anchos de columna
        self.tree.column("id", width=50)
        self.tree.column("fecha", width=100)
        self.tree.column("inquilino", width=200)
        self.tree.column("apartamento", width=100)
        self.tree.column("monto", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Empaquetar widgets
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        btn_frame2 = ttk.Frame(self.frame)
        btn_frame2.pack(fill="x", pady=5)

        ttk.Button(btn_frame2, text="Generar Recibo",
                   command=self.generar_recibo).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame2, text="Eliminar Pago",
                   command=self.eliminar_pago).pack(side="left")

        # Cargar datos iniciales
        self.cargar_inquilinos_combo()
        self.cargar_pagos()

    def cargar_inquilinos_combo(self):
        """Carga la lista de inquilinos en los combos"""
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nombre, apartamento FROM inquilinos 
            ORDER BY nombre
        """)

        inquilinos = []
        self.mapa_inquilinos = {}  # Para mantener relación ID-nombre
        self.mapa_rentas = {}  # Para acceder a la renta por ID

        for id, nombre, apto in cursor.fetchall():
            texto = f"{nombre} - Apto {apto}"
            inquilinos.append(texto)
            self.mapa_inquilinos[texto] = id

            # Obtener renta
            cursor.execute("SELECT renta FROM inquilinos WHERE id = ?", (id,))
            renta = cursor.fetchone()[0]
            self.mapa_rentas[texto] = renta

        # Actualizar combos
        self.combo_inquilinos['values'] = inquilinos
        if inquilinos:
            self.combo_inquilinos.current(0)
            self.actualizar_monto()

        # Combo de filtro con opción adicional "Todos"
        self.combo_filtro['values'] = ["Todos"] + inquilinos
        self.combo_filtro.current(0)

        conn.close()

    def actualizar_monto(self, event=None):
        """Actualiza el monto según el inquilino seleccionado"""
        inquilino = self.inquilino_var.get()
        if inquilino in self.mapa_rentas:
            self.entry_monto.delete(0, tk.END)
            self.entry_monto.insert(0, str(self.mapa_rentas[inquilino]))

    def cargar_pagos(self):
        """Carga todos los pagos en el treeview"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Cargar desde la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.fecha, i.nombre, i.apartamento, p.monto 
            FROM pagos p
            JOIN inquilinos i ON p.inquilino_id = i.id
            ORDER BY p.fecha DESC
        """)

        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

        conn.close()

    def filtrar_pagos(self):
        """Filtra los pagos por inquilino seleccionado"""
        filtro = self.filtro_var.get()
        if filtro == "Todos":
            self.cargar_pagos()
            return

        # Obtener ID del inquilino
        inquilino_id = self.mapa_inquilinos.get(filtro)
        if not inquilino_id:
            return

        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Cargar pagos filtrados
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.id, p.fecha, i.nombre, i.apartamento, p.monto 
            FROM pagos p
            JOIN inquilinos i ON p.inquilino_id = i.id
            WHERE p.inquilino_id = ?
            ORDER BY p.fecha DESC
        """, (inquilino_id,))

        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

        conn.close()

    def registrar_pago(self):
        """Registra un nuevo pago"""
        inquilino = self.inquilino_var.get()
        monto = self.entry_monto.get()
        fecha = self.entry_fecha.get()

        # Validaciones
        if not inquilino:
            messagebox.showwarning("Selección", "Por favor selecciona un inquilino.")
            return

        if not monto:
            messagebox.showwarning("Monto", "Por favor ingresa el monto del pago.")
            return

        try:
            monto = float(monto)
            if monto <= 0:
                messagebox.showerror("Error", "El monto debe ser un número positivo.")
                return
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número.")
            return

        try:
            datetime.date.fromisoformat(fecha)
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD.")
            return

        # Obtener ID del inquilino
        inquilino_id = self.mapa_inquilinos.get(inquilino)
        if not inquilino_id:
            messagebox.showerror("Error", "Inquilino no encontrado.")
            return

        # Verificar que el inquilino existe en la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM inquilinos WHERE id = ?", (inquilino_id,))
        if not cursor.fetchone():
            conn.close()
            messagebox.showerror("Error", "El inquilino seleccionado ya no existe en la base de datos.")
            # Actualizar el combo box para reflejar los cambios
            self.cargar_inquilinos_combo()
            return

        # Guardar en la base de datos
        cursor.execute("INSERT INTO pagos (fecha, inquilino_id, monto) VALUES (?, ?, ?)",
                       (fecha, inquilino_id, monto))

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Pago registrado correctamente.")

        # Generar recibo
        self.generar_recibo_pago(inquilino, monto, fecha)

        # Recargar lista de pagos y actualizar estadísticas
        self.cargar_pagos()
        self.manager.tenant_module.actualizar_estadisticas()

    def generar_recibo_pago(self, inquilino_texto, monto, fecha):
        """Genera un recibo de pago en PDF"""
        # Extraer nombre y apartamento
        nombre, apto_texto = inquilino_texto.split(" - Apto ")
        apartamento = apto_texto.strip()

        # Generar nombre de archivo
        nombre_archivo = f"recibo_pago_{nombre.replace(' ', '_')}_{apartamento}_{fecha}.pdf"

        # Crear PDF
        c = canvas.Canvas(nombre_archivo, pagesize=letter)
        ancho, alto = letter
        margen_izquierdo = 1 * inch
        y = alto - 1 * inch

        # Contenido del recibo
        lineas = [
            f"Fecha: {fecha}",
            "",
            "",
            "Muñoz & Asociados Buildings",
            "Pitalito - Huila",
            "",
            "",
            f"Asunto: Constancia de pago del canon de arrendamiento - Apto:{apartamento}.",
            "",
            "",
            f"A la fecha de este documento, recibimos del señor(a) {nombre}",
            f"el valor de ${round(monto)} por concepto de pago del canon de",
            f"arrendamiento correspondiente al siguiente mes.",
            "",
            "",
            "",
            "Atentamente,",
            "Administración - Muñoz y Asociados Buildings."
        ]

        # Dibujar texto
        text = c.beginText(margen_izquierdo, y)
        text.setFont("Helvetica", 12)
        text.setLeading(18)  # Espaciado entre líneas
        text.textLines(lineas)
        c.drawText(text)

        # Guardar y abrir el PDF
        c.save()
        messagebox.showinfo("Recibo generado", f"Se ha generado el recibo: {nombre_archivo}")

        # Abrir el PDF (solo funciona en Windows)
        try:
            os.startfile(nombre_archivo)
        except:
            messagebox.showinfo("Información", f"El recibo se guardó como: {nombre_archivo}")

    def generar_recibo(self):
        """Genera un recibo para el pago seleccionado"""
        # Obtener item seleccionado
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor selecciona un pago para generar su recibo.")
            return

        # Obtener datos del pago
        values = self.tree.item(selected[0], "values")
        fecha = values[1]
        nombre = values[2]
        apartamento = values[3]
        monto = float(values[4])

        # Generar nombre de archivo
        nombre_archivo = f"recibo_pago_{nombre.replace(' ', '_')}_{apartamento}_{fecha}.pdf"

        # Crear PDF
        c = canvas.Canvas(nombre_archivo, pagesize=letter)
        ancho, alto = letter
        margen_izquierdo = 1 * inch
        y = alto - 1 * inch

        # Contenido del recibo
        lineas = [
            f"Fecha: {fecha}",
            "",
            "",
            "Muñoz & Asociados Buildings",
            "Pitalito - Huila",
            "",
            "",
            f"Asunto: Constancia de pago del canon de arrendamiento - Apto:{apartamento}.",
            "",
            "",
            f"A la fecha de este documento, recibimos del señor(a) {nombre}",
            f"el valor de ${round(monto)} por concepto de pago del canon de",
            f"arrendamiento correspondiente al siguiente mes.",
            "",
            "",
            "",
            "Atentamente,",
            "Administración - Muñoz y Asociados Buildings."
        ]

        # Dibujar texto
        text = c.beginText(margen_izquierdo, y)
        text.setFont("Helvetica", 12)
        text.setLeading(18)  # Espaciado entre líneas
        text.textLines(lineas)
        c.drawText(text)

        # Guardar y abrir el PDF
        c.save()
        messagebox.showinfo("Recibo generado", f"Se ha generado el recibo: {nombre_archivo}")

        # Abrir el PDF (solo funciona en Windows)
        try:
            os.startfile(nombre_archivo)
        except:
            messagebox.showinfo("Información", f"El recibo se guardó como: {nombre_archivo}")

    def eliminar_pago(self):
        """Elimina el pago seleccionado"""
        # Obtener item seleccionado
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor selecciona un pago para eliminar.")
            return

        # Obtener datos del pago
        values = self.tree.item(selected[0], "values")
        pago_id = values[0]
        fecha = values[1]
        nombre = values[2]

        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar eliminación",
                                   f"¿Estás seguro de eliminar el pago de {nombre} del {fecha}?"):
            return

        # Eliminar de la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM pagos WHERE id = ?", (pago_id,))

        conn.commit()
        conn.close()

        messagebox.showinfo("Eliminado", "Pago eliminado exitosamente.")

        # Recargar lista de pagos y actualizar estadísticas
        self.cargar_pagos()
        self.manager.tenant_module.actualizar_estadisticas()

class ExpenseModule:
    def __init__(self, manager):
        self.manager = manager

    def setup_ui(self, parent):
        """Configura la interfaz de gestión de gastos"""
        # Frame principal
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text=" 📊 Gastos ")
        
        # Botón para volver al dashboard
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill="x", padx=20, pady=(20,10))
        
        back_btn = tk.Button(header_frame,
                           text="← Volver al Dashboard",
                           command=lambda: self.manager.notebook.select(0),
                           font=("Segoe UI", 10),
                           bg="#f0f0f0",
                           fg="#1a73e8",
                           bd=0,
                           padx=15,
                           pady=5,
                           cursor="hand2")
        back_btn.pack(side="left")

        # Frame para registrar gastos
        register_frame = ttk.LabelFrame(self.frame, text="Registrar Nuevo Gasto", padding="10")
        register_frame.pack(fill="x", pady=10)

        # Tipo de gasto
        row1 = ttk.Frame(register_frame)
        row1.pack(fill="x", pady=5)

        ttk.Label(row1, text="Tipo de gasto:").pack(side="left", padx=(0, 5))

        self.tipo_var = StringVar()
        self.tipo_var.set("Servicios Públicos")

        tipos_gasto = ["Servicios Públicos", "Impuestos", "Mantenimiento", "Reparaciones", "Otros"]
        self.combo_tipo = ttk.Combobox(row1, textvariable=self.tipo_var, values=tipos_gasto, width=20)
        self.combo_tipo.pack(side="left")

        # Fecha
        ttk.Label(row1, text="Fecha:").pack(side="left", padx=(15, 5))

        self.entry_fecha = ttk.Entry(row1, width=15)
        self.entry_fecha.insert(0, datetime.date.today().isoformat())
        self.entry_fecha.pack(side="left")

        # Descripción
        row2 = ttk.Frame(register_frame)
        row2.pack(fill="x", pady=5)

        ttk.Label(row2, text="Descripción:").pack(side="left", padx=(0, 5))
        self.entry_desc = ttk.Entry(row2, width=50)
        self.entry_desc.pack(side="left", fill="x", expand=True)

        # Monto
        row3 = ttk.Frame(register_frame)
        row3.pack(fill="x", pady=5)

        ttk.Label(row3, text="Monto:").pack(side="left", padx=(0, 5))
        self.entry_monto = ttk.Entry(row3, width=15)
        self.entry_monto.pack(side="left")

        # Botón de registrar
        btn_frame = ttk.Frame(register_frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Registrar Gasto",
                   command=self.registrar_gasto).pack(side="right")

        # Frame para historial de gastos
        history_frame = ttk.LabelFrame(self.frame, text="Historial de Gastos", padding="10")
        history_frame.pack(fill="both", expand=True, pady=10)

        # Filtro de historial
        filter_frame = ttk.Frame(history_frame)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="Filtrar por tipo:").pack(side="left", padx=(0, 5))

        self.filtro_var = StringVar()
        self.filtro_var.set("Todos")

        filtro_tipos = ["Todos"] + tipos_gasto
        self.combo_filtro = ttk.Combobox(filter_frame, textvariable=self.filtro_var,
                                         values=filtro_tipos, width=20)
        self.combo_filtro.pack(side="left", padx=(0, 5))

        ttk.Button(filter_frame, text="Filtrar",
                   command=self.filtrar_gastos).pack(side="left")

        # Treeview para historial
        columns = ("id", "fecha", "tipo", "descripcion", "monto")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings")

        # Definir encabezados
        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("descripcion", text="Descripción")
        self.tree.heading("monto", text="Monto")

        # Ajustar anchos de columna
        self.tree.column("id", width=50)
        self.tree.column("fecha", width=100)
        self.tree.column("tipo", width=120)
        self.tree.column("descripcion", width=250)
        self.tree.column("monto", width=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Empaquetar widgets
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botones de acción
        btn_frame2 = ttk.Frame(self.frame)
        btn_frame2.pack(fill="x", pady=5)

        ttk.Button(btn_frame2, text="Editar Gasto",
                   command=self.editar_gasto).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame2, text="Eliminar Gasto",
                   command=self.eliminar_gasto).pack(side="left")

        # Cargar datos iniciales
        self.cargar_gastos()

    def cargar_gastos(self):
        """Carga todos los gastos en el treeview"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Cargar desde la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, fecha, tipo, descripcion, monto
            FROM gastos
            ORDER BY fecha DESC
        """)

        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

        conn.close()

    def filtrar_gastos(self):
        """Filtra los gastos por tipo"""
        filtro = self.filtro_var.get()
        if filtro == "Todos":
            self.cargar_gastos()
            return

        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Cargar gastos filtrados
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, fecha, tipo, descripcion, monto
            FROM gastos
            WHERE tipo = ?
            ORDER BY fecha DESC
        """, (filtro,))

        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)

        conn.close()

    def registrar_gasto(self):
        """Registra un nuevo gasto"""
        tipo = self.tipo_var.get()
        fecha = self.entry_fecha.get()
        descripcion = self.entry_desc.get()
        monto = self.entry_monto.get()

        # Validaciones
        if not tipo:
            messagebox.showwarning("Tipo", "Por favor selecciona un tipo de gasto.")
            return

        if not monto:
            messagebox.showwarning("Monto", "Por favor ingresa el monto del gasto.")
            return

        try:
            monto = float(monto)
            if monto <= 0:
                messagebox.showerror("Error", "El monto debe ser un número positivo.")
                return
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número.")
            return

        try:
            datetime.date.fromisoformat(fecha)
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD.")
            return

        # Guardar en la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO gastos (fecha, tipo, descripcion, monto) 
            VALUES (?, ?, ?, ?)
        """, (fecha, tipo, descripcion, monto))

        conn.commit()
        conn.close()

        messagebox.showinfo("Éxito", "Gasto registrado correctamente.")

        # Limpiar campos
        self.entry_desc.delete(0, tk.END)
        self.entry_monto.delete(0, tk.END)
        self.entry_fecha.delete(0, tk.END)
        self.entry_fecha.insert(0, datetime.date.today().isoformat())

        # Recargar lista y actualizar estadísticas
        self.cargar_gastos()
        self.manager.tenant_module.actualizar_estadisticas()

    def editar_gasto(self):
        """Abre ventana para editar el gasto seleccionado"""
        # Obtener item seleccionado
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor selecciona un gasto para editar.")
            return

        # Obtener datos del gasto seleccionado
        values = self.tree.item(selected[0], "values")
        gasto_id = values[0]

        # Crear ventana de edición
        edit_window = Toplevel()
        edit_window.title("Editar Gasto")
        edit_window.geometry("400x250")
        edit_window.transient(self.manager.root)  # Hacer ventana modal

        # Contenido de la ventana
        ttk.Label(edit_window, text="Tipo de gasto:").pack(pady=5)

        tipo_var = StringVar()
        tipo_var.set(values[2])

        tipos_gasto = ["Servicios Públicos", "Impuestos", "Mantenimiento", "Reparaciones", "Otros"]
        combo_tipo = ttk.Combobox(edit_window, textvariable=tipo_var, values=tipos_gasto, width=20)
        combo_tipo.pack()

        ttk.Label(edit_window, text="Fecha (YYYY-MM-DD):").pack(pady=5)
        entry_fecha = ttk.Entry(edit_window, width=15)
        entry_fecha.insert(0, values[1])
        entry_fecha.pack()

        ttk.Label(edit_window, text="Descripción:").pack(pady=5)
        entry_desc = ttk.Entry(edit_window, width=50)
        entry_desc.insert(0, values[3])
        entry_desc.pack()

        ttk.Label(edit_window, text="Monto:").pack(pady=5)
        entry_monto = ttk.Entry(edit_window, width=15)
        entry_monto.insert(0, values[4])
        entry_monto.pack()

        def guardar_cambios():
            tipo = tipo_var.get()
            fecha = entry_fecha.get()
            descripcion = entry_desc.get()
            monto = entry_monto.get()

            # Validaciones básicas
            if not tipo or not fecha or not monto:
                messagebox.showwarning("Campos vacíos", "Por favor completa los campos obligatorios.")
                return

            try:
                monto = float(monto)
                if monto <= 0:
                    messagebox.showerror("Error", "El monto debe ser un número positivo.")
                    return
            except ValueError:
                messagebox.showerror("Error", "El monto debe ser un número.")
                return

            # Actualizar en la base de datos
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE gastos 
                SET fecha = ?, tipo = ?, descripcion = ?, monto = ? 
                WHERE id = ?
            """, (fecha, tipo, descripcion, monto, gasto_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Actualizado", "Gasto actualizado exitosamente.")
            edit_window.destroy()

            # Recargar lista
            self.cargar_gastos()
            self.manager.tenant_module.actualizar_estadisticas()

        ttk.Button(edit_window, text="Guardar Cambios",
                   command=guardar_cambios).pack(pady=15)

    def eliminar_gasto(self):
        """Elimina el gasto seleccionado"""
        # Obtener item seleccionado
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selección", "Por favor selecciona un gasto para eliminar.")
            return

        # Obtener datos del gasto seleccionado
        values = self.tree.item(selected[0], "values")
        gasto_id = values[0]
        tipo = values[2]
        monto = values[4]

        # Confirmar eliminación
        if not messagebox.askyesno("Confirmar eliminación",
                                   f"¿Estás seguro de eliminar el gasto de {tipo} por ${monto}?"):
            return

        # Eliminar de la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        cursor.execute("DELETE FROM gastos WHERE id = ?", (gasto_id,))

        conn.commit()
        conn.close()

        messagebox.showinfo("Eliminado", "Gasto eliminado exitosamente.")

        # Recargar lista y actualizar estadísticas
        self.cargar_gastos()
        self.manager.tenant_module.actualizar_estadisticas()

class ReportModule:
    def __init__(self, manager):
        self.manager = manager
        self.current_report_data = None  # Para almacenar datos del reporte actual

    def setup_ui(self, parent):
        """Configura la interfaz de reportes"""
        # Frame principal
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text=" 📈 Reportes ")
        
        # Botón para volver al dashboard
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill="x", padx=20, pady=(20,10))
        
        back_btn = tk.Button(header_frame,
                           text="← Volver al Dashboard",
                           command=lambda: self.manager.notebook.select(0),
                           font=("Segoe UI", 10),
                           bg="#f0f0f0",
                           fg="#1a73e8",
                           bd=0,
                           padx=15,
                           pady=5,
                           cursor="hand2")
        back_btn.pack(side="left")

        # Frame para selección de reportes
        select_frame = ttk.LabelFrame(self.frame, text="Generar Reporte", padding="10")
        select_frame.pack(fill="x", pady=10)

        # Tipo de reporte
        row1 = ttk.Frame(select_frame)
        row1.pack(fill="x", pady=5)

        ttk.Label(row1, text="Tipo de reporte:").pack(side="left", padx=(0, 5))

        self.tipo_reporte_var = StringVar()
        self.tipo_reporte_var.set("Mensual")

        tipos_reporte = ["Mensual", "Anual"]
        self.combo_tipo = ttk.Combobox(row1, textvariable=self.tipo_reporte_var,
                                       values=tipos_reporte, width=15)
        self.combo_tipo.pack(side="left")
        self.combo_tipo.bind("<<ComboboxSelected>>", self.actualizar_campos_fecha)

        # Año
        ttk.Label(row1, text="Año:").pack(side="left", padx=(15, 5))

        # Obtener año actual
        anio_actual = datetime.date.today().year
        anios = list(range(anio_actual - 5, anio_actual + 1))

        self.anio_var = StringVar()
        self.anio_var.set(str(anio_actual))

        self.combo_anio = ttk.Combobox(row1, textvariable=self.anio_var,
                                       values=[str(a) for a in anios], width=10)
        self.combo_anio.pack(side="left")

        # Mes (visible solo para reporte mensual)
        ttk.Label(row1, text="Mes:").pack(side="left", padx=(15, 5))

        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        self.mes_var = StringVar()
        self.mes_var.set(meses[datetime.date.today().month - 1])

        self.combo_mes = ttk.Combobox(row1, textvariable=self.mes_var,
                                      values=meses, width=15)
        self.combo_mes.pack(side="left")

        # Botón para generar
        btn_frame = ttk.Frame(select_frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Generar Reporte",
                   command=self.generar_reporte).pack(side="right")

        # Frame para mostrar reporte
        report_frame = ttk.LabelFrame(self.frame, text="Vista Previa del Reporte", padding="10")
        report_frame.pack(fill="both", expand=True, pady=10)

        # Widget de texto para mostrar reporte
        self.text_reporte = tk.Text(report_frame, height=15, width=70)
        self.text_reporte.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=self.text_reporte.yview)
        self.text_reporte.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Frame para gráficos
        self.graph_frame = ttk.LabelFrame(self.frame, text="Gráficos", padding="10")
        self.graph_frame.pack(fill="both", expand=True, pady=10)

        # Se añadirá el gráfico dinámicamente
        self.graph_container = ttk.Frame(self.graph_frame)
        self.graph_container.pack(fill="both", expand=True)

        # Botones de acción
        btn_frame2 = ttk.Frame(self.frame)
        btn_frame2.pack(fill="x", pady=5)

        ttk.Button(btn_frame2, text="Exportar a PDF",
                   command=self.exportar_pdf).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame2, text="Exportar a Excel",
                   command=self.exportar_excel).pack(side="left")

    def actualizar_campos_fecha(self, event=None):
        """Actualiza la visibilidad de los campos de fecha según el tipo de reporte"""
        if self.tipo_reporte_var.get() == "Mensual":
            self.combo_mes.config(state="readonly")
        else:
            self.combo_mes.config(state="disabled")

    def obtener_numero_mes(self, nombre_mes):
        """Convierte el nombre del mes a su número correspondiente"""
        meses = {"Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
                 "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12}
        return meses.get(nombre_mes, 1)

    def obtener_nombre_mes(self, numero_mes):
        """Convierte el número del mes a su nombre correspondiente"""
        meses = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
                 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
        return meses.get(numero_mes, "")

    def generar_reporte(self):
        """Genera y muestra el reporte según los parámetros seleccionados"""
        tipo_reporte = self.tipo_reporte_var.get()

        try:
            anio = int(self.anio_var.get())
            if tipo_reporte == "Mensual":
                mes = self.obtener_numero_mes(self.mes_var.get())
            else:
                mes = None
        except (ValueError, KeyError):
            messagebox.showerror("Error", "Por favor selecciona valores válidos para año y mes.")
            return

        # Obtener datos desde la base de datos
        total_ingresos = 0
        ingresos_por_mes = {i: 0 for i in range(1, 13)} if tipo_reporte == "Anual" else {}

        total_gastos = {"Servicios Públicos": 0, "Impuestos": 0, "Mantenimiento": 0,
                        "Reparaciones": 0, "Otros": 0}
        gastos_por_mes = {i: 0 for i in range(1, 13)} if tipo_reporte == "Anual" else {}

        # Conectar a la base de datos
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()

        # Consultar ingresos
        if tipo_reporte == "Mensual":
            cursor.execute("""
                SELECT SUM(monto) FROM pagos
                WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
            """, (str(anio), f"{mes:02d}"))

            result = cursor.fetchone()
            if result[0]:
                total_ingresos = result[0]
        else:  # Anual
            cursor.execute("""
                SELECT strftime('%m', fecha) as mes, SUM(monto) 
                FROM pagos
                WHERE strftime('%Y', fecha) = ?
                GROUP BY mes
            """, (str(anio),))

            for row in cursor.fetchall():
                mes_num = int(row[0])
                ingresos_por_mes[mes_num] = row[1]
                total_ingresos += row[1]

        # Consultar gastos
        if tipo_reporte == "Mensual":
            cursor.execute("""
                SELECT tipo, SUM(monto) FROM gastos
                WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
                GROUP BY tipo
            """, (str(anio), f"{mes:02d}"))

            for tipo, monto in cursor.fetchall():
                if tipo in total_gastos:
                    total_gastos[tipo] = monto
        else:  # Anual
            # Total por tipo
            cursor.execute("""
                SELECT tipo, SUM(monto) FROM gastos
                WHERE strftime('%Y', fecha) = ?
                GROUP BY tipo
            """, (str(anio),))

            for tipo, monto in cursor.fetchall():
                if tipo in total_gastos:
                    total_gastos[tipo] = monto

            # Por mes para el gráfico
            cursor.execute("""
                SELECT strftime('%m', fecha) as mes, SUM(monto) 
                FROM gastos
                WHERE strftime('%Y', fecha) = ?
                GROUP BY mes
            """, (str(anio),))

            for row in cursor.fetchall():
                mes_num = int(row[0])
                gastos_por_mes[mes_num] = row[1]

        conn.close()

        # Calcular totales
        total_gastos_sum = sum(total_gastos.values())
        balance = total_ingresos - total_gastos_sum

        # Guardar datos del reporte actual
        self.current_report_data = {
            'tipo': tipo_reporte,
            'anio': anio,
            'mes': mes,
            'total_ingresos': total_ingresos,
            'total_gastos': total_gastos,
            'total_gastos_sum': total_gastos_sum,
            'balance': balance,
            'ingresos_por_mes': ingresos_por_mes,
            'gastos_por_mes': gastos_por_mes
        }

        # Mostrar reporte en el widget de texto
        self.text_reporte.config(state='normal')
        self.text_reporte.delete(1.0, tk.END)

        if tipo_reporte == "Mensual":
            nombre_mes = self.mes_var.get()
            self.text_reporte.insert(tk.END, f"--- REPORTE DEL MES DE {nombre_mes.upper()} {anio} ---\n\n")
        else:
            self.text_reporte.insert(tk.END, f"--- REPORTE ANUAL {anio} ---\n\n")

        self.text_reporte.insert(tk.END, f"Ingresos totales: ${total_ingresos:.2f}\n\n")
        self.text_reporte.insert(tk.END, f"Gastos por categoría:\n")

        for tipo, monto in total_gastos.items():
            if monto > 0:  # Solo mostrar categorías con gastos
                self.text_reporte.insert(tk.END, f"  {tipo}: ${monto:.2f}\n")

        self.text_reporte.insert(tk.END, f"\nTotal gastos: ${total_gastos_sum:.2f}\n")
        self.text_reporte.insert(tk.END, f"\nBALANCE: ${balance:.2f}\n")

        # Colorear el balance según sea positivo o negativo
        self.text_reporte.tag_configure("positivo", foreground="green")
        self.text_reporte.tag_configure("negativo", foreground="red")

        balance_line = self.text_reporte.get("end-2l", "end-1l")
        self.text_reporte.delete("end-2l", "end-1l")

        if balance >= 0:
            self.text_reporte.insert(tk.END, balance_line, "positivo")
        else:
            self.text_reporte.insert(tk.END, balance_line, "negativo")

        self.text_reporte.config(state='disabled')

        # Generar gráfico
        self.generar_grafico()

    def generar_grafico(self):
        """Genera y muestra gráficos según el tipo de reporte"""
        if not self.current_report_data:
            return

        # Limpiar gráfico anterior
        for widget in self.graph_container.winfo_children():
            widget.destroy()

        # Crear nueva figura
        fig = plt.Figure(figsize=(8, 4))

        if self.current_report_data['tipo'] == "Mensual":
            # Gráfico de pastel para gastos mensuales
            ax = fig.add_subplot(111)

            # Filtrar solo categorías con gastos
            gastos_filtrados = {k: v for k, v in self.current_report_data['total_gastos'].items() if v > 0}

            if gastos_filtrados:
                labels = list(gastos_filtrados.keys())
                sizes = list(gastos_filtrados.values())

                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                ax.set_title(f'Distribución de Gastos - {self.mes_var.get()} {self.current_report_data["anio"]}')
            else:
                ax.text(0.5, 0.5, "No hay datos de gastos para mostrar", ha='center', va='center')
                ax.axis('off')
        else:
            # Gráfico de barras para ingresos vs gastos anuales
            ax = fig.add_subplot(111)

            meses = range(1, 13)
            ingresos = [self.current_report_data['ingresos_por_mes'].get(m, 0) for m in meses]
            gastos = [self.current_report_data['gastos_por_mes'].get(m, 0) for m in meses]

            etiquetas_meses = [self.obtener_nombre_mes(m) for m in meses]

            x = range(len(meses))
            ancho = 0.35

            ax.bar([i - ancho / 2 for i in x], ingresos, ancho, label='Ingresos')
            ax.bar([i + ancho / 2 for i in x], gastos, ancho, label='Gastos')

            ax.set_ylabel('Monto ($)')
            ax.set_title(f'Ingresos vs Gastos por Mes - {self.current_report_data["anio"]}')
            ax.set_xticks(x)
            ax.set_xticklabels(etiquetas_meses, rotation=45, ha='right')
            ax.legend()

            # Ajustar layout
            fig.tight_layout()

        # Mostrar gráfico en la interfaz
        canvas = FigureCanvasTkAgg(fig, self.graph_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def exportar_pdf(self):
        """Exporta el reporte actual a PDF"""
        if not self.current_report_data:
            messagebox.showwarning("Sin datos", "Primero debes generar un reporte.")
            return

        # Crear nombre de archivo
        if self.current_report_data['tipo'] == "Mensual":
            nombre_mes = self.obtener_nombre_mes(self.current_report_data['mes'])
            nombre_archivo = f"reporte_{self.current_report_data['anio']}_{nombre_mes}.pdf"
        else:
            nombre_archivo = f"reporte_anual_{self.current_report_data['anio']}.pdf"

        # Crear PDF
        c = canvas.Canvas(nombre_archivo, pagesize=letter)
        ancho, alto = letter

        # Título
        c.setFont("Helvetica-Bold", 16)
        if self.current_report_data['tipo'] == "Mensual":
            nombre_mes = self.obtener_nombre_mes(self.current_report_data['mes'])
            titulo = f"REPORTE DEL MES DE {nombre_mes.upper()} {self.current_report_data['anio']}"
        else:
            titulo = f"REPORTE ANUAL {self.current_report_data['anio']}"

        c.drawCentredString(ancho / 2, alto - 40, titulo)

        # Fecha de generación
        c.setFont("Helvetica", 10)
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.drawRightString(ancho - 50, alto - 60, f"Generado: {fecha_actual}")

        # Contenido
        y = alto - 100
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "RESUMEN FINANCIERO")
        y -= 20

        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Ingresos totales: ${self.current_report_data['total_ingresos']:.2f}")
        y -= 30

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Gastos por categoría:")
        y -= 20

        c.setFont("Helvetica", 12)
        for tipo, monto in self.current_report_data['total_gastos'].items():
            if monto > 0:  # Solo mostrar categorías con gastos
                c.drawString(70, y, f"{tipo}: ${monto:.2f}")
                y -= 15

        y -= 10
        c.drawString(50, y, f"Total gastos: ${self.current_report_data['total_gastos_sum']:.2f}")
        y -= 20

        # Balance con color
        balance = self.current_report_data['balance']
        if balance >= 0:
            c.setFillColorRGB(0, 0.5, 0)  # Verde
        else:
            c.setFillColorRGB(0.8, 0, 0)  # Rojo

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"BALANCE: ${balance:.2f}")
        c.setFillColorRGB(0, 0, 0)  # Volver a negro

        # Añadir gráfico si hay datos
        if self.current_report_data['tipo'] == "Mensual":
            # Solo añadir gráfico si hay gastos
            gastos_filtrados = {k: v for k, v in self.current_report_data['total_gastos'].items() if v > 0}
            if gastos_filtrados:
                fig = plt.Figure(figsize=(6, 4))
                ax = fig.add_subplot(111)

                labels = list(gastos_filtrados.keys())
                sizes = list(gastos_filtrados.values())

                ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')

                # Guardar temporalmente y añadir al PDF
                fig.savefig("temp_chart.png")
                c.drawImage("temp_chart.png", 50, y - 300, width=400, height=250)

                # Eliminar archivo temporal
                try:
                    os.remove("temp_chart.png")
                except:
                    pass
        else:
            # Gráfico de barras para reporte anual
            fig = plt.Figure(figsize=(8, 4))
            ax = fig.add_subplot(111)

            meses = range(1, 13)
            ingresos = [self.current_report_data['ingresos_por_mes'].get(m, 0) for m in meses]
            gastos = [self.current_report_data['gastos_por_mes'].get(m, 0) for m in meses]

            etiquetas_meses = [self.obtener_nombre_mes(m)[:3] for m in meses]  # Abreviar nombres

            x = range(len(meses))
            ancho = 0.35

            ax.bar([i - ancho / 2 for i in x], ingresos, ancho, label='Ingresos')
            ax.bar([i + ancho / 2 for i in x], gastos, ancho, label='Gastos')

            ax.set_ylabel('Monto ($)')
            ax.set_xticks(x)
            ax.set_xticklabels(etiquetas_meses)
            ax.legend()

            # Guardar temporalmente y añadir al PDF
            fig.savefig("temp_chart.png")
            c.drawImage("temp_chart.png", 50, y - 300, width=500, height=250)

            # Eliminar archivo temporal
            try:
                os.remove("temp_chart.png")
            except:
                pass

        # Guardar PDF
        c.save()
        messagebox.showinfo("PDF Generado", f"El reporte se ha guardado como: {nombre_archivo}")

        # Abrir el PDF
        try:
            os.startfile(nombre_archivo)
        except:
            pass

    def exportar_excel(self):
        """Exporta el reporte actual a Excel"""
        if not self.current_report_data:
            messagebox.showwarning("Sin datos", "Primero debes generar un reporte.")
            return

        # Crear nombre de archivo
        if self.current_report_data['tipo'] == "Mensual":
            nombre_mes = self.obtener_nombre_mes(self.current_report_data['mes'])
            nombre_archivo = f"reporte_{self.current_report_data['anio']}_{nombre_mes}.xlsx"
        else:
            nombre_archivo = f"reporte_anual_{self.current_report_data['anio']}.xlsx"

        # Crear DataFrame para el resumen
        resumen_data = {
            'Concepto': ['Ingresos Totales'] +
                        [f"Gastos - {tipo}" for tipo in self.current_report_data['total_gastos'].keys()] +
                        ['Total Gastos', 'Balance'],
            'Monto': [self.current_report_data['total_ingresos']] +
                     list(self.current_report_data['total_gastos'].values()) +
                     [self.current_report_data['total_gastos_sum'], self.current_report_data['balance']]
        }

        df_resumen = pd.DataFrame(resumen_data)

        # Crear DataFrames adicionales según el tipo de reporte
        if self.current_report_data['tipo'] == "Anual":
            # Datos mensuales
            meses = range(1, 13)
            nombres_meses = [self.obtener_nombre_mes(m) for m in meses]

            ingresos = [self.current_report_data['ingresos_por_mes'].get(m, 0) for m in meses]
            gastos = [self.current_report_data['gastos_por_mes'].get(m, 0) for m in meses]
            balance = [ingresos[i] - gastos[i] for i in range(len(meses))]

            df_mensual = pd.DataFrame({
                'Mes': nombres_meses,
                'Ingresos': ingresos,
                'Gastos': gastos,
                'Balance': balance
            })

            # Crear Excel con múltiples hojas
            with pd.ExcelWriter(nombre_archivo) as writer:
                df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
                df_mensual.to_excel(writer, sheet_name='Detalle Mensual', index=False)
        else:
            # Solo crear la hoja de resumen para reporte mensual
            df_resumen.to_excel(nombre_archivo, sheet_name='Resumen', index=False)

        messagebox.showinfo("Excel Generado", f"El reporte se ha guardado como: {nombre_archivo}")

        # Abrir el Excel
        try:
            os.startfile(nombre_archivo)
        except:
            pass

class BackupModule:
    def __init__(self, manager):
        self.manager = manager
        self.backup_config_file = "backup_config.json"
        self.load_backup_config()

    def load_backup_config(self):
        """Carga la configuración de respaldos"""
        try:
            if os.path.exists(self.backup_config_file):
                with open(self.backup_config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "auto_backup": True,
                    "backup_folder": "Respaldos",
                    "max_backups": 10,
                    "include_pdfs": True,
                    "backup_on_exit": True
                }
                self.save_backup_config()
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando configuración: {e}")
            self.config = {}

    def save_backup_config(self):
        """Guarda la configuración de respaldos"""
        try:
            with open(self.backup_config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando configuración: {e}")

    def setup_ui(self, parent):
        """Configura la interfaz del módulo de respaldos"""
        # Frame principal
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text=" 💾 Respaldos ")

        # Título
        title_label = ttk.Label(self.frame, text="Sistema de Respaldos",
                                font=("Helvetica", 14, "bold"))
        title_label.pack(pady=10)

        # Frame de respaldo manual
        manual_frame = ttk.LabelFrame(self.frame, text="Respaldo Manual", padding="10")
        manual_frame.pack(fill="x", pady=10)

        # Botones de respaldo manual
        btn_frame1 = ttk.Frame(manual_frame)
        btn_frame1.pack(fill="x", pady=5)

        ttk.Button(btn_frame1, text="🗄️ Crear Respaldo Completo",
                   command=self.crear_respaldo_manual).pack(side="left", padx=(0, 10))

        ttk.Button(btn_frame1, text="📁 Abrir Carpeta de Respaldos",
                   command=self.abrir_carpeta_respaldos).pack(side="left")

        # Frame de configuración automática
        auto_frame = ttk.LabelFrame(self.frame, text="Configuración Automática", padding="10")
        auto_frame.pack(fill="x", pady=10)

        # Checkbox para respaldo automático
        self.auto_backup_var = tk.BooleanVar(value=self.config.get("auto_backup", True))
        ttk.Checkbutton(auto_frame, text="Activar respaldos automáticos al cerrar",
                        variable=self.auto_backup_var,
                        command=self.update_config).pack(anchor="w", pady=2)

        # Checkbox para incluir PDFs
        self.include_pdfs_var = tk.BooleanVar(value=self.config.get("include_pdfs", True))
        ttk.Checkbutton(auto_frame, text="Incluir archivos PDF en respaldos",
                        variable=self.include_pdfs_var,
                        command=self.update_config).pack(anchor="w", pady=2)

        # Configuración de cantidad de respaldos
        qty_frame = ttk.Frame(auto_frame)
        qty_frame.pack(fill="x", pady=5)

        ttk.Label(qty_frame, text="Mantener últimos:").pack(side="left")
        self.max_backups_var = tk.StringVar(value=str(self.config.get("max_backups", 10)))
        max_backups_spin = ttk.Spinbox(qty_frame, from_=1, to=50, width=5,
                                       textvariable=self.max_backups_var,
                                       command=self.update_config)
        max_backups_spin.pack(side="left", padx=5)
        ttk.Label(qty_frame, text="respaldos").pack(side="left")

        # Frame de información
        info_frame = ttk.LabelFrame(self.frame, text="Información", padding="10")
        info_frame.pack(fill="both", expand=True, pady=10)

        self.info_text = tk.Text(info_frame, height=8, wrap=tk.WORD)
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical",
                                       command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)

        self.info_text.pack(side="left", fill="both", expand=True)
        info_scrollbar.pack(side="right", fill="y")

        # Cargar información inicial
        self.actualizar_info()

    def update_config(self):
        """Actualiza la configuración cuando cambian los valores"""
        self.config["auto_backup"] = self.auto_backup_var.get()
        self.config["include_pdfs"] = self.include_pdfs_var.get()
        try:
            self.config["max_backups"] = int(self.max_backups_var.get())
        except ValueError:
            self.config["max_backups"] = 10

        self.save_backup_config()

    def crear_respaldo_manual(self):
        """Crea un respaldo manual completo"""
        try:
            # Permitir al usuario elegir ubicación
            carpeta_destino = filedialog.askdirectory(
                title="Seleccionar carpeta para respaldo",
                initialdir=os.path.expanduser("~")
            )

            if not carpeta_destino:
                return

            resultado = self.crear_respaldo(carpeta_destino, manual=True)

            if resultado:
                messagebox.showinfo("Respaldo Exitoso",
                                    f"Respaldo creado exitosamente en:\n{resultado}")
                self.actualizar_info()

        except Exception as e:
            messagebox.showerror("Error", f"Error creando respaldo manual: {e}")

    def crear_respaldo_automatico(self):
        """Crea un respaldo automático al cerrar la aplicación"""
        if not self.config.get("auto_backup", True):
            return

        try:
            carpeta_respaldos = self.config.get("backup_folder", "Respaldos")
            resultado = self.crear_respaldo(carpeta_respaldos, manual=False)

            if resultado:
                self.limpiar_respaldos_antiguos()
                print(f"Respaldo automático creado: {resultado}")

        except Exception as e:
            print(f"Error en respaldo automático: {e}")

    def crear_respaldo(self, carpeta_destino, manual=True):
        """Función principal para crear respaldos"""
        try:
            # Crear carpeta de respaldos si no existe
            if not os.path.exists(carpeta_destino):
                os.makedirs(carpeta_destino)

            # Generar nombre único para el respaldo
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            tipo = "Manual" if manual else "Auto"
            nombre_respaldo = f"Respaldo_{tipo}_{timestamp}"

            carpeta_respaldo = os.path.join(carpeta_destino, nombre_respaldo)
            os.makedirs(carpeta_respaldo)

            archivos_copiados = []

            # 1. Copiar base de datos
            if os.path.exists("edificio.db"):
                shutil.copy2("edificio.db", os.path.join(carpeta_respaldo, "edificio.db"))
                archivos_copiados.append("Base de datos (edificio.db)")

            # 2. Copiar archivos de configuración
            config_files = ["backup_config.json"]
            for config_file in config_files:
                if os.path.exists(config_file):
                    shutil.copy2(config_file, os.path.join(carpeta_respaldo, config_file))
                    archivos_copiados.append(f"Configuración ({config_file})")

            # 3. Copiar PDFs si está habilitado
            if self.config.get("include_pdfs", True):
                pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf")]
                if pdf_files:
                    pdf_folder = os.path.join(carpeta_respaldo, "PDFs")
                    os.makedirs(pdf_folder)

                    for pdf_file in pdf_files:
                        shutil.copy2(pdf_file, os.path.join(pdf_folder, pdf_file))

                    archivos_copiados.append(f"Archivos PDF ({len(pdf_files)} archivos)")

            # 4. Crear archivo de información del respaldo
            info_respaldo = {
                "fecha_respaldo": datetime.datetime.now().isoformat(),
                "tipo": tipo,
                "archivos_incluidos": archivos_copiados,
                "version_app": "1.1"
            }

            with open(os.path.join(carpeta_respaldo, "info_respaldo.json"), 'w') as f:
                json.dump(info_respaldo, f, indent=2)

            # 5. Crear ZIP del respaldo
            zip_filename = f"{carpeta_respaldo}.zip"
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(carpeta_respaldo):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, carpeta_respaldo)
                        zipf.write(file_path, arcname)

            # Eliminar carpeta temporal, mantener solo ZIP
            shutil.rmtree(carpeta_respaldo)

            return zip_filename

        except Exception as e:
            raise Exception(f"Error creando respaldo: {e}")

    def limpiar_respaldos_antiguos(self):
        """Elimina respaldos antiguos manteniendo solo los más recientes"""
        try:
            carpeta_respaldos = self.config.get("backup_folder", "Respaldos")
            max_respaldos = self.config.get("max_backups", 10)

            if not os.path.exists(carpeta_respaldos):
                return

            # Obtener todos los archivos de respaldo
            archivos_respaldo = []
            for archivo in os.listdir(carpeta_respaldos):
                if archivo.startswith("Respaldo_") and archivo.endswith(".zip"):
                    ruta_completa = os.path.join(carpeta_respaldos, archivo)
                    fecha_mod = os.path.getmtime(ruta_completa)
                    archivos_respaldo.append((fecha_mod, ruta_completa))

            # Ordenar por fecha (más reciente primero)
            archivos_respaldo.sort(reverse=True)

            # Eliminar respaldos antiguos
            for _, ruta_archivo in archivos_respaldo[max_respaldos:]:
                os.remove(ruta_archivo)
                print(f"Respaldo antiguo eliminado: {os.path.basename(ruta_archivo)}")

        except Exception as e:
            print(f"Error limpiando respaldos antiguos: {e}")

    def abrir_carpeta_respaldos(self):
        """Abre la carpeta de respaldos en el explorador"""
        try:
            carpeta_respaldos = self.config.get("backup_folder", "Respaldos")

            if not os.path.exists(carpeta_respaldos):
                os.makedirs(carpeta_respaldos)

            # Abrir carpeta en el explorador
            if os.name == 'nt':  # Windows
                os.startfile(carpeta_respaldos)
            elif os.name == 'posix':  # macOS y Linux
                os.system(f'open "{carpeta_respaldos}"')

        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo carpeta: {e}")

    def actualizar_info(self):
        """Actualiza la información mostrada en el panel"""
        try:
            self.info_text.delete(1.0, tk.END)

            info = "=== INFORMACIÓN DEL SISTEMA DE RESPALDOS ===\n\n"

            # Configuración actual
            info += "Configuración Actual:\n"
            info += f"• Respaldo automático: {'Activado' if self.config.get('auto_backup') else 'Desactivado'}\n"
            info += f"• Incluir PDFs: {'Sí' if self.config.get('include_pdfs') else 'No'}\n"
            info += f"• Máximo respaldos: {self.config.get('max_backups', 10)}\n"
            info += f"• Carpeta de respaldos: {self.config.get('backup_folder', 'Respaldos')}\n\n"

            # Estado de la base de datos
            if os.path.exists("edificio.db"):
                tamaño_db = os.path.getsize("edificio.db")
                fecha_db = datetime.datetime.fromtimestamp(os.path.getmtime("edificio.db"))
                info += f"Base de Datos:\n"
                info += f"• Tamaño: {tamaño_db / 1024:.2f} KB\n"
                info += f"• Última modificación: {fecha_db.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            # Archivos PDF
            pdf_files = [f for f in os.listdir(".") if f.endswith(".pdf")]
            if pdf_files:
                info += f"Archivos PDF encontrados: {len(pdf_files)}\n"
                for pdf in pdf_files[:5]:  # Mostrar solo los primeros 5
                    info += f"• {pdf}\n"
                if len(pdf_files) > 5:
                    info += f"• ... y {len(pdf_files) - 5} más\n"
            else:
                info += "No se encontraron archivos PDF\n"

            info += "\n=== RECOMENDACIONES ===\n"
            info += "• Crea respaldos regularmente\n"
            info += "• Guarda respaldos en ubicaciones seguras (USB, nube)\n"
            info += "• Verifica los respaldos ocasionalmente\n"
            info += "• Mantén múltiples copias de seguridad\n"

            self.info_text.insert(tk.END, info)

        except Exception as e:
            self.info_text.insert(tk.END, f"Error actualizando información: {e}")

class ApartmentManager:
    def __init__(self, root):
        """Inicializa el administrador de apartamentos"""
        self.root = root
        self.root.title("Sistema de Administración de Edificios")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configurar estilos
        self.setup_styles()
        
        # Configurar base de datos
        self.setup_database()
        
        # Inicializar módulos en el orden correcto
        self.dashboard_module = DashboardModule(self)  # Dashboard primero
        self.tenant_module = TenantModule(self)
        self.payment_module = PaymentModule(self)
        self.expense_module = ExpenseModule(self)
        self.report_module = ReportModule(self)
        self.backup_module = BackupModule(self)
        
        # Configurar interfaz después de tener los módulos
        self.setup_ui()
        
        # Actualizar estadísticas inmediatamente después de iniciar
        self.root.after(100, self.tenant_module.actualizar_estadisticas)
        self.root.after(100, self.dashboard_module.actualizar_metricas)
        
        # Configurar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        """Configura los estilos de la aplicación"""
        style = ttk.Style()
        
        # Estilo principal
        style.configure("Main.TFrame", background="#ffffff")
        
        # Estilos para las cards
        style.configure("Card.TFrame",
                       background="#ffffff",
                       relief="solid",
                       borderwidth=1)
        
        style.configure("CardHover.TFrame",
                       background="#f8f9fa",
                       relief="solid",
                       borderwidth=1)
        
        # Estilos para las métricas
        style.configure("Metric.TFrame",
                       background="#ffffff",
                       relief="solid",
                       borderwidth=1)
        
        style.configure("MetricHover.TFrame",
                       background="#f8f9fa",
                       relief="solid",
                       borderwidth=1)
        
        # Configurar tema
        try:
            self.root.tk.call("source", "azure.tcl")
            style.theme_use("azure")
        except tk.TclError:
            style.theme_use("clam")
            
        # Configurar colores
        self.root.configure(bg="#ffffff")
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff")
        style.configure("TNotebook", background="#ffffff", borderwidth=0)
        style.configure("TNotebook.Tab", padding=[12, 4], font=("Segoe UI", 10))
        
    def setup_ui(self):
        """Configura la interfaz principal de la aplicación"""
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        
        # Agregar módulos al notebook
        self.notebook.add(self.dashboard_module.setup_ui(self.notebook), text=" 🏠 Dashboard ")
        self.notebook.add(self.tenant_module.setup_ui(self.notebook), text=" 👥 Inquilinos ")
        self.notebook.add(self.payment_module.setup_ui(self.notebook), text=" 💰 Pagos ")
        self.notebook.add(self.expense_module.setup_ui(self.notebook), text=" 💳 Gastos ")
        self.notebook.add(self.report_module.setup_ui(self.notebook), text=" 📊 Reportes ")
        self.notebook.add(self.backup_module.setup_ui(self.notebook), text=" 💾 Respaldos ")
        
    def on_closing(self):
        """Función llamada al cerrar la aplicación"""
        # Crear respaldo automático antes de cerrar
        if hasattr(self, 'backup_module'):
            self.backup_module.crear_respaldo_automatico()
            
        # Cerrar aplicación
        self.root.destroy()

    def setup_database(self):
        """Inicializa la base de datos SQLite"""
        conn = sqlite3.connect('edificio.db')
        cursor = conn.cursor()
        
        # Tabla de inquilinos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inquilinos (
            id INTEGER PRIMARY KEY,
            nombre TEXT,
            apartamento TEXT,
            renta REAL,
            identificacion TEXT,
            email TEXT,
            celular TEXT,
            profesion TEXT,
            fecha_ingreso TEXT,
            deposito REAL DEFAULT 0,
            estado TEXT DEFAULT 'Activo',
            contacto_emergencia TEXT,
            telefono_emergencia TEXT,
            relacion_emergencia TEXT,
            notas TEXT,
            archivo_identificacion TEXT,
            archivo_contrato TEXT,
            fecha_archivo_id TEXT,
            fecha_archivo_contrato TEXT
        )
        ''')
        
        # Tabla de pagos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY,
            fecha TEXT,
            inquilino_id INTEGER,
            monto REAL,
            FOREIGN KEY (inquilino_id) REFERENCES inquilinos (id)
        )
        ''')
        
        # Tabla de gastos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY,
            fecha TEXT,
            tipo TEXT,
            descripcion TEXT,
            monto REAL
        )
        ''')
        
        # === MIGRACIÓN AUTOMÁTICA DE COLUMNAS ===
        try:
            cursor.execute("PRAGMA table_info(inquilinos)")
            existing_columns = [col[1] for col in cursor.fetchall()]
            
            # Definir todas las columnas nuevas que necesitamos
            required_columns = [
                ("identificacion", "TEXT"),
                ("email", "TEXT"),
                ("celular", "TEXT"),
                ("profesion", "TEXT"),
                ("fecha_ingreso", "TEXT"),
                ("deposito", "REAL DEFAULT 0"),
                ("estado", "TEXT DEFAULT 'Activo'"),
                ("contacto_emergencia", "TEXT"),
                ("telefono_emergencia", "TEXT"),
                ("relacion_emergencia", "TEXT"),
                ("notas", "TEXT"),
                ("archivo_identificacion", "TEXT"),
                ("archivo_contrato", "TEXT"),
                ("fecha_archivo_id", "TEXT"),
                ("fecha_archivo_contrato", "TEXT")
            ]
            
            # Agregar solo las columnas que no existen
            columns_added = 0
            for col_name, col_type in required_columns:
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE inquilinos ADD COLUMN {col_name} {col_type}")
                        columns_added += 1
                        print(f"✅ Columna agregada automáticamente: {col_name}")
                    except sqlite3.Error as e:
                        print(f"⚠️ Error agregando columna {col_name}: {e}")
            
            if columns_added > 0:
                print(f"🔄 Migración automática completada: {columns_added} columnas agregadas")
            else:
                print("✅ Base de datos ya está actualizada")
            
            conn.commit()
            
        except sqlite3.Error as e:
            print(f"❌ Error en migración: {e}")
        finally:
            conn.close()
            
        # Migrar datos existentes si existen archivos CSV
        self.migrar_datos_csv_a_sqlite()
        
    def migrar_datos_csv_a_sqlite(self):
        """Migra los datos de archivos CSV a SQLite si existen"""
        # Migrar inquilinos
        if os.path.exists("inquilinos.csv"):
            try:
                conn = sqlite3.connect('edificio.db')
                cursor = conn.cursor()
                
                with open("inquilinos.csv", "r") as archivo:
                    import csv
                    lector = csv.reader(archivo)
                    for fila in lector:
                        if len(fila) >= 3:
                            # Verificar si ya existe el inquilino
                            cursor.execute("SELECT id FROM inquilinos WHERE nombre=? AND apartamento=?",
                                        (fila[0], fila[1]))
                            if not cursor.fetchone():
                                cursor.execute("INSERT INTO inquilinos (nombre, apartamento, renta) VALUES (?, ?, ?)",
                                            (fila[0], fila[1], float(fila[2])))
                
                # Migrar pagos si existe el archivo
                if os.path.exists("pagos.csv"):
                    with open("pagos.csv", "r") as archivo:
                        lector = csv.reader(archivo)
                        for fila in lector:
                            if len(fila) >= 3:
                                fecha = fila[0]
                                inquilino_info = fila[1]
                                monto = float(fila[2])
                                
                                # Extraer nombre del inquilino
                                if " - Apto " in inquilino_info:
                                    nombre, _ = inquilino_info.split(" - Apto ")
                                    cursor.execute("SELECT id FROM inquilinos WHERE nombre=?", (nombre,))
                                    inquilino_id = cursor.fetchone()
                                    
                                    if inquilino_id:
                                        cursor.execute(
                                            "INSERT INTO pagos (fecha, inquilino_id, monto) VALUES (?, ?, ?)",
                                            (fecha, inquilino_id[0], monto))
                
                # Migrar gastos si existe el archivo
                if os.path.exists("gastos.csv"):
                    with open("gastos.csv", "r") as archivo:
                        lector = csv.reader(archivo)
                        for fila in lector:
                            if len(fila) >= 4:
                                fecha = fila[0]
                                tipo = fila[1]
                                descripcion = fila[2]
                                monto = float(fila[3])
                                
                                cursor.execute(
                                    "INSERT INTO gastos (fecha, tipo, descripcion, monto) VALUES (?, ?, ?, ?)",
                                    (fecha, tipo, descripcion, monto))
                
                conn.commit()
                conn.close()
                
                # Crear respaldo de archivos CSV originales
                self.crear_respaldo()
            except Exception as e:
                messagebox.showerror("Error en migración", f"Error al migrar datos: {str(e)}")
                
    def crear_respaldo(self):
        """Crea un respaldo de los archivos de datos"""
        fecha = datetime.datetime.now().strftime("%Y%m%d")
        carpeta_respaldo = f"respaldo_{fecha}"
        
        if not os.path.exists(carpeta_respaldo):
            os.makedirs(carpeta_respaldo)
        
        for archivo in ["inquilinos.csv", "pagos.csv", "gastos.csv"]:
            if os.path.exists(archivo):
                shutil.copy2(archivo, os.path.join(carpeta_respaldo, archivo))
                
class DashboardModule:
    def __init__(self, manager):
        self.manager = manager
        self.frame = None

    def setup_ui(self, parent):
        """Configura la interfaz del módulo de dashboard"""
        self.frame = ttk.Frame(parent)
        
        # Crear contenedor principal con scroll
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill="both", expand=True)
        
        # Canvas para scroll
        canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        # Frame para el contenido
        content_frame = ttk.Frame(canvas)
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Configurar canvas
        canvas.create_window((0, 0), window=content_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título del Dashboard
        title_label = ttk.Label(content_frame, 
                              text="Dashboard - Vista General",
                              font=('Segoe UI', 24, 'bold'),
                              style='Title.TLabel')
        title_label.pack(pady=(20,30))
        
        # Crear métricas
        self.create_metrics_section(content_frame)
        
        # Empaquetar elementos de scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Programar la primera actualización de métricas para 100ms después de iniciar
        self.frame.after(100, self.actualizar_metricas)
        
        return self.frame

    def actualizar_metricas(self):
        """Actualiza las métricas mostradas en el dashboard"""
        try:
            conn = sqlite3.connect('edificio.db')
            cursor = conn.cursor()
            
            # Actualizar métricas de inquilinos
            cursor.execute("SELECT COUNT(*) FROM inquilinos WHERE estado='Activo'")
            total_activos = cursor.fetchone()[0]
            
            # Actualizar métricas de pagos del mes actual
            fecha_actual = datetime.date.today()
            mes_actual = fecha_actual.month
            año_actual = fecha_actual.year
            
            cursor.execute("""
                SELECT COALESCE(SUM(monto), 0)
                FROM pagos
                WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
            """, (str(año_actual), f"{mes_actual:02d}"))
            ingresos_mes = cursor.fetchone()[0] or 0
            
            # Actualizar métricas de gastos del mes actual
            cursor.execute("""
                SELECT COALESCE(SUM(monto), 0)
                FROM gastos
                WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
            """, (str(año_actual), f"{mes_actual:02d}"))
            gastos_mes = cursor.fetchone()[0] or 0
            
            conn.close()
            
            # Actualizar labels con formato de moneda
            if hasattr(self, 'inquilinos_metric'):
                self.inquilinos_metric.configure(text=str(total_activos))
            if hasattr(self, 'ingresos_metric'):
                self.ingresos_metric.configure(text=f"${ingresos_mes:,.2f}")
            if hasattr(self, 'gastos_metric'):
                self.gastos_metric.configure(text=f"${gastos_mes:,.2f}")
            
            # Forzar actualización visual
            self.frame.update_idletasks()
            
            # Programar próxima actualización en 5 minutos
            if hasattr(self, 'frame') and self.frame:
                self.frame.after(300000, self.actualizar_metricas)
            
        except Exception as e:
            logging.error(f"Error actualizando métricas del dashboard: {e}")
            # Reintentar en 1 minuto si hay error
            if hasattr(self, 'frame') and self.frame:
                self.frame.after(60000, self.actualizar_metricas)

    def actualizar_metricas(self):
        """Alias para actualizar_estadisticas"""
        self.actualizar_estadisticas()

# Función principal
def main():
    root = tk.Tk()
    app = ApartmentManager(root)
    root.mainloop()

# Llamada a la función principal
if __name__ == "__main__":
    main()