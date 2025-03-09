from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from .models import Base

# Create config directory for secure storage
config_dir = Path.home() / '.config' / 'hood-mail'
config_dir.mkdir(parents=True, exist_ok=True)

# Create database engine
db_path = config_dir / 'mail.db'
engine = create_engine(f'sqlite:///{db_path}')

# Create all tables
Base.metadata.create_all(engine)

# Create session factory
Session = sessionmaker(bind=engine)
