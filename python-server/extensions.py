# extensions.py
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'mysql+pymysql://username:password@localhost/dbname')

# Create SQLAlchemy engine with better connection pooling for concurrent handling
engine = create_engine(
    DATABASE_URL,
    pool_size=20,           # Increased pool size
    max_overflow=30,        # Allow more overflow connections
    pool_pre_ping=True,     # Enable pessimistic disconnect handling
    pool_recycle=3600,      # Recycle connections every hour
    pool_timeout=30,        # Timeout for getting connection from pool
    echo=False,             # Set to True for SQL debugging
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False
    }
)

# Create base class for models
Base = declarative_base()

# Create session maker with better isolation
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # Keep objects accessible after commit
)

# Database dependency for FastAPI with proper error handling
def get_db():
    db = SessionLocal()
    try:
        # Ensure the session is clean before yielding
        db.rollback()
        yield db
        # Commit if no exceptions occurred
        db.commit()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        try:
            db.rollback()
        except Exception as rollback_error:
            logger.error(f"Error during rollback: {rollback_error}")
        raise
    finally:
        try:
            # Always rollback any pending transaction before closing
            db.rollback()
            db.close()
        except Exception as close_error:
            logger.error(f"Error closing database session: {close_error}")

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
        self.Float = Float
        self.ForeignKey = ForeignKey
        self.relationship = relationship
        self.func = func
    
    def create_all(self):
        Base.metadata.create_all(bind=engine)
    
    def get_session(self):
        """Get a new database session"""
        return SessionLocal()

db = DatabaseWrapper()