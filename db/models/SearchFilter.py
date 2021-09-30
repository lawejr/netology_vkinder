import sqlalchemy as sq
from sqlalchemy import CheckConstraint

from .Base import Base


class SearchFilter(Base):
    __tablename__ = 'filter'
    __service_fields = ['created_at', 'updated_at', 'id', 'user_id']

    sex = sq.Column(sq.Integer, default=0)
    age_min = sq.Column(sq.Integer)
    age_max = sq.Column(sq.Integer)
    status = sq.Column(sq.String)
    home_town = sq.Column(sq.String)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'))

    @property
    def empty_fields(self):
        return [i for i in self.__dict__.keys() if i[:1] != '_' and i not in self.__service_fields]

    __table_args__ = (
        CheckConstraint(0 <= sex, name='check_sex_gte_0'),
        CheckConstraint(sex <= 2, name='check_sex_lte_2'),
        {})
