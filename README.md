# Building Manager Pro

Aplicación de escritorio para la gestión integral de edificios y arrendamientos, desarrollada en Python + Tkinter.

Incluye gestión de inquilinos, pagos, gastos, unidades (apartamentos/locales), reportes, configuración y backups, con persistencia en JSON y documentos locales.

---

## Demo del proyecto

> Recomendado: agrega aquí capturas/GIFs de las pantallas principales.

- Dashboard con métricas operativas
  <img width="1365" height="723" alt="image" src="https://github.com/user-attachments/assets/667409ef-c03c-407d-adfc-6cb826186eaf" />

- Gestión de inquilinos (activos/inactivos)
  <img width="1365" height="722" alt="image" src="https://github.com/user-attachments/assets/d8d55974-8fb6-4c6a-9acf-f9a61831a8b8" />

- Registro y edición de pagos/gastos
  <img width="1365" height="717" alt="image" src="https://github.com/user-attachments/assets/565abb5b-3340-4f8d-a6bb-2a2c8822ca79" />
  <img width="1365" height="719" alt="image" src="https://github.com/user-attachments/assets/9163bb4c-ba39-46a5-9f62-50b6693b11ca" />
  <img width="1365" height="721" alt="image" src="https://github.com/user-attachments/assets/6a656296-aa70-4b91-af6c-8669dfe2b415" />

- Módulo de administración (usuarios, backup, unidades, edificio)
  <img width="1365" height="719" alt="image" src="https://github.com/user-attachments/assets/e75c365d-3a51-40bf-93ef-f39e5aed7462" />

- Modulo de Contabilidad
  <img width="1365" height="720" alt="image" src="https://github.com/user-attachments/assets/c3a25dfd-ab40-42d6-9c52-f4be012d3303" />

- Reportes exportables (CSV/TXT)
  <img width="1365" height="720" alt="image" src="https://github.com/user-attachments/assets/4df38d44-9eb1-47d0-a05d-6cc961cc9740" />

- Modulo de configuraciones
  <img width="1365" height="767" alt="image" src="https://github.com/user-attachments/assets/969de99d-c2f6-453a-968a-130cd7efd450" />
 
---

## Stack tecnológico

- **Lenguaje:** Python 3
- **UI:** Tkinter / ttk
- **Persistencia:** JSON (sin base de datos relacional)
- **Empaquetado:** PyInstaller
- **Instalador Windows:** Inno Setup

---

## Arquitectura

El proyecto sigue una organización por capas dentro de `manager/app/`:

- `ui/views/` → pantallas y flujos
- `ui/components/` → componentes reutilizables (theme, widgets, iconos)
- `services/` → lógica de negocio + persistencia JSON
- `presenters/` → lógica de presentación (MVP, en expansión)
- `paths_config.py` → rutas centralizadas y portables
- `main.py` / `app_controller.py` → arranque y navegación

Documentación técnica completa en:
- `ARCHITECTURE.md`
- `AUDIT_V1_0.md`

---

## Estructura principal

```text
building_manager_cursor/
├── run.py
├── build_installer.py
├── installer/
│   └── BuildingManagerPro.iss
├── manager/
│   ├── app/
│   │   ├── main.py
│   │   ├── app_controller.py
│   │   ├── paths_config.py
│   │   ├── services/
│   │   ├── presenters/
│   │   └── ui/
│   │       ├── components/
│   │       └── views/
│   └── data/
└── assets/


ok, primero creame el archivo readme aqui en la raiz del proyecto

Perfecto. En este momento estoy en modo solo lectura, así que no puedo escribir archivos directamente en tu workspace.

Si quieres, te lo dejo listo para copiar/pegar ahora mismo como README.md en la raíz (C:\Users\Will\building_manager_cursor\README.md).
Aquí va:

# Building Manager Pro
Aplicación de escritorio para la gestión integral de edificios y arrendamientos, desarrollada en Python + Tkinter.
Incluye gestión de inquilinos, pagos, gastos, unidades (apartamentos/locales), reportes, configuración y backups, con persistencia en JSON y documentos locales.
---
## Demo del proyecto
> Recomendado: agrega aquí capturas/GIFs de las pantallas principales.
- Dashboard con métricas operativas
- Gestión de inquilinos (activos/inactivos)
- Registro y edición de pagos/gastos
- Módulo de administración (usuarios, backup, unidades, edificio)
- Reportes exportables (CSV/TXT)
---
## Stack tecnológico
- **Lenguaje:** Python 3
- **UI:** Tkinter / ttk
- **Persistencia:** JSON (sin base de datos relacional)
- **Empaquetado:** PyInstaller
- **Instalador Windows:** Inno Setup
---
## Arquitectura
El proyecto sigue una organización por capas dentro de `manager/app/`:
- `ui/views/` → pantallas y flujos
- `ui/components/` → componentes reutilizables (theme, widgets, iconos)
- `services/` → lógica de negocio + persistencia JSON
- `presenters/` → lógica de presentación (MVP, en expansión)
- `paths_config.py` → rutas centralizadas y portables
- `main.py` / `app_controller.py` → arranque y navegación
Documentación técnica completa en:
- `ARCHITECTURE.md`
- `AUDIT_V1_0.md`
---
## Estructura principal
```text
building_manager_cursor/
├── run.py
├── build_installer.py
├── installer/
│   └── BuildingManagerPro.iss
├── manager/
│   ├── app/
│   │   ├── main.py
│   │   ├── app_controller.py
│   │   ├── paths_config.py
│   │   ├── services/
│   │   ├── presenters/
│   │   └── ui/
│   │       ├── components/
│   │       └── views/
│   └── data/
└── assets/

Funcionalidades destacadas:
* CRUD completo de inquilinos
* Registro y control de pagos
* Registro y clasificación de gastos
* Gestión de apartamentos/locales y estado de ocupación
* Reportes exportables (CSV/TXT)
*  Backups y restauración de datos
* Gestión de usuarios y configuración
* Sistema de temas (light/dark) y UI modular

Ejecución en desarrollo
1) Requisitos
Python 3.10+ (recomendado)
pip

2) Instalar dependencias
pip install -r requirements.txt

3) Ejecutar
python run.py
Generar ejecutable e instalador (Windows)
Ejecutable (PyInstaller)
python build_installer.py
Instalador (Inno Setup)
Si tienes Inno Setup instalado, el mismo build_installer.py lo compila. También puedes ejecutar manualmente:

"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\BuildingManagerPro.iss
Salida esperada:

dist/Building Manager Pro/ (app empaquetada)
dist/BuildingManagerPro_Setup_1.0.2.exe (instalador)
Persistencia de datos
En desarrollo: se usan archivos JSON y carpetas locales del proyecto.
En ejecutable/instalado: los datos se guardan en %APPDATA%\Building Manager Pro para evitar problemas de permisos.
Carpetas típicas de datos:

data/
backups/
gastos_docs/
exports/
data/documentos_inquilinos/

* Calidad técnica / mejoras aplicadas

Estandarización visual de botones y componentes
Ajustes de UX en navegación entre módulos
Mejoras de compactación y layout en vistas complejas
Mejoras en scroll y comportamiento de listados
Validaciones de formularios y robustez en flujos críticos
Auditoría técnica base en AUDIT_V1_0.md
Roadmap (próximos pasos sugeridos)
Tests automatizados (unitarios e integración de servicios)
Pipeline CI para lint + tests + build
Hardening de .gitignore para artefactos de ejecución
Métricas de rendimiento y observabilidad
Mejoras de seguridad para gestión de credenciales

Autor
William Muñoz
Proyecto desarrollado como solución real de gestión inmobiliaria y como portfolio técnico profesional.

Si quieres colaborar o ver más detalles técnicos, revisa ARCHITECTURE.md y PROJECT_MANIFEST.md.


