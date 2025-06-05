#!/usr/bin/env python3
"""
Building Manager - Sistema de Administración de Edificios
Aplicación principal de entrada
"""

import sys
import os

# Agregar el directorio app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.main import main

if __name__ == "__main__":
    main() 