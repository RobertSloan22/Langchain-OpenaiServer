from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Replace these variables with your actual database credentials
DB_USERNAME = 'your_actual_username'
DB_PASSWORD = 'your_actual_password'
DB_HOST = 'your_actual_host'
DB_PORT = 'your_actual_port'  # e.g., '5432'
DB_NAME = 'your_actual_db_name'

DATABASE_URL = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
