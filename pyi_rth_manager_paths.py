# -*- coding: utf-8 -*-
# PyInstaller runtime hook: carga paths_config antes de run.py
# Evita "name 'ensure_dirs' is not defined" en la cadena main -> main_window -> ...
import sys
try:
    if getattr(sys, 'frozen', False):
        import manager.app.paths_config as _paths
        if hasattr(_paths, 'ensure_dirs'):
            _paths.ensure_dirs()
except Exception:
    pass
