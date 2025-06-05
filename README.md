# Building Manager v1.0

Sistema moderno de administración de edificios residenciales desarrollado desde cero con arquitectura limpia.

## 🏗️ Características

- 🏠 **Gestión completa de inquilinos** - Registro, edición, búsqueda
- 💰 **Control de pagos y finanzas** - Seguimiento de pagos y estados
- 📊 **Reportes y estadísticas** - Dashboards con métricas en tiempo real
- 📁 **Manejo de documentos** - Archivos de identificación y contratos
- 🎨 **Interfaz moderna** - Diseño profesional y amigable

## 🔧 Arquitectura

- **MVC Pattern**: Separación clara de responsabilidades
- **Service Layer**: Lógica de negocio centralizada
- **Repository Pattern**: Acceso a datos abstracto
- **Component-Based UI**: Interfaz modular y reutilizable

## 📁 Estructura del Proyecto

```
manager/
├── app/
│   ├── config/          # Configuraciones globales
│   ├── models/          # Modelos de datos (Tenant, Payment, etc.)
│   ├── services/        # Lógica de negocio y acceso a datos
│   ├── ui/              # Interfaz de usuario
│   │   ├── components/  # Componentes reutilizables
│   │   └── views/       # Vistas específicas
│   └── utils/           # Utilidades generales
├── data/                # Base de datos SQLite
├── files/               # Archivos adjuntos
└── requirements.txt     # Dependencias
```

## 🚀 Instalación y Uso

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python run.py
```

## ✨ Funcionalidades Principales

### Gestión de Inquilinos
- Registro completo con validaciones
- Edición de información personal y contractual
- Búsqueda avanzada con filtros
- Gestión de documentos (ID, contratos)

### Control Financiero
- Registro de pagos mensuales
- Estados: Al día, Pendiente, Moroso
- Reportes financieros detallados
- Exportación a Excel y PDF

### Dashboard Ejecutivo
- Métricas en tiempo real
- Gráficos de estado de pagos
- Resumen de ingresos mensuales
- Alertas de inquilinos morosos

## 🛠️ Tecnologías

- **Python 3.8+** - Lenguaje principal
- **Tkinter** - Interfaz gráfica nativa
- **SQLite** - Base de datos embebida
- **ReportLab** - Generación de PDFs
- **OpenPyXL** - Exportación Excel 