import sqlite3
import telebot
import config

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands = ['start'])
def welcome(message):
    bot.send_message(message.chat.id, """Приветствую, {0.first_name}!\n Это бот, созданный для организации процесса стриминга в нашем проекте. Здесь ты можешь отмечать время, когда ты будешь стримить, а так же выполнять некоторые другие действия.""".format(message.from_user), parse_mode='html')

@bot.message_handler(content_types=['text'])
def lalala(message):
    bot.send_message(message.chat.id, message.text) 

bot.polling(none_stop = True)