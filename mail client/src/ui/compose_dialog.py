from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QComboBox,
    QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from database.session import Session
from database.models import Account
from utils.email_service import EmailService

class ComposeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.email_services = {}
        self.load_accounts()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the compose dialog UI"""
        self.setWindowTitle("Compose Email")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Form layout for email fields
        form_layout = QFormLayout()
        
        # From account selector
        self.from_combo = QComboBox()
        for email in self.email_services.keys():
            self.from_combo.addItem(email)
        form_layout.addRow("From:", self.from_combo)
        
        # To field
        self.to_input = QLineEdit()
        self.to_input.setPlaceholderText("recipient@example.com")
        form_layout.addRow("To:", self.to_input)
        
        # Subject field
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Enter subject")
        form_layout.addRow("Subject:", self.subject_input)
        
        layout.addLayout(form_layout)
        
        # Message body
        layout.addWidget(QLabel("Message:"))
        
        self.body_input = QTextEdit()
        layout.addWidget(self.body_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_email)
        button_layout.addWidget(send_btn)
        
        layout.addLayout(button_layout)
    
    def load_accounts(self):
        """Load email accounts from database"""
        try:
            with Session() as session:
                accounts = session.query(Account).all()
                for account in accounts:
                    config = {
                        'email': account.email,
                        'password': account.encrypted_credentials,
                        'imap_server': account.imap_server,
                        'smtp_server': account.smtp_server,
                        'use_oauth2': account.use_oauth2,
                        'oauth2_refresh_token': account.oauth2_refresh_token
                    }
                    self.email_services[account.email] = EmailService(config)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not load accounts: {str(e)}"
            )
    
    def send_email(self):
        """Send the email"""
        from_email = self.from_combo.currentText()
        to_email = self.to_input.text()
        subject = self.subject_input.text()
        body = self.body_input.toPlainText()
        
        if not all([from_email, to_email, subject, body]):
            QMessageBox.warning(
                self,
                "Error",
                "Please fill in all fields"
            )
            return
        
        try:
            service = self.email_services.get(from_email)
            if not service:
                raise Exception("No email service available")
            
            if service.send_email(to_email, subject, body):
                QMessageBox.information(
                    self,
                    "Success",
                    "Email sent successfully"
                )
                self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not send email: {str(e)}"
            )
