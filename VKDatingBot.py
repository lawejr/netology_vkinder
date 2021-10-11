from random import randrange
from datetime import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from init_db import Session
from db.models import User, SearchFilter
from constants import GenderType, RelationType, FilterType


class VKDatingBot:
    @staticmethod
    def is_message_to_me(event):
        return event.type == VkEventType.MESSAGE_NEW and event.to_me

    def __init__(self, group_client, app_client):
        self.db_session = Session()
        self.group_client = group_client
        self.app_client = app_client
        self.longpoll = VkLongPoll(self.group_client)

        print('=== Бот готов принять сообщение в чате ===')
        for event in self.longpoll.listen():
            self.handle_event(event)

    def handle_event(self, event):
        if VKDatingBot.is_message_to_me(event):
            request = event.text.lower()
            vk_id = event.user_id

            if request == 'привет' or request == 'start':
                self.init(vk_id)
                return
            elif request == 'пока' or request == 'stop':
                self.write_msg(vk_id, 'До свидания! Если с кем-нибудь познакомиться напишите  "Привет" или "Start".')
                return
            else:
                START = 'Start'
                init_keyboard = VkKeyboard(one_time=True)
                init_keyboard.add_button(START, color=VkKeyboardColor.PRIMARY)
                init_keyboard = init_keyboard.get_keyboard()
                self.write_msg(vk_id, 'Я вас не понял. \n'
                                      'Чтобы с кем-нибудь познакомиться напишите "Привет" или "Start".', keyboard=init_keyboard)
                return

    def init(self, vk_id):
        user = self.get_user_by_vkid(vk_id)
        self.write_msg(vk_id, f'Привет, {user.first_name}! Я могу помочь вам с кем-нибудь познакомиться.')

        user_filter = SearchFilter()

        if not user.search_filter:
            user_filter.age_min = user.age
            user_filter.age_max = user.age
            user_filter.city = user.city

            if user.sex == GenderType.MAN:
                user_filter.sex = GenderType.WOMAN
            elif user.sex == GenderType.MAN:
                user_filter.sex = GenderType.MAN
            user = self.save_filter(user.id, user_filter)
        else:
            user_filter = user.search_filter

        if user_filter.empty_fields:
            self.write_msg(vk_id, 'Давайте уточним некоторые параметры для поиска')

            for field in user_filter.empty_fields:
                get_method = getattr(self, f'get_{field}_filter')
                new_value = get_method(vk_id, user_filter)
                setattr(user_filter, field, new_value)

            self.save_filter(user.id, user_filter)
            self.start(vk_id, user_filter, init_message='Теперь все готово, можем приступить к поиску')
        else:
            self.start(vk_id, user_filter)

    def start(self, vk_id, filter, init_message='Выберите действие из списка:'):
        START = 'Искать'
        EDIT = 'Изменить параметры'
        start_keyboard = VkKeyboard(one_time=True)
        start_keyboard.add_button(START, color=VkKeyboardColor.PRIMARY)
        start_keyboard.add_button(EDIT, color=VkKeyboardColor.SECONDARY)
        start_keyboard = start_keyboard.get_keyboard()

        display_city = self.app_client.method('database.getCitiesById', {'city_ids': filter.city})[0].get('title') \
            if filter.city \
            else 'Любой'

        self.write_msg(vk_id, 'Параметры поиска:\n'
                              '\n'
                              f'Пол: {GenderType(filter.sex).name}\n'
                              f'Возраст: от {filter.age_min} до {filter.age_max}\n'
                              f'Семейное положение: {filter.relation}\n'
                              f'Город: {display_city}')
        self.write_msg(vk_id, init_message, keyboard=start_keyboard)

        for start_event in self.longpoll.listen():
            if self.is_message_to_me(start_event):
                if start_event.text == START:
                    result = self.start_search(vk_id)

                    if not result:
                        self.write_msg(vk_id, 'Не удалось найти пользователей по заданным параметрам.\n'
                                              'Попробуйте изменить настройки поиска')
                        return self.edit_filter(vk_id)
                    else:
                        self.write_msg(vk_id, 'Вот кого я нашёл:')

                        for people in result:
                            candidate = User.create_from_vk(people)
                            photos = ','.join(self.select_photos(candidate.vk_id))
                            self.write_msg(vk_id, f'{candidate.first_name} {candidate.last_name}\n'
                                                  f'{candidate.profile_link}', attachment=photos)

                        self.write_msg(vk_id,
                                       'Можем поискать ещё или изменить параметры поиска',
                                       keyboard=start_keyboard)
                elif start_event.text == EDIT:
                    return self.edit_filter(vk_id)
                else:
                    self.write_msg(vk_id,
                                   'Я вас не понял. \n'
                                   'Выберите действие из списка',
                                   keyboard=start_keyboard)

    def start_search(self, vk_id):
        result = self.search(vk_id)
        filtered_result = list(filter(lambda item: not item['is_closed'], result))

        if not result:
            return None
        elif filtered_result:
            return filtered_result
        else:
            return self.start_search(vk_id)

    def search(self, vk_id):
        user = self.get_user_by_vkid(vk_id)
        candidate_param = user.search_filter.vk_params

        result = self.app_client.method('users.search', candidate_param).get('items')

        user.search_filter.offset += SearchFilter.RESULT_COUNT
        self.save_filter(user.id, user.search_filter)

        return result

    def get_sex_filter(self, vk_id, _=None):
        GIRL = GenderType.WOMAN.name
        BOY = GenderType.MAN.name
        ANYONE = GenderType.UNKNOWN.name

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(GIRL, color=VkKeyboardColor.PRIMARY)
        keyboard.add_button(BOY, color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(ANYONE, color=VkKeyboardColor.SECONDARY)
        keyboard = keyboard.get_keyboard()

        self.write_msg(vk_id, 'Пожалуйста, уточните пол', keyboard=keyboard)

        for filter_event in self.longpoll.listen():
            if VKDatingBot.is_message_to_me(filter_event):
                if filter_event.text == GIRL:
                    return GenderType.WOMAN
                elif filter_event.text == BOY:
                    return GenderType.MAN
                elif filter_event.text == ANYONE:
                    return GenderType.UNKNOWN
                else:
                    self.write_msg(vk_id, 'Выберите пол из списка', keyboard=keyboard)

    def get_age_min_filter(self, vk_id, _=None):
        self.write_msg(vk_id, 'Укажите минимальный возраст партнера цифрами. Например: 20')

        for min_age_event in self.longpoll.listen():
            if VKDatingBot.is_message_to_me(min_age_event):
                try:
                    result = int(min_age_event.text)

                    if 14 <= result <= 90:
                        return result
                    else:
                        raise ValueError('Значение меньше 14 или больше 90')
                except ValueError:
                    self.write_msg(vk_id, 'К сожалению, вы указали недопустимый возраст.\n'
                                          'Введите число от 14 до 90')

    def get_age_max_filter(self, vk_id, current_filter):
        self.write_msg(vk_id, 'Укажите максимальный возраст партнера в цифрах. Например, 30')
        for max_age_event in self.longpoll.listen():
            if VKDatingBot.is_message_to_me(max_age_event):
                try:
                    result = int(max_age_event.text)

                    if current_filter.age_min and current_filter.age_min <= result <= 90:
                        return result
                    elif not current_filter.age_min and 14 <= result <= 90:
                        return result
                    else:
                        raise ValueError('Значение меньше минимального фильтра или больше 90')
                except ValueError:
                    self.write_msg(vk_id, 'К сожалению, вы указали недопустимый возраст.\n'
                                          f'Введите число от '
                                          f'{current_filter.age_min if current_filter.age_min else 14} до 90')

    def get_city_filter(self, vk_id, _=None):
        self.write_msg(vk_id, 'Напишите название российского города, в котором будем искать:')

        for city_event in self.longpoll.listen():
            if VKDatingBot.is_message_to_me(city_event):
                city_param = {
                    'q': city_event.text,
                    'country_id': 1,
                    'count': 1,
                    'v': 5.131
                }

                result_cities = self.app_client.method('database.getCities', city_param).get('items')

                if not result_cities:
                    self.write_msg(vk_id, f'В России не удалось найти город "{city_event.text}".\n'
                                          'Попробуйте ввести другое название города:')
                elif city_event.text.lower() != result_cities[0].get('title', '').lower():
                    YES = 'Да'
                    NO = 'Нет'

                    keyboard = VkKeyboard(one_time=True)
                    keyboard.add_button(YES, color=VkKeyboardColor.POSITIVE)
                    keyboard.add_button(NO, color=VkKeyboardColor.NEGATIVE)
                    keyboard = keyboard.get_keyboard()

                    self.write_msg(vk_id, f'Вы имели ввиду город {result_cities[0].get("title")}?', keyboard=keyboard)

                    for confirm_event in self.longpoll.listen():
                        if VKDatingBot.is_message_to_me(confirm_event):
                            if confirm_event.text == YES:
                                return result_cities[0].get('id')
                            else:
                                self.write_msg(vk_id, f'В России не удалось найти город "{city_event.text}".\n'
                                                      'Попробуйте ввести другое название города:')
                                break
                else:
                    return result_cities[0].get('id')

    def get_relation_filter(self, vk_id, _=None):
        NOT_MARRIED = RelationType.NOT_MARRIED.name
        HAS_FRIEND = RelationType.HAS_FRIEND.name
        ENGAGED = RelationType.ENGAGED.name
        DIFFICULTLY = RelationType.DIFFICULTLY.name
        IN_SEARCH = RelationType.IN_SEARCH.name
        IN_LOVE = RelationType.IN_LOVE.name
        CIVIL_MARRIED = RelationType.CIVIL_MARRIED.name
        UNKNOWN = RelationType.UNKNOWN.name

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(IN_SEARCH, color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(NOT_MARRIED, color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button(UNKNOWN, color=VkKeyboardColor.SECONDARY)
        keyboard.add_button(DIFFICULTLY, color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(HAS_FRIEND, color=VkKeyboardColor.SECONDARY)
        keyboard.add_button(ENGAGED, color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(IN_LOVE, color=VkKeyboardColor.SECONDARY)
        keyboard.add_button(CIVIL_MARRIED, color=VkKeyboardColor.SECONDARY)
        keyboard = keyboard.get_keyboard()

        self.write_msg(vk_id, 'Выберите семейное положение', keyboard=keyboard)

        for relation_event in self.longpoll.listen():
            if VKDatingBot.is_message_to_me(relation_event):
                if relation_event.text == NOT_MARRIED:
                    return RelationType.NOT_MARRIED
                elif relation_event.text == HAS_FRIEND:
                    return RelationType.HAS_FRIEND
                elif relation_event.text == ENGAGED:
                    return RelationType.ENGAGED
                elif relation_event.text == DIFFICULTLY:
                    return RelationType.DIFFICULTLY
                elif relation_event.text == IN_SEARCH:
                    return RelationType.IN_SEARCH
                elif relation_event.text == IN_LOVE:
                    return RelationType.IN_LOVE
                elif relation_event.text == CIVIL_MARRIED:
                    return RelationType.CIVIL_MARRIED
                elif relation_event.text == UNKNOWN:
                    return RelationType.UNKNOWN
                else:
                    self.write_msg(vk_id, 'Выберите пол из списка', keyboard=keyboard)

    def get_user_by_vkid(self, vk_id):
        session = self.db_session
        user = session.query(User).filter(User.vk_id == vk_id).first()
        users_params = {'user_ids': [vk_id], 'fields': 'sex,bdate,city,status'}

        if user:
            if user.updated_at.date() == datetime.today().date():
                return user
            else:
                row_user = \
                    self.app_client.method('users.get', users_params)[0]
                user.update_from_vk(row_user)
                session.add(user)
                session.commit()
                session.refresh(user)
                return user
        else:
            row_user = self.app_client.method('users.get', users_params)[0]
            user = User.create_from_vk(row_user)
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    def save_filter(self, user_id, search_filter):
        session = self.db_session
        user = session.query(User).get(user_id)
        session.add(search_filter)
        user.search_filter = search_filter
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    def edit_filter(self, vk_id):
        user = self.get_user_by_vkid(vk_id)

        SEX = FilterType.SEX.name
        CITY = FilterType.CITY.name
        RELATION = FilterType.RELATION.name
        AGE_MIN = FilterType.AGE_MIN.name
        AGE_MAX = FilterType.AGE_MAX.name
        CANCEL = 'Отменить'

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(SEX, color=VkKeyboardColor.SECONDARY)
        keyboard.add_button(CITY, color=VkKeyboardColor.SECONDARY)
        keyboard.add_button(RELATION, color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(AGE_MIN, color=VkKeyboardColor.SECONDARY)
        keyboard.add_button(AGE_MAX, color=VkKeyboardColor.SECONDARY)
        keyboard.add_line()
        keyboard.add_button(CANCEL, color=VkKeyboardColor.PRIMARY)
        keyboard = keyboard.get_keyboard()

        self.write_msg(vk_id, 'Что хотите изменить?', keyboard=keyboard)

        for edit_event in self.longpoll.listen():
            if VKDatingBot.is_message_to_me(edit_event):
                prev_value = None
                is_updated = False
                result = user.search_filter or SearchFilter()

                if edit_event.text == SEX:
                    prev_value = result.sex
                    result.sex = self.get_sex_filter(vk_id)
                    is_updated = prev_value and result.sex != prev_value
                elif edit_event.text == CITY:
                    prev_value = result.city
                    result.city = self.get_city_filter(vk_id)
                    is_updated = prev_value and result.city != prev_value
                elif edit_event.text == RELATION:
                    prev_value = result.relation
                    result.relation = self.get_relation_filter(vk_id)
                    is_updated = prev_value and result.relation != prev_value
                elif edit_event.text == AGE_MIN:
                    prev_value = result.age_min
                    result.age_min = self.get_age_min_filter(vk_id)
                    is_updated = prev_value and result.age_min != prev_value
                elif edit_event.text == AGE_MAX:
                    prev_value = result.age_max
                    result.age_max = self.get_age_max_filter(vk_id, result)
                    is_updated = prev_value and result.age_max != prev_value
                elif edit_event.text == CANCEL:
                    return self.start(vk_id, result)
                else:
                    self.write_msg(vk_id, 'Выберите действие из списка', keyboard=keyboard)
                    continue

                if is_updated:
                    result.offset = 0
                self.save_filter(user.id, result)
                return self.start(vk_id, result, init_message='Параметры поиска изменены, '
                                                              'можем приступить к поиску')

    def select_photos(self, owner_id):
        photo_param = {'owner_id': owner_id, 'album_id': 'profile',
                       'extended': '1', 'count': '20', 'photo_sizes': '0', 'v': 5.131}
        photos = self.app_client.method('photos.get', photo_param)
        photos_count = 3 if photos.get('count') >= 3 else photos.get('count')
        photo_list = photos.get('items')
        photo_dict = {}
        if photos_count:
            for photo in photo_list:
                photo_id = photo.get('id')
                likes = photo.get('likes', {}).get('count')
                photo_dict[likes] = f'photo{owner_id}_{photo_id}'

        photo_dict = {likes_count: photo_dict[likes_count] for likes_count in sorted(photo_dict, reverse=True)}
        result = list(photo_dict.values())[0:photos_count]
        return result

    def write_msg(self, vk_id, message, attachment=None, keyboard=None):
        self.group_client.method('messages.send', {
            'user_id': vk_id,
            'message': message,
            'attachment': attachment,
            'random_id': randrange(10 ** 7),
            'keyboard': keyboard
        })
