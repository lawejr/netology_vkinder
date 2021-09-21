import sqlalchemy as sq

from .Base import Base


class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)

    pass
