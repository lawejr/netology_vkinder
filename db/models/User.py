import sqlalchemy as sq
from sqlalchemy import CheckConstraint

from .Base import Base


class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    sex = sq.Column(sq.Integer, default=0)
    birth_date = sq.Column(sq.Date)
    status = sq.Column(sq.String)
    home_town = sq.Column(sq.String)

    @property
    def profile_link(self):
        return f'https://vk.com/id{self.id}'

    @property
    def age(self):
        if self.birth_date:
            # TODO: текущая дата - self.birth_date
            return 0
        else:
            return None

    __table_args__ = (
        CheckConstraint(0 <= sex <= 2, name='check_sex_from_0_to_2'),
        {})


