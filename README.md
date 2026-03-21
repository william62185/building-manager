
## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características Principales](#-características-principales)
- [Arquitectura](#-arquitectura)
- [Tecnologías](#-tecnologías)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Testing](#-testing)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Capturas de Pantalla](#-capturas-de-pantalla)
- [Roadmap](#-roadmap)
- [Contribución](#-contribución)
- [Licencia](#-licencia)

## 🎯 Descripción

**Building Manager Pro** es una aplicación de escritorio profesional diseñada para la gestión integral de edificios residenciales y comerciales. Desarrollada con Python y Tkinter, ofrece una interfaz moderna e intuitiva para administrar inquilinos, pagos, gastos, unidades y generar reportes detallados.

### Problema que Resuelve

La gestión manual de edificios mediante hojas de cálculo y documentos dispersos es propensa a errores, consume tiempo y dificulta el seguimiento de pagos, gastos y documentación. Building Manager Pro centraliza toda la información en una aplicación de escritorio segura y fácil de usar.

### Valor Agregado

- ✅ **Sin dependencias de internet**: Funciona completamente offline
- ✅ **Datos locales seguros**: Toda la información se almacena localmente con backup encriptado en la nube.
- ✅ **Interfaz intuitiva**: Diseño moderno con temas claro/oscuro
- ✅ **Gestión documental**: Organización automática de documentos por inquilino
- ✅ **Reportes exportables**: CSV, TXT y Excel para análisis externo
- ✅ **Backups automáticos**: Protección de datos integrada

## ✨ Características Principales

### 👥 Gestión de Inquilinos
- Registro completo de inquilinos con datos personales y de contacto
- Búsqueda avanzada con múltiples filtros
- Gestión de documentos (cédula, contrato, recibos, ficha)
- Historial de pagos por inquilino
- Estados de pago automáticos (al día, atrasado, sin pagos)

### 💰 Gestión de Pagos
- Registro de pagos de arriendo
- Múltiples métodos de pago (efectivo, transferencia, cheque)
- Generación automática de recibos en PDF
- Filtros por inquilino, fecha y método
- Cálculo automático de totales

### 📊 Gestión de Gastos
- Categorización de gastos (mantenimiento, servicios, administración)
- Asignación de gastos por apartamento o generales
- Adjuntos de comprobantes
- Reportes de gastos por período y categoría

### 🏗️ Gestión de Unidades
- Administración de apartamentos y locales
- Estados de ocupación
- Asignación de inquilinos a unidades
- Estructura de edificios por pisos

### 📈 Reportes y Análisis
- Dashboard con métricas clave
- Reporte de pagos pendientes
- Análisis de ingresos vs gastos
- Estado de ocupación
- Exportación a múltiples formatos

### 🔐 Administración
- Sistema de usuarios con roles
- Gestión de edificios
- Backups automáticos y manuales
- Configuración de temas
- Historial de actividad

## 🏗️ Arquitectura

Building Manager Pro sigue una arquitectura en capas limpia y mantenible:

```
┌─────────────────────────────────────┐
│         UI Layer (Views)            │
│  - Tkinter Components               │
│  - Modern Widgets                   │
│  - Theme Manager                    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Presentation Layer             │
│  - Presenters (MVP Pattern)         │
│  - View Controllers                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Business Logic Layer          │
│  - Services (CRUD Operations)       │
│  - Domain Logic                     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Data Persistence Layer        │
│  - JSON Storage                     │
│  - File Management                  │
│  - Backup System                    │
└─────────────────────────────────────┘
```

### Patrones de Diseño Implementados

- **MVP (Model-View-Presenter)**: Separación clara entre lógica de presentación y UI
- **Service Layer**: Encapsulación de lógica de negocio
- **Repository Pattern**: Abstracción de persistencia de datos
- **Singleton**: Servicios globales (tenant_service, payment_service, etc.)
- **Factory**: Creación de componentes UI estandarizados

## 🛠️ Tecnologías

### Core
- **Python 3.13**: Lenguaje principal
- **Tkinter**: Framework de interfaz gráfica
- **JSON**: Persistencia de datos

### Testing
- **Pytest**: Framework de testing
- **pytest-cov**: Cobertura de código
- **pytest-mock**: Mocking para tests

### Librerías Adicionales
- **Pillow**: Procesamiento de imágenes
- **python-dateutil**: Manejo avanzado de fechas
- **ReportLab**: Generación de PDFs
- **openpyxl**: Exportación a Excel

### Herramientas de Desarrollo
- **PyInstaller**: Empaquetado de ejecutables
- **Inno Setup**: Creador de instaladores
- **Git**: Control de versiones

## 📦 Instalación

### Requisitos Previos

- Python 3.13 o superior
- pip (gestor de paquetes de Python)
- Windows 10/11 (recomendado)

### Instalación para Desarrollo

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/building-manager-pro.git
cd building-manager-pro
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
```

3. **Activar entorno virtual**
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Ejecutar la aplicación**
```bash
python run.py
```

### Instalación para Usuarios Finales

1. Descargar el instalador desde [Releases](https://github.com/tu-usuario/building-manager-pro/releases)
2. Ejecutar `BuildingManagerPro_Setup.exe`
3. Seguir el asistente de instalación
4. Lanzar desde el menú de inicio o acceso directo

## 🚀 Uso

### Primer Inicio

1. Al iniciar por primera vez, se solicitará crear un usuario administrador
2. Completar el formulario con los datos del administrador
3. Iniciar sesión con las credenciales creadas

### Flujo de Trabajo Típico

1. **Configurar Edificio**
   - Ir a Administración → Gestión de Edificios
   - Crear la estructura del edificio (pisos y unidades)
   - Actualizar los detalles de cada apartamento creado (# de habitaciones, # de baños, canon de renta base, area, etc)

2. **Registrar Inquilinos**
   - Ir a Inquilinos → Nuevo Inquilino
   - Completar datos personales y de contacto
   - Asignar unidad y valor de arriendo
   - Adjuntar documentos (cédula, contrato)

3. **Registrar Pagos**
   - Ir a Pagos → Registrar Nuevo Pago
   - Seleccionar inquilino
   - Ingresar monto, fecha y método de pago
   - El sistema genera automáticamente el recibo

4. **Registrar Gastos**
   - Ir a Gastos → Registrar Gasto
   - Seleccionar categoría y tipo
   - Ingresar monto y fecha
   - Adjuntar comprobante (opcional)

5. **Generar Reportes**
   - Ir a Reportes
   - Seleccionar tipo de reporte
   - Aplicar filtros según necesidad
   - Exportar a CSV, TXT o Excel

## 🧪 Testing

El proyecto incluye una suite completa de tests unitarios y de integración.

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests con cobertura
pytest --cov=manager/app --cov-report=html

# Tests específicos
pytest manager/tests/test_services/test_tenant_service.py

# Tests con verbose
pytest -v
```

### Cobertura Actual

```
Service                Coverage
─────────────────────  ────────
expense_service.py     69%
payment_service.py     71%
tenant_service.py      56%
─────────────────────  ────────
Total                  22%
```

### Resultados de Tests

```
================================= test session starts =================================
collected 30 items

manager/tests/test_services/test_expense_service.py::TestExpenseService ✓✓✓✓✓✓✓✓✓✓✓✓
manager/tests/test_services/test_payment_service.py::TestPaymentService ✓✓✓✓✓✓✓✓
manager/tests/test_services/test_tenant_service.py::TestTenantService ✓✓✓✓✓✓✓✓✓✓

================================= 30 passed in 2.28s ==================================
```

## 📁 Estructura del Proyecto

```
building-manager-pro/
├── manager/                    # Paquete principal
│   ├── app/                   # Código de la aplicación
│   │   ├── main.py           # Punto de entrada
│   │   ├── paths_config.py   # Configuración de rutas
│   │   ├── logger.py         # Sistema de logging
│   │   ├── persistence.py    # Persistencia atómica
│   │   ├── services/         # Capa de servicios
│   │   │   ├── tenant_service.py
│   │   │   ├── payment_service.py
│   │   │   ├── expense_service.py
│   │   │   ├── apartment_service.py
│   │   │   ├── building_service.py
│   │   │   ├── user_service.py
│   │   │   ├── backup_service.py
│   │   │   └── ...
│   │   ├── presenters/       # Lógica de presentación
│   │   │   ├── tenant_presenter.py
│   │   │   ├── payment_presenter.py
│   │   │   ├── dashboard_presenter.py
│   │   │   └── ...
│   │   └── ui/               # Interfaz de usuario
│   │       ├── components/   # Componentes reutilizables
│   │       │   ├── theme_manager.py
│   │       │   ├── modern_widgets.py
│   │       │   ├── button_templates.py
│   │       │   └── ...
│   │       └── views/        # Vistas/Pantallas
│   │           ├── main_window.py
│   │           ├── login_view.py
│   │           ├── tenants_view.py
│   │           ├── payments_view.py
│   │           └── ...
│   ├── data/                 # Datos de la aplicación
│   │   ├── tenants.json
│   │   ├── payments.json
│   │   ├── gastos.json
│   │   └── ...
│   └── tests/                # Suite de tests
│       ├── conftest.py
│       ├── test_services/
│       └── ...
├── assets/                   # Recursos (iconos, imágenes)
├── installer/                # Scripts de instalador
├── docs/                     # Documentación
│   ├── ARCHITECTURE.md
│   └── AUDIT_V1_0.md
├── run.py                    # Lanzador de la aplicación
├── pytest.ini                # Configuración de pytest
├── requirements.txt          # Dependencias
└── README.md                 # Este archivo
```

## 📸 Capturas de Pantalla

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)
*Vista principal con métricas clave y accesos rápidos*

### Gestión de Inquilinos
![Inquilinos](docs/screenshots/tenants.png)
*Lista de inquilinos con búsqueda avanzada*

### Registro de Pagos
![Pagos](docs/screenshots/payments.png)
*Formulario de registro de pagos con generación de recibos*

### Reportes
![Reportes](docs/screenshots/reports.png)
*Sistema de reportes con múltiples filtros y exportación*

## 🗺️ Roadmap

### Versión 1.1 (Q2 2026)
- [ ] Notificaciones automáticas de pagos pendientes
- [ ] Integración con servicios de email
- [ ] Reportes avanzados con gráficos
- [ ] Modo multi-edificio

### Versión 1.2 (Q3 2026)
- [ ] API REST para integraciones
- [ ] Aplicación móvil complementaria
- [ ] Portal web para inquilinos
- [ ] Pagos en línea

### Versión 2.0 (Q4 2026)
- [ ] Migración a base de datos SQL
- [ ] Arquitectura multi-tenant
- [ ] Módulo de contabilidad avanzada
- [ ] Inteligencia artificial para predicciones

## 🤝 Contribución

Este es un proyecto propietario. Para consultas sobre colaboración o licenciamiento, contactar a:

**Email**: [william62185@gmail.com](mailto:william62185@gmail.com)

## 📄 Licencia

Copyright © 2026 [William Muñoz]. Todos los derechos reservados.

Este software es propietario y confidencial. No está permitida su distribución, modificación o uso sin autorización expresa del autor.

---

## 👨‍💻 Autor

**[William Muñoz]**
- GitHub: [@william62185](https://github.com/william62185)
- LinkedIn: [William Muñoz](https://linkedin.com/in/william62185)
- Email: william62185@gmail.com

---

## 🙏 Agradecimientos

- A la comunidad de Python por las excelentes herramientas
- A los usuarios beta por su feedback valioso

---

<p align="center">
  Hecho con ❤️ y Python
</p>
