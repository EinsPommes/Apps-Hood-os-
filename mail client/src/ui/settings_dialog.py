from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QSpinBox, QCheckBox, QPushButton,
                               QTabWidget, QWidget, QGroupBox, QFormLayout,
                               QComboBox, QMessageBox)
from PyQt6.QtCore import Qt, QSettings

class SettingsDialog(QDialog):
    """Dialog for managing application settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        
        # Load settings
        self.settings = QSettings('HoodOS', 'MailClient')
        
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # General settings tab
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        
        # Check interval
        check_group = QGroupBox("Mail Check Settings")
        check_layout = QFormLayout()
        
        self.check_interval = QSpinBox()
        self.check_interval.setMinimum(1)
        self.check_interval.setMaximum(60)
        self.check_interval.setSuffix(" minutes")
        check_layout.addRow("Check interval:", self.check_interval)
        
        self.check_on_startup = QCheckBox("Check mail on startup")
        check_layout.addRow(self.check_on_startup)
        
        check_group.setLayout(check_layout)
        general_layout.addWidget(check_group)
        
        # Display settings
        display_group = QGroupBox("Display Settings")
        display_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        display_layout.addRow("Theme:", self.theme_combo)
        
        self.font_size = QSpinBox()
        self.font_size.setMinimum(8)
        self.font_size.setMaximum(24)
        self.font_size.setSuffix(" pt")
        display_layout.addRow("Font size:", self.font_size)
        
        display_group.setLayout(display_layout)
        general_layout.addWidget(display_group)
        
        # Notification settings
        notify_group = QGroupBox("Notification Settings")
        notify_layout = QFormLayout()
        
        self.notify_new_mail = QCheckBox("Show notifications for new mail")
        self.notify_sound = QCheckBox("Play sound for new mail")
        
        notify_layout.addRow(self.notify_new_mail)
        notify_layout.addRow(self.notify_sound)
        
        notify_group.setLayout(notify_layout)
        general_layout.addWidget(notify_group)
        
        general_layout.addStretch()
        general_tab.setLayout(general_layout)
        
        # Security settings tab
        security_tab = QWidget()
        security_layout = QVBoxLayout()
        
        # Encryption settings
        encrypt_group = QGroupBox("Encryption")
        encrypt_layout = QFormLayout()
        
        self.encrypt_storage = QCheckBox("Encrypt local mail storage")
        self.encrypt_attachments = QCheckBox("Encrypt attachments")
        
        encrypt_layout.addRow(self.encrypt_storage)
        encrypt_layout.addRow(self.encrypt_attachments)
        
        encrypt_group.setLayout(encrypt_layout)
        security_layout.addWidget(encrypt_group)
        
        # Password settings
        password_group = QGroupBox("Password Settings")
        password_layout = QFormLayout()
        
        self.store_passwords = QCheckBox("Store passwords securely")
        self.auto_lock = QCheckBox("Auto-lock application when inactive")
        
        password_layout.addRow(self.store_passwords)
        password_layout.addRow(self.auto_lock)
        
        password_group.setLayout(password_layout)
        security_layout.addWidget(password_group)
        
        security_layout.addStretch()
        security_tab.setLayout(security_layout)
        
        # Add tabs to widget
        tab_widget.addTab(general_tab, "General")
        tab_widget.addTab(security_tab, "Security")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_settings(self):
        """Load settings from QSettings"""
        # General settings
        self.check_interval.setValue(self.settings.value('check_interval', 5, int))
        self.check_on_startup.setChecked(self.settings.value('check_on_startup', True, bool))
        
        self.theme_combo.setCurrentText(self.settings.value('theme', 'System'))
        self.font_size.setValue(self.settings.value('font_size', 12, int))
        
        self.notify_new_mail.setChecked(self.settings.value('notify_new_mail', True, bool))
        self.notify_sound.setChecked(self.settings.value('notify_sound', True, bool))
        
        # Security settings
        self.encrypt_storage.setChecked(self.settings.value('encrypt_storage', False, bool))
        self.encrypt_attachments.setChecked(self.settings.value('encrypt_attachments', False, bool))
        
        self.store_passwords.setChecked(self.settings.value('store_passwords', True, bool))
        self.auto_lock.setChecked(self.settings.value('auto_lock', False, bool))
    
    def save_settings(self):
        """Save settings to QSettings"""
        try:
            # General settings
            self.settings.setValue('check_interval', self.check_interval.value())
            self.settings.setValue('check_on_startup', self.check_on_startup.isChecked())
            
            self.settings.setValue('theme', self.theme_combo.currentText())
            self.settings.setValue('font_size', self.font_size.value())
            
            self.settings.setValue('notify_new_mail', self.notify_new_mail.isChecked())
            self.settings.setValue('notify_sound', self.notify_sound.isChecked())
            
            # Security settings
            self.settings.setValue('encrypt_storage', self.encrypt_storage.isChecked())
            self.settings.setValue('encrypt_attachments', self.encrypt_attachments.isChecked())
            
            self.settings.setValue('store_passwords', self.store_passwords.isChecked())
            self.settings.setValue('auto_lock', self.auto_lock.isChecked())
            
            # Sync settings
            self.settings.sync()
            
            # Apply settings
            self.apply_settings()
            
            QMessageBox.information(self, "Success", "Settings saved successfully")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def apply_settings(self):
        """Apply settings to application"""
        if self.parent:
            # Update check interval
            if hasattr(self.parent, 'check_mail_timer'):
                self.parent.check_mail_timer.setInterval(self.check_interval.value() * 60 * 1000)
            
            # Apply theme
            # TODO: Implement theme switching
            
            # Apply font size
            # TODO: Implement font size changes
            
            # Apply security settings
            # TODO: Implement security settings
