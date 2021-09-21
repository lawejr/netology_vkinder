import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker

from db.models import Base

engine = sq.create_engine('postgresql://vkinder_admin:vkinder@localhost:5432/vkinder')
Session = sessionmaker(bind=engine)

if __name__ == '__main__':
    session = Base.metadata.create_all(engine)
