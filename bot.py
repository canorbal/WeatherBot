import telebot
import config
from requests import get
import bisect
import pymorphy2
import re
from datetime import datetime
import bing_picture


weather_command = "weather"
help_command = "help"
bot = telebot.TeleBot(config.token)


def parse_input(text):

    text = [char for char in text if char not in config.DEPRECATED_SYMBOLS]
    text = "".join(text)
    words = text.split(" ")

    normalizer = pymorphy2.MorphAnalyzer()
    words = [normalizer.parse(word)[0].normal_form
             for word in words]
    return words


def find_date(words, verbose=False):
    day_of_week = []
    for number, value in enumerate(config.DAY_OF_WEEK.values()):
        day_of_week += [number for word in words
                        if word in value]

    month = []
    for number, value in enumerate(config.MONTHS.values()):
        month += [number for word in words
                  if word in value]

    relatives = []
    for number, value in enumerate(config.RELATIVE.values()):
        relatives += [number + 1 for word in words
                      if word in value]

    now = []
    for value in config.NOW.values():
        now += [word for word in words
                if word in value]

    if len(now) > 0:
        now = True
    else:
        now = False

    if verbose:
        print(" ".join(day_of_week))
        print(" ".join(month))
        print("now = {}".format(now))

    return day_of_week, month, now, relatives


def find_format_date(text):
    return re.findall('(\d{2})[/.-](\d{2})', text)


def find_city(text):

    city = {}

    for word in text:
        if word in config.STOP_WORDS:
            continue

        if len(word) < 3:
            continue

        index_geo_id = bisect.bisect_left(config.KEYS, word.strip().title())

        if (index_geo_id != len(config.GEO_ID) and
                config.GEO_ID[index_geo_id]["name"] == word.title()):

            city.update({word.title():
                             str(config.GEO_ID[index_geo_id]["geoid"])})
    return city


def decode_cloudness(value):
    if value == 0:
        return "ясно"
    elif value == 0.25:
        return "малооблачно"
    elif value == 0.5:
        return "облачно с прояснениями"
    elif value == 0.75:
        return "облачно с прояснениями"
    else:
        return "пасмурно"


def decode_prec(value):
    return config.PREC_TYPE[value]


def make_answer(city, index, req):

    weather = req.json()["forecasts"][index]

    answer = ""
    answer += "Погода в " + city + " " + weather["date"] + "\n"

    answer += "Температура днём {} °C\n".\
        format(weather["parts"]["day"]["temp_avg"])

    answer += "Температура ночью {} °C\n".\
        format(weather["parts"]["night"]["temp_avg"])

    day_info = weather["parts"]["day"]

    answer += "Скорость ветра {} м/с\n".format(day_info["wind_speed"])

    answer += "Давление {} (в мм рт. ст.)\n".\
        format(day_info["pressure_mm"])

    answer += "Облачность: {}\n".\
        format(decode_cloudness(day_info["cloudness"]))

    answer += "Осадки: {}\n".\
        format(decode_prec(day_info["prec_type"]))
    return answer


def find_cloudness_in_answer(index, req):
    weather = req.json()["forecasts"][index]
    day_info = weather["parts"]["day"]
    return decode_cloudness(day_info["cloudness"])


def find_prec_in_answer(index, req):
    weather = req.json()["forecasts"][index]
    day_info = weather["parts"]["day"]
    return decode_prec(day_info["prec_type"])


@bot.message_handler(commands=[help_command])
def handle_help(message):
    bot.send_message(message.chat.id, config.HELP_MESSAGE)


@bot.message_handler(commands=[weather_command])
def handle_start_help(message):

    input_string = message.text.replace("/" + weather_command, "").strip()
    if len(input_string) == 0:
        bot.send_message(message.chat.id, config.NO_ENTRY_FOUND)
        return

    format_date = find_format_date(input_string)

    input_words = parse_input(input_string)
    city = find_city(input_words)
    input_words = [str.lower(word) for word in input_words]
    day_of_week, month, today, relatives = find_date(input_words)

    if len(city) == 0:
        bot.send_message(message.chat.id, config.NO_CITY_FOUND)
        return

    geo_id = list(city.values())[0]
    city = list(city.keys())[0]

    index = 0

    if len(relatives) > 0:
        index = relatives[0]

    if len(day_of_week) > 0:
        day_of_week = day_of_week[0]
        today = datetime.weekday(datetime.today())

        if today < day_of_week:
            index = day_of_week - today - 1
        elif today > day_of_week:
            index = 7 + day_of_week - today - 1

    if len(format_date) > 0:

        print(format_date)
        mm = int(format_date[0][1])
        dd = int(format_date[0][0])

        if dd not in range(1, 32):
            bot.send_message(message.chat.id, config.WRONG_DATA)
            return

        if mm not in range(1, 13):
            bot.send_message(message.chat.id, config.WRONG_DATA)
            return

        forecast_for_datetime = datetime(2017, mm, dd)

        today = datetime.today()
        index = (forecast_for_datetime - today).days

    if index not in range(0, 10):
        bot.send_message(message.chat.id, config.FORECAST_ATTENTION)
        return

    string_api = "https://api.weather.yandex.ru/v1/forecast?" \
                 "geoid=" + geo_id + "&l10n=true&" \
                                     "limit=10&extra=true"

    try:
        req = get(string_api, headers=config.yandex_header)

        bot.send_message(message.chat.id, make_answer(city, index, req))

        query = city + " " + find_prec_in_answer(index, req)
        print(query)
        url_photo = bing_picture.find_picture(query)
        if url_photo is None:
            bot.send_message(message.chat.id, config.NO_PICTURE_FOUND)
        bot.send_photo(message.chat.id, photo=url_photo)
    except Exception:
        bot.send_message(message.chat.id, config.SMTH_GO_WRONG)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    bot.send_message(message.chat.id, config.SUPPORT)


if __name__ == '__main__':
    bot.polling(none_stop=True)
