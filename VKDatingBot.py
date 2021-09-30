from random import randrange
from datetime import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from init_db import Session
from db.models import User, SearchFilter


class VKDatingBot:
    def __init__(self, client):
        self.client = client
        self.longpoll = VkLongPoll(self.client)

        print('=== Бот готов принять сообщение в чате ===')
        for event in self.longpoll.listen():
            self._handle_event(event)

    def _handle_event(self, event):
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text.lower()
            user_id = event.user_id

            if request == "привет" or request == "start":
                self._start(user_id)
                return
            elif request == "пока":
                self.write_msg(event.user_id, "Пока((")
                return
            else:
                self.write_msg(event.user_id, "Я вас не понял. \n"
                                              "Чтобы с кем-нибудь познакомиться напишите \"Привет\" или \"Start\".")
                return

    def _start(self, user_id):
        self.write_msg(user_id, f"Хай, {user_id}")
        user = self._get_user_by_id(user_id)

        if not user.search_filter:
            user_filter = SearchFilter()
            user_filter.age_min = user.age
            user_filter.age_max = user.age
            user_filter.sex = user.sex
            user_filter.home_town = user.home_town
            user_filter.status = user.status
            user = self._save_filter(user.id, user_filter)
        else:
            print(user.search_filter.empty_fields)

    def _get_user_by_id(self, user_id):
        session = Session()
        user = session.query(User).filter(User.vk_id == user_id).first()

        if user:
            if user.updated_at.date() == datetime.today().date():
                return user
            else:
                row_user = self.client.method('users.get', {'user_ids': [user_id], 'fields': 'sex,bdate,home_town,status'})[0]
                user.update_from_vk(row_user)
                session.add(user)
                session.commit()
                session.refresh(user)
                return user
        else:
            row_user = self.client.method('users.get', {'user_ids': [user_id], 'fields': 'sex,bdate,home_town,status'})[0]
            user = User.create_from_vk(row_user)
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    def _save_filter(self, user_id, search_filter):
        session = Session()
        user = session.query(User).get(user_id)
        session.add(search_filter)
        user.search_filter = search_filter
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


    def write_msg(self, user_id, message):
        self.client.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})


# message текст сообщения
# text текст сообщения
# user_id 675920716