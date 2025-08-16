# extensions.py
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'mysql+pymysql://username:password@localhost/dbname')

# Create SQLAlchemy engine with connection pooling for better concurrent handling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Enable pessimistic disconnect handling
    pool_recycle=3600,   # Recycle connections every hour
    echo=False  # Set to True for SQL debugging
)

# Create base class for models
Base = declarative_base()

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# For backward compatibility with Flask-SQLAlchemy style
class DatabaseWrapper:
    def __init__(self):
        self.engine = engine
        # Provide Flask-SQLAlchemy compatible attributes
        self.Model = Base
        self.Column = Column
        self.Integer = Integer
        self.String = String
        self.Text = Text
        self.Boolean = Boolean
        self.DateTime = DateTime
        self.ForeignKey = ForeignKey
        self.relationship = relationship
        self.func = func
    
    def create_all(self):
        Base.metadata.create_all(bind=engine)
    
    # Remove session-specific methods as they should be handled per request
    def get_session(self):
        """Get a new database session"""
        return SessionLocal()

db = DatabaseWrapper()