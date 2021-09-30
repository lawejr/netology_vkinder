import vk_api
from VKDatingBot import VKDatingBot

if __name__ == '__main__':
    # TODO: вернуть запрос токена
    # token = input('Введите token ВКонтакте: ')
    token = 'b886013ad748409f3f5c8568d225fd0fb05394f375a942762aa21366e14dd4e95bec41baf7c94a94e7be5'
    vk = vk_api.VkApi(token=token)

    VKDatingBot(vk)
