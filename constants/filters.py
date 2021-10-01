from enum import Enum, IntEnum

# TODO: Проверить использование всех енамов
class GenderType(IntEnum):
    WOMAN = 1
    MAN = 2
    UNKNOWN = 0


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


class Filter(Enum):
    SEX = 'sex'
    AGE_MIN = 'age_min'
    AGE_MAX = 'age_max'
    STATUS = 'status'
    HOME_TOWN = 'home_town'


FilterName = {
    Filter.SEX.value: 'Пол',
    Filter.AGE_MIN.value: 'Минимальный возвраст',
    Filter.AGE_MAX.value: 'Максимальный возвраст',
    Filter.STATUS.value: 'Семейное положение',
    Filter.HOME_TOWN.value: 'Город'
}

