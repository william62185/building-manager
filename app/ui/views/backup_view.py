"""
Vista para gestión completa de backups del sistema
Permite crear backups completos y restaurar desde archivos externos
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Optional
from datetime import datetime
from pathlib import Path
import threading
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.icons import Icons
from manager.app.ui.components.modern_widgets import create_rounded_button, get_module_colors
from manager.app.services.backup_service import backup_service


class BackupView(tk.Frame):
    """Vista para gestión de backups completos del sistema"""

    def __init__(self, parent, on_back: Callable = None, on_navigate: Callable = None):
        super().__init__(parent)
        theme = theme_manager.themes[theme_manager.current_theme]
        self._content_bg = theme.get("content_bg", theme["bg_primary"])
        self.configure(bg=self._content_bg)
        self.on_back = on_back
        self.on_navigate = on_navigate
        self._create_layout()

    def _create_layout(self):
        for widget in self.winfo_children():
            widget.destroy()
        theme = theme_manager.themes[theme_manager.current_theme]
        cb = self._content_bg
        fg = theme.get("text_primary", "#1f2937")

        header = tk.Frame(self, bg=cb)
        header.pack(fill="x", pady=(0, Spacing.SM), padx=Spacing.MD)
        tk.Label(header, text="Backup de Datos", font=("Segoe UI", 16, "bold"), bg=cb, fg=fg).pack(side="left")
        buttons_frame = tk.Frame(header, bg=cb)
        buttons_frame.pack(side="right")

        colors = get_module_colors("administración")
        purple_primary = colors["primary"]
        purple_hover = colors["hover"]
        purple_light = colors["light"]
        purple_text = colors["text"]
        btn_bg = theme.get("btn_secondary_bg", "#e5e7eb")

        def go_to_dashboard():
            if self.on_navigate:
                self.on_navigate("dashboard")
            elif self.on_back:
                self.on_back()

        def go_back():
            if self.on_back:
                self.on_back()

        btn_volver = create_rounded_button(
            buttons_frame, text=f"{Icons.ARROW_LEFT} Volver",
            bg_color=btn_bg, fg_color=purple_primary,
            hover_bg=purple_light, hover_fg=purple_text,
            command=go_back, padx=12, pady=5, radius=4, border_color=purple_light
        )
        btn_volver.pack(side="right", padx=(Spacing.SM, 0))
        btn_dashboard = create_rounded_button(
            buttons_frame, text=f"{Icons.APARTMENTS} Dashboard",
            bg_color=purple_primary, fg_color="white",
            hover_bg=purple_hover, hover_fg="white",
            command=go_to_dashboard, padx=12, pady=5, radius=4, border_color=purple_hover
        )
        btn_dashboard.pack(side="right")

        container = tk.Frame(self, bg=cb)
        container.pack(fill="both", expand=True, padx=Spacing.MD, pady=(0, Spacing.SM))
        canvas = tk.Canvas(container, bg=cb, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        main_container = tk.Frame(canvas, bg=cb)
        main_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_window = canvas.create_window((0, 0), window=main_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def update_canvas_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", update_canvas_width)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self._create_backup_section(main_container)
        tk.Frame(main_container, height=1, bg=theme.get("border_light", "#d1d5db")).pack(fill="x", pady=(2, 2))
        self._create_restore_section(main_container)
        tk.Frame(main_container, height=1, bg=theme.get("border_light", "#d1d5db")).pack(fill="x", pady=(2, 2))
        self._create_backups_list_section(main_container)
        self.after(100, self._refresh_backups_list)
    
    def _create_backup_section(self, parent):
        """Crea la sección para crear backups"""
        card_bg = "#f3e8ff"
        cb = self._content_bg
        fg = theme_manager.themes[theme_manager.current_theme].get("text_primary", "#1f2937")
        card = tk.Frame(parent, bg=card_bg)
        card.pack(fill="x", pady=(0, 2))
        content = tk.Frame(card, bg=card_bg)
        content.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)

        title_frame = tk.Frame(content, bg=card_bg)
        title_frame.pack(fill="x", pady=(0, 2))
        tk.Label(title_frame, text="💾", font=("Segoe UI", 14), bg=card_bg).pack(side="left", padx=(0, 4))
        tk.Label(title_frame, text="Crear Backup Completo", font=("Segoe UI", 12, "bold"), bg=card_bg, fg=fg).pack(side="left")

        description = tk.Label(
            content,
            text="Copia completa: datos JSON, edificios, recibos, fichas, gastos. Permite restaurar en otra PC.",
            font=("Segoe UI", 9), fg="#374151", justify="left", bg=card_bg
        )
        description.pack(anchor="w", pady=(0, 4))

        buttons_frame = tk.Frame(content, bg=card_bg)
        buttons_frame.pack(fill="x", pady=(0, 2))
        btn_create_local = tk.Button(
            buttons_frame, text=f"{Icons.SAVE} Crear Backup Local",
            font=("Segoe UI", 9), bg="#8b5cf6", fg="white",
            activebackground="#7c3aed", activeforeground="white",
            bd=0, relief="flat", padx=10, pady=4, cursor="hand2",
            command=self._create_backup_local
        )
        btn_create_local.pack(side="left", padx=(0, 6))
        btn_create_external = tk.Button(
            buttons_frame, text=f"{Icons.SAVE} Crear Backup Externo",
            font=("Segoe UI", 9), bg="#8b5cf6", fg="white",
            activebackground="#7c3aed", activeforeground="white",
            bd=0, relief="flat", padx=10, pady=4, cursor="hand2",
            command=self._create_backup_external
        )
        btn_create_external.pack(side="left")

        self.backup_status_label = tk.Label(content, text="", font=("Segoe UI", 8), fg="#666", bg=card_bg)
        self.backup_status_label.pack(anchor="w", pady=(2, 0))
    
    def _create_restore_section(self, parent):
        """Crea la sección para restaurar backups"""
        card_bg = "#f3e8ff"
        cb = self._content_bg
        fg = theme_manager.themes[theme_manager.current_theme].get("text_primary", "#1f2937")
        card = tk.Frame(parent, bg=card_bg)
        card.pack(fill="x", pady=(0, 2))
        content = tk.Frame(card, bg=card_bg)
        content.pack(fill="both", expand=True, padx=Spacing.SM, pady=Spacing.SM)

        title_frame = tk.Frame(content, bg=card_bg)
        title_frame.pack(fill="x", pady=(0, 2))
        tk.Label(title_frame, text="🔄", font=("Segoe UI", 14), bg=card_bg).pack(side="left", padx=(0, 4))
        tk.Label(title_frame, text="Restaurar desde Backup", font=("Segoe UI", 12, "bold"), bg=card_bg, fg=fg).pack(side="left")

        description = tk.Label(
            content,
            text="Restaura desde archivo externo. Valida backup, crea copia de seguridad y restaura datos. ⚠ Reemplaza todos los datos actuales.",
            font=("Segoe UI", 9), fg="#374151", justify="left", bg=card_bg
        )
        description.pack(anchor="w", pady=(0, 4))

        btn_restore = tk.Button(
            content, text="🔄 Seleccionar y Restaurar Backup",
            font=("Segoe UI", 9), bg="#9333ea", fg="white",
            activebackground="#7c3aed", activeforeground="white",
            bd=0, relief="flat", padx=10, pady=4, cursor="hand2",
            command=self._restore_from_backup
        )
        btn_restore.pack(anchor="w", pady=(0, 2))

        self.restore_status_label = tk.Label(content, text="", font=("Segoe UI", 8), fg="#666", bg=card_bg)
        self.restore_status_label.pack(anchor="w", pady=(2, 0))
    
    def _create_backups_list_section(self, parent):
        """Crea la sección con lista de backups locales"""
        card_bg = "#f3e8ff"
        fg = theme_manager.themes[theme_manager.current_theme].get("text_primary", "#1f2937")
        card = tk.Frame(parent, bg=card_bg)
        card.pack(fill="x", pady=(0, 2))
        content = tk.Frame(card, bg=card_bg)
        content.pack(fill="x", expand=False, padx=Spacing.SM, pady=Spacing.SM)
        tk.Label(content, text="Backups Locales", font=("Segoe UI", 12, "bold"), bg=card_bg, fg=fg).pack(anchor="w", pady=(0, 4))
        scrollable_frame = tk.Frame(content, bg=card_bg)
        scrollable_frame.pack(fill="x", expand=False)
        self.backups_list_frame = scrollable_frame
        self._load_backups_list(scrollable_frame)
    
    def _create_backup_local(self):
        """Crea un backup y lo guarda localmente"""
        self.backup_status_label.config(text="⏳ Creando backup...", fg="#f59e0b")
        self.update()
        
        def create_backup_thread():
            try:
                backup_path = backup_service.create_full_backup()
                if backup_path:
                    backup_file = Path(backup_path)
                    size_mb = backup_file.stat().st_size / (1024 * 1024)
                    self.backup_status_label.after(0, lambda: self.backup_status_label.config(
                        text=f"✅ Backup creado exitosamente: {backup_file.name} ({size_mb:.2f} MB)",
                        fg="#10b981"
                    ))
                    # Actualizar lista de backups automáticamente
                    if hasattr(self, 'backups_list_frame') and self.backups_list_frame:
                        self.after(100, lambda: self._load_backups_list(self.backups_list_frame))
                    messagebox.showinfo(
                        "Backup Exitoso",
                        f"Backup creado exitosamente:\n\n"
                        f"Archivo: {backup_file.name}\n"
                        f"Tamaño: {size_mb:.2f} MB\n"
                        f"Ubicación: {backup_file.parent}"
                    )
                else:
                    self.backup_status_label.after(0, lambda: self.backup_status_label.config(
                        text="❌ Error al crear backup",
                        fg="#ef4444"
                    ))
                    messagebox.showerror("Error", "No se pudo crear el backup. Revisa los logs para más detalles.")
            except Exception as e:
                self.backup_status_label.after(0, lambda: self.backup_status_label.config(
                    text=f"❌ Error: {str(e)}",
                    fg="#ef4444"
                ))
                messagebox.showerror("Error", f"Error al crear backup: {str(e)}")
        
        thread = threading.Thread(target=create_backup_thread, daemon=True)
        thread.start()
    
    def _create_backup_external(self):
        """Crea un backup y permite guardarlo en una ubicación externa"""
        # Pedir ubicación donde guardar
        backup_dir = filedialog.askdirectory(
            title="Seleccionar ubicación para guardar el backup"
        )
        
        if not backup_dir:
            return
        
        self.backup_status_label.config(text="⏳ Creando backup...", fg="#f59e0b")
        self.update()
        
        def create_backup_thread():
            try:
                backup_path = backup_service.create_full_backup(output_path=backup_dir)
                if backup_path:
                    backup_file = Path(backup_path)
                    size_mb = backup_file.stat().st_size / (1024 * 1024)
                    self.backup_status_label.after(0, lambda: self.backup_status_label.config(
                        text=f"✅ Backup creado exitosamente: {backup_file.name} ({size_mb:.2f} MB)",
                        fg="#10b981"
                    ))
                    # Actualizar lista de backups automáticamente (solo si se guardó localmente)
                    # Si se guardó externamente, no actualizamos la lista local
                    backup_dir_path = Path(backup_dir)
                    if str(backup_file.parent) == str(backup_service.BACKUP_DIR):
                        if hasattr(self, 'backups_list_frame') and self.backups_list_frame:
                            self.after(100, lambda: self._load_backups_list(self.backups_list_frame))
                    messagebox.showinfo(
                        "Backup Exitoso",
                        f"Backup creado exitosamente:\n\n"
                        f"Archivo: {backup_file.name}\n"
                        f"Tamaño: {size_mb:.2f} MB\n"
                        f"Ubicación: {backup_file.parent}"
                    )
                else:
                    self.backup_status_label.after(0, lambda: self.backup_status_label.config(
                        text="❌ Error al crear backup",
                        fg="#ef4444"
                    ))
                    messagebox.showerror("Error", "No se pudo crear el backup. Revisa los logs para más detalles.")
            except Exception as e:
                self.backup_status_label.after(0, lambda: self.backup_status_label.config(
                    text=f"❌ Error: {str(e)}",
                    fg="#ef4444"
                ))
                messagebox.showerror("Error", f"Error al crear backup: {str(e)}")
        
        thread = threading.Thread(target=create_backup_thread, daemon=True)
        thread.start()
    
    def _restore_from_backup(self):
        """Restaura desde un archivo de backup"""
        # Seleccionar archivo de backup
        backup_path = filedialog.askopenfilename(
            title="Seleccionar archivo de backup para restaurar",
            filetypes=[("Archivos ZIP", "*.zip"), ("Todos los archivos", "*.*")]
        )
        
        if not backup_path:
            return
        
        # Validar backup
        validation = backup_service.validate_backup(backup_path)
        if not validation["valid"]:
            messagebox.showerror(
                "Backup Inválido",
                f"El archivo seleccionado no es un backup válido:\n\n{validation['message']}"
            )
            return
        
        metadata = validation.get("metadata", {})
        stats = metadata.get("statistics", {})
        
        # Formatear fecha de creación
        try:
            created_date = datetime.fromisoformat(metadata.get('created_at', ''))
            formatted_date = created_date.strftime("%d/%m/%Y %H:%M:%S")
        except:
            formatted_date = metadata.get('created_at', 'Desconocida')
        
        # Información del sistema donde se creó
        system_info = metadata.get('system_info', {})
        system_text = ""
        if system_info:
            system_text = f"\nSistema origen: {system_info.get('platform', 'N/A')} {system_info.get('platform_version', '')[:20]}"
        
        # Mostrar información del backup y confirmar
        info_text = (
            f"Información del Backup:\n\n"
            f"📅 Fecha de creación: {formatted_date}\n"
            f"📦 Versión del backup: {metadata.get('version', 'Desconocida')}\n"
            f"📁 Archivos en backup: {validation['files_count']}\n"
            f"{system_text}\n\n"
            f"📊 Estadísticas del Backup:\n"
            f"• Inquilinos: {stats.get('total_tenants', 0)} "
            f"(Activos: {stats.get('active_tenants', 0)}, Inactivos: {stats.get('inactive_tenants', 0)})\n"
            f"• Pagos: {stats.get('total_payments', 0)}\n"
            f"• Apartamentos: {stats.get('total_apartments', 0)} "
            f"(Disponibles: {stats.get('available_apartments', 0)}, Ocupados: {stats.get('occupied_apartments', 0)})\n"
            f"• Gastos: {stats.get('total_expenses', 0)}\n"
            f"• Documentos: {stats.get('total_documents', 0)}\n\n"
            f"⚠️ ADVERTENCIA IMPORTANTE:\n"
            f"Esta acción reemplazará TODOS los datos actuales del sistema.\n"
            f"Se creará automáticamente un backup de seguridad antes de restaurar.\n\n"
            f"¿Deseas continuar con la restauración?"
        )
        
        confirm = messagebox.askyesno(
            "Confirmar Restauración",
            info_text,
            icon="warning"
        )
        
        if not confirm:
            return
        
        self.restore_status_label.config(text="⏳ Restaurando backup...", fg="#f59e0b")
        self.update()
        
        def restore_backup_thread():
            try:
                def confirm_callback(metadata):
                    # Ya confirmamos arriba
                    return True
                
                result = backup_service.restore_from_backup(backup_path, confirm_callback)
                
                if result["success"]:
                    self.restore_status_label.after(0, lambda: self.restore_status_label.config(
                        text=f"✅ {result['message']}",
                        fg="#10b981"
                    ))
                    # Actualizar lista de backups automáticamente
                    if hasattr(self, 'backups_list_frame') and self.backups_list_frame:
                        self.after(100, lambda: self._load_backups_list(self.backups_list_frame))
                    messagebox.showinfo(
                        "Restauración Exitosa",
                        f"{result['message']}\n\n"
                        f"Archivos restaurados: {len(result.get('restored_files', []))}\n\n"
                        f"Por favor, reinicia la aplicación para ver los cambios."
                    )
                else:
                    self.restore_status_label.after(0, lambda: self.restore_status_label.config(
                        text=f"❌ {result['message']}",
                        fg="#ef4444"
                    ))
                    messagebox.showerror("Error en Restauración", result["message"])
            except Exception as e:
                self.restore_status_label.after(0, lambda: self.restore_status_label.config(
                    text=f"❌ Error: {str(e)}",
                    fg="#ef4444"
                ))
                messagebox.showerror("Error", f"Error al restaurar backup: {str(e)}")
        
        thread = threading.Thread(target=restore_backup_thread, daemon=True)
        thread.start()
    
    def _refresh_backups_list(self):
        """Actualiza la lista de backups si existe el frame"""
        if hasattr(self, 'backups_list_frame') and self.backups_list_frame:
            try:
                if self.backups_list_frame.winfo_exists():
                    self._load_backups_list(self.backups_list_frame)
            except (tk.TclError, AttributeError):
                pass
    
    def _load_backups_list(self, parent):
        """Carga la lista de backups locales (solo los 10 más recientes)"""
        # Limpiar lista actual
        for widget in parent.winfo_children():
            widget.destroy()
        
        backups = backup_service.get_backup_list()
        
        # Limitar a los 10 últimos backups
        backups = backups[:10]
        
        card_bg = "#f3e8ff"
        if not backups:
            tk.Label(
                parent, text="No hay backups locales disponibles",
                font=("Segoe UI", 10), fg="#6b7280", bg=card_bg
            ).pack(pady=Spacing.MD)
            return
        
        for backup in backups:
            self._create_backup_card(parent, backup)
    
    def _create_backup_card(self, parent, backup_info):
        """Crea una tarjeta compacta y horizontal para mostrar información de un backup"""
        card_bg = "#e9d5ff"
        card = tk.Frame(parent, bg=card_bg, relief="flat", bd=0)
        card.pack(fill="x", pady=2, padx=0)
        content = tk.Frame(card, bg=card_bg)
        content.pack(fill="x", padx=6, pady=4)
        main_row = tk.Frame(content, bg=card_bg)
        main_row.pack(fill="x")

        filename = backup_info["filename"]
        if len(filename) > 35:
            filename = filename[:32] + "..."
        tk.Label(main_row, text=filename, font=("Segoe UI", 9, "bold"), fg="#333", bg=card_bg, anchor="w").pack(side="left", padx=(0, 6))
        tk.Label(main_row, text=f"{backup_info.get('size_mb', 0):.2f} MB", font=("Segoe UI", 8), fg="#666", bg=card_bg).pack(side="left", padx=(0, 6))
        try:
            created_date = datetime.fromisoformat(backup_info["created"])
            date_str = created_date.strftime("%d/%m/%Y %H:%M")
        except Exception:
            date_str = backup_info.get("created", "N/A")
        tk.Label(main_row, text=f"📅 {date_str}", font=("Segoe UI", 8), fg="#666", bg=card_bg).pack(side="left", padx=(0, 6))

        stats = backup_info.get("statistics", {})
        if stats:
            stats_parts = []
            if stats.get("total_tenants"):
                stats_parts.append(f"👥{stats['total_tenants']}")
            if stats.get("total_apartments"):
                stats_parts.append(f"🏠{stats['total_apartments']}")
            if stats.get("total_payments"):
                stats_parts.append(f"💰{stats['total_payments']}")
            if stats_parts:
                tk.Label(main_row, text=" ".join(stats_parts), font=("Segoe UI", 8), fg="#888", bg=card_bg).pack(side="left", padx=(0, 6))

        btn_restore = tk.Button(
            main_row, text="🔄 Restaurar",
            font=("Segoe UI", 8), bg="#9333ea", fg="white",
            activebackground="#7c3aed", activeforeground="white",
            bd=0, relief="flat", padx=8, pady=3, cursor="hand2",
            command=lambda path=backup_info["path"]: self._restore_from_local_backup(path)
        )
        btn_restore.pack(side="right")

    def _restore_from_local_backup(self, backup_path: str):
        """Restaura desde un backup local"""
        # Validar backup
        validation = backup_service.validate_backup(backup_path)
        if not validation["valid"]:
            messagebox.showerror(
                "Backup Inválido",
                f"El backup seleccionado no es válido:\n\n{validation['message']}"
            )
            return
        
        metadata = validation.get("metadata", {})
        stats = metadata.get("statistics", {})
        
        # Formatear fecha
        try:
            created_date = datetime.fromisoformat(metadata.get('created_at', ''))
            formatted_date = created_date.strftime("%d/%m/%Y %H:%M:%S")
        except:
            formatted_date = metadata.get('created_at', 'Desconocida')
        
        # Confirmar restauración
        info_text = (
            f"¿Deseas restaurar este backup?\n\n"
            f"📅 Fecha: {formatted_date}\n"
            f"📊 Contenido:\n"
            f"• Inquilinos: {stats.get('total_tenants', 0)}\n"
            f"• Pagos: {stats.get('total_payments', 0)}\n"
            f"• Apartamentos: {stats.get('total_apartments', 0)}\n"
            f"• Documentos: {stats.get('total_documents', 0)}\n\n"
            f"⚠️ Esta acción reemplazará todos los datos actuales.\n"
            f"Se creará un backup de seguridad antes de restaurar."
        )
        
        confirm = messagebox.askyesno("Confirmar Restauración", info_text, icon="warning")
        if not confirm:
            return
        
        self.restore_status_label.config(text="⏳ Restaurando backup...", fg="#f59e0b")
        self.update()
        
        def restore_backup_thread():
            try:
                def confirm_callback(metadata):
                    return True
                
                result = backup_service.restore_from_backup(backup_path, confirm_callback)
                
                if result["success"]:
                    self.restore_status_label.after(0, lambda: self.restore_status_label.config(
                        text=f"✅ {result['message']}",
                        fg="#10b981"
                    ))
                    # Actualizar lista de backups automáticamente
                    if hasattr(self, 'backups_list_frame') and self.backups_list_frame:
                        self.after(100, lambda: self._load_backups_list(self.backups_list_frame))
                    messagebox.showinfo(
                        "Restauración Exitosa",
                        f"{result['message']}\n\n"
                        f"Por favor, reinicia la aplicación para ver los cambios."
                    )
                else:
                    self.restore_status_label.after(0, lambda: self.restore_status_label.config(
                        text=f"❌ {result['message']}",
                        fg="#ef4444"
                    ))
                    messagebox.showerror("Error", result["message"])
            except Exception as e:
                self.restore_status_label.after(0, lambda: self.restore_status_label.config(
                    text=f"❌ Error: {str(e)}",
                    fg="#ef4444"
                ))
                messagebox.showerror("Error", f"Error al restaurar: {str(e)}")
        
        thread = threading.Thread(target=restore_backup_thread, daemon=True)
        thread.start()
