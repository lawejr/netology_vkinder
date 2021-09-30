import sqlalchemy as sq
from sqlalchemy import Column, DateTime, sql
from sqlalchemy.orm import declarative_base

DecBase = declarative_base()


class Base(DecBase):
    __abstract__ = True

    created_at = Column(DateTime, default=sql.func.now())
    updated_at = Column(DateTime, default=sql.func.now(), onupdate=sql.func.now())
    id = sq.Column(sq.Integer, primary_key=True)

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)
