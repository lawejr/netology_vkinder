import vk_api
from VKDatingBot import VKDatingBot

if __name__ == '__main__':
    group_token = input('Введите token группы ВКонтакте: ')
    app_token = input('Введите token с правами на поиск пользователей: ')
    group_api = vk_api.VkApi(token=group_token)
    app_api = vk_api.VkApi(token=app_token)
    VKDatingBot(group_client=group_api, app_client=app_api)
