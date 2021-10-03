from random import randrange
from datetime import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from init_db import Session
from db.models import User, SearchFilter
from constants import Message, GenderType, RelationType


class VKDatingBot:
    @staticmethod
    def is_message_to_me(event):
        return event.type == VkEventType.MESSAGE_NEW and event.to_me

    def __init__(self, client):
        self.db_session = Session()
        self.client = client
        self.longpoll = VkLongPoll(self.client)

        print('=== Бот готов принять сообщение в чате ===')
        for event in self.longpoll.listen():
            self.handle_event(event)

    def handle_event(self, event):
        if VKDatingBot.is_message_to_me(event):
            request = event.text.lower()
            vk_id = event.user_id

            if request == Message.HELLO.value or request == Message.START.value:
                self.start(vk_id)
                return
            elif request == Message.BYE.value:
                self.write_msg(vk_id, 'Пока((')
                return
            else:
                self.write_msg(vk_id, 'Я вас не понял. \n'
                                      'Чтобы с кем-нибудь познакомиться напишите "Привет" или "Start".')
                return

    def start(self, vk_id):
        self.write_msg(vk_id, f'Хай, {vk_id}')
        user = self.get_user_by_vkid(vk_id)
        user_filter = SearchFilter()

        if not user.search_filter:
            user_filter.age_min = user.age
            user_filter.age_max = user.age
            user_filter.home_town = user.home_town
            if user.sex == GenderType.MAN.value:
                user_filter.sex = GenderType.WOMAN.value
            elif user.sex == GenderType.MAN.value:
                user_filter.sex = GenderType.MAN.value
            user = self.save_filter(user.id, user_filter)
        else:
            user_filter = user.search_filter

        empty_fields = user_filter.empty_fields

        if empty_fields:
            for field in empty_fields:
                get_method = getattr(self, f'get_{field}_filter')
                new_value = get_method(vk_id, user_filter)
                setattr(user_filter, field, new_value)

            self.save_filter(user.id, user_filter)
            print('Теперь все поля заполнены, можно приступить к поиску')
        else:
            print('Все фильтры заполнены, можно приступить к поиску')

    def get_sex_filter(self, vk_id, _):
        girl = 'Девушка 👩'
        boy = 'Парень 👨'
        anyone = 'Любого пола'

        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(girl, color=VkKeyboardColor.PRIMARY)
        keyboard.add_button(boy, color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(anyone, color=VkKeyboardColor.SECONDARY)
        keyboard = keyboard.get_keyboard()

        self.write_msg(vk_id, 'Пожалуйста, уточните пол', keyboard=keyboard)

        for filter_event in self.longpoll.listen():
            if VKDatingBot.is_message_to_me(filter_event):
                if filter_event.text == girl:
                    return GenderType.WOMAN.value
                elif filter_event.text == boy:
                    return GenderType.MAN.value
                elif filter_event.text == anyone:
                    return GenderType.UNKNOWN.value
                else:
                    self.write_msg(vk_id, 'Выберите пол из списка', keyboard=keyboard)

    def get_age_min_filter(self, vk_id, _):
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

    def get_home_town_filter(self, vk_id, _):
        print(vk_id)

    def get_relation_filter(self, vk_id, _):
        NOT_MARRIED = 'Не женат / не замужем'
        HAS_FRIEND = 'Есть друг / есть подруга'
        ENGAGED = 'Помолвлен / помолвлена'
        DIFFICULTLY = 'Всё сложно'
        IN_SEARCH = 'В активном поиске'
        IN_LOVE = 'Влюблён / влюблена'
        CIVIL_MARRIED = 'В гражданском браке'
        UNKNOWN = 'Не указано'

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

        for filter_event in self.longpoll.listen():
            if VKDatingBot.is_message_to_me(filter_event):
                if filter_event.text == NOT_MARRIED:
                    return RelationType.NOT_MARRIED.value
                elif filter_event.text == HAS_FRIEND:
                    return RelationType.HAS_FRIEND.value
                elif filter_event.text == ENGAGED:
                    return RelationType.ENGAGED.value
                elif filter_event.text == DIFFICULTLY:
                    return RelationType.DIFFICULTLY.value
                elif filter_event.text == IN_SEARCH:
                    return RelationType.IN_SEARCH.value
                elif filter_event.text == IN_LOVE:
                    return RelationType.IN_LOVE.value
                elif filter_event.text == CIVIL_MARRIED:
                    return RelationType.CIVIL_MARRIED.value
                elif filter_event.text == UNKNOWN:
                    return RelationType.UNKNOWN.value
                else:
                    self.write_msg(vk_id, 'Выберите пол из списка', keyboard=keyboard)

    def get_user_by_vkid(self, vk_id):
        session = self.db_session
        user = session.query(User).filter(User.vk_id == vk_id).first()

        if user:
            if user.updated_at.date() == datetime.today().date():
                return user
            else:
                row_user = \
                    self.client.method('users.get', {'user_ids': [vk_id], 'fields': 'sex,bdate,home_town,status'})[0]
                user.update_from_vk(row_user)
                session.add(user)
                session.commit()
                session.refresh(user)
                return user
        else:
            row_user = self.client.method('users.get', {'user_ids': [vk_id], 'fields': 'sex,bdate,home_town,status'})[0]
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

    def write_msg(self, vk_id, message, keyboard=None):
        self.client.method('messages.send', {
            'user_id': vk_id,
            'message': message,
            'random_id': randrange(10 ** 7),
            'keyboard': keyboard
        })
