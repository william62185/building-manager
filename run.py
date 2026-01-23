#!/usr/bin/env python3
"""
Building Manager Pro - Lanzador principal
Sistema profesional de gestión de edificios
"""

import sys
from pathlib import Path

# Agregar el directorio manager al path
sys.path.insert(0, str(Path(__file__).parent / "manager"))

from manager.app.main import main

if __name__ == "__main__":
    main() 