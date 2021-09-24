from random import randrange
from vk_api.longpoll import VkLongPoll, VkEventType
from init_db import Session
from db.models import User


class VKDatingBot:
    def __init__(self, client):
        self.client = client
        self.longpoll = VkLongPoll(self.client)

        print('=== Бот готов принять сообщение в чате ===')
        for event in self.longpoll.listen():
            self._handle_event(event)

    def _handle_event(self, event):
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text

                user = self._get_user_by_id(event.user_id)

                if request == "привет":
                    self.write_msg(event.user_id, f"Хай, {event.user_id}")
                elif request == "пока":
                    self.write_msg(event.user_id, "Пока((")
                else:
                    self.write_msg(event.user_id, "Не понял вашего ответа...")

    def _get_user_by_id(self, user_id):
        session = Session()
        user = session.query(User).filter(User.vk_id == user_id).first()

        if user:
            return user
        else:
            row_user = self.client.method('users.get', {'user_ids': [user_id], 'fields': 'sex,bdate,home_town,status'})[0]
            user = User.from_vk(row_user)
            session.add(user)
            session.commit()
        return user

    def write_msg(self, user_id, message):
        self.client.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})


# message текст сообщения
# text текст сообщения
# user_id 675920716