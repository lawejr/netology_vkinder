import sqlalchemy as sq

from .Base import Base


class Dating(Base):
    __tablename__ = 'dating'

    user_id = sq.Column(sq.ForeignKey('user.id'), primary_key=True)
    candidate_id = sq.Column(sq.ForeignKey('user.id'), primary_key=True)
