from random import randrange
from datetime import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from init_db import Session
from db.models import User, SearchFilter
from constants import Message, GenderType


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
                self.write_msg(vk_id, "Пока((")
                return
            else:
                self.write_msg(vk_id, "Я вас не понял. \n"
                                      "Чтобы с кем-нибудь познакомиться напишите \"Привет\" или \"Start\".")
                return

    def start(self, vk_id):
        self.write_msg(vk_id, f"Хай, {vk_id}")
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
                get_method = getattr(self, f"_get_{field}_filter")
                new_value = get_method(vk_id)
                setattr(user_filter, field, new_value)

            self.save_filter(user.id, user_filter)
            print('Теперь все поля заполнены, можно приступить к поиску')
        else:
            print('Все фильтры заполнены, можно приступить к поиску')

    def get_sex_filter(self, vk_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Девушка 👩', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('Парень 👨', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('Любого пола', color=VkKeyboardColor.SECONDARY)
        keyboard = keyboard.get_keyboard()

        self.write_msg(vk_id, f"Пожалуйста, уточните пол", keyboard=keyboard)

        for filter_event in self.longpoll.listen():
            if VKDatingBot.is_message_to_me(filter_event):
                if filter_event.text == 'Девушка 👩':
                    return 1
                elif filter_event.text == 'Парень 👨':
                    return 2
                elif filter_event.text == 'Любого пола':
                    return 0
                else:
                    self.write_msg(vk_id, f"Пожалуйста, выберите пол из списка", keyboard=keyboard)

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
