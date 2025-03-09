#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from ui.main_window import MainWindow
from database.session import Session
from pathlib import Path

def main():
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Email Client")
    app.setOrganizationName("Hood OS")
    app.setOrganizationDomain("hoodos.org")
    
    # Load settings
    settings = QSettings()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
