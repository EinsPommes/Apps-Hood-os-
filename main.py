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
                             QGridLayout, QSplitter, QComboBox, QCheckBox)
from PySide6.QtCore import Qt, QDir, QModelIndex, QFileInfo, QSize
from PySide6.QtGui import QAction, QIcon

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

class FileManager(QMainWindow):
    """Main file manager window with tree view and list view"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hood OS File Manager")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize managers
        self.tag_manager = TagManager()
        self.disk_analyzer = DiskUsageAnalyzer()
        self.setup_ui()

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
        self.splitter.addWidget(self.tree_view)

        # Setup list view for current directory
        self.list_view = QListView()
        self.list_view.setViewMode(QListView.IconMode)
        self.list_view.setIconSize(QSize(48, 48))
        self.list_view.setGridSize(QSize(120, 80))
        self.list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(self.show_context_menu)
        self.splitter.addWidget(self.list_view)

        # Initialize file system model
        self.setup_model()

        # Set initial directory to home
        self.navigate_home()

        # Initialize clipboard
        self.clipboard_source = None
        self.clipboard_action = None

    def setup_toolbar(self, toolbar):
        """Setup navigation toolbar with actions"""
        actions = {
            "back": (QStyle.StandardPixmap.SP_ArrowBack, "Back"),
            "forward": (QStyle.StandardPixmap.SP_ArrowForward, "Forward"),
            "up": (QStyle.StandardPixmap.SP_ArrowUp, "Up"),
            "home": (QStyle.StandardPixmap.SP_DirHomeIcon, "Home"),
            "search": (QStyle.StandardPixmap.SP_FileDialogContentsView, "Search")
        }

        for name, (icon, text) in actions.items():
            action = QAction(self.style().standardIcon(icon), text, self)
            toolbar.addAction(action)
            if name == "up":
                action.triggered.connect(self.navigate_up)
            elif name == "home":
                action.triggered.connect(self.navigate_home)
            elif name == "search":
                action.triggered.connect(self.show_search_dialog)

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

        # Hide unnecessary columns in tree view
        for col in range(1, 4):
            self.tree_view.setColumnHidden(col, True)

        # Connect view signals
        self.tree_view.clicked.connect(self.tree_view_clicked)
        self.list_view.clicked.connect(self.list_view_clicked)

    def show_context_menu(self, position):
        """Show context menu with file operations"""
        sender = self.sender()
        index = sender.indexAt(position)
        menu = QMenu()
        
        if index.isValid():
            file_path = self.model.filePath(index)
            
            # Add file operations
            operations = [
                ("Open", self.open_item),
                ("Copy", lambda: self.set_clipboard('copy')),
                ("Cut", lambda: self.set_clipboard('cut')),
                ("Delete", self.delete_item),
                ("Rename", self.rename_item)
            ]

            for text, handler in operations:
                action = menu.addAction(text)
                action.triggered.connect(lambda checked, h=handler: h(index))
                menu.addSeparator()

            # Add tag operations
            self.add_tag_menu(menu, file_path)

            # Add size analysis for directories
            if os.path.isdir(file_path):
                analyze_action = menu.addAction("Size Analysis")
                analyze_action.triggered.connect(lambda: self.analyze_directory(file_path))

        # Show paste option if clipboard has content
        if self.clipboard_source:
            paste_action = menu.addAction("Paste")
            paste_action.triggered.connect(lambda: self.paste_item(self.model.filePath(index)))

        menu.exec_(sender.mapToGlobal(position))

    def add_tag_menu(self, menu, file_path):
        """Add tag operations to context menu"""
        tag_menu = menu.addMenu("Tags")
        add_action = tag_menu.addAction("Add Tag")
        remove_action = tag_menu.addAction("Remove Tag")
        
        add_action.triggered.connect(lambda: self.add_tag(file_path))
        remove_action.triggered.connect(lambda: self.remove_tag(file_path))

        # Show existing tags
        current_tags = self.tag_manager.get_tags(file_path)
        if current_tags:
            tag_menu.addSeparator()
            for tag in current_tags:
                tag_menu.addAction(f"#{tag}")

    def add_tag(self, file_path):
        tag, ok = QInputDialog.getText(
            self,
            "Add Tag",
            "Enter tag name:",
            QLineEdit.Normal
        )
        if ok and tag:
            self.tag_manager.add_tag(file_path, tag)

    def remove_tag(self, file_path):
        tags = self.tag_manager.get_tags(file_path)
        if not tags:
            QMessageBox.information(
                self,
                "Remove Tag",
                "No tags to remove."
            )
            return

        tag, ok = QInputDialog.getItem(
            self,
            "Remove Tag",
            "Select tag to remove:",
            tags,
            0,
            False
        )
        if ok and tag:
            self.tag_manager.remove_tag(file_path, tag)

    def open_item(self, index):
        """Open the selected file or directory"""
        if index.isValid():
            file_path = self.model.filePath(index)
            os.system(f'xdg-open "{file_path}"')

    def delete_item(self, index):
        """Delete the selected file or directory"""
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
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete: {str(e)}"
                )

    def rename_item(self, index):
        """Rename the selected file or directory"""
        if not index.isValid():
            return

        old_path = self.model.filePath(index)
        old_name = os.path.basename(old_path)
        
        new_name, ok = QInputDialog.getText(
            self,
            "Rename",
            "Enter new name:",
            QLineEdit.Normal,
            old_name
        )

        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to rename: {str(e)}"
                )

    def paste_item(self, target_dir):
        """Paste the copied/cut item to the target directory"""
        if not self.clipboard_source or not os.path.exists(self.clipboard_source):
            return

        source_name = os.path.basename(self.clipboard_source)
        target_path = os.path.join(target_dir, source_name)

        try:
            if self.clipboard_action == 'copy':
                if os.path.isdir(self.clipboard_source):
                    shutil.copytree(self.clipboard_source, target_path)
                else:
                    shutil.copy2(self.clipboard_source, target_path)
            elif self.clipboard_action == 'cut':
                shutil.move(self.clipboard_source, target_path)
                self.clipboard_source = None
                self.clipboard_action = None
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Operation failed: {str(e)}"
            )

    def analyze_directory(self, path):
        """Analyze directory size and show visualization"""
        self.disk_analyzer.analyze_directory(path)

    def tree_view_clicked(self, index):
        """Handle tree view item click"""
        path = self.model.filePath(index)
        self.list_view.setRootIndex(index)
        self.address_bar.setText(path)

    def list_view_clicked(self, index):
        """Handle list view item click"""
        if self.model.isDir(index):
            self.list_view.setRootIndex(index)
            self.address_bar.setText(self.model.filePath(index))

    def navigate_to_path(self):
        """Navigate to the path entered in the address bar"""
        path = self.address_bar.text()
        index = self.model.index(path)
        if index.isValid():
            self.list_view.setRootIndex(index)
            self.tree_view.setCurrentIndex(index)

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
        if dialog.exec_():
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

def main():
    app = QApplication(sys.argv)
    window = FileManager()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
