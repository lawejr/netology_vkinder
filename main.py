import vk_api
from VKDatingBot import VKDatingBot

if __name__ == '__main__':
    token = input('Введите token ВКонтакте: ')
    vk = vk_api.VkApi(token=token)

    VKDatingBot(vk)
