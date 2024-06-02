from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Replace these variables with your actual database credentials
DB_USERNAME = ''
DB_PASSWORD = '
DB_HOST = ''
DB_PORT = ''  # e.g., '5432'
DB_NAME = ''

DATABASE_URL = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
