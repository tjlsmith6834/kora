import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Load database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure all required variables are set
if not all([DATABASE_URL]):
    raise ValueError("⚠️ Missing required database environment variables!")

# Initialize the engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    # optional tuning:
    pool_size=10,
    max_overflow=20,
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI
def get_db() -> Session:
    """Dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db  # Provide the session to the request
    finally:
        db.close()  # Ensure session is closed