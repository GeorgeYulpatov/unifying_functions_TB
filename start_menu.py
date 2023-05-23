import aiogram
import weather
import requests
import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from config import TOKEN_API, open_weather_token, api_key, base_url

bot = Bot(TOKEN_API)
dp: Dispatcher = Dispatcher(bot)
# Кнопки основного меню
kb = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton(text='Погода')
b2 = KeyboardButton('/Конвертер_валют')
b3 = KeyboardButton('/Милое_фото')
b4 = KeyboardButton('/Создать_опрос')
kb.add(b1).insert(b2).add(b3).insert(b4)




# Функция фотографии
def get_dog():
    resource = requests.get('https://dog.ceo/api/breeds/image/random').json()
    return resource['message']


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text='Добро пожаловать!При помощи этого бота можно узнать погоду в своем городе,'
                                'произвеси конвертацию валют, получить милую картинку и создать опрос(в разработке).',
                           reply_markup=kb)

    await message.delete()


# Вывод погоды


@dp.message_handler(commands=['Погода'])
async def weather_command(message: types.Message):
    await message.answer("Напиши мне название города, я пришлю сводку погоды!")
    await message.delete()

    @dp.message_handler()
    async def get_weather(message: types.Message):
        code_to_smile = {  # Забираю данные из  сформированного json для того чтобы подставить эмоджи
            'Clear': 'Ясно \U00002600',
            'Clouds': 'Облачно \U00002601',
            'Rain': 'Дождь \U00002614',
            'Drizzle': 'Дщждь \U00002614',
            'Thunderstorm': 'Гроза \U000026A1',
            'Snow': 'Снег \U0001F328',
            'Mist': 'Туман \U0001F32B'

        }

        try:
            r = requests.get(  # Подсветилась библиотека requests
                f"https://api.openweathermap.org/data/2.5/weather?q={message.text}&appid={open_weather_token}&units=metric"
            )  # Сформировал запрос
            data = r.json()
            # pprint(data)
            # Забираю данные из  сформированного json
            city = data['name']  # Город
            cur_weather = data['main']['temp']  # Температура

            weather_description = data['weather'][0]['main']  # Вид погоды + эмоджи
            if weather_description in code_to_smile:
                wd = code_to_smile[weather_description]
            else:
                wd = 'Посмотрие в окно, не пойму что там за погода!'

            humidity = data['main']['humidity']  # Влажность
            pressure = data['main']['pressure']  # Давление
            wind = data['wind']['speed']  # Скорость ветра
            sunrise_timestamp = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
            sunset_timestamp = datetime.datetime.fromtimestamp(data['sys']['sunset'])
            length_of_day = datetime.datetime.fromtimestamp(data['sys']['sunset']) - datetime.datetime.fromtimestamp(
                data['sys']['sunrise'])
            # Заполняю плейсхолдеры
            await message.answer(f"***{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                                f'Погода в городе: {city}\nТемпература: {cur_weather}°C {wd}\n'
                                f'Влажность: {humidity}%\nДавление: {pressure}  мм.рт.ст\nВетер: {wind} м/с\n'
                                f'Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\n'
                                f'Продолжительность дня: {length_of_day}\n'
                                f'***Хорошего дня***'
                                )

        except:
            await message.answer("\U00002620 Проверьте название города \U00002620")



@dp.message_handler(commands=['Конвертер_валют'])
async def conversion(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id, text='Введите сумму в RUB для перевода в USD')
    await message.delete()


    @dp.message_handler()
    async def get_conversion(message: types.Message):
        from_c = 'USD'
        to_c = 'RUB'

        user_number = message.text
        print(message.text)
        main_url = base_url + '&from_currency=' + from_c + '&to_currency=' + to_c + '&apikey=' + api_key
        response = requests.get(main_url)
        result = response.json()
        key = result['Realtime Currency Exchange Rate']
        rate = key['5. Exchange Rate']
        rate_c = float(rate)
        conversion_result = (float(user_number) * rate_c)

        await message.answer(f'1 {from_c} : {rate} {to_c}\n'
                            f'{user_number} {from_c} : {conversion_result} {to_c}')


@dp.message_handler(commands=['Милое_фото'])
async def photo_command(message):
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=get_dog(), reply_markup=kb)
    await message.delete()


@dp.message_handler(commands=['Создать_опрос'])
async def desc_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Функция находится в разработке",
                           parse_mode="HTML", reply_markup=kb)
    await message.delete()


if __name__ == "__main__":
    executor.start_polling(dp)
