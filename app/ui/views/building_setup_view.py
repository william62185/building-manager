"""
Vista para el asistente de configuración del edificio.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, List, Dict, Any

from manager.app.services.building_service import building_service
from manager.app.services.apartment_service import apartment_service
from manager.app.ui.components.theme_manager import theme_manager, Spacing
from manager.app.ui.components.modern_widgets import ModernButton

class BuildingSetupView(tk.Frame):
    """Asistente paso a paso para configurar la estructura del edificio."""

    def __init__(self, parent, on_back: Callable):
        super().__init__(parent, **theme_manager.get_style("frame"))
        self.on_back = on_back
        self.current_step = 0
        self.wizard_data = {}

        if building_service.has_buildings():
            self._show_existing_building_info()
        else:
            self._create_step_ui()

    def _show_existing_building_info(self):
        """Muestra la información del edificio existente y ofrece reconfigurar."""
        # Limpiar contenido actual
        for widget in self.winfo_children():
            widget.destroy()

        # Header
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)
        tk.Label(header, text="Configuración del Edificio", **theme_manager.get_style("label_title")).pack(side="left")

        # Contenido principal
        main_container = tk.Frame(self, **theme_manager.get_style("frame"))
        main_container.pack(fill="both", expand=True, padx=Spacing.MD, pady=Spacing.MD)

        # Obtener información del edificio existente
        active_building = building_service.get_active_building()
        
        if active_building:
            # Mostrar información del edificio existente
            info_frame = tk.Frame(main_container, **theme_manager.get_style("card"))
            info_frame.pack(fill="x", pady=Spacing.MD)

            # Título
            title_label = tk.Label(
                info_frame,
                text="🏢 Edificio Configurado",
                font=("Segoe UI", 16, "bold"),
                fg="#1976d2",
                bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"]
            )
            title_label.pack(pady=Spacing.MD)

            # Información del edificio
            building_info = tk.Frame(info_frame, **theme_manager.get_style("card_content"))
            building_info.pack(fill="x", padx=Spacing.LG, pady=Spacing.MD)

            # Nombre del edificio
            name_label = tk.Label(
                building_info,
                text=f"Nombre: {active_building.get('name', 'Sin nombre')}",
                font=("Segoe UI", 12, "bold"),
                anchor="w"
            )
            name_label.pack(fill="x", pady=2)

            # Detalles del edificio
            details_text = f"Pisos: {active_building.get('floor_count', 0)} | "
            details_text += f"Apartamentos: {active_building.get('apartment_count', 0)} | "
            details_text += f"Unidades Especiales: {active_building.get('special_unit_count', 0)}"

            details_label = tk.Label(
                building_info,
                text=details_text,
                font=("Segoe UI", 10),
                fg="#666666",
                anchor="w"
            )
            details_label.pack(fill="x", pady=2)

        # Mensaje informativo
        message_frame = tk.Frame(main_container, **theme_manager.get_style("card"))
        message_frame.pack(fill="x", pady=Spacing.MD)

        message_label = tk.Label(
            message_frame,
            text="ℹ️ Información Importante",
            font=("Segoe UI", 14, "bold"),
            fg="#f57c00",
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"]
        )
        message_label.pack(pady=Spacing.MD)

        info_text = (
            "La versión profesional de Building Manager está diseñada para gestionar "
            "un solo edificio por instalación.\n\n"
            "Ya tienes un edificio configurado en esta instalación. "
            "Si necesitas gestionar múltiples edificios, considera adquirir "
            "la versión empresarial.\n\n"
            "Para modificar la configuración del edificio actual, "
            "puedes usar la opción 'Gestionar Edificio' desde el menú principal."
        )

        info_label = tk.Label(
            message_frame,
            text=info_text,
            font=("Segoe UI", 10),
            justify="left",
            wraplength=600,
            bg=theme_manager.themes[theme_manager.current_theme]["bg_primary"]
        )
        info_label.pack(padx=Spacing.LG, pady=Spacing.MD)

        # Botones de acción
        buttons_frame = tk.Frame(main_container, **theme_manager.get_style("frame"))
        buttons_frame.pack(fill="x", pady=Spacing.LG)

        # Botón para ir a gestión del edificio
        ModernButton(
            buttons_frame,
            text="Gestionar Edificio Actual",
            icon="🏢",
            command=self._go_to_building_management
        ).pack(side="left", padx=(0, Spacing.MD))

        # Botón para volver
        ModernButton(
            buttons_frame,
            text="Volver al Menú Principal",
            style="secondary",
            command=self.on_back
        ).pack(side="right")

    def _go_to_building_management(self):
        """Navega a la gestión del edificio actual."""
        # Aquí podrías implementar la navegación a la gestión del edificio
        # Por ahora, solo volvemos al menú principal
        self.on_back()

    def _create_step_ui(self):
        """Crea la UI para el paso actual del asistente."""
        for widget in self.winfo_children():
            widget.destroy()

        # Header
        header = tk.Frame(self, **theme_manager.get_style("frame"))
        header.pack(fill="x", pady=(0, Spacing.LG), padx=Spacing.MD)
        tk.Label(header, text="Asistente de Configuración del Edificio", **theme_manager.get_style("label_title")).pack(side="left")

        # Área con scroll para el contenido del paso (evita que los botones se corran)
        scroll_outer = tk.Frame(self, **theme_manager.get_style("frame"))
        scroll_outer.pack(fill="both", expand=True, padx=Spacing.MD, pady=(0, Spacing.SM))

        self._wizard_canvas = tk.Canvas(scroll_outer, highlightthickness=0, **theme_manager.get_style("frame"))
        canvas = self._wizard_canvas
        scrollbar = ttk.Scrollbar(scroll_outer)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=canvas.yview)

        self.step_container = tk.Frame(canvas, **theme_manager.get_style("frame"))
        canvas_window = canvas.create_window((0, 0), window=self.step_container, anchor="nw")

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        def _on_step_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", _on_canvas_configure)
        self.step_container.bind("<Configure>", _on_step_configure)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(_):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(_):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

        # Botones de navegación fijos abajo
        self.nav_frame = tk.Frame(self, **theme_manager.get_style("frame"))
        self.nav_frame.pack(side="bottom", fill="x", padx=Spacing.MD, pady=Spacing.MD)

        self.render_current_step()
        self.update_nav_buttons()
        # Asegurar scrollregion tras render
        self.after(50, lambda: canvas.configure(scrollregion=canvas.bbox("all")))

    def render_current_step(self):
        """Renderiza el contenido del paso actual."""
        for widget in self.step_container.winfo_children():
            widget.destroy()

        if self.current_step == 0:
            self._step0_welcome()
        elif self.current_step == 1:
            self._step1_name_and_floors()
        elif self.current_step == 2:
            self._step2_apartments_per_floor()
        elif self.current_step == 3:
            self._step3_summary_and_special_units()
        # ... más pasos aquí

    def update_nav_buttons(self):
        """Actualiza los botones de navegación según el paso."""
        for widget in self.nav_frame.winfo_children():
            widget.destroy()

        if self.current_step > 0:
            ModernButton(self.nav_frame, text="← Atrás", style="secondary", command=self._prev_step).pack(side="left")
        
        # Botón Salir/Cancelar
        ModernButton(self.nav_frame, text="Salir", command=self.on_back).pack(side="left", padx=Spacing.MD)

        if self.current_step < 3: # Actualizar cuando haya más pasos
            ModernButton(self.nav_frame, text="Siguiente →", command=self._next_step).pack(side="right")
        else:
            ModernButton(self.nav_frame, text="Finalizar y Guardar", icon="💾", style="purple", command=self._finish_setup).pack(side="right")  # Morado para mantener tonalidad morada del módulo
    
    def _prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1
            self.render_current_step()
            self.update_nav_buttons()

    def _next_step(self):
        if self.current_step == 1:
            if not self._validate_step1():
                return
        elif self.current_step == 2:
            if not self._validate_step2():
                return
        self.current_step += 1
        self.render_current_step()
        self.update_nav_buttons()

    def _finish_setup(self):
        if not self._validate_step3():
            return
        
        try:
            building_service.create_building_from_wizard(
                name=self.wizard_data['building_name_var'].get().strip(),
                floors_config=self.wizard_data['floors_config'],
                special_units=self.wizard_data.get('special_units', []),
                address=self.wizard_data.get('address_var', tk.StringVar()).get().strip(),
                city=self.wizard_data.get('city_var', tk.StringVar()).get().strip(),
                country=self.wizard_data.get('country_var', tk.StringVar()).get().strip(),
                phone=self.wizard_data.get('phone_var', tk.StringVar()).get().strip(),
                email=self.wizard_data.get('email_var', tk.StringVar()).get().strip(),
            )
            messagebox.showinfo("Éxito", "La estructura del edificio ha sido creada y los apartamentos han sido generados.")
            self.on_back()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}")

    def _validate_step1(self) -> bool:
        name = self.wizard_data.get('building_name_var', tk.StringVar()).get()
        floors_str = self.wizard_data.get('floor_count_var', tk.StringVar()).get()
        if not name.strip():
            messagebox.showerror("Error", "El nombre del edificio es obligatorio.")
            return False
        try:
            floors = int(floors_str)
            if floors <= 0:
                raise ValueError
            self.wizard_data['floor_count'] = floors
        except ValueError:
            messagebox.showerror("Error", "La cantidad de pisos debe ser un número entero positivo.")
            return False
        return True

    def _validate_step2(self) -> bool:
        self.wizard_data['floors_config'] = []
        for i, var in enumerate(self.wizard_data['apartments_per_floor_vars']):
            try:
                count = int(var.get())
                if count < 0: raise ValueError
                self.wizard_data['floors_config'].append({
                    "floor_number": i + 1,
                    "apartment_count": count
                })
            except ValueError:
                messagebox.showerror("Error", f"La cantidad de apartamentos para el piso {i+1} debe ser un número entero no negativo.")
                return False
        return True

    def _validate_step3(self) -> bool:
        self.wizard_data['special_units'] = []
        if hasattr(self, 'special_units_entries'):
            for entry_set in self.special_units_entries:
                name = entry_set['name_var'].get().strip()
                unit_type = entry_set['type_var'].get().strip()
                floor = entry_set['floor_var'].get().strip()
                if name: # Only add if name is provided
                    if not unit_type or not floor:
                        messagebox.showerror("Error", f"Para la unidad especial '{name}', debe especificar el tipo y el piso.")
                        return False
                    self.wizard_data['special_units'].append({"name": name, "type": unit_type, "floor": floor})
        return True

    # --- Step Implementations ---

    def _step0_welcome(self):
        """Paso 0: Bienvenida e introducción."""
        tk.Label(self.step_container, text="Bienvenido al Asistente de Configuración",
                 font=("Segoe UI", 18, "bold")).pack(pady=Spacing.LG)
        welcome_text = (
            "Este asistente te guiará para crear la estructura de tu edificio.\n"
            "Podrás definir el nombre, el número de pisos y la cantidad de apartamentos por cada uno.\n\n"
            "Haz clic en 'Siguiente' para comenzar."
        )
        tk.Label(self.step_container, text=welcome_text, justify="center", wraplength=500).pack()

    def _step1_name_and_floors(self):
        """Paso 1: Definir nombre del edificio, cantidad de pisos y datos de contacto/ubicación."""
        container = tk.Frame(self.step_container, **theme_manager.get_style("frame"))
        container.pack(pady=Spacing.XL)

        row = 0

        # Nombre del Edificio (obligatorio)
        tk.Label(container, text="Nombre del Edificio:", **theme_manager.get_style("label_body")).grid(row=row, column=0, sticky="w", pady=Spacing.SM)
        self.wizard_data['building_name_var'] = tk.StringVar()
        ttk.Entry(container, textvariable=self.wizard_data['building_name_var'], width=40).grid(row=row, column=1, padx=Spacing.MD)
        tk.Label(container, text="*", fg="red", font=("Segoe UI", 10, "bold")).grid(row=row, column=2, sticky="w")
        row += 1

        # Cantidad de Pisos
        tk.Label(container, text="Cantidad de Pisos:", **theme_manager.get_style("label_body")).grid(row=row, column=0, sticky="w", pady=Spacing.SM)
        self.wizard_data['floor_count_var'] = tk.StringVar()
        ttk.Entry(container, textvariable=self.wizard_data['floor_count_var'], width=10).grid(row=row, column=1, padx=Spacing.MD, sticky="w")
        row += 1

        # Dirección
        tk.Label(container, text="Dirección:", **theme_manager.get_style("label_body")).grid(row=row, column=0, sticky="w", pady=Spacing.SM)
        self.wizard_data['address_var'] = tk.StringVar()
        ttk.Entry(container, textvariable=self.wizard_data['address_var'], width=40).grid(row=row, column=1, padx=Spacing.MD)
        row += 1

        # Ciudad
        tk.Label(container, text="Ciudad:", **theme_manager.get_style("label_body")).grid(row=row, column=0, sticky="w", pady=Spacing.SM)
        self.wizard_data['city_var'] = tk.StringVar()
        ttk.Entry(container, textvariable=self.wizard_data['city_var'], width=40).grid(row=row, column=1, padx=Spacing.MD)
        row += 1

        # País
        tk.Label(container, text="País:", **theme_manager.get_style("label_body")).grid(row=row, column=0, sticky="w", pady=Spacing.SM)
        self.wizard_data['country_var'] = tk.StringVar()
        ttk.Entry(container, textvariable=self.wizard_data['country_var'], width=40).grid(row=row, column=1, padx=Spacing.MD)
        row += 1

        # Teléfono
        tk.Label(container, text="Teléfono:", **theme_manager.get_style("label_body")).grid(row=row, column=0, sticky="w", pady=Spacing.SM)
        self.wizard_data['phone_var'] = tk.StringVar()
        ttk.Entry(container, textvariable=self.wizard_data['phone_var'], width=40).grid(row=row, column=1, padx=Spacing.MD)
        row += 1

        # Email
        tk.Label(container, text="Email:", **theme_manager.get_style("label_body")).grid(row=row, column=0, sticky="w", pady=Spacing.SM)
        self.wizard_data['email_var'] = tk.StringVar()
        ttk.Entry(container, textvariable=self.wizard_data['email_var'], width=40).grid(row=row, column=1, padx=Spacing.MD)

    def _step2_apartments_per_floor(self):
        """Paso 2: Definir cuántos apartamentos hay por piso."""
        tk.Label(self.step_container, text="Define los Apartamentos por Piso",
                 font=("Segoe UI", 16, "bold")).pack(pady=Spacing.MD)

        self.wizard_data['apartments_per_floor_vars'] = []
        
        container = tk.Frame(self.step_container, **theme_manager.get_style("frame"))
        container.pack(pady=Spacing.LG)
        
        num_floors = self.wizard_data.get('floor_count', 0)
        for i in range(num_floors):
            floor_num = i + 1
            tk.Label(container, text=f"Piso {floor_num}:", font=("Segoe UI", 12)).grid(row=i, column=0, sticky="w", padx=Spacing.MD, pady=Spacing.SM)
            var = tk.StringVar()
            ttk.Entry(container, textvariable=var, width=10).grid(row=i, column=1, sticky="w", padx=Spacing.MD)
            tk.Label(container, text="apartamentos", font=("Segoe UI", 12)).grid(row=i, column=2, sticky="w")
            self.wizard_data['apartments_per_floor_vars'].append(var)

    def _step3_summary_and_special_units(self):
        """Paso 3: Resumen y añadir unidades especiales."""
        tk.Label(self.step_container, text="Resumen y Unidades Especiales", font=("Segoe UI", 16, "bold")).pack(pady=Spacing.MD)

        # Summary Frame
        summary_frame = tk.LabelFrame(self.step_container, text="Resumen del Edificio", padx=10, pady=10)
        summary_frame.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)
        tk.Label(summary_frame, text=f"Nombre: {self.wizard_data['building_name_var'].get()}", font=("Segoe UI", 11)).pack(anchor="w")
        total_apts = sum(f['apartment_count'] for f in self.wizard_data['floors_config'])
        tk.Label(summary_frame, text=f"Total de Apartamentos: {total_apts}", font=("Segoe UI", 11)).pack(anchor="w")
        # Mostrar ubicación/contacto si se completaron
        addr = self.wizard_data.get('address_var', tk.StringVar()).get().strip()
        city = self.wizard_data.get('city_var', tk.StringVar()).get().strip()
        country = self.wizard_data.get('country_var', tk.StringVar()).get().strip()
        if addr or city or country:
            loc = " | ".join(x for x in [addr, city, country] if x)
            tk.Label(summary_frame, text=f"Ubicación: {loc}", font=("Segoe UI", 11)).pack(anchor="w")
        phone = self.wizard_data.get('phone_var', tk.StringVar()).get().strip()
        email = self.wizard_data.get('email_var', tk.StringVar()).get().strip()
        if phone or email:
            contact = " | ".join(x for x in [phone, email] if x)
            tk.Label(summary_frame, text=f"Contacto: {contact}", font=("Segoe UI", 11)).pack(anchor="w")

        # Special Units Frame
        special_units_frame = tk.LabelFrame(self.step_container, text="Añadir Unidades Especiales (Opcional)", padx=10, pady=10)
        special_units_frame.pack(fill="x", padx=Spacing.MD, pady=Spacing.SM)
        
        self.special_units_container = tk.Frame(special_units_frame)
        self.special_units_container.pack(fill="x")
        self.special_units_entries = []

        # Header
        header_frame = tk.Frame(self.special_units_container)
        header_frame.pack(fill="x", pady=(0, Spacing.SM))
        tk.Label(header_frame, text="Nombre (ej. Penthouse A)", font=("Segoe UI", 10, "bold")).pack(side="left", expand=True)
        tk.Label(header_frame, text="Tipo (ej. Local)", font=("Segoe UI", 10, "bold")).pack(side="left", expand=True)
        tk.Label(header_frame, text="Piso", font=("Segoe UI", 10, "bold")).pack(side="left", expand=True, padx=(0, Spacing.MD))

        self._add_special_unit_row() # Add the first row

        ModernButton(special_units_frame, text="+ Añadir otra unidad", style="info", small=True, command=self._add_special_unit_row).pack(pady=Spacing.SM)

    # Opciones de tipo de unidad especial para el combobox
    SPECIAL_UNIT_TYPES = (
        "Apartamento Estándar",
        "Local comercial",
        "Penthouse",
        "Depósito/Bodega",
        "Otro",
    )

    def _add_special_unit_row(self):
        row_frame = tk.Frame(self.special_units_container)
        row_frame.pack(fill="x", pady=Spacing.XS)
        
        name_var = tk.StringVar()
        type_var = tk.StringVar()
        floor_var = tk.StringVar()
        
        ttk.Entry(row_frame, textvariable=name_var).pack(side="left", expand=True, fill="x", padx=(0, Spacing.SM))
        type_combo = ttk.Combobox(
            row_frame,
            textvariable=type_var,
            values=list(self.SPECIAL_UNIT_TYPES),
            state="readonly",
            width=22,
        )
        type_combo.pack(side="left", expand=True, fill="x", padx=(0, Spacing.SM))
        ttk.Entry(row_frame, textvariable=floor_var, width=10).pack(side="left")
        
        self.special_units_entries.append({'name_var': name_var, 'type_var': type_var, 'floor_var': floor_var})
        # Actualizar scroll para que se vea la nueva fila
        if hasattr(self, "_wizard_canvas") and self._wizard_canvas.winfo_exists():
            self.after(100, lambda: self._wizard_canvas.configure(scrollregion=self._wizard_canvas.bbox("all"))) 