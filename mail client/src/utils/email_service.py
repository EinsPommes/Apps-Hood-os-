import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import email
import os
from datetime import datetime
from .crypto import decrypt_password

class EmailService:
    def __init__(self, config):
        self.email = config['email']
        self.encrypted_credentials = config.get('encrypted_credentials', config.get('password', ''))  # Support both old and new field names
        self.imap_server = config['imap_server']
        self.smtp_server = config['smtp_server']
        self.use_oauth2 = config.get('use_oauth2', False)
        self.oauth2_refresh_token = config.get('oauth2_refresh_token')
        self.imap = None
        self.smtp = None

    def _get_password(self):
        """Get decrypted password"""
        if self.use_oauth2:
            return None  # OAuth2 doesn't use password
        return decrypt_password(self.encrypted_credentials)

    def connect(self):
        """Connect to email servers"""
        try:
            # Get decrypted password if not using OAuth2
            password = None
            if not self.use_oauth2:
                password = self._get_password()
                if not password:
                    raise Exception("No password available")

            # Connect to IMAP
            self.imap = imaplib.IMAP4_SSL(self.imap_server)
            if self.use_oauth2:
                raise NotImplementedError("OAuth2 authentication is not yet implemented")
            else:
                self.imap.login(self.email, password)

            # Connect to SMTP
            self.smtp = smtplib.SMTP(self.smtp_server)
            self.smtp.starttls()
            if not self.use_oauth2:
                self.smtp.login(self.email, password)

        except Exception as e:
            if self.imap:
                try:
                    self.imap.logout()
                except:
                    pass
            if self.smtp:
                try:
                    self.smtp.quit()
                except:
                    pass
            raise Exception(f"Connection failed: {str(e)}")

    def disconnect(self):
        """Disconnect from email servers"""
        try:
            if self.imap:
                self.imap.logout()
                self.imap = None
            if self.smtp:
                self.smtp.quit()
                self.smtp = None
        except Exception as e:
            raise Exception(f"Error disconnecting: {str(e)}")

    def test_connection(self):
        """Test connection to email servers"""
        try:
            self.connect()
            self.disconnect()
            return True
        except:
            return False

    def get_folders(self):
        """Get list of email folders"""
        try:
            if not self.imap:
                self.connect()
            
            folders = []
            for folder_data in self.imap.list()[1]:
                folder_name = folder_data.decode().split('"/"')[-1].strip('" ')
                folders.append(folder_name)
            
            # Add default folders if not present
            default_folders = ['INBOX', 'Sent', 'Drafts', 'Trash', 'Spam']
            for folder in default_folders:
                if folder not in folders:
                    folders.append(folder)

            return sorted(folders)
            
        except Exception as e:
            raise Exception(f"Could not retrieve folders: {str(e)}")

    def get_emails(self, folder, limit=50):
        """Get emails from specified folder"""
        try:
            if not self.imap:
                self.connect()

            self.imap.select(folder)
            _, messages = self.imap.search(None, 'ALL')
            email_list = []

            # Get the last 'limit' messages
            message_numbers = messages[0].split()
            start_index = max(0, len(message_numbers) - limit)
            
            for num in message_numbers[start_index:]:
                _, msg_data = self.imap.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)

                # Decode subject
                subject = decode_header(email_message['subject'])[0]
                subject = subject[0].decode() if isinstance(subject[0], bytes) else subject[0]

                # Get sender
                sender = decode_header(email_message['from'])[0]
                sender = sender[0].decode() if isinstance(sender[0], bytes) else sender[0]

                # Get date
                date_str = email_message['date']
                date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')

                # Get body
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/html":
                            body = part.get_payload(decode=True).decode()
                            break
                        elif part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                else:
                    body = email_message.get_payload(decode=True).decode()

                email_list.append({
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'body': body
                })

            return email_list
        except Exception as e:
            raise Exception(f"Could not retrieve emails from {folder}: {str(e)}")

    def send_email(self, to, subject, body):
        """Send email"""
        try:
            if not self.smtp:
                self.connect()

            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = to
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            self.smtp.send_message(msg)
            return True
        except Exception as e:
            raise Exception(f"Could not send email: {str(e)}")

    def refresh_oauth2_token(self):
        """Refresh OAuth2 token"""
        # TODO: Implement OAuth2 token refresh
        pass

    def __del__(self):
        """Cleanup connections"""
        self.disconnect()
