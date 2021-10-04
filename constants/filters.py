from enum import Enum, IntEnum

class GenderType(IntEnum):
    WOMAN = 1
    MAN = 2
    UNKNOWN = 0

    @property
    def name(self):
        return _GenderTypeName[self]


_GenderTypeName = {
    GenderType.WOMAN: 'Девушка ♀️',
    GenderType.MAN: 'Парень ♂️',
    GenderType.UNKNOWN: 'Любой пол'
}


class RelationType(IntEnum):
    NOT_MARRIED = 1
    HAS_FRIEND = 2
    ENGAGED = 3
    MARRIED = 4
    DIFFICULTLY = 5
    IN_SEARCH = 6
    IN_LOVE = 7
    CIVIL_MARRIED = 8
    UNKNOWN = 0

    @property
    def name(self):
        return _RelationTypeName[self]


_RelationTypeName = {
    RelationType.NOT_MARRIED: 'Не женат / не замужем',
    RelationType.HAS_FRIEND: 'Есть друг / есть подруга',
    RelationType.ENGAGED: 'Помолвлен / помолвлена',
    RelationType.MARRIED: 'Женат / Замужем',
    RelationType.DIFFICULTLY: 'Всё сложно',
    RelationType.IN_SEARCH: 'В активном поиске',
    RelationType.IN_LOVE: 'Влюблён / влюблена',
    RelationType.CIVIL_MARRIED: 'В гражданском браке',
    RelationType.UNKNOWN: 'Не указано'
}


class FilterType(Enum):
    SEX = 'sex'
    AGE_MIN = 'age_min'
    AGE_MAX = 'age_max'
    RELATION = 'relation'
    CITY = 'city'

    @property
    def name(self):
        return _FilterName[self]


_FilterName = {
    FilterType.SEX: 'Пол',
    FilterType.AGE_MIN: 'Минимальный возвраст',
    FilterType.AGE_MAX: 'Максимальный возвраст',
    FilterType.RELATION: 'Семейное положение',
    FilterType.CITY: 'Город'
}

