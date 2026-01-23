#!/usr/bin/env python3
"""
Building Manager Pro - Punto de entrada principal
"""

from manager.app.ui.views.main_window import MainWindow

def main():
    """Función principal que inicia la aplicación"""
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()

