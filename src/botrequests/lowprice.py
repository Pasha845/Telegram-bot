from decouple import config
from requests import get
import telebot
import requests
import json

core_bot = telebot.TeleBot(config("telebot_key"))
server_key = config("rapidapi_key")


class Users:
    users = dict()

    def __init__(self, user_id):
        self.city_name = list()
        self.hotels_quantity = list()
        self.photo_quantity = list()
        self.id_town = list()
        self.hotel_id = list()
        self.name_hotel = list()
        self.address = list()
        self.destination = list()
        self.price = list()
        self.url_photo = list()
        Users.add_user(user_id, self)

    @staticmethod
    def get_user(user_id):
        if Users.users.get(user_id) is None:
            new_user = Users(user_id)
            return new_user
        return Users.users.get(user_id)

    @classmethod
    def add_user(cls, user_id, user):
        cls.users[user_id] = user


@core_bot.message_handler(commands=["start"])
def greetings(message):
    core_bot.send_message(message.chat.id, "Добрый день, что бы вы хотели узнать?")


@core_bot.message_handler(content_types=["text"])
def get_command(message):
    if message.text == "/help":
        core_bot.send_message(message.chat.id, "Бот выполняет следующие команды:\n"
                                               "/help — помощь по командам бота;\n"
                                               "/lowprice — вывод самых дешёвых отелей в городе;\n"
                                               "/highprice - вывод самых дорогих отелей в городе;\n "
                                               "/bestdeal - вывод отелей, наиболее подходящих по цене и "
                                               "расположению от центра;\n"
                                               "/history — вывод истории поиска отелей")

    elif message.text == "/lowprice":
        core_bot.send_message(message.chat.id, "Введите название города")
        core_bot.register_next_step_handler(message, get_city)
    else:
        core_bot.send_message(message.chat.id, "Я тебя не понимаю. Напиши /help")


def get_city(message):
    user = Users.get_user(message.chat.id)
    if not message.text.isalpha():
        core_bot.send_message(message.chat.id, "Название города дожно состоять только из букв! "
                                               "Попробуйте еще раз")
        core_bot.register_next_step_handler(message, get_city)
        return
    else:
        user.city_name.append(message.text)
        core_bot.send_message(message.chat.id, "Введите количество отелей, не более 25")
        core_bot.register_next_step_handler(message, get_quantity)


def get_quantity(message):
    user = Users.get_user(message.chat.id)
    if not message.text.isdigit():
        core_bot.send_message(message.chat.id, "Количество отелей пишется числом без пробелов! "
                                               "Попробуйте еще раз")
        core_bot.register_next_step_handler(message, get_quantity)
        return
    elif int(message.text) < 1:
        core_bot.send_message(message.chat.id, "Количество отелей не может быть меньше 1! "
                                               "Попробуйте еще раз")
        core_bot.register_next_step_handler(message, get_quantity)
        return
    else:
        user.hotels_quantity.append(int(message.text))
        core_bot.send_message(message.chat.id, "Хотите вывести фотографии отеля, Да/Нет")
        core_bot.register_next_step_handler(message, get_photo)


def get_photo(message):
    user = Users.get_user(message.chat.id)
    if message.text == "Да":
        core_bot.send_message(message.chat.id, "Сколько вывести фотографий?")
        core_bot.register_next_step_handler(message, get_volume_photo)
    elif message.text == "Нет":
        user.photo_quantity.append(0)
        core_bot.send_message(message.chat.id, "Введите любой символ для подтверждения")
        core_bot.register_next_step_handler(message, get_info)
    else:
        core_bot.send_message(message.chat.id, "Команда введена неправильно! "
                                               'Введите "Да" или "Нет"')
        core_bot.register_next_step_handler(message, get_photo)
        return


def get_volume_photo(message):
    user = Users.get_user(message.chat.id)
    if not message.text.isdigit():
        core_bot.send_message(message.chat.id, "Количество фотографий пишется числом без пробелов! "
                                               "Попробуйте еще раз")
        core_bot.register_next_step_handler(message, get_volume_photo)
        return
    elif int(message.text) < 1:
        core_bot.send_message(message.chat.id, "Количество фотографий не может быть меньше 1! "
                                               "Попробуйте еще раз")
        core_bot.register_next_step_handler(message, get_volume_photo)
        return
    else:
        user.photo_quantity.append(int(message.text))
        core_bot.send_message(message.chat.id, "Введите любой символ для подтверждения")
        core_bot.register_next_step_handler(message, get_info)


def get_info(message):
    user = Users.get_user(message.chat.id)
    city_url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    city_querystring = {"query": user.city_name[-1],
                        "locale": "ru_RU", "currency": "USD"}
    hotel_headers = {
        "x-rapidapi-host": "hotels4.p.rapidapi.com",
        "x-rapidapi-key": server_key
    }
    url_info = requests.get(city_url, headers=hotel_headers, params=city_querystring)
    data_city = json.loads(url_info.text)
    user.id_town.append(int(data_city["suggestions"][0]["entities"][0]["destinationId"]))
    hotel_url = "https://hotels4.p.rapidapi.com/properties/list"
    hotel_querystring = {"destinationId": user.id_town[-1],
                         "pageSize": user.hotels_quantity[-1], "adults1": "1",
                         "sortOrder": "PRICE", "currency": "USD", "locale": "ru_RU"}
    hotel_site = requests.get(hotel_url, headers=hotel_headers, params=hotel_querystring)
    info_data = json.loads(hotel_site.text)
    if "data" in info_data:
        core_bot.send_message(message.chat.id,
                              f"\nСписок отелей города {user.city_name[-1]}:\n")
        for elem in info_data["data"]["body"]["searchResults"]["results"]:
            if "ratePlan" in elem and "address" in elem:
                user.hotel_id.append(int(elem["id"]))
                user.name_hotel.append(elem["name"])
                user.address.append(elem["address"]["streetAddress"])
                user.destination.append(elem["landmarks"][0]["distance"])
                user.price.append(elem["ratePlan"]["price"]["exactCurrent"])
                core_bot.send_message(message.chat.id,
                                      f"\nНазвание отеля: {user.name_hotel[-1]};"
                                      f"\nАдрес: {user.address[-1]};"
                                      f"\nРасстояние от центра: {user.destination[-1]};"
                                      f"\nЦена: {user.price[-1]} $;\n")
                if user.photo_quantity[-1] != 0:
                    url_photo = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
                    querystring = {"id": user.hotel_id[-1]}
                    response = requests.request("GET", url_photo, headers=hotel_headers, params=querystring)
                    data_city = json.loads(response.text)
                    photo = data_city["hotelImages"][0]["sizes"][0]["suffix"]
                    for num, thing in enumerate(data_city["hotelImages"]):
                        if num < user.photo_quantity[-1]:
                            user.url_photo.append(thing["baseUrl"].replace("{size}", photo))
                            core_bot.send_photo(message.chat.id,
                                                get(user.url_photo[-1]).content)
                        else:
                            break
        core_bot.send_message(message.chat.id, "Поиск отелей завершен! Введите соответствующую команду бота, чтобы "
                                               "начать новый поиск отелей")
    else:
        core_bot.send_message(message.chat.id, "Извините. В этом городе бот не сможет найти отели! "
                                               "Введите другой город")
        core_bot.register_next_step_handler(message, get_command)
        return


if __name__ == '__main__':
    core_bot.polling(none_stop=True, interval=0)
