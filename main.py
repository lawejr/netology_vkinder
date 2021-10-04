import vk_api
from VKDatingBot import VKDatingBot

if __name__ == '__main__':
    # TODO: вернуть запрос токена
    # group_token = input('Введите token группы ВКонтакте: ')
    # app_token = input('Введите token с правами на поиск пользователей: ')
    group_token = 'b886013ad748409f3f5c8568d225fd0fb05394f375a942762aa21366e14dd4e95bec41baf7c94a94e7be5'
    app_token = '0f008a032f9409f5eaab075fa5f9ac914f63f2d0456fb0576c70753bca71c87b4478094fdf46a265c0e2e'
    group_api = vk_api.VkApi(token=group_token)
    app_api = vk_api.VkApi(token=app_token)
    VKDatingBot(group_client=group_api, app_client=app_api)
