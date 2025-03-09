# Email Client

A modern email client for Linux desktop with multi-account support and secure credential storage.

## Features

- Multi-account support with presets for:
  - Gmail (with OAuth2)
  - Outlook (with OAuth2)
  - Web.de
  - GMX
  - Yahoo (with OAuth2)
  - Custom IMAP/SMTP servers
- Modern Qt6-based user interface
- Secure password storage using encryption
- OAuth2 support for modern authentication
- Email composition with HTML support
- Folder organization and management
- English user interface

## Requirements

- Python 3.8 or higher
- PyQt6
- SQLAlchemy
- cryptography

## Installation

1. Clone the repository:
```bash
git clone https://github.com/EinsPommes/Apps-Hood-os-.git
cd "Apps-Hood-os-/mail client"
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python3 src/main.py
```

2. Add your email account:
   - Click "File" -> "Add Account"
   - Select your email provider from the dropdown
   - For Gmail, Outlook, and Yahoo:
     - Server settings will be automatically configured
     - OAuth2 will be enabled for better security
   - For Web.de and GMX:
     - Server settings will be automatically configured
     - Use your regular password
   - For custom servers:
     - Enter your IMAP and SMTP server details
     - Choose between password or OAuth2 authentication

3. Start using the client:
   - View your folders in the left panel
   - Read emails in the main view
   - Compose new emails using the compose button

## Security

- All passwords are encrypted using Fernet symmetric encryption
- Credentials are stored securely in `~/.config/hood-mail/`
- No plaintext passwords are stored in the database
- Secure connection handling for IMAP/SMTP
- OAuth2 support for providers that recommend it

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is part of Hood OS. All rights reserved.
