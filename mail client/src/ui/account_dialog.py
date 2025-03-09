from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QMessageBox,
    QComboBox
)
from PyQt6.QtCore import Qt

from database.session import Session
from database.models import Account
from utils.crypto import encrypt_password

class AccountDialog(QDialog):
    # Email provider presets
    EMAIL_PRESETS = {
        'Custom': {
            'imap_server': '',
            'smtp_server': '',
            'use_oauth2': False
        },
        'Gmail': {
            'imap_server': 'imap.gmail.com',
            'smtp_server': 'smtp.gmail.com',
            'use_oauth2': True
        },
        'Outlook': {
            'imap_server': 'outlook.office365.com',
            'smtp_server': 'smtp.office365.com',
            'use_oauth2': True
        },
        'Web.de': {
            'imap_server': 'imap.web.de',
            'smtp_server': 'smtp.web.de',
            'use_oauth2': False
        },
        'GMX': {
            'imap_server': 'imap.gmx.net',
            'smtp_server': 'mail.gmx.net',
            'use_oauth2': False
        },
        'Yahoo': {
            'imap_server': 'imap.mail.yahoo.com',
            'smtp_server': 'smtp.mail.yahoo.com',
            'use_oauth2': True
        }
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Add Email Account")
        layout = QVBoxLayout(self)
        
        # Provider selection
        provider_layout = QHBoxLayout()
        provider_label = QLabel("Email Provider:")
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(self.EMAIL_PRESETS.keys())
        self.provider_combo.currentTextChanged.connect(self.provider_changed)
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self.provider_combo)
        layout.addLayout(provider_layout)
        
        # Email field
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@example.com")
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)
        
        # Password field
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your password")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # Server settings group
        server_label = QLabel("Server Settings")
        server_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(server_label)
        
        # IMAP server field
        imap_layout = QHBoxLayout()
        imap_label = QLabel("IMAP Server:")
        self.imap_input = QLineEdit()
        self.imap_input.setPlaceholderText("imap.example.com")
        imap_layout.addWidget(imap_label)
        imap_layout.addWidget(self.imap_input)
        layout.addLayout(imap_layout)
        
        # SMTP server field
        smtp_layout = QHBoxLayout()
        smtp_label = QLabel("SMTP Server:")
        self.smtp_input = QLineEdit()
        self.smtp_input.setPlaceholderText("smtp.example.com")
        smtp_layout.addWidget(smtp_label)
        smtp_layout.addWidget(self.smtp_input)
        layout.addLayout(smtp_layout)
        
        # OAuth2 checkbox
        oauth_layout = QHBoxLayout()
        self.oauth_checkbox = QCheckBox("Use OAuth2")
        self.oauth_checkbox.stateChanged.connect(self.toggle_oauth)
        oauth_layout.addWidget(self.oauth_checkbox)
        layout.addLayout(oauth_layout)
        
        # Help text for OAuth2
        self.oauth_help = QLabel(
            "Note: OAuth2 is recommended for Gmail, Outlook, and Yahoo.\n"
            "It provides better security and avoids less secure app access."
        )
        self.oauth_help.setStyleSheet("color: gray; font-size: 10px;")
        self.oauth_help.setWordWrap(True)
        layout.addWidget(self.oauth_help)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_account)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Set initial provider
        self.provider_changed("Custom")
    
    def provider_changed(self, provider):
        """Handle provider selection change"""
        preset = self.EMAIL_PRESETS[provider]
        
        # Update server fields
        self.imap_input.setText(preset['imap_server'])
        self.smtp_input.setText(preset['smtp_server'])
        
        # Update OAuth2 checkbox
        self.oauth_checkbox.setChecked(preset['use_oauth2'])
        
        # Update field states
        is_custom = (provider == "Custom")
        self.imap_input.setEnabled(is_custom)
        self.smtp_input.setEnabled(is_custom)
        
        # Show/hide OAuth2 help text
        self.oauth_help.setVisible(preset['use_oauth2'])
        
        # Clear email field if it doesn't match the provider
        if not is_custom and not self.email_input.text().endswith(f"@{provider.lower()}.com"):
            self.email_input.clear()
    
    def toggle_oauth(self, state):
        """Toggle password field based on OAuth2 checkbox"""
        self.password_input.setEnabled(not state)
        if state:
            self.password_input.clear()
            self.password_input.setPlaceholderText("Not needed with OAuth2")
        else:
            self.password_input.setPlaceholderText("Enter your password")
    
    def save_account(self):
        """Save the account details"""
        try:
            email = self.email_input.text().strip()
            password = self.password_input.text()
            imap_server = self.imap_input.text().strip()
            smtp_server = self.smtp_input.text().strip()
            use_oauth2 = self.oauth_checkbox.isChecked()
            
            # Validate inputs
            if not email:
                raise ValueError("Email is required")
            if not use_oauth2 and not password:
                raise ValueError("Password is required when not using OAuth2")
            if not imap_server:
                raise ValueError("IMAP server is required")
            if not smtp_server:
                raise ValueError("SMTP server is required")
            
            # Create account
            with Session() as session:
                account = Account(
                    email=email,
                    encrypted_credentials=encrypt_password(password) if password else None,
                    imap_server=imap_server,
                    smtp_server=smtp_server,
                    use_oauth2=use_oauth2
                )
                session.add(account)
                session.commit()
            
            self.accept()
        
        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save account: {str(e)}")
