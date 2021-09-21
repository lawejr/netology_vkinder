import sqlalchemy as sq

from .Base import Base


class Dating(Base):
    __tablename__ = 'dating'

    id = sq.Column(sq.Integer, primary_key=True)

    pass
