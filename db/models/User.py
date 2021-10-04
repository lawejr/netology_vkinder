import sqlalchemy as sq
from datetime import date
from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint

from .Base import Base


class User(Base):
    __tablename__ = 'user'

    vk_id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    sex = sq.Column(sq.Integer, default=0)
    birth_date = sq.Column(sq.Date)
    status = sq.Column(sq.String)
    city = sq.Column(sq.Integer)
    search_filter = relationship('SearchFilter', uselist=False, cascade='delete')

    @property
    def profile_link(self):
        return f'https://vk.com/id{self.id}'

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

            return age
        else:
            return None

    __table_args__ = (
        CheckConstraint(0 <= sex, name='check_sex_gte_0'),
        CheckConstraint(sex <= 2, name='check_sex_lte_2'),
        {})

    @classmethod
    def create_from_vk(cls, row_user):
        user = cls()

        user.vk_id = row_user.get('id')
        user.first_name = row_user.get('first_name')
        user.last_name = row_user.get('last_name')
        user.sex = row_user.get('sex')
        user.birth_date = row_user.get('bdate')
        user.status = row_user.get('status')
        user.city = row_user.get('city', {}).get('id')

        return user

    def update_from_vk(self, row_user):
        self.vk_id = row_user.get('id')
        self.first_name = row_user.get('first_name')
        self.last_name = row_user.get('last_name')
        self.sex = row_user.get('sex')
        self.birth_date = row_user.get('bdate')
        self.status = row_user.get('status')
        self.city = row_user.get('city', {}).get('id')
