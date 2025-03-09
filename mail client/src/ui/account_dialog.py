from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFormLayout, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import Qt
from database.session import Session
from database.models import Account
from utils.crypto import encrypt_password

class AccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the account dialog UI"""
        self.setWindowTitle("Add Email Account")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Account details
        details_form = QFormLayout()
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email@example.com")
        details_form.addRow("Email:", self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        details_form.addRow("Password:", self.password_input)
        
        layout.addLayout(details_form)
        
        # Server settings
        server_form = QFormLayout()
        
        self.imap_input = QLineEdit()
        self.imap_input.setPlaceholderText("imap.example.com")
        server_form.addRow("IMAP Server:", self.imap_input)
        
        self.smtp_input = QLineEdit()
        self.smtp_input.setPlaceholderText("smtp.example.com")
        server_form.addRow("SMTP Server:", self.smtp_input)
        
        layout.addLayout(server_form)
        
        # OAuth2 settings
        self.oauth2_check = QCheckBox("Use OAuth2 Authentication")
        self.oauth2_check.stateChanged.connect(self.toggle_oauth2)
        layout.addWidget(self.oauth2_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_account)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def toggle_oauth2(self, state):
        """Toggle OAuth2 settings"""
        self.password_input.setEnabled(not state)
    
    def save_account(self):
        """Save account details"""
        email = self.email_input.text()
        password = self.password_input.text()
        imap_server = self.imap_input.text()
        smtp_server = self.smtp_input.text()
        use_oauth2 = self.oauth2_check.isChecked()
        
        if not all([email, imap_server, smtp_server]) or (not use_oauth2 and not password):
            QMessageBox.warning(
                self,
                "Error",
                "Please fill in all required fields"
            )
            return
        
        try:
            # Encrypt password if not using OAuth2
            encrypted_password = ''
            if not use_oauth2:
                encrypted_password = encrypt_password(password)
            
            # Create account
            account = Account(
                email=email,
                encrypted_credentials=encrypted_password if password else None,
                imap_server=imap_server,
                smtp_server=smtp_server,
                use_oauth2=use_oauth2
            )
            
            # Save to database
            with Session() as session:
                session.add(account)
                session.commit()
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not save account: {str(e)}"
            )
