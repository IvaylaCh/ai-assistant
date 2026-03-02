from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

# Зарежда .env файла
load_dotenv()

# Взима DATABASE_URL от .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Създава "engine" — връзката към PostgreSQL
# pool_pre_ping=True означава "проверявай дали връзката е жива преди всяка заявка"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal е "фабрика" за database сесии
# autocommit=False — промените не се записват автоматично, трябва изричен commit()
# autoflush=False — не изпращай SQL преди commit
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base клас — всички наши модели ще наследяват от него
class Base(DeclarativeBase):
    pass

# Dependency за FastAPI — дава сесия на всеки endpoint и я затваря след приключване
def get_db():
    db = SessionLocal()
    try:
        yield db          # дай сесията на endpoint-а
    finally:
        db.close()        # ВИНАГИ затвори сесията (дори при грешка)