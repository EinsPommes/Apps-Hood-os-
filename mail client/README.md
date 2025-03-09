# Hood OS Mail Client

A modern, feature-rich email client built with Python and Qt6 for Hood OS. This application provides a robust and user-friendly interface for managing multiple email accounts with support for both OAuth2 and traditional authentication methods.

## Features

- **Multi-Account Support**
  - Support for multiple email providers (Gmail, Outlook, Custom)
  - OAuth2 authentication for modern email services
  - Traditional username/password authentication
  - Secure credential storage

- **Email Management**
  - IMAP/SMTP support for email synchronization
  - Folder organization (Inbox, Sent, Drafts, Trash, etc.)
  - Email composition with HTML support
  - File attachments with drag-and-drop support
  - Search and filter capabilities

- **Modern Interface**
  - Clean and intuitive Qt6-based UI
  - Customizable themes and layouts
  - Email preview pane
  - Unread message counters
  - Rich text email composition

- **Security Features**
  - Encrypted credential storage
  - SSL/TLS support for secure connections
  - Remote content blocking
  - Spam filtering

## Requirements

- Python 3.8+
- Qt 6.4.0+
- Required Python packages (see requirements.txt)

## Installation

1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python src/main.py
   ```

## Configuration

The application stores its configuration in the following locations:
- Email accounts: SQLite database in `data/mailclient.db`
- Application settings: Qt settings storage
- OAuth2 configuration: `config/oauth2_config.json`

## Development

The project follows a Model-View-Controller (MVC) architecture:

- **Models**: Handle data management and business logic
  - `models/email_list_model.py`: Email list display model
  - `models/folder_tree_model.py`: Folder hierarchy model
  - `database/models.py`: Database models for accounts and emails

- **Views**: User interface components
  - `ui/main_window.py`: Main application window
  - `ui/compose_dialog.py`: Email composition dialog
  - `ui/account_dialog.py`: Account management dialog
  - `ui/settings_dialog.py`: Application settings dialog

- **Utils**: Helper classes and utilities
  - `utils/email_service.py`: Email service implementation
  - `utils/oauth2_handler.py`: OAuth2 authentication handler

## License

This project is part of Hood OS and follows its licensing terms.

## Contributing

When contributing to this project, please:
1. Follow the existing code style
2. Add unit tests for new features
3. Update documentation as needed
4. Ensure all tests pass before submitting changes
