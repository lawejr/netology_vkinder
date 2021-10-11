import os
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from db.models import Base

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

DB_URL = os.getenv('DB_URL')
if not DB_URL:
    raise EnvironmentError('DB_URL не задан в переменных окружения')

engine = sq.create_engine(DB_URL)
Session = sessionmaker(bind=engine)

if __name__ == '__main__':
    session = Base.metadata.create_all(engine)
