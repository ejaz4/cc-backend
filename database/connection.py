import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

from config import Config

logger = logging.getLogger(__name__)

# Create SQLAlchemy base class
Base = declarative_base()

# Global engine and session factory
engine = None
SessionLocal = None

def init_database():
    """Initialize database connection"""
    global engine, SessionLocal
    
    try:
        # Create engine
        engine = create_engine(
            Config.DATABASE_URL,
            poolclass=StaticPool,
            pool_pre_ping=True,
            echo=Config.DEBUG  # Log SQL queries in debug mode
        )
        
        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        logger.info("Database connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def get_db_session():
    """Get database session"""
    if SessionLocal is None:
        init_database()
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db():
    """Context manager for database sessions"""
    if SessionLocal is None:
        init_database()
    
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    if engine is None:
        init_database()
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise

def drop_tables():
    """Drop all tables (use with caution!)"""
    if engine is None:
        init_database()
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        raise

def check_connection():
    """Check if database connection is working"""
    try:
        with get_db() as db:
            db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False 