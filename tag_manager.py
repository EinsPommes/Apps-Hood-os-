from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
import os

Base = declarative_base()

class FileTag(Base):
    """SQLAlchemy model for file tags"""
    __tablename__ = 'file_tags'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String, nullable=False)
    tag = Column(String, nullable=False)

class TagManager:
    """Manages file tagging operations using SQLAlchemy"""
    def __init__(self, db_path='tags.db'):
        """Initialize tag manager with SQLite database"""
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_tag(self, file_path, tag):
        """Add a tag to a file"""
        file_tag = FileTag(file_path=file_path, tag=tag)
        self.session.add(file_tag)
        self.session.commit()

    def remove_tag(self, file_path, tag):
        """Remove a tag from a file"""
        self.session.query(FileTag).filter_by(
            file_path=file_path, tag=tag
        ).delete()
        self.session.commit()

    def get_tags(self, file_path):
        """Get all tags for a file"""
        tags = self.session.query(FileTag.tag).filter_by(
            file_path=file_path
        ).all()
        return [tag[0] for tag in tags]

    def get_files_by_tag(self, tag):
        """Get all files with a specific tag"""
        files = self.session.query(FileTag.file_path).filter_by(
            tag=tag
        ).all()
        return [file[0] for file in files]

    def clear_missing_files(self):
        """Remove tags for files that no longer exist"""
        all_tags = self.session.query(FileTag).all()
        for tag in all_tags:
            if not os.path.exists(tag.file_path):
                self.session.delete(tag)
        self.session.commit()
