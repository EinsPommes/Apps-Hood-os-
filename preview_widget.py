from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QScrollArea
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QSize
import magic
from PIL import Image
import io

class PreviewWidget(QWidget):
    """Widget for previewing file contents"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Create scroll area for large content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)
        
        # Create container for content
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.scroll_area.setWidget(self.content_widget)
        
        # Create label for images
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.image_label)
        
        # Create text edit for text
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.content_layout.addWidget(self.text_preview)
        
        # Initially hide both widgets
        self.image_label.hide()
        self.text_preview.hide()

    def clear_preview(self):
        """Clear current preview"""
        self.image_label.clear()
        self.text_preview.clear()
        self.image_label.hide()
        self.text_preview.hide()

    def show_preview(self, file_path):
        """Show preview of the selected file"""
        if not os.path.exists(file_path):
            return

        # Clear previous preview
        self.clear_preview()
        
        try:
            # Detect file type using python-magic
            mime = magic.Magic(mime=True)
            file_type = mime.from_file(file_path)
            
            if file_type.startswith('image/'):
                self.show_image_preview(file_path)
            elif file_type.startswith('text/'):
                self.show_text_preview(file_path)
            else:
                # Show file type for unsupported formats
                self.text_preview.setText(f"Preview not available for: {file_type}")
                self.text_preview.show()
        
        except Exception as e:
            self.text_preview.setText(f"Error previewing file: {str(e)}")
            self.text_preview.show()

    def show_image_preview(self, file_path):
        """Show image preview"""
        try:
            # Open and resize image if needed
            with Image.open(file_path) as img:
                # Calculate resize ratio to fit widget
                max_size = QSize(400, 300)
                img.thumbnail((max_size.width(), max_size.height()))
                
                # Convert to QPixmap
                data = io.BytesIO()
                img.save(data, format=img.format)
                pixmap = QPixmap()
                pixmap.loadFromData(data.getvalue())
                
                self.image_label.setPixmap(pixmap)
                self.image_label.show()
        
        except Exception as e:
            self.text_preview.setText(f"Error loading image: {str(e)}")
            self.text_preview.show()

    def show_text_preview(self, file_path, max_size=4096):
        """Show text file preview"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read(max_size)
                if len(text) == max_size:
                    text += "\n... (File truncated)"
                self.text_preview.setText(text)
                self.text_preview.show()
        except Exception as e:
            self.text_preview.setText(f"Error loading text: {str(e)}")
            self.text_preview.show()
