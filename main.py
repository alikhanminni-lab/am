import telebot
import json
import os
from Flask import Flask, requests
import requests
import gdown
import re
import logging
import sys

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    sys.exit("Переменная API-TOKEN не задана в переменных окружения")


bot = telebot.TeleBot(API_TOKEN)




if os.path.exists("data.json") and os.path.getsize("data.json") != 0:
    with open("data.json", "r", encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {"users": {}}
    with open("data.json", "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

app = Flask(__name__)

@app.route("/")
def index ():
    return"бот запущен"
@app.route(f"/{API_TOKEN}", methods=['POST'])
def webhook():
    try:
        json_str = requests.get_data(as_text=True)
        update = telebot.types.Update.de_json(json_str)
        if update:
            bot.process_new_updates([update])
    except Exception as e:
        app.logger.exception(e)
    return "", 200

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if str(user_id) not in data["users"]:


        data["users"][str(user_id)] = {}
        data["users"][str(user_id)]["status"] = "name"
        with open("data.json", "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        bot.send_message(message.chat.id, "как тебя зовут ?")
        return

    data["users"][str(user_id)]["money"] = 10000
    with open("data.json", "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_1 = telebot.types.KeyboardButton("курс доллара")

    keyboard.add(btn_1)
    btn_2 = telebot.types.KeyboardButton("курс евро")
    diceButton = telebot.types.KeyboardButton('Игра в кубик')
    slotButton = telebot.types.KeyboardButton('Игровая рулетка')
    keyboard.add(btn_2, diceButton, slotButton)
    bot.send_message(message.chat.id, "Привет", reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def answer(message):
    user_id = message.from_user.id

    if data["users"][str(user_id)]["status"] == "name":
        data["users"][str(user_id)]["name"] = message.text


        data["users"][str(user_id)]["status"] = "age"
        bot.send_message(message.chat.id, "сколько тебе лет?")
        with open("data.json", "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return
    elif data["users"][str(user_id)]["status"] == "age":
        data["users"][str(user_id)]["age"] = message.text

        data["users"][str(user_id)]["status"] = "city"
        bot.send_message(message.chat.id, "из какого ты города ?")
        with open("data.json", "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return
    elif data["users"][str(user_id)]["status"] == "city":
        data["users"][str(user_id)]["city"] = message.text

        data["users"][str(user_id)]["status"] = None
        data["users"][str(user_id)]["money"] = 10000
        with open("data.json", "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        start(message)
    elif data["users"][str(user_id)]["status"] == "bet":

        try:
            bet = int(message.text)
            if bet > int(data ["users"][str(user_id)]["money"]):
                bot.send_message(message.chat.id, "недостаточно кредитов для ставки")
                return
            elif bet < 0:
                bot.send_message(message.chat.id, "Ставка не может быть отрицательной")
                return
            else :
                bet = int(message.text)
                data["users"][str(user_id)]["money"]-=bet
                with open("data.json", "w", encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                bot.send_message(message.chat.id, f"ставка принята,\n текущий баланс {data['users'][str(user_id)]['money']}")
                slotGame(message, bet)
                return
        except ValueError as e:
            bot.send_message(message.chat.id, "нужно ввести число")
            print(e)
            return
        except Exception as e:
            bot.send_message(message.chat.id, "неизвестная ошибка")
            print(e)
            return
    if message.text == 'Привет':
        bot.send_message(message.chat.id, 'Привет')
    elif message.text == 'что ты делаешь ?':
        bot.send_message(message.chat.id, "я обмениваю валюту")
    elif message.text == 'курс доллара':
        bot.send_message(message.chat.id, "78")
    elif message.text == "курс евро":
        bot.send_message(message.chat.id, "92")
    elif message.text == "Игра в кубик":
        diceGame(message)
    elif message.text == 'Игровая рулетка':
        bot.send_message(message.chat.id, "введите ставку")
        data["users"][str(user_id)]["status"] = "bet"
        with open("data.json", "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        bot.send_message(message.chat.id, message.text )

def slotGame(message, bet):
    value = bot.send_dice(message.chat.id, emoji="🎰").dice.value
    user_id = message.from_user.id
    if value in (1,22,43):
        data["users"][str(message.from_user.id)]["money"] += bet * 6
        bot.send_message(message.chat.id, f"big win \n текущий баланс {data['users'][str(user_id)]['money']}")
        with open("data.json", "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    elif value in (16,32,48):
        data["users"][str(message.from_user.id)]["money"] += bet * 3.5
        bot.send_message(message.chat.id, f"win \n текущий баланс {data['users'][str(user_id)]['money']}")
        with open("data.json", "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    elif value ==64:
        data["users"][str(message.from_user.id)]["money"] += bet * 15
        bot.send_message(message.chat.id, f"jackpot \n текущий баланс {data['users'][str(user_id)]['money']}")
        with open("data.json", "w", encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    else:
        bot.send_message(message.chat.id, "ты проиграл")
    data["users"][str(message.from_user.id)]["status"] = None
    with open("data.json", "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)





def diceGame(message):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)

    btn1 = telebot.types.InlineKeyboardButton("1", callback_data='1')
    btn2 = telebot.types.InlineKeyboardButton("2", callback_data='2')
    btn3 = telebot.types.InlineKeyboardButton("3", callback_data='3')
    btn4 = telebot.types.InlineKeyboardButton("4", callback_data='4')
    btn5 = telebot.types.InlineKeyboardButton("5", callback_data='5')
    btn6 = telebot.types.InlineKeyboardButton("6", callback_data="6")

    keyboard.add(btn1,btn2,btn3,btn4,btn5,btn6)
    bot.send_message(message.chat.id, "угадай число на кубике", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data in ('1', '2', '3', '4', '5', '6'))
def throwDice(call):
    value = bot.send_dice(call.message.chat.id, emoji='').dice.value

    if str(value) == call.data:
        bot.send_message(call.message.chat.id, "угадал")
    else:
        bot.send_message(call.message.chat.id, "попробуй еще раз ")


if __name__ == '__main__':
    SERVER_URL = os.getenv("RENDER_EXTERNAL_URL")

    if SERVER_URL and API_TOKEN:
        webhook_url = f "{SERVER_URL.rstrip("/")}/{API_TOKEN}"

        try:
            r=requests.get(f"https://api.telegram.org/bot{API_TOKEN}/setWebhook", params={"url": webhook_url}, timeout=10)

            logging.info("Вебхук установлен")
        except Exception as e:
            logging.error("ошибка при установке webhook")
        port = int(os.environ.get("PORT", 10000))
        logging.info(f"Запуск приложения на порте {port}")
        app.run (host = "0.0.0.0", port=port)
    else:
        logging.info("Запуск бота в режиме polling")
        bot.remove_webhook()
        bot.infinity_polling(timeout=60)
        
