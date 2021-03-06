import sqlalchemy as sq
from sqlalchemy import CheckConstraint
from constants import RelationType

from .Base import Base


class SearchFilter(Base):
    RESULT_COUNT = 3

    __tablename__ = 'filter'
    __service_fields = ['created_at', 'updated_at', 'id', 'user_id', 'offset']

    sex = sq.Column(sq.Integer)
    age_min = sq.Column(sq.Integer)
    age_max = sq.Column(sq.Integer)
    relation = sq.Column(sq.String, default=RelationType.IN_SEARCH.value)
    city = sq.Column(sq.Integer)
    offset = sq.Column(sq.Integer, default=0)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'))

    @property
    def empty_fields(self):
        return sorted([i for i in self.__dict__.keys() if i[:1] != '_'
                       and i not in self.__service_fields
                       and not getattr(self, i)
                       ], reverse=True)

    @property
    def vk_params(self):
        return {
            'has_photo': 1,
            'sex': self.sex,
            'status': self.relation,
            'city': self.city,
            'age_from': self.age_min,
            'age_to': self.age_max,
            'offset': self.offset,
            'count': SearchFilter.RESULT_COUNT,
            'fields': 'city',
            'v': 5.131
        }

    __table_args__ = (
        CheckConstraint(0 <= sex, name='check_sex_gte_0'),
        CheckConstraint(sex <= 2, name='check_sex_lte_2'),
        {})
