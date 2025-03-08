#!/usr/bin/env python3
"""
Hood OS File Manager
A modern, efficient file manager with advanced features like file tagging,
disk usage analysis, and advanced search capabilities.
"""
import sys
import os
import shutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTreeView, QListView, QLineEdit,
                             QPushButton, QFileSystemModel, QStyle, QToolBar,
                             QMenu, QMessageBox, QInputDialog, QDialog, QLabel,
                             QGridLayout, QSplitter, QComboBox, QCheckBox,
                             QStatusBar, QHeaderView, QGroupBox, QSlider, QListWidget, QListWidgetItem)
from PySide6.QtCore import (Qt, QDir, QModelIndex, QFileInfo, QSize, QSettings, 
                          QUrl, QMimeDatabase, QStandardPaths)
from PySide6.QtGui import QAction, QIcon, QPalette, QColor, QKeySequence, QDesktopServices
from PySide6.QtDBus import QDBusInterface
import subprocess

from tag_manager import TagManager
from disk_usage_analyzer import DiskUsageAnalyzer

class SearchDialog(QDialog):
    """Advanced search dialog with filters for name, type, size, and tags"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Search")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Search term input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search term...")
        layout.addWidget(self.search_input)
        
        # File type filter
        self.type_combo = QComboBox()
        self.type_combo.addItems(["All Files", "Files Only", "Folders Only"])
        layout.addWidget(self.type_combo)
        
        # Size filter
        size_layout = QHBoxLayout()
        self.min_size = QLineEdit()
        self.min_size.setPlaceholderText("Min Size (MB)")
        self.max_size = QLineEdit()
        self.max_size.setPlaceholderText("Max Size (MB)")
        size_layout.addWidget(self.min_size)
        size_layout.addWidget(self.max_size)
        layout.addLayout(size_layout)
        
        # Tag filter
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Filter by tag...")
        layout.addWidget(self.tag_input)
        
        # Action buttons
        buttons = QHBoxLayout()
        self.ok_button = QPushButton("Search")
        self.cancel_button = QPushButton("Cancel")
        buttons.addWidget(self.ok_button)
        buttons.addWidget(self.cancel_button)
        layout.addLayout(buttons)
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

class PropertiesDialog(QDialog):
    """File properties dialog showing detailed information about files/folders"""
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Properties")
        self.setMinimumWidth(400)
        
        layout = QGridLayout(self)
        file_info = QFileInfo(file_path)
        
        # Display file information
        layout.addWidget(QLabel("Name:"), 0, 0)
        layout.addWidget(QLabel(file_info.fileName()), 0, 1)
        
        layout.addWidget(QLabel("Path:"), 1, 0)
        layout.addWidget(QLabel(file_info.filePath()), 1, 1)
        
        size = file_info.size()
        size_str = self.format_size(size)
        layout.addWidget(QLabel("Size:"), 2, 0)
        layout.addWidget(QLabel(size_str), 2, 1)
        
        layout.addWidget(QLabel("Type:"), 3, 0)
        type_str = "Folder" if file_info.isDir() else "File"
        layout.addWidget(QLabel(type_str), 3, 1)
        
        # Show permissions
        layout.addWidget(QLabel("Permissions:"), 4, 0)
        perms = []
        if file_info.isReadable(): perms.append("Read")
        if file_info.isWritable(): perms.append("Write")
        if file_info.isExecutable(): perms.append("Execute")
        layout.addWidget(QLabel(", ".join(perms)), 4, 1)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, 5, 0, 1, 2)

    def format_size(self, size):
        """Convert file size to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

class SettingsDialog(QDialog):
    """Settings dialog for customizing the file manager"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout()
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentText(parent.current_theme.capitalize())
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        appearance_layout.addLayout(theme_layout)
        
        # Icon size
        icon_layout = QHBoxLayout()
        icon_label = QLabel("Icon Size:")
        self.icon_slider = QSlider(Qt.Horizontal)
        self.icon_slider.setMinimum(16)
        self.icon_slider.setMaximum(128)
        self.icon_slider.setValue(parent.list_view.iconSize().width())
        self.icon_size_label = QLabel(f"{self.icon_slider.value()}px")
        self.icon_slider.valueChanged.connect(
            lambda v: self.icon_size_label.setText(f"{v}px")
        )
        icon_layout.addWidget(icon_label)
        icon_layout.addWidget(self.icon_slider)
        icon_layout.addWidget(self.icon_size_label)
        appearance_layout.addLayout(icon_layout)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # View group
        view_group = QGroupBox("View Settings")
        view_layout = QVBoxLayout()
        
        # Show/hide columns
        self.column_checks = []
        columns = ["Size", "Type", "Date Modified"]
        for col, name in enumerate(columns, 1):
            check = QCheckBox(name)
            check.setChecked(not parent.tree_view.isColumnHidden(col))
            self.column_checks.append((col, check))
            view_layout.addWidget(check)
            
        view_group.setLayout(view_layout)
        layout.addWidget(view_group)
        
        # Buttons
        button_box = QHBoxLayout()
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(apply_button)
        button_box.addWidget(cancel_button)
        layout.addLayout(button_box)

    def apply_settings(self):
        # Apply theme
        new_theme = self.theme_combo.currentText().lower()
        if new_theme != self.parent.current_theme:
            self.parent.current_theme = new_theme
            self.parent.settings.setValue("theme", new_theme)
            self.parent.apply_theme()
        
        # Apply icon size
        new_size = self.icon_slider.value()
        self.parent.list_view.setIconSize(QSize(new_size, new_size))
        self.parent.settings.setValue("icon_size", new_size)
        
        # Apply column visibility
        for col, check in self.column_checks:
            self.parent.tree_view.setColumnHidden(col, not check.isChecked())
            self.parent.settings.setValue(f"show_column_{col}", check.isChecked())
        
        self.accept()

class OpenWithDialog(QDialog):
    """Dialog for choosing an application to open a file with"""
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle("Open With")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Application list
        self.app_list = QListWidget()
        self.populate_app_list()
        layout.addWidget(self.app_list)
        
        # Remember choice checkbox
        self.remember_choice = QCheckBox("Remember my choice for this file type")
        layout.addWidget(self.remember_choice)
        
        # Buttons
        buttons = QHBoxLayout()
        self.ok_button = QPushButton("Open")
        self.browse_button = QPushButton("Browse...")
        self.cancel_button = QPushButton("Cancel")
        
        buttons.addWidget(self.ok_button)
        buttons.addWidget(self.browse_button)
        buttons.addWidget(self.cancel_button)
        
        self.ok_button.clicked.connect(self.accept)
        self.browse_button.clicked.connect(self.browse_for_app)
        self.cancel_button.clicked.connect(self.reject)
        
        layout.addLayout(buttons)

    def populate_app_list(self):
        """Populate the list with common applications"""
        # Get file type
        mime_type = QMimeDatabase().mimeTypeForFile(self.file_path)
        
        # Get default and alternative applications
        apps = []
        
        # Add system default if available
        default_app = QStandardPaths.findExecutable(mime_type.defaultApplication())
        if default_app:
            self.app_list.addItem(QListWidgetItem(
                self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon),
                f"Default Application ({os.path.basename(default_app)})"
            ))
        
        # Add some common applications based on file type
        if mime_type.name().startswith('text/'):
            editors = ['gedit', 'kate', 'mousepad', 'notepadqq']
            for editor in editors:
                path = QStandardPaths.findExecutable(editor)
                if path:
                    self.app_list.addItem(QListWidgetItem(
                        self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon),
                        os.path.basename(path)
                    ))
        
        elif mime_type.name().startswith('image/'):
            viewers = ['eog', 'gwenview', 'gthumb', 'gimp']
            for viewer in viewers:
                path = QStandardPaths.findExecutable(viewer)
                if path:
                    self.app_list.addItem(QListWidgetItem(
                        self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon),
                        os.path.basename(path)
                    ))

    def browse_for_app(self):
        """Open file dialog to browse for an application"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Application",
            "/usr/bin/",
            "All Files (*)"
        )
        if file_path:
            self.app_list.addItem(QListWidgetItem(
                self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon),
                os.path.basename(file_path)
            ))
            self.app_list.setCurrentRow(self.app_list.count() - 1)

class FileManager(QMainWindow):
    """Main file manager window with tree view and list view"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hood OS File Manager")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize settings
        self.settings = QSettings("Hood OS", "File Manager")
        self.current_theme = self.settings.value("theme", "light")

        # Initialize managers
        self.tag_manager = TagManager()
        self.disk_analyzer = DiskUsageAnalyzer()
        
        self.setup_ui()
        self.apply_theme()
        self.load_settings()

    def setup_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Setup toolbar with navigation actions
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        self.setup_toolbar(toolbar)

        # Main splitter with tree and list views
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)

        # Setup tree view for navigation
        self.tree_view = QTreeView()
        self.tree_view.setMinimumWidth(300)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        self.tree_view.doubleClicked.connect(self.handle_double_click)
        self.splitter.addWidget(self.tree_view)

        # Setup list view for current directory
        self.list_view = QListView()
        self.list_view.setViewMode(QListView.IconMode)
        self.list_view.setIconSize(QSize(48, 48))
        self.list_view.setGridSize(QSize(120, 80))
        self.list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(self.show_context_menu)
        self.list_view.doubleClicked.connect(self.handle_double_click)
        self.splitter.addWidget(self.list_view)

        # Initialize file system model
        self.setup_model()

        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Set initial directory to home
        self.navigate_home()

        # Initialize clipboard
        self.clipboard_source = None
        self.clipboard_action = None

        # Setup keyboard shortcuts
        self.setup_shortcuts()

    def setup_toolbar(self, toolbar):
        """Setup navigation toolbar with actions"""
        actions = {
            "back": (QStyle.StandardPixmap.SP_ArrowBack, "Back", QKeySequence.Back),
            "forward": (QStyle.StandardPixmap.SP_ArrowForward, "Forward", QKeySequence.Forward),
            "up": (QStyle.StandardPixmap.SP_ArrowUp, "Up", QKeySequence("Alt+Up")),
            "home": (QStyle.StandardPixmap.SP_DirHomeIcon, "Home", QKeySequence("Ctrl+H")),
            "search": (QStyle.StandardPixmap.SP_FileDialogContentsView, "Search", QKeySequence("Ctrl+F")),
            "refresh": (QStyle.StandardPixmap.SP_BrowserReload, "Refresh", QKeySequence("F5")),
            "settings": (QStyle.StandardPixmap.SP_FileDialogDetailedView, "Settings", QKeySequence("Ctrl+,"))
        }

        for name, (icon, text, shortcut) in actions.items():
            action = QAction(self.style().standardIcon(icon), text, self)
            action.setShortcut(shortcut)
            toolbar.addAction(action)
            if name == "up":
                action.triggered.connect(self.navigate_up)
            elif name == "home":
                action.triggered.connect(self.navigate_home)
            elif name == "search":
                action.triggered.connect(self.show_search_dialog)
            elif name == "refresh":
                action.triggered.connect(self.refresh_view)
            elif name == "settings":
                action.triggered.connect(self.show_settings)

        # Add address bar
        self.address_bar = QLineEdit()
        toolbar.addWidget(self.address_bar)
        self.address_bar.returnPressed.connect(self.navigate_to_path)

    def setup_model(self):
        """Initialize and configure the file system model"""
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        
        self.tree_view.setModel(self.model)
        self.list_view.setModel(self.model)

        # Show all columns in tree view
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, 4):
            self.tree_view.header().setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
            self.tree_view.setColumnHidden(col, False)

    def setup_shortcuts(self):
        """Setup additional keyboard shortcuts"""
        shortcuts = {
            "copy": (QKeySequence.Copy, self.copy_selected),
            "cut": (QKeySequence.Cut, self.cut_selected),
            "paste": (QKeySequence.Paste, self.paste_files),
            "delete": (QKeySequence.Delete, self.delete_selected),
            "properties": (QKeySequence("Alt+Return"), lambda: self.show_properties_dialog(self.model.filePath(self.list_view.currentIndex()))),
            "new_folder": (QKeySequence("Ctrl+Shift+N"), self.create_folder),
            "new_file": (QKeySequence("Ctrl+N"), self.create_file)
        }

        for name, (shortcut, slot) in shortcuts.items():
            action = QAction(self)
            action.setShortcut(shortcut)
            action.triggered.connect(slot)
            self.addAction(action)

    def apply_theme(self):
        """Apply the current theme to the application"""
        palette = QPalette()
        if self.current_theme == "dark":
            # Dark theme colors
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
        else:
            # Light theme (default Qt palette)
            palette = self.style().standardPalette()

        QApplication.setPalette(palette)

    def load_settings(self):
        """Load saved settings"""
        # Load icon size
        icon_size = self.settings.value("icon_size", 48, type=int)
        self.list_view.setIconSize(QSize(icon_size, icon_size))
        
        # Load column visibility
        for col in range(1, 4):
            show = self.settings.value(f"show_column_{col}", True, type=bool)
            self.tree_view.setColumnHidden(col, not show)

    def show_settings(self):
        """Show the settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def refresh_view(self):
        """Refresh the current view"""
        self.model.setRootPath("")  # This forces a refresh
        self.model.setRootPath(QDir.rootPath())
        current_path = self.address_bar.text()
        self.navigate_to_path()
        self.status_bar.showMessage("View refreshed", 2000)

    def update_status(self, path):
        """Update status bar with current directory info"""
        dir_info = QFileInfo(path)
        if dir_info.isDir():
            item_count = len(os.listdir(path))
            free_space = shutil.disk_usage(path).free
            free_space_str = self.format_size(free_space)
            self.status_bar.showMessage(f"Items: {item_count} | Free Space: {free_space_str}")

    def format_size(self, size):
        """Convert file size to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def navigate_to_path(self):
        """Navigate to the path entered in the address bar"""
        path = self.address_bar.text()
        index = self.model.index(path)
        if index.isValid():
            self.tree_view.setCurrentIndex(index)
            self.list_view.setRootIndex(index)
            self.update_status(path)
        else:
            self.status_bar.showMessage("Invalid path", 2000)

    def show_context_menu(self, position):
        """Show context menu with file operations"""
        sender = self.sender()
        index = sender.indexAt(position)
        menu = QMenu()

        if index.isValid():
            # Context menu for files/folders
            file_path = self.model.filePath(index)
            
            # Open actions
            open_action = menu.addAction("Open")
            open_with_menu = QMenu("Open With", menu)
            menu.addMenu(open_with_menu)
            
            # Add some common applications based on file type
            if os.path.isfile(file_path):  # Only show "Open With" for files
                try:
                    mime_type = QMimeDatabase().mimeTypeForFile(file_path)
                    if mime_type.name().startswith('text/'):
                        editors = ['gedit', 'kate', 'mousepad', 'notepadqq']
                        for editor in editors:
                            path = QStandardPaths.findExecutable(editor)
                            if path:
                                action = open_with_menu.addAction(os.path.basename(path))
                                action.triggered.connect(lambda _, app=path: self.open_with(file_path, app))
                    
                    elif mime_type.name().startswith('image/'):
                        viewers = ['eog', 'gwenview', 'gthumb', 'gimp']
                        for viewer in viewers:
                            path = QStandardPaths.findExecutable(viewer)
                            if path:
                                action = open_with_menu.addAction(os.path.basename(path))
                                action.triggered.connect(lambda _, app=path: self.open_with(file_path, app))
                    
                    # Other applications...
                    open_with_menu.addSeparator()
                    choose_app_action = open_with_menu.addAction("Choose Application...")
                    choose_app_action.triggered.connect(lambda: self.show_open_with_dialog(file_path))
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to get MIME type: {str(e)}"
                    )
            
            menu.addSeparator()
            
            # File operations
            copy_action = menu.addAction("Copy")
            cut_action = menu.addAction("Cut")
            if self.clipboard_source:
                paste_action = menu.addAction("Paste")
            delete_action = menu.addAction("Delete")
            rename_action = menu.addAction("Rename")
            
            menu.addSeparator()
            properties_action = menu.addAction("Properties")
            
            # Connect actions
            open_action.triggered.connect(lambda: self.open_item(index))
            copy_action.triggered.connect(self.copy_selected)
            cut_action.triggered.connect(self.cut_selected)
            if self.clipboard_source:
                paste_action.triggered.connect(self.paste_files)
            delete_action.triggered.connect(self.delete_selected)
            rename_action.triggered.connect(lambda: self.rename_item(index))
            properties_action.triggered.connect(lambda: self.show_properties_dialog(file_path))
        
        else:
            # Context menu for empty space
            current_path = self.model.filePath(self.list_view.rootIndex())
            
            # Create new items
            new_menu = QMenu("New", menu)
            menu.addMenu(new_menu)
            
            new_file_action = new_menu.addAction("File")
            new_folder_action = new_menu.addAction("Folder")
            
            # Paste action if clipboard has content
            if self.clipboard_source:
                menu.addSeparator()
                paste_action = menu.addAction("Paste")
                paste_action.triggered.connect(self.paste_files)
            
            # Connect create actions
            new_file_action.triggered.connect(self.create_file)
            new_folder_action.triggered.connect(self.create_folder)
            
            menu.addSeparator()
            refresh_action = menu.addAction("Refresh")
            refresh_action.triggered.connect(self.refresh_view)
        
        menu.exec(sender.mapToGlobal(position))

    def handle_double_click(self, index):
        """Handle double click on items"""
        file_path = self.model.filePath(index)
        if os.path.isdir(file_path):
            # If it's a directory, navigate into it
            self.list_view.setRootIndex(index)
            self.tree_view.setCurrentIndex(index)
            self.address_bar.setText(file_path)
            self.update_status(file_path)
        else:
            # If it's a file, open it
            self.open_item(index)

    def open_item(self, index):
        """Open a file or directory"""
        file_path = self.model.filePath(index)
        if os.path.isdir(file_path):
            self.list_view.setRootIndex(index)
            self.tree_view.setCurrentIndex(index)
            self.address_bar.setText(file_path)
            self.update_status(file_path)
        else:
            # Try to open the file with default application
            url = QUrl.fromLocalFile(file_path)
            QDesktopServices.openUrl(url)

    def open_with(self, file_path, application):
        """Open a file with a specific application"""
        try:
            subprocess.Popen([application, file_path])
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open file with {application}: {str(e)}"
            )

    def show_open_with_dialog(self, file_path):
        """Show the 'Open With' dialog"""
        dialog = OpenWithDialog(file_path, self)
        if dialog.exec() == QDialog.Accepted and dialog.app_list.currentItem():
            app_name = dialog.app_list.currentItem().text()
            if "Default Application" in app_name:
                # Use system default
                url = QUrl.fromLocalFile(file_path)
                QDesktopServices.openUrl(url)
            else:
                # Use selected application
                app_path = QStandardPaths.findExecutable(app_name)
                if app_path:
                    self.open_with(file_path, app_path)
                    
                    # Save as default if requested
                    if dialog.remember_choice.isChecked():
                        mime_type = QMimeDatabase().mimeTypeForFile(file_path)
                        self.settings.setValue(f"default_app_{mime_type.name()}", app_path)

    def navigate_up(self):
        """Navigate to parent directory"""
        index = self.list_view.rootIndex()
        parent = index.parent()
        if parent.isValid():
            self.list_view.setRootIndex(parent)
            self.tree_view.setCurrentIndex(parent)
            self.address_bar.setText(self.model.filePath(parent))

    def navigate_home(self):
        """Navigate to home directory"""
        home_path = QDir.homePath()
        index = self.model.index(home_path)
        self.list_view.setRootIndex(index)
        self.tree_view.setCurrentIndex(index)
        self.address_bar.setText(home_path)

    def set_clipboard(self, action):
        """Set clipboard content and action"""
        index = self.list_view.currentIndex()
        self.clipboard_source = self.model.filePath(index)
        self.clipboard_action = action

    def show_search_dialog(self):
        """Show the search dialog and process results"""
        dialog = SearchDialog(self)
        if dialog.exec():
            search_term = dialog.search_input.text()
            file_type = dialog.type_combo.currentText()
            min_size = dialog.min_size.text()
            max_size = dialog.max_size.text()
            tag = dialog.tag_input.text()
            
            # TODO: Implement search functionality
            # For now, just show a message that search is not implemented
            QMessageBox.information(
                self,
                "Search",
                "Search functionality is coming soon!"
            )

    def copy_selected(self):
        """Copy the selected file or directory"""
        index = self.list_view.currentIndex()
        if index.isValid():
            self.clipboard_source = self.model.filePath(index)
            self.clipboard_action = 'copy'
            self.status_bar.showMessage("Item copied to clipboard", 2000)

    def cut_selected(self):
        """Cut the selected file or directory"""
        index = self.list_view.currentIndex()
        if index.isValid():
            self.clipboard_source = self.model.filePath(index)
            self.clipboard_action = 'cut'
            self.status_bar.showMessage("Item cut to clipboard", 2000)

    def paste_files(self):
        """Paste files from clipboard"""
        if not self.clipboard_source or not os.path.exists(self.clipboard_source):
            self.status_bar.showMessage("Nothing to paste", 2000)
            return

        current_path = self.model.filePath(self.list_view.rootIndex())
        source_name = os.path.basename(self.clipboard_source)
        target_path = os.path.join(current_path, source_name)

        try:
            if self.clipboard_action == 'copy':
                if os.path.isdir(self.clipboard_source):
                    shutil.copytree(self.clipboard_source, target_path)
                else:
                    shutil.copy2(self.clipboard_source, target_path)
                self.status_bar.showMessage("Item copied successfully", 2000)
            elif self.clipboard_action == 'cut':
                shutil.move(self.clipboard_source, target_path)
                self.clipboard_source = None
                self.clipboard_action = None
                self.status_bar.showMessage("Item moved successfully", 2000)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to paste: {str(e)}"
            )

    def delete_selected(self):
        """Delete the selected file or directory"""
        index = self.list_view.currentIndex()
        if not index.isValid():
            return

        file_path = self.model.filePath(index)
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {os.path.basename(file_path)}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                self.status_bar.showMessage("Item deleted successfully", 2000)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete: {str(e)}"
                )

    def rename_item(self, index):
        """Rename a file or directory"""
        if not index.isValid():
            return
            
        old_path = self.model.filePath(index)
        old_name = os.path.basename(old_path)
        parent_dir = os.path.dirname(old_path)
        
        new_name, ok = QInputDialog.getText(
            self,
            "Rename",
            "Enter new name:",
            QLineEdit.Normal,
            old_name
        )
        
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(parent_dir, new_name)
            try:
                os.rename(old_path, new_path)
                self.status_bar.showMessage(f"Renamed to {new_name}", 2000)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to rename: {str(e)}"
                )

    def show_properties_dialog(self, file_path):
        """Show the properties dialog"""
        dialog = PropertiesDialog(file_path, self)
        dialog.exec()

    def create_folder(self):
        """Create a new folder in the current directory"""
        current_path = self.model.filePath(self.list_view.rootIndex())
        name, ok = QInputDialog.getText(
            self,
            "Create Folder",
            "Enter folder name:",
            QLineEdit.Normal
        )
        if ok and name:
            try:
                new_folder_path = os.path.join(current_path, name)
                os.mkdir(new_folder_path)
                self.status_bar.showMessage(f"Created folder: {name}", 2000)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create folder: {str(e)}"
                )

    def create_file(self):
        """Create a new empty file in the current directory"""
        current_path = self.model.filePath(self.list_view.rootIndex())
        name, ok = QInputDialog.getText(
            self,
            "Create File",
            "Enter file name:",
            QLineEdit.Normal
        )
        if ok and name:
            try:
                new_file_path = os.path.join(current_path, name)
                with open(new_file_path, 'w') as f:
                    pass  # Create empty file
                self.status_bar.showMessage(f"Created file: {name}", 2000)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create file: {str(e)}"
                )

def main():
    app = QApplication(sys.argv)
    window = FileManager()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
