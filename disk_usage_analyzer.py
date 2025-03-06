import os
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class DiskUsageAnalyzer(QWidget):
    """Widget for analyzing and visualizing directory sizes"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Create Matplotlib Figure
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def analyze_directory(self, directory):
        """Analyze directory sizes and create pie chart visualization"""
        # Collect folder sizes
        sizes = []
        labels = []
        
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            if os.path.isdir(path):
                size = self.get_directory_size(path)
                if size > 0:  # Only show non-empty folders
                    sizes.append(size)
                    labels.append(item)
        
        # Sort by size
        sizes, labels = zip(*sorted(zip(sizes, labels), reverse=True))
        
        # Show only top 10
        if len(sizes) > 10:
            sizes = sizes[:10]
            labels = labels[:10]
        
        # Create plot
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Create pie chart
        sizes_mb = [size / (1024 * 1024) for size in sizes]  # Convert to MB
        ax.pie(sizes_mb, labels=labels, autopct='%1.1f%%')
        ax.set_title('Directory Size Distribution')
        
        self.canvas.draw()

    def get_directory_size(self, directory):
        """Calculate total size of a directory recursively"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, FileNotFoundError):
                    continue
        return total_size
