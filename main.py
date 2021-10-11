import os
import vk_api
from vk_api.longpoll import VkLongPoll
from dotenv import load_dotenv

from VKDatingBot import VKDatingBot

if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    APP_TOKEN = os.getenv('APP_TOKEN')
    GROUP_TOKEN = os.getenv('GROUP_TOKEN')
    if not APP_TOKEN:
        raise EnvironmentError('APP_TOKEN не задан в переменных окружения')
    if not GROUP_TOKEN:
        raise EnvironmentError('GROUP_TOKEN не задан в переменных окружения')

    app_api = vk_api.VkApi(token=APP_TOKEN)
    group_api = vk_api.VkApi(token=GROUP_TOKEN)

    # Проверка созданных клиентов api и токенов на валидность, в случае ошибки будет выброшено исключение
    app_api.method('users.get')
    VkLongPoll(group_api)
    # Если проверка пройдена передаём управление боту
    VKDatingBot(group_client=group_api, app_client=app_api)
