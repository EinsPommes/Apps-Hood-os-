from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from cryptography.fernet import Fernet
import json
import os

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    encrypted_credentials = Column(String, nullable=True)  # Null if using OAuth2
    imap_server = Column(String, nullable=False)
    smtp_server = Column(String, nullable=False)
    use_oauth2 = Column(Boolean, default=False)
    oauth2_refresh_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    folders = relationship("Folder", back_populates="account", cascade="all, delete-orphan")
    emails = relationship("Email", back_populates="account", cascade="all, delete-orphan")

class Folder(Base):
    __tablename__ = 'folders'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account = relationship("Account", back_populates="folders")
    emails = relationship("Email", back_populates="folder", cascade="all, delete-orphan")

class Email(Base):
    __tablename__ = 'emails'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(String, nullable=False)
    subject = Column(String)
    sender = Column(String)
    recipients = Column(Text)
    body = Column(Text)
    received_date = Column(DateTime)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    folder_id = Column(Integer, ForeignKey('folders.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account = relationship("Account", back_populates="emails")
    folder = relationship("Folder", back_populates="emails")
    attachments = relationship("Attachment", back_populates="email", cascade="all, delete-orphan")

class Attachment(Base):
    __tablename__ = 'attachments'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    content_type = Column(String)
    size = Column(Integer)
    data = Column(Text)  # Base64 encoded data
    email_id = Column(Integer, ForeignKey('emails.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    email = relationship("Email", back_populates="attachments")

def init_db():
    """Initialize the database"""
    # Create database directory if it doesn't exist
    db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    os.makedirs(db_dir, exist_ok=True)

    # Create database engine
    db_path = os.path.join(db_dir, 'email.db')
    engine = create_engine(f'sqlite:///{db_path}')

    # Create all tables
    Base.metadata.create_all(engine)
    return engine
