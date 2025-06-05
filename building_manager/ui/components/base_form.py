import tkinter as tk
import ttkbootstrap as ttk
from typing import Any, Dict, List, Optional, Callable
from datetime import date, datetime
from tkinter import filedialog
import os

class BaseForm(ttk.Frame):
    """Formulario base con funcionalidades comunes."""
    def __init__(
        self,
        master: Any,
        on_submit: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None
    ):
        super().__init__(master)
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        self.fields: Dict[str, Dict[str, Any]] = {}
        self.sections: List[Dict[str, Any]] = []
        self.current_section: Optional[Dict[str, Any]] = None
        self.file_paths: Dict[str, str] = {}
        self.tab_widgets: List[ttk.Widget] = []
        
        # Configurar el estilo
        self.style = ttk.Style()
        self._setup_styles()
        
        # Crear estructura base del formulario
        self._create_form()
        
        # Crear las secciones y campos
        self._setup_form_fields()

        # Configurar eventos de tabulación
        self._setup_tab_navigation()

    def _setup_styles(self):
        """Configura los estilos del formulario."""
        self.style.configure("Section.TLabelframe", padding=(10, 5))
        self.style.configure("Section.TLabelframe.Label", font=("Helvetica", 11, "bold"))
        self.style.configure("FileButton.TButton", padding=5)
        self.style.configure("Primary.TButton", padding=5)
        self.style.configure("Secondary.TButton", padding=5)

    def _setup_form_fields(self):
        """Configura los campos del formulario."""
        # Datos personales
        self.add_section("Datos Personales")
        self.add_field("name", "Nombre", required=True)
        self.add_field("identification", "Documento de Identidad", required=True)
        self.add_field("id_file_path", "Archivo de Identidad", field_type="file", required=False)
        self.add_field("email", "Correo Electrónico", required=True)
        self.add_field("phone", "Teléfono", required=True)
        self.add_field("profession", "Profesión", required=False)

        # Datos del apartamento
        self.add_section("Datos del Apartamento")
        self.add_field("apartment", "Apartamento", required=True)
        self.add_field("rent", "Renta Mensual", required=True)
        self.add_field("deposit", "Depósito", required=True)
        self.add_field("entry_date", "Fecha de Ingreso", field_type="date", required=True)
        self.add_field("status", "Estado", field_type="combobox", values=["Activo", "Pendiente", "Moroso", "Suspendido"], required=True)
        self.add_field("contract_file_path", "Contrato", field_type="file", required=False)

        # Contacto de emergencia
        self.add_section("Contacto de Emergencia")
        self.add_field("emergency_contact_name", "Nombre del Contacto")
        self.add_field("emergency_contact_phone", "Teléfono")
        self.add_field("emergency_contact_relation", "Relación")

        # Notas adicionales
        self.add_section("Notas Adicionales")
        self.add_field("notes", "Notas", field_type="text", required=False)

    def _setup_tab_navigation(self):
        """Configura la navegación por tabulación."""
        # Agregar los botones al final de la lista de tabulación
        self.tab_widgets.append(self.submit_button)
        self.tab_widgets.append(self.cancel_button)

        # Configurar el evento de tabulación para los botones
        self.submit_button.bind("<Tab>", self._next_widget)
        self.cancel_button.bind("<Tab>", self._next_widget)

    def _create_form(self):
        """Crea la estructura base del formulario."""
        # Frame principal
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True)

        # Frame para el contenido con scroll
        self.content_frame = ttk.Frame(main_container)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Canvas y scrollbar
        self.canvas = ttk.Canvas(self.content_frame)
        self.scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.canvas.yview)
        
        # Frame scrollable para el contenido del formulario
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Crear ventana en el canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Configurar el scroll con el mouse
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Empaquetar canvas y scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Frame para los botones
        button_container = ttk.Frame(main_container)
        button_container.pack(fill="x", side="bottom", pady=10)

        # Separador
        separator = ttk.Separator(button_container, orient="horizontal")
        separator.pack(fill="x", pady=(0, 10))

        # Frame para los botones (alineados a la derecha)
        self.button_frame = ttk.Frame(button_container)
        self.button_frame.pack(side="right", padx=20)

        # Botones
        self.cancel_button = ttk.Button(
            self.button_frame,
            text="Cancelar",
            command=self._handle_cancel,
            style="Secondary.TButton",
            width=12
        )
        self.submit_button = ttk.Button(
            self.button_frame,
            text="Guardar",
            command=self._handle_submit,
            style="Primary.TButton",
            width=12
        )

        self.cancel_button.pack(side="right", padx=(5, 0))
        self.submit_button.pack(side="right")

    def add_section(self, title: str):
        """Agrega una nueva sección al formulario."""
        # Limpiar la sección actual si existe
        self.current_section = None
        
        # Frame para la sección
        section_frame = ttk.LabelFrame(
            self.scrollable_frame,
            text=title,
            style="Section.TLabelframe"
        )
        section_frame.pack(fill="x", padx=5, pady=5)

        # Crear contenedor para las columnas
        columns_frame = ttk.Frame(section_frame)
        columns_frame.pack(fill="x", padx=5, pady=5)
        
        # Configurar el grid para dos columnas de igual ancho
        columns_frame.grid_columnconfigure(0, weight=1, uniform="column")
        columns_frame.grid_columnconfigure(1, weight=1, uniform="column")

        # Crear columnas
        left_column = ttk.Frame(columns_frame)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        right_column = ttk.Frame(columns_frame)
        right_column.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # Guardar referencia a la sección actual
        self.current_section = {
            "frame": section_frame,
            "left_column": left_column,
            "right_column": right_column,
            "column_count": 0
        }
        
        self.sections.append(self.current_section)

    def add_field(
        self,
        name: str,
        label: str,
        field_type: str = "text",
        required: bool = False,
        values: Optional[List[str]] = None,
        file_types: Optional[List[tuple]] = None
    ):
        """Agrega un campo al formulario."""
        if not self.current_section:
            self.add_section("General")

        # Determinar en qué columna va el campo
        parent = (self.current_section["left_column"] 
                 if self.current_section["column_count"] % 2 == 0 
                 else self.current_section["right_column"])
        
        # Contenedor del campo
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, pady=1)
        container.grid_columnconfigure(0, weight=1)

        # Etiqueta del campo
        label_text = f"{label}{'*' if required else ''}"
        label_widget = ttk.Label(container, text=label_text)
        label_widget.pack(anchor=tk.W, padx=5)

        if field_type == "file":
            widget = self._create_file_field(container, name, label, file_types)
            # Agregar el entry y el botón a la lista de tabulación
            self.tab_widgets.append(widget["entry"])
            self.tab_widgets.append(widget["button"])
        elif field_type == "text":
            widget = ttk.Entry(container, width=40)
            widget.pack(fill=tk.X, padx=5)
            self.tab_widgets.append(widget)
        elif field_type == "date":
            widget = ttk.DateEntry(container, width=20)
            widget.pack(anchor=tk.W, padx=5)
            self.tab_widgets.append(widget)
        elif field_type == "combobox":
            widget = ttk.Combobox(
                container,
                values=values or [],
                state="readonly",
                width=40
            )
            widget.pack(fill=tk.X, padx=5)
            self.tab_widgets.append(widget)
        else:
            widget = ttk.Entry(container, width=40)
            widget.pack(fill=tk.X, padx=5)
            self.tab_widgets.append(widget)

        # Incrementar el contador de columnas
        self.current_section["column_count"] += 1

        # Guardar referencia al campo
        self.fields[name] = {
            "widget": widget,
            "type": field_type,
            "required": required
        }

        # Configurar el orden de tabulación para este widget
        if isinstance(widget, dict):  # Para campos de archivo
            widget["entry"].bind("<Tab>", self._next_widget)
            widget["button"].bind("<Tab>", self._next_widget)
        else:
            widget.bind("<Tab>", self._next_widget)

    def _create_file_field(self, container, name, label, file_types):
        """Crea un campo de tipo archivo."""
        file_container = ttk.Frame(container)
        file_container.pack(fill=tk.X, padx=5)
        file_container.grid_columnconfigure(0, weight=1)
        
        entry = ttk.Entry(file_container, width=30)
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.tab_widgets.append(entry)
        
        def select_file():
            file_path = filedialog.askopenfilename(
                title=f"Seleccionar {label}",
                filetypes=file_types or [("Todos los archivos", "*.*")]
            )
            if file_path:
                self.file_paths[name] = file_path
                entry.delete(0, tk.END)
                entry.insert(0, os.path.basename(file_path))
        
        btn = ttk.Button(
            file_container,
            text="Examinar",
            command=select_file,
            style="FileButton.TButton",
            width=10
        )
        btn.grid(row=0, column=1)
        self.tab_widgets.append(btn)
        
        return {"entry": entry, "button": btn}

    def set_data(self, data: Dict[str, Any]):
        """Establece los valores de los campos."""
        for name, value in data.items():
            if name in self.fields:
                field = self.fields[name]
                widget = field["widget"]
                
                if field["type"] == "file":
                    if value:
                        widget["entry"].delete(0, tk.END)
                        widget["entry"].insert(0, os.path.basename(value))
                        self.file_paths[name] = value
                elif field["type"] == "text":
                    widget.delete(0, tk.END)
                    widget.insert(0, str(value or ""))
                elif field["type"] == "date":
                    if isinstance(value, (date, datetime)):
                        widget.set_date(value)
                    elif isinstance(value, str):
                        try:
                            widget.set_date(datetime.strptime(value, "%Y-%m-%d").date())
                        except ValueError:
                            pass
                elif field["type"] == "combobox":
                    if value in widget["values"]:
                        widget.set(value)
                else:
                    widget.delete(0, tk.END)
                    widget.insert(0, str(value or ""))

    def get_data(self) -> Dict[str, Any]:
        """Obtiene los datos del formulario."""
        data = {}
        for field_name, field in self.fields.items():
            widget = field["widget"]
            value = None
            
            # Obtener el valor según el tipo de widget
            if field["type"] == "file":
                value = self.file_paths.get(field_name, "")
            elif field["type"] == "date":
                # Para DateEntry, obtener la fecha directamente
                try:
                    if hasattr(widget, 'entry'):
                        value = widget.entry.get().strip()
                    else:
                        value = widget.get().strip()
                except:
                    value = ""
            else:
                value = widget.get().strip() if hasattr(widget, 'get') else None
            
            # Validar campos requeridos
            if field["required"] and not value:
                raise ValueError(f"El campo {field_name} es requerido")
            
            # Guardar el valor
            data[field_name] = value
            
        return data

    def _handle_submit(self):
        """Maneja el envío del formulario."""
        if self.on_submit:
            try:
                data = self.get_data()
                self.on_submit(data)
            except ValueError as e:
                tk.messagebox.showerror("Error", str(e))

    def _handle_cancel(self):
        """Maneja la cancelación del formulario."""
        if self.on_cancel:
            self.on_cancel()

    def destroy(self):
        """Limpia los recursos al destruir el widget."""
        self.canvas.unbind_all("<MouseWheel>")
        super().destroy()

    def _next_widget(self, event):
        """Maneja el evento de tabulación para mover al siguiente widget."""
        current = event.widget
        try:
            idx = self.tab_widgets.index(current)
            next_idx = (idx + 1) % len(self.tab_widgets)
            next_widget = self.tab_widgets[next_idx]
            next_widget.focus_set()
            
            # Si es un combobox, asegurarse de que se pueda interactuar con él
            if isinstance(next_widget, ttk.Combobox):
                next_widget.selection_clear()
                next_widget.selection_range(0, tk.END)
        except ValueError:
            # Si el widget no está en la lista, ir al primero
            if self.tab_widgets:
                self.tab_widgets[0].focus_set()
        return "break"  # Prevenir el comportamiento predeterminado de Tab 