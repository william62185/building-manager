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
   - **Datos en ejecutable empaquetado:** Los datos (JSON, PDFs, backups, exports) se crean en **`%APPDATA%\Building Manager Pro`** (p. ej. `C:\Users\<usuario>\AppData\Roaming\Building Manager Pro`), no en la carpeta del .exe. Ahí encontrarás `data/`, `backups/`, `gastos_docs/`, `exports/`, etc.

## Instalador Windows (Inno Setup)

1. Instala [Inno Setup 6](https://jrsoftware.org/isinfo.php).
2. Ejecuta el build de PyInstaller (paso anterior).
3. Genera el instalador:
   ```bash
   "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\BuildingManagerPro.iss
   ```
   O ejecuta `python build_installer.py`; si encuentra Inno Setup, creará el instalador en `dist/`.

4. El instalador estará en `dist/BuildingManagerPro_Setup_1.0.1.exe` (o la versión definida en `installer/BuildingManagerPro.iss`).

5. **Tras instalar:** Los datos de la aplicación (JSON, documentos, backups, exports) se guardan en **`%APPDATA%\Building Manager Pro`**, no en la carpeta de instalación. Así se evitan problemas de permisos (p. ej. en Program Files).

## Icono del programa y del instalador

Para que el acceso directo en el escritorio y el .exe se vean con tu propio icono:

1. Coloca un archivo **`icon.ico`** en la carpeta **`assets/`** (junto a `splash.png`).
2. Si solo tienes una imagen PNG (p. ej. `icon.ico.png`), conviértela a ICO:
   - Herramientas online: [icoconvert.com](https://icoconvert.com), [convertio.co](https://convertio.co/es/png-ico/).
   - Tamaño recomendado: 256×256 px; el .ico puede incluir 16, 32, 48 y 256 px para buena calidad.
3. Vuelve a generar el instalador (`python build_installer.py`). El .exe y el instalador usarán ese icono.

Si no existe `assets/icon.ico`, el build sigue funcionando pero Windows mostrará un icono por defecto.

## Requisitos para construir

- Python 3.10+
- Dependencias del proyecto (`pip install -r requirements.txt`)
- Para el instalador: PyInstaller (`pip install -r requirements-build.txt`) y, opcionalmente, Inno Setup 6
