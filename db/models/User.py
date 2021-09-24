import sqlalchemy as sq
from sqlalchemy import CheckConstraint

from .Base import Base


class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer)
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
        CheckConstraint(0 <= sex, name='check_sex_gte_0'),
        CheckConstraint(sex <= 2, name='check_sex_lte_2'),
        {})

    @classmethod
    def from_vk(cls, row_user):
        user = cls()

        user.vk_id = row_user.get('id')
        user.first_name = row_user.get('first_name')
        user.last_name = row_user.get('last_name')
        user.sex = row_user.get('sex')
        user.birth_date = row_user.get('bdate')
        user.status = row_user.get('status')
        user.home_town = row_user.get('home_town')

        return user

