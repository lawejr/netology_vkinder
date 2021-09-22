from random import randrange
from vk_api.longpoll import VkLongPoll, VkEventType


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

                if request == "привет":
                    self.write_msg(event.user_id, f"Хай, {event.user_id}")
                elif request == "пока":
                    self.write_msg(event.user_id, "Пока((")
                else:
                    self.write_msg(event.user_id, "Не понял вашего ответа...")

    def write_msg(self, user_id, message):
        self.client.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})