# Building Manager Pro 🏢

**Sistema profesional de gestión de edificios con diseño moderno y componentes elegantes**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)](https://docs.python.org/3/library/tkinter.html)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Características Profesionales

### ✨ Diseño Moderno
- **Sistema de iconos profesional** con más de 50 iconos elegantes
- **Paleta de colores** basada en design systems modernos
- **Componentes personalizados** (Cards, Buttons, Badges, Metrics)
- **Tipografía consistente** con Segoe UI
- **Efectos hover** y transiciones suaves
- **Layout responsive** y espaciado profesional

### 🎨 Sistema de Temas
- **ThemeManager** centralizado para consistencia visual
- **Paleta de colores** primary, success, warning, error
- **Espaciado** sistemático (XS, SM, MD, LG, XL)
- **Tipografía** escalable (xs, sm, base, lg, xl, 2xl...)
- **Soporte futuro** para tema oscuro

### 🧩 Componentes Profesionales
- **ModernButton** - Botones con iconos y estados
- **ModernCard** - Tarjetas con bordes elegantes
- **ModernEntry** - Campos con placeholders animados
- **ModernMetricCard** - Métricas con tendencias
- **ModernBadge** - Etiquetas de estado
- **ModernProgressBar** - Barras de progreso animadas
- **ModernSeparator** - Divisores elegantes

### 📊 Dashboard Inteligente
- **Métricas en tiempo real** con tendencias
- **Acciones rápidas** para funciones principales
- **Navegación intuitiva** con sidebar profesional
- **Estados visuales** claros y comprensibles

## 🏗️ Arquitectura del Sistema

```
manager/
├── app/
│   ├── main.py                     # Aplicación principal
│   ├── config/
│   │   └── settings.py             # Configuraciones
│   ├── ui/
│   │   ├── components/
│   │   │   ├── icons.py            # Sistema de iconos
│   │   │   ├── theme_manager.py    # Gestor de temas
│   │   │   └── modern_widgets.py   # Componentes modernos
│   │   └── views/
│   │       └── main_window.py      # Ventana principal
│   ├── models/                     # Modelos de datos
│   ├── services/                   # Lógica de negocio
│   └── utils/                      # Utilidades
├── run.py                          # Lanzador principal
├── requirements.txt                # Dependencias
└── README.md                       # Documentación
```

## 🎯 Módulos del Sistema

### 1. **Dashboard** 📈
- Métricas principales del edificio
- Acciones rápidas para gestión
- Resumen de estado general
- Tendencias y análisis

### 2. **Gestión de Inquilinos** 👥
- Registro y edición de inquilinos
- Gestión de contratos de arrendamiento
- Contactos de emergencia
- Historial y documentos

### 3. **Control de Pagos** 💳
- Registro de pagos recibidos
- Seguimiento de pagos pendientes
- Generación de facturas
- Historial de transacciones

### 4. **Gestión de Gastos** 📊
- Registro de gastos operativos
- Categorización por tipo
- Análisis de costos
- Control presupuestario

### 5. **Reportes y Análisis** 📈
- Reportes financieros detallados
- Análisis de ocupación
- Métricas de desempeño
- Exportación de datos

### 6. **Configuración** ⚙️
- Personalización del sistema
- Gestión de usuarios
- Configuración de edificios
- Respaldo de datos

## 🚀 Inicio Rápido

### Prerequisitos
- Python 3.8 o superior
- Sistema operativo: Windows, macOS, Linux

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/william62185/building-manager.git
cd building-manager/manager
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Ejecutar la aplicación**
```bash
python run.py
```

## 🎨 Uso del Sistema de Diseño

### Importar Componentes
```python
from ui.components.modern_widgets import ModernButton, ModernCard
from ui.components.icons import Icons
from ui.components.theme_manager import theme_manager
```

### Crear Botón Profesional
```python
button = ModernButton(
    parent=frame,
    text="Nuevo Inquilino",
    icon=Icons.ADD,
    style="primary",
    command=self.add_tenant
)
```

### Crear Card Elegante
```python
card = ModernCard(
    parent=container,
    title="Métricas del Mes",
    subtitle="Resumen de actividad"
)
```

### Usar Iconos Profesionales
```python
# Iconos disponibles
Icons.TENANTS       # 👥 Inquilinos
Icons.PAYMENTS      # 💳 Pagos
Icons.EXPENSES      # 📊 Gastos
Icons.ADD           # + Agregar
Icons.EDIT          # ✏ Editar
Icons.SUCCESS       # ✓ Éxito
```

## 🎯 Próximas Características

### Funcionalidades Avanzadas
- [ ] **Notificaciones push** para eventos importantes
- [ ] **Modo oscuro** completo
- [ ] **Dashboard personalizable** con widgets
- [ ] **Integración con APIs** de pago
- [ ] **Generación de contratos** automática
- [ ] **Backup automático** en la nube

### Mejoras de UX
- [ ] **Búsqueda global** inteligente
- [ ] **Filtros avanzados** en todas las vistas
- [ ] **Shortcuts de teclado** para acciones rápidas
- [ ] **Drag & drop** para archivos
- [ ] **Vista previa** de documentos
- [ ] **Historial de cambios** con audit trail

### Tecnológicas
- [ ] **Base de datos** PostgreSQL/MySQL
- [ ] **API REST** para integración web
- [ ] **Autenticación** multi-usuario
- [ ] **Roles y permisos** granulares
- [ ] **Logging avanzado** con métricas
- [ ] **Testing automatizado** completo

## 🛠️ Desarrollo

### Estructura del Código
- **Separación clara** entre UI y lógica de negocio
- **Componentes reutilizables** y modulares
- **Gestión centralizada** de temas y estilos
- **Convenciones consistentes** de naming
- **Documentación completa** en español

### Estándares de Calidad
- **Code style** consistente con PEP 8
- **Type hints** para mejor mantenibilidad
- **Error handling** robusto
- **Performance optimizada** para UI fluida
- **Memory management** eficiente

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📞 Soporte

Para soporte y consultas:
- **Issues**: [GitHub Issues](https://github.com/william62185/building-manager/issues)
- **Email**: [william62185@github.com]
- **Documentación**: Ver carpeta `/docs`

---

**Building Manager Pro** - *Sistema profesional de gestión de edificios* 🏢✨ 