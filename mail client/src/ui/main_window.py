from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTreeView, QTableView, QTextEdit,
    QMenuBar, QMenu, QMessageBox, QSplitter,
    QHeaderView, QLabel, QStatusBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QStandardItemModel, QStandardItem
from database.session import Session
from database.models import Account
from utils.email_service import EmailService
from .account_dialog import AccountDialog
from .compose_dialog import ComposeDialog
from .settings_dialog import SettingsDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.email_services = {}
        self.setup_ui()
        self.load_accounts()
        
    def setup_ui(self):
        """Setup the main window UI"""
        self.setWindowTitle("Email Client")
        self.setMinimumSize(QSize(800, 600))
        
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_email_action = QAction("New Email", self)
        new_email_action.triggered.connect(self.compose_email)
        file_menu.addAction(new_email_action)
        
        add_account_action = QAction("Add Account", self)
        add_account_action.triggered.connect(self.add_account)
        file_menu.addAction(add_account_action)
        
        check_mail_action = QAction("Check Mail", self)
        check_mail_action.triggered.connect(self.check_mail)
        file_menu.addAction(check_mail_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_folders)
        view_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        layout = QHBoxLayout(main_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Folder panel
        folder_widget = QWidget()
        folder_layout = QVBoxLayout(folder_widget)
        
        self.folder_tree = QTreeView()
        self.folder_model = QStandardItemModel()
        self.folder_model.setHorizontalHeaderLabels(["Folders"])
        self.folder_tree.setModel(self.folder_model)
        self.folder_tree.clicked.connect(self.folder_selected)
        folder_layout.addWidget(self.folder_tree)
        
        splitter.addWidget(folder_widget)
        
        # Email list and preview panel
        email_widget = QWidget()
        email_layout = QVBoxLayout(email_widget)
        
        # Email list
        self.email_list = QTableView()
        self.email_model = QStandardItemModel()
        self.email_model.setHorizontalHeaderLabels(["Subject", "From", "Date"])
        self.email_list.setModel(self.email_model)
        self.email_list.clicked.connect(self.email_selected)
        
        # Set column widths
        header = self.email_list.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        email_layout.addWidget(self.email_list)
        
        # Email preview
        self.email_preview = QTextEdit()
        self.email_preview.setReadOnly(True)
        email_layout.addWidget(self.email_preview)
        
        splitter.addWidget(email_widget)
        
        # Set initial splitter sizes
        splitter.setSizes([200, 600])
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def load_accounts(self):
        """Load email accounts from database"""
        try:
            with Session() as session:
                accounts = session.query(Account).all()
                for account in accounts:
                    config = {
                        'email': account.email,
                        'encrypted_credentials': account.encrypted_credentials,
                        'imap_server': account.imap_server,
                        'smtp_server': account.smtp_server,
                        'use_oauth2': account.use_oauth2,
                        'oauth2_refresh_token': account.oauth2_refresh_token
                    }
                    self.email_services[account.email] = EmailService(config)
            self.refresh_folders()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not load accounts: {str(e)}"
            )
    
    def refresh_folders(self):
        """Refresh the folder tree"""
        try:
            self.folder_model.clear()
            self.folder_model.setHorizontalHeaderLabels(["Folders"])
            
            for email, service in self.email_services.items():
                account_item = QStandardItem(email)
                self.folder_model.appendRow(account_item)
                
                try:
                    folders = service.get_folders()
                    for folder in folders:
                        folder_item = QStandardItem(folder)
                        account_item.appendRow(folder_item)
                    
                    self.folder_tree.expand(account_item.index())
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Warning",
                        f"Could not load folders for {email}: {str(e)}"
                    )
            
            self.status_bar.showMessage("Folders refreshed")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not refresh folders: {str(e)}"
            )
    
    def folder_selected(self, index):
        """Handle folder selection"""
        try:
            item = self.folder_model.itemFromIndex(index)
            if not item.parent():  # Skip if account is selected
                return
                
            account_email = item.parent().text()
            folder_name = item.text()
            
            service = self.email_services.get(account_email)
            if service:
                emails = service.get_emails(folder_name)
                self.display_emails(emails)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not load emails: {str(e)}"
            )
    
    def display_emails(self, emails):
        """Display emails in the email list"""
        self.email_model.clear()
        self.email_model.setHorizontalHeaderLabels(["Subject", "From", "Date"])
        
        for email in emails:
            subject_item = QStandardItem(email['subject'])
            from_item = QStandardItem(email['sender'])
            date_item = QStandardItem(str(email['date']))
            
            self.email_model.appendRow([subject_item, from_item, date_item])
    
    def email_selected(self, index):
        """Handle email selection"""
        row = index.row()
        try:
            email_body = self.email_model.index(row, 0).data()  # Use subject as preview for now
            self.email_preview.setHtml(email_body)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not display email: {str(e)}"
            )
    
    def add_account(self):
        """Show dialog to add new account"""
        dialog = AccountDialog(self)
        if dialog.exec():
            self.load_accounts()
    
    def compose_email(self):
        """Show dialog to compose new email"""
        dialog = ComposeDialog(self)
        dialog.exec()
    
    def check_mail(self):
        """Check for new mail"""
        try:
            self.refresh_folders()
            self.status_bar.showMessage("Mail check complete")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not check mail: {str(e)}"
            )
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Email Client",
            "A modern email client for Linux desktop.\n\n"
            "Version: 1.0.0\n"
            " 2024 Hood OS"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Disconnect all email services
        for service in self.email_services.values():
            try:
                service.disconnect()
            except:
                pass
        event.accept()
