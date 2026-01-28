# Instalador – Building Manager Pro

## Probar en local (sin instalador)

1. **Generar el ejecutable**
   ```bash
   python build_installer.py
   ```
   O manualmente:
   ```bash
   pip install pyinstaller
   pyinstaller --clean --noconfirm BuildingManagerPro.spec
   ```

2. **Ejecutar**
   - Abre la carpeta `dist/Building Manager Pro/`
   - Ejecuta `Building Manager Pro.exe`
   - Los datos (JSON, PDFs, etc.) se crean en esa misma carpeta (`data/`, `recibos/`, `exports/`, etc.)

## Instalador Windows (Inno Setup)

1. Instala [Inno Setup 6](https://jrsoftware.org/isinfo.php).
2. Ejecuta el build de PyInstaller (paso anterior).
3. Genera el instalador:
   ```bash
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\BuildingManagerPro.iss
   ```
   O ejecuta `python build_installer.py`; si encuentra Inno Setup, creará el instalador en `dist/`.

4. El instalador estará en `dist/BuildingManagerPro_Setup_1.0.exe`.

## Requisitos para construir

- Python 3.10+
- Dependencias del proyecto (`pip install -r requirements.txt`)
- Para el instalador: PyInstaller (`pip install -r requirements-build.txt`) y, opcionalmente, Inno Setup 6
