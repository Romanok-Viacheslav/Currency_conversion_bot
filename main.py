import requests
import telebot
from telebot import types


# Tокен отриманий від BotFather
TOKEN = '6446394565:AAG71RVz0zaRyf_I5ov4N-X-qEJU_4vsytE'
bot = telebot.TeleBot(TOKEN)


# URL для отримання курсу валют від НБУ в форматі JSON
NBU_URL = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json'


# Функція для отримання курсу валют
def get_exchange_rates():
   response = requests.get(NBU_URL)
   if response.status_code == 200:
       return response.json()
   else:
       return None


# Отримання курсів
rates = get_exchange_rates()
if rates is None:
   print("Error: Could not fetch exchange rates from NBU")
   exit()


# Створимо словник для швидкого доступу до курсів
exchange_rates = {item['cc']: item['rate'] for item in rates}
exchange_rates['UAH'] = 1  # Додаємо курс для гривні


# Словник прапорів для валют
currency_flags = {
   "AUD": "🇦🇺",
   "CAD": "🇨🇦",
   "CNY": "🇨🇳",
   "CZK": "🇨🇿",
   "DKK": "🇩🇰",
   "HKD": "🇭🇰",
   "HUF": "🇭🇺",
   "INR": "🇮🇳",
   "IDR": "🇮🇩",
   "ILS": "🇮🇱",
   "JPY": "🇯🇵",
   "KZT": "🇰🇿",
   "KRW": "🇰🇷",
   "MXN": "🇲🇽",
   "MDL": "🇲🇩",
   "NZD": "🇳🇿",
   "NOK": "🇳🇴",
   "RUB": "🇷🇺",
   "SGD": "🇸🇬",
   "ZAR": "🇿🇦",
   "SEK": "🇸🇪",
   "CHF": "🇨🇭",
   "EGP": "🇪🇬",
   "GBP": "🇬🇧",
   "USD": "🇺🇸",
   "BYN": "🇧🇾",
   "AZN": "🇦🇿",
   "RON": "🇷🇴",
   "TRY": "🇹🇷",
   "XDR": "🌐",
   "BGN": "🇧🇬",
   "EUR": "🇪🇺",
   "PLN": "🇵🇱",
   "DZD": "🇩🇿",
   "BDT": "🇧🇩",
   "AMD": "🇦🇲",
   "DOP": "🇩🇴",
   "IRR": "🇮🇷",
   "IQD": "🇮🇶",
   "KGS": "🇰🇬",
   "LBP": "🇱🇧",
   "LYD": "🇱🇾",
   "MYR": "🇲🇾",
   "MAD": "🇲🇦",
   "PKR": "🇵🇰",
   "SAR": "🇸🇦",
   "VND": "🇻🇳",
   "THB": "🇹🇭",
   "AED": "🇦🇪",
   "TND": "🇹🇳",
   "UZS": "🇺🇿",
   "TWD": "🇹🇼",
   "TMT": "🇹🇲",
   "RSD": "🇷🇸",
   "TJS": "🇹🇯",
   "GEL": "🇬🇪",
   "BRL": "🇧🇷",
   "XAU": "🥇",
   "XAG": "🥈",
   "XPT": "🥉",
   "XPD": "🎖"
}


# Додаємо прапор до валюти, якщо він є в словнику прапорів
def get_currency_button(currency):
   flag = currency_flags.get(currency, '')
   return f"{flag}{currency}"


# Отримання списку всіх валют
currency_list = list(exchange_rates.keys())


# Видаляємо прапори з назви валюти
def remove_flag(text):
   for flag in currency_flags.values():
       text = text.replace(flag, '')
   return text.strip()


# Функція для конвертації
def convert(amount, from_currency, to_currency):
   if from_currency not in exchange_rates or to_currency not in exchange_rates:
       return None
   amount_in_uah = amount * exchange_rates[from_currency]
   return amount_in_uah / exchange_rates[to_currency]


# Перший крок: вибір валюти для конвертації
@bot.message_handler(commands=['start'])
def start(message):
   markup = types.ReplyKeyboardMarkup(row_width=4)
   buttons = [types.KeyboardButton(get_currency_button(currency)) for currency in currency_list]
   for i in range(0, len(buttons), 4):
       markup.add(*buttons[i:i + 4])
   bot.send_message(message.chat.id, "Виберіть валюту з якої конвертуємо:", reply_markup=markup)


# Збереження вибору валюти з якої конвертуємо
@bot.message_handler(func=lambda message: remove_flag(message.text) in currency_list)
def choose_from_currency(message):
   from_currency_code = remove_flag(message.text)
   bot.send_message(message.chat.id, f"Ви вибрали {from_currency_code}. Тепер виберіть валюту в яку конвертуємо:")


   markup = types.ReplyKeyboardMarkup(row_width=4)
   buttons = [types.KeyboardButton(get_currency_button(currency)) for currency in currency_list if currency != from_currency_code]
   for i in range(0, len(buttons), 4):
       markup.add(*buttons[i:i + 4])
   bot.send_message(message.chat.id, "Виберіть валюту в яку конвертуємо:", reply_markup=markup)


   bot.register_next_step_handler(message, choose_to_currency, from_currency_code)


# Збереження вибору валюти в яку конвертуємо
def choose_to_currency(message, from_currency_code):
   to_currency_code = remove_flag(message.text)
   bot.send_message(message.chat.id, f"Ви вибрали конвертувати з {from_currency_code} в {to_currency_code}. Введіть суму:")
   bot.register_next_step_handler(message, get_amount, from_currency_code, to_currency_code)


# Введення суми та конвертація
def get_amount(message, from_currency_code, to_currency_code):
   try:
       amount = float(message.text)
       result = convert(amount, from_currency_code, to_currency_code)
       if result is not None:
           bot.send_message(message.chat.id, f"{amount} {from_currency_code} = {result:.2f} {to_currency_code}")
       else:
           bot.send_message(message.chat.id, "Помилка конвертації. Спробуйте ще раз.")
   except ValueError:
       bot.send_message(message.chat.id, "Будь ласка, введіть коректну числову суму.")
   finally:
       start(message)


if __name__ == '__main__':
   bot.polling(none_stop=True)