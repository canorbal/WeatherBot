from operator import itemgetter
from requests import get
import string

token = "*************************"

yandex_header = {'X-Yandex-API-Key': '*****************************'}


def get_geo_id():
    string = "https://api.weather.yandex.ru/v1/locations?lang=ru_RU"
    req = get(string,
              headers={'X-Yandex-API-Key':
                           '982cb0f7-f2ba-44ec-92ff-90ee399c473e'})

    return sorted(req.json(), key = itemgetter("name"))


GEO_ID = get_geo_id()
KEYS = [value["name"] for value in GEO_ID]


NO_CITY_FOUND = "Такого города нет"
NO_ENTRY_FOUND = "Вы ничего не ввели"
FORECAST_ATTENTION = "Прогноз возможен на ближайшие 10 дней"
SUPPORT = "Используйте команду \weather"
NO_PICTURE_FOUND = "Картинку города с такой погодой найти не получилось"
WRONG_DATA = "Что-то не так с датой"
SMTH_GO_WRONG = "Что-то пошло не так"

HELP_MESSAGE = '''
Это телеграм бот для получения прогноза погоды.
Чтобы начать, вызовите команду /weather
Пример: /weather погода на субботу в москве
'''





DEPRECATED_SYMBOLS = set(string.punctuation) - set("-")


PREC_TYPE = {
    0: "без осадков",
    1: " дождь",
    2: "дождь со снегом",
    3: "снег"
}


DAY_OF_WEEK = {
    0: ["понедельник", "пндк", "пн"],
    1: ["вторник", "вт"],
    2: ["среда", "ср"],
    3: ["четверг", "чт"],
    4: ["пятница", "пт"],
    5: ["суббота", "сб"],
    6: ["воскресенье", "вскр", "вс", "вск", "воскресение"]
}


MONTHS = {
    0: ["январь"],
    1: ["февраль"],
    2: ["март"],
    3: ["апрель"],
    4: ["май"],
    5: ["июнь"],
    6: ["июль"],
    7: ["август"],
    8: ["сентябрь"],
    9: ["октябрь"],
    10: ["ноябрь"],
    11: ["декабрь"],
}


NOW = {
    0: "сейчас",
    1: "сегодня",
}

RELATIVE = {
    1: ["завтра"],
    2: ["послезавтра"]
}


def flatit(iterable):

    for elem in iterable:
        if hasattr(elem, "__iter__"):

            if isinstance(elem, str):
                yield elem
            else:
                yield from flatit(elem)
        else:
            yield elem


STOP_WORDS = list(flatit(DAY_OF_WEEK.values()))
STOP_WORDS += list(flatit(MONTHS.values()))
STOP_WORDS += list(flatit(NOW.values()))
STOP_WORDS += list(flatit(RELATIVE.values()))
STOP_WORDS = set(STOP_WORDS)