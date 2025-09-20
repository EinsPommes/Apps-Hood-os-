#!/usr/bin/env python3
"""
Hood OS System Settings
A comprehensive system configuration manager for Hood OS with modules for
appearance, network, hardware, security, and system preferences.
"""
import sys
import os
import json
import subprocess
import platform
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTreeWidget, QTreeWidgetItem, QStackedWidget,
                             QPushButton, QLabel, QGroupBox, QGridLayout, QComboBox,
                             QCheckBox, QSlider, QLineEdit, QSpinBox, QTabWidget,
                             QListWidget, QListWidgetItem, QMessageBox, QFileDialog,
                             QProgressBar, QTextEdit, QScrollArea, QFrame, QSplitter)
from PySide6.QtCore import (Qt, QTimer, QThread, pyqtSignal, QSettings, QSize,
                          QStandardPaths, QProcess)
from PySide6.QtGui import QIcon, QFont, QPalette, QColor, QPixmap, QAction

class SystemInfoWorker(QThread):
    """Worker thread for gathering system information"""
    info_ready = pyqtSignal(dict)
    
    def run(self):
        """Collect system information"""
        info = {
            'os': platform.system(),
            'os_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'hostname': platform.node(),
            'python_version': platform.python_version(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_info(),
            'network': self.get_network_info()
        }
        self.info_ready.emit(info)
    
    def get_memory_info(self):
        """Get memory information"""
        try:
            if platform.system() == "Linux":
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                total = int([line for line in meminfo.split('\n') if 'MemTotal' in line][0].split()[1]) * 1024
                available = int([line for line in meminfo.split('\n') if 'MemAvailable' in line][0].split()[1]) * 1024
                return {'total': total, 'available': available}
        except:
            pass
        return {'total': 0, 'available': 0}
    
    def get_disk_info(self):
        """Get disk usage information"""
        try:
            result = subprocess.run(['df', '-h'], capture_output=True, text=True)
            return result.stdout
        except:
            return "Disk information unavailable"
    
    def get_network_info(self):
        """Get network interface information"""
        try:
            result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
            return result.stdout
        except:
            return "Network information unavailable"

class AppearanceSettings(QWidget):
    """Appearance and theme settings"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the appearance settings UI"""
        layout = QVBoxLayout(self)
        
        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QGridLayout()
        
        theme_layout.addWidget(QLabel("Color Scheme:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "Auto"])
        theme_layout.addWidget(self.theme_combo, 0, 1)
        
        theme_layout.addWidget(QLabel("Accent Color:"), 1, 0)
        self.accent_color_btn = QPushButton("Choose Color")
        self.accent_color_btn.clicked.connect(self.choose_accent_color)
        theme_layout.addWidget(self.accent_color_btn, 1, 1)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Font settings
        font_group = QGroupBox("Fonts")
        font_layout = QGridLayout()
        
        font_layout.addWidget(QLabel("System Font:"), 0, 0)
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Default", "Ubuntu", "Roboto", "Open Sans", "Liberation Sans"])
        font_layout.addWidget(self.font_combo, 0, 1)
        
        font_layout.addWidget(QLabel("Font Size:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        font_layout.addWidget(self.font_size_spin, 1, 1)
        
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)
        
        # Desktop settings
        desktop_group = QGroupBox("Desktop")
        desktop_layout = QGridLayout()
        
        desktop_layout.addWidget(QLabel("Wallpaper:"), 0, 0)
        self.wallpaper_btn = QPushButton("Choose Wallpaper")
        self.wallpaper_btn.clicked.connect(self.choose_wallpaper)
        desktop_layout.addWidget(self.wallpaper_btn, 0, 1)
        
        desktop_layout.addWidget(QLabel("Icon Size:"), 1, 0)
        self.icon_size_slider = QSlider(Qt.Horizontal)
        self.icon_size_slider.setRange(16, 128)
        self.icon_size_slider.setValue(48)
        self.icon_size_label = QLabel("48px")
        self.icon_size_slider.valueChanged.connect(
            lambda v: self.icon_size_label.setText(f"{v}px")
        )
        desktop_layout.addWidget(self.icon_size_slider, 1, 1)
        desktop_layout.addWidget(self.icon_size_label, 1, 2)
        
        desktop_group.setLayout(desktop_layout)
        layout.addWidget(desktop_group)
        
        # Apply button
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_btn)
        
        layout.addStretch()
    
    def choose_accent_color(self):
        """Open color picker for accent color"""
        from PySide6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            self.accent_color_btn.setStyleSheet(f"background-color: {color.name()}")
    
    def choose_wallpaper(self):
        """Choose wallpaper image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choose Wallpaper", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.wallpaper_btn.setText(f"Wallpaper: {Path(file_path).name}")
    
    def load_settings(self):
        """Load current settings"""
        settings = QSettings("HoodOS", "SystemSettings")
        self.theme_combo.setCurrentText(settings.value("theme", "Light"))
        self.font_combo.setCurrentText(settings.value("font", "Default"))
        self.font_size_spin.setValue(int(settings.value("font_size", 12)))
        self.icon_size_slider.setValue(int(settings.value("icon_size", 48)))
    
    def apply_settings(self):
        """Apply appearance settings"""
        settings = QSettings("HoodOS", "SystemSettings")
        settings.setValue("theme", self.theme_combo.currentText())
        settings.setValue("font", self.font_combo.currentText())
        settings.setValue("font_size", self.font_size_spin.value())
        settings.setValue("icon_size", self.icon_size_slider.value())
        
        QMessageBox.information(self, "Settings Applied", 
                              "Appearance settings have been applied. Restart applications to see changes.")

class NetworkSettings(QWidget):
    """Network configuration settings"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.load_network_info()
    
    def init_ui(self):
        """Initialize network settings UI"""
        layout = QVBoxLayout(self)
        
        # Network interfaces
        interfaces_group = QGroupBox("Network Interfaces")
        interfaces_layout = QVBoxLayout()
        
        self.interfaces_list = QListWidget()
        interfaces_layout.addWidget(self.interfaces_list)
        
        interfaces_group.setLayout(interfaces_layout)
        layout.addWidget(interfaces_group)
        
        # Connection settings
        connection_group = QGroupBox("Connection Settings")
        connection_layout = QGridLayout()
        
        connection_layout.addWidget(QLabel("Default Gateway:"), 0, 0)
        self.gateway_edit = QLineEdit()
        connection_layout.addWidget(self.gateway_edit, 0, 1)
        
        connection_layout.addWidget(QLabel("DNS Servers:"), 1, 0)
        self.dns_edit = QLineEdit()
        self.dns_edit.setPlaceholderText("8.8.8.8, 8.8.4.4")
        connection_layout.addWidget(self.dns_edit, 1, 1)
        
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)
        
        # Firewall settings
        firewall_group = QGroupBox("Firewall")
        firewall_layout = QVBoxLayout()
        
        self.firewall_enabled = QCheckBox("Enable Firewall")
        firewall_layout.addWidget(self.firewall_enabled)
        
        self.ssh_enabled = QCheckBox("Allow SSH (Port 22)")
        firewall_layout.addWidget(self.ssh_enabled)
        
        self.http_enabled = QCheckBox("Allow HTTP (Port 80)")
        firewall_layout.addWidget(self.http_enabled)
        
        firewall_group.setLayout(firewall_layout)
        layout.addWidget(firewall_group)
        
        # Apply button
        self.apply_btn = QPushButton("Apply Network Settings")
        self.apply_btn.clicked.connect(self.apply_network_settings)
        layout.addWidget(self.apply_btn)
        
        layout.addStretch()
    
    def load_network_info(self):
        """Load network interface information"""
        try:
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            interfaces = []
            for line in result.stdout.split('\n'):
                if ': ' in line and not line.startswith(' '):
                    interface = line.split(':')[1].strip()
                    if not interface.startswith('lo'):
                        interfaces.append(interface)
            
            for interface in interfaces:
                item = QListWidgetItem(interface)
                self.interfaces_list.addItem(item)
        except:
            self.interfaces_list.addItem("Network information unavailable")
    
    def apply_network_settings(self):
        """Apply network configuration"""
        QMessageBox.information(self, "Network Settings", 
                              "Network settings have been applied. Some changes may require a restart.")

class SystemInfoWidget(QWidget):
    """System information display"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.load_system_info()
    
    def init_ui(self):
        """Initialize system info UI"""
        layout = QVBoxLayout(self)
        
        # System overview
        overview_group = QGroupBox("System Overview")
        overview_layout = QGridLayout()
        
        self.os_label = QLabel("Operating System:")
        self.os_value = QLabel("Loading...")
        overview_layout.addWidget(self.os_label, 0, 0)
        overview_layout.addWidget(self.os_value, 0, 1)
        
        self.arch_label = QLabel("Architecture:")
        self.arch_value = QLabel("Loading...")
        overview_layout.addWidget(self.arch_label, 1, 0)
        overview_layout.addWidget(self.arch_value, 1, 1)
        
        self.hostname_label = QLabel("Hostname:")
        self.hostname_value = QLabel("Loading...")
        overview_layout.addWidget(self.hostname_label, 2, 0)
        overview_layout.addWidget(self.hostname_value, 2, 1)
        
        overview_group.setLayout(overview_layout)
        layout.addWidget(overview_group)
        
        # Hardware info
        hardware_group = QGroupBox("Hardware")
        hardware_layout = QGridLayout()
        
        self.processor_label = QLabel("Processor:")
        self.processor_value = QLabel("Loading...")
        hardware_layout.addWidget(self.processor_label, 0, 0)
        hardware_layout.addWidget(self.processor_value, 0, 1)
        
        self.memory_label = QLabel("Memory:")
        self.memory_value = QLabel("Loading...")
        hardware_layout.addWidget(self.memory_label, 1, 0)
        hardware_layout.addWidget(self.memory_value, 1, 1)
        
        hardware_group.setLayout(hardware_layout)
        layout.addWidget(hardware_group)
        
        # Disk usage
        disk_group = QGroupBox("Disk Usage")
        disk_layout = QVBoxLayout()
        
        self.disk_text = QTextEdit()
        self.disk_text.setMaximumHeight(150)
        self.disk_text.setReadOnly(True)
        disk_layout.addWidget(self.disk_text)
        
        disk_group.setLayout(disk_layout)
        layout.addWidget(disk_group)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh Information")
        self.refresh_btn.clicked.connect(self.load_system_info)
        layout.addWidget(self.refresh_btn)
        
        layout.addStretch()
    
    def load_system_info(self):
        """Load and display system information"""
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("Loading...")
        
        self.worker = SystemInfoWorker()
        self.worker.info_ready.connect(self.update_system_info)
        self.worker.start()
    
    def update_system_info(self, info):
        """Update the system information display"""
        self.os_value.setText(f"{info['os']} {info['os_version']}")
        self.arch_value.setText(info['architecture'])
        self.hostname_value.setText(info['hostname'])
        self.processor_value.setText(info['processor'])
        
        # Format memory info
        if info['memory']['total'] > 0:
            total_gb = info['memory']['total'] / (1024**3)
            available_gb = info['memory']['available'] / (1024**3)
            self.memory_value.setText(f"{available_gb:.1f} GB / {total_gb:.1f} GB")
        else:
            self.memory_value.setText("Unavailable")
        
        # Display disk info
        self.disk_text.setText(info['disk'])
        
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("Refresh Information")

class SecuritySettings(QWidget):
    """Security and privacy settings"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
        self.load_security_settings()
    
    def init_ui(self):
        """Initialize security settings UI"""
        layout = QVBoxLayout(self)
        
        # User accounts
        accounts_group = QGroupBox("User Accounts")
        accounts_layout = QVBoxLayout()
        
        self.users_list = QListWidget()
        accounts_layout.addWidget(self.users_list)
        
        accounts_buttons = QHBoxLayout()
        self.add_user_btn = QPushButton("Add User")
        self.remove_user_btn = QPushButton("Remove User")
        self.change_password_btn = QPushButton("Change Password")
        
        accounts_buttons.addWidget(self.add_user_btn)
        accounts_buttons.addWidget(self.remove_user_btn)
        accounts_buttons.addWidget(self.change_password_btn)
        accounts_layout.addLayout(accounts_buttons)
        
        accounts_group.setLayout(accounts_layout)
        layout.addWidget(accounts_group)
        
        # Privacy settings
        privacy_group = QGroupBox("Privacy")
        privacy_layout = QVBoxLayout()
        
        self.telemetry_enabled = QCheckBox("Enable Telemetry")
        self.crash_reports = QCheckBox("Send Crash Reports")
        self.usage_stats = QCheckBox("Send Usage Statistics")
        
        privacy_layout.addWidget(self.telemetry_enabled)
        privacy_layout.addWidget(self.crash_reports)
        privacy_layout.addWidget(self.usage_stats)
        
        privacy_group.setLayout(privacy_layout)
        layout.addWidget(privacy_group)
        
        # Security policies
        security_group = QGroupBox("Security Policies")
        security_layout = QVBoxLayout()
        
        self.auto_updates = QCheckBox("Enable Automatic Updates")
        self.secure_boot = QCheckBox("Enable Secure Boot")
        self.encryption = QCheckBox("Enable Disk Encryption")
        
        security_layout.addWidget(self.auto_updates)
        security_layout.addWidget(self.secure_boot)
        security_layout.addWidget(self.encryption)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        # Apply button
        self.apply_btn = QPushButton("Apply Security Settings")
        self.apply_btn.clicked.connect(self.apply_security_settings)
        layout.addWidget(self.apply_btn)
        
        layout.addStretch()
    
    def load_security_settings(self):
        """Load current security settings"""
        # Load user accounts
        try:
            result = subprocess.run(['cut', '-d:', '-f1', '/etc/passwd'], 
                                  capture_output=True, text=True)
            users = [user.strip() for user in result.stdout.split('\n') if user.strip()]
            for user in users[:10]:  # Show first 10 users
                self.users_list.addItem(user)
        except:
            self.users_list.addItem("User information unavailable")
        
        # Load privacy settings
        settings = QSettings("HoodOS", "SecuritySettings")
        self.telemetry_enabled.setChecked(settings.value("telemetry", False, type=bool))
        self.crash_reports.setChecked(settings.value("crash_reports", False, type=bool))
        self.usage_stats.setChecked(settings.value("usage_stats", False, type=bool))
        self.auto_updates.setChecked(settings.value("auto_updates", True, type=bool))
    
    def apply_security_settings(self):
        """Apply security settings"""
        settings = QSettings("HoodOS", "SecuritySettings")
        settings.setValue("telemetry", self.telemetry_enabled.isChecked())
        settings.setValue("crash_reports", self.crash_reports.isChecked())
        settings.setValue("usage_stats", self.usage_stats.isChecked())
        settings.setValue("auto_updates", self.auto_updates.isChecked())
        
        QMessageBox.information(self, "Security Settings", 
                              "Security settings have been applied.")

class SystemSettingsMainWindow(QMainWindow):
    """Main window for Hood OS System Settings"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hood OS System Settings")
        self.setMinimumSize(800, 600)
        self.setGeometry(100, 100, 1000, 700)
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for sidebar and content
        splitter = QSplitter(Qt.Horizontal)
        
        # Sidebar with categories
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderLabel("Categories")
        self.sidebar.setMaximumWidth(200)
        
        # Add categories
        categories = [
            ("Appearance", "Customize look and feel"),
            ("Network", "Network configuration"),
            ("Security", "Security and privacy"),
            ("System Info", "System information")
        ]
        
        for category, description in categories:
            item = QTreeWidgetItem([category])
            item.setToolTip(0, description)
            self.sidebar.addTopLevelItem(item)
        
        self.sidebar.itemClicked.connect(self.on_category_selected)
        
        # Content area
        self.content_stack = QStackedWidget()
        
        # Add settings widgets
        self.appearance_widget = AppearanceSettings(self)
        self.network_widget = NetworkSettings(self)
        self.security_widget = SecuritySettings(self)
        self.system_info_widget = SystemInfoWidget(self)
        
        self.content_stack.addWidget(self.appearance_widget)
        self.content_stack.addWidget(self.network_widget)
        self.content_stack.addWidget(self.security_widget)
        self.content_stack.addWidget(self.system_info_widget)
        
        # Add to splitter
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.content_stack)
        splitter.setSizes([200, 800])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Hood OS System Settings")
        
        # Select first category by default
        self.sidebar.setCurrentItem(self.sidebar.topLevelItem(0))
        self.content_stack.setCurrentIndex(0)
    
    def on_category_selected(self, item, column):
        """Handle category selection"""
        category = item.text(0)
        category_map = {
            "Appearance": 0,
            "Network": 1,
            "Security": 2,
            "System Info": 3
        }
        
        if category in category_map:
            self.content_stack.setCurrentIndex(category_map[category])
            self.status_bar.showMessage(f"Selected: {category}")
    
    def load_settings(self):
        """Load application settings"""
        settings = QSettings("HoodOS", "SystemSettings")
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
    
    def closeEvent(self, event):
        """Save settings on close"""
        settings = QSettings("HoodOS", "SystemSettings")
        settings.setValue("geometry", self.saveGeometry())
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Hood OS System Settings")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Hood OS")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = SystemSettingsMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
