# Hood OS File Manager

A modern, efficient file manager with advanced features for Hood OS.

## Features

- **Clean, Minimalist Interface**
  - Tree view for easy directory navigation
  - Icon-based list view for files and folders
  - Horizontal splitter layout
  - Address bar with navigation buttons

- **Advanced File Management**
  - Basic operations (Open, Copy, Cut, Paste, Delete, Rename)
  - File and folder properties viewer
  - Right-click context menu for quick actions
  - Drag and drop support (coming soon)

- **Smart Features**
  - File tagging system
  - Advanced search with filters (name, type, size, tags)
  - Disk usage analyzer with pie chart visualization
  - File previews for common formats

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Linux/macOS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the file manager:
```bash
python main.py
```

### Navigation
- Use the tree view on the left to browse directories
- Double-click folders in the list view to enter them
- Use the address bar to directly enter paths
- Navigation buttons: Back, Forward, Up, Home

### File Operations
- Right-click files/folders for available actions
- Use keyboard shortcuts (Ctrl+C, Ctrl+X, Ctrl+V) for copy/cut/paste
- Drag and drop files between locations (coming soon)

### Advanced Features
- **Tags**: Right-click > Tags > Add/Remove Tag
- **Search**: Click the search icon or press Ctrl+F
- **Disk Analysis**: Right-click folder > Size Analysis

## Dependencies

- Python 3.12+
- PySide6 >= 6.4.0 (Qt for Python)
- Pillow >= 10.0.0 (Image processing)
- python-magic >= 0.4.27 (File type detection)
- matplotlib >= 3.7.0 (Disk usage visualization)
- sqlalchemy >= 2.0.0 (Tag database)
