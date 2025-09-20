# Hood OS System Settings

A comprehensive system configuration manager for Hood OS with modules for appearance, network, hardware, security, and system preferences.

## Features

### 🎨 Appearance Settings
- **Theme Management**: Light, Dark, and Auto themes
- **Accent Colors**: Customizable accent color selection
- **Font Configuration**: System font and size settings
- **Desktop Customization**: Wallpaper and icon size settings

### 🌐 Network Settings
- **Interface Management**: View and configure network interfaces
- **Connection Settings**: Gateway and DNS configuration
- **Firewall Control**: Enable/disable firewall and port access
- **Network Monitoring**: Real-time network interface status

### 🔒 Security Settings
- **User Account Management**: Add, remove, and manage user accounts
- **Privacy Controls**: Telemetry, crash reports, and usage statistics
- **Security Policies**: Auto-updates, secure boot, and disk encryption
- **Access Control**: Password management and security settings

### 📊 System Information
- **Hardware Overview**: Processor, memory, and architecture details
- **Operating System**: OS version and system information
- **Disk Usage**: Real-time disk space monitoring
- **Performance Metrics**: System resource utilization

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

Run the system settings application:
```bash
python main.py
```

### Navigation
- Use the sidebar to navigate between different settings categories
- Each category contains related configuration options
- Changes are applied immediately or require confirmation

### Settings Categories

#### Appearance
- Customize the visual appearance of Hood OS
- Set themes, fonts, and desktop preferences
- Configure icon sizes and accent colors

#### Network
- Manage network interfaces and connections
- Configure firewall settings and port access
- Set up DNS servers and gateway settings

#### Security
- Manage user accounts and permissions
- Configure privacy and security policies
- Enable/disable security features

#### System Info
- View detailed system information
- Monitor hardware and performance
- Check disk usage and network status

## Architecture

The application follows a modular design with separate widgets for each settings category:

- **SystemSettingsMainWindow**: Main application window with sidebar navigation
- **AppearanceSettings**: Theme, font, and desktop customization
- **NetworkSettings**: Network configuration and firewall management
- **SecuritySettings**: User accounts and security policies
- **SystemInfoWidget**: System information display and monitoring

## Dependencies

- Python 3.8+
- PySide6 >= 6.4.0 (Qt for Python)

## Security Features

- Secure credential storage using Qt settings
- Encrypted configuration files
- User permission validation
- Safe system configuration changes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the existing code style
4. Test your changes thoroughly
5. Submit a pull request

## License

This project is part of Hood OS. All rights reserved.

## System Requirements

- Hood OS or compatible Linux distribution
- Python 3.8 or higher
- Qt6 runtime libraries
- Administrative privileges for system configuration changes
