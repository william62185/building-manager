import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from typing import Any, Callable, Dict, List, Optional, Tuple

class DataTable(ttk.Frame):
    """
    Componente para mostrar datos tabulares con estilo Material Design.
    """
    def __init__(
        self,
        master: Any,
        columns: List[Tuple[str, str, Optional[int]]],  # [(id, display_name, width), ...]
        on_select: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_double_click: Optional[Callable[[Dict[str, Any]], None]] = None,
        height: int = 10
    ):
        super().__init__(master)
        self.columns = columns
        self.on_select = on_select
        self.on_double_click = on_double_click
        self.widgets = []  # Lista para mantener referencia a widgets en la tabla
        
        self._setup_ui(height)
        self._setup_bindings()

    def _setup_ui(self, height: int):
        """Configura la interfaz de la tabla."""
        # Frame para la búsqueda
        self.search_frame = ttk.Frame(self)
        self.search_frame.pack(fill=tk.X, pady=(0, 10))

        # Label para la búsqueda
        search_label = ttk.Label(
            self.search_frame,
            text="Buscar:",
            bootstyle="primary"
        )
        search_label.pack(side=tk.LEFT, padx=(0, 5))

        # Campo de búsqueda
        self.search_entry = ttk.Entry(self.search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Estilo personalizado para la tabla
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            rowheight=40,  # Altura de cada fila
            padding=(5, 5),  # Padding interno de las celdas
            font=("Segoe UI", 10)  # Fuente por defecto
        )
        style.configure(
            "Custom.Treeview.Heading",
            padding=(5, 5),
            font=("Segoe UI", 10, "bold")  # Fuente para encabezados
        )

        # Tabla con el nuevo estilo
        self.tree = ttk.Treeview(
            self,
            columns=[col_id for col_id, _, _ in self.columns],
            show="headings",
            height=height,
            style="Custom.Treeview"
        )

        # Configurar columnas
        for col_id, display_name, width in self.columns:
            self.tree.heading(col_id, text=display_name, style="Custom.Treeview.Heading")
            # Ajustar el ancho de la columna según lo especificado o usar un valor por defecto
            col_width = width if width is not None else 150
            self.tree.column(col_id, width=col_width, minwidth=100, anchor=tk.W)

        # Scrollbars
        y_scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        x_scrollbar = ttk.Scrollbar(
            self,
            orient=tk.HORIZONTAL,
            command=self.tree.xview
        )
        self.tree.configure(
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set
        )

        # Layout
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _setup_bindings(self):
        """Configura los eventos de la tabla."""
        if self.on_select:
            self.tree.bind("<<TreeviewSelect>>", self._handle_select)
        if self.on_double_click:
            self.tree.bind("<Double-1>", self._handle_double_click)
        self.search_entry.bind("<KeyRelease>", self._handle_search)

    def clear(self):
        """Limpia todos los datos de la tabla y destruye widgets asociados."""
        try:
            # Destruir widgets existentes
            for widget in self.widgets:
                if widget.winfo_exists():
                    widget.destroy()
            self.widgets = []
            
            # Limpiar filas
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Limpiar búsqueda
            if hasattr(self, 'search_entry'):
                self.search_entry.delete(0, tk.END)
        except Exception as e:
            print(f"Error al limpiar tabla: {e}")
            # No lanzar el error, solo registrarlo

    def set_data(self, data: List[Dict[str, Any]]):
        """
        Establece los datos de la tabla.
        
        Args:
            data: Lista de diccionarios con los datos a mostrar
        """
        # Limpiar datos y widgets existentes
        self.clear()

        # Insertar nuevos datos
        for row in data:
            values = []
            for col_id, _, _ in self.columns:
                value = row.get(col_id)
                if isinstance(value, tk.Widget):
                    # Si el valor es un widget, usar un placeholder y guardarlo
                    self.widgets.append(value)
                    values.append("")  # Placeholder para el widget
                else:
                    # Para valores normales, convertir a string
                    values.append(str(value if value is not None else ""))
            
            item = self.tree.insert("", tk.END, values=values, tags=(str(row.get("id", "")),))
            
            # Configurar widgets en la tabla si existen
            for i, (col_id, _, _) in enumerate(self.columns):
                value = row.get(col_id)
                if isinstance(value, tk.Widget):
                    self.tree.set(item, col_id, "")  # Limpiar el texto
                    bbox = self.tree.bbox(item, col_id)
                    if bbox:  # Asegurarse de que el item es visible
                        x, y, w, h = bbox
                        value.place(in_=self.tree, x=x+2, y=y+2)

    def get_selected(self) -> Optional[Dict[str, Any]]:
        """Obtiene el elemento seleccionado."""
        selection = self.tree.selection()
        if not selection:
            return None

        item = selection[0]
        values = self.tree.item(item)["values"]
        return dict(zip([col_id for col_id, _, _ in self.columns], values))

    def _handle_select(self, event):
        """Maneja el evento de selección."""
        if self.on_select:
            selected = self.get_selected()
            if selected:
                self.on_select(selected)

    def _handle_double_click(self, event):
        """Maneja el evento de doble clic."""
        if self.on_double_click:
            selected = self.get_selected()
            if selected:
                self.on_double_click(selected)

    def _handle_search(self, event):
        """Maneja el evento de búsqueda."""
        search_term = self.search_entry.get().lower()
        
        for item in self.tree.get_children():
            values = self.tree.item(item)["values"]
            if any(search_term in str(value).lower() for value in values):
                self.tree.reattach(item, "", tk.END)
            else:
                self.tree.detach(item)

    def clear_selection(self):
        """Limpia la selección actual."""
        self.tree.selection_remove(self.tree.selection()) 