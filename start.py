import sqlite3
import telebot
import config
from telebot import types
import random
from sql import SQL
import datetime
import re
from Structure import Structure


bot = telebot.TeleBot(config.TOKEN)
db = SQL('streamers')
structure = Structure() 
 

@bot.message_handler(commands = ['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item1 = types.KeyboardButton("Начать!")
    markup.add(item1)
    bot.send_message(message.chat.id, """Приветствую, <b>{0.first_name}</b>!\n Это бот, созданный для организации процесса стриминга в нашем проекте. Здесь ты можешь отмечать время, когда ты будешь стримить, а так же выполнять некоторые другие действия.""".format(message.from_user), parse_mode='html', reply_markup=markup)
    structure.usr = message.from_user.first_name
    


@bot.message_handler(commands=['new'])
def date_new(message):
    bot.send_message(message.chat.id,'Введите дату, когда хотите стримить в формате: <b>2021/11/25</b>', parse_mode='html')
    bot.register_next_step_handler(message, check_date)

def check_date(message):
    if re.match(r'^202\d\/\d[0-2]\/([1-2]?[1-9]|[1-3][0-2])$', message.text):
        bot.send_message(message.chat.id, 'Ок!')
        structure.date = message.text
        bot.send_message(message.chat.id,'Введите время, когда хотите стримить в формате: <b>12:25</b>', parse_mode='html')
        bot.register_next_step_handler(message, check_time_new)
    else:
        bot.send_message(message.chat.id,'Неверный формат даты, введите заново.')
        bot.register_next_step_handler(message, check_date)


def check_time_new(message):
    if re.match(r'^[0-2][0-3]:[0-5][0-9]$', message.text):
        bot.send_message(message.chat.id, 'Ок!')
        structure.time_begin = message.text
        bot.send_message(message.chat.id,'Введите время, когда закончите стримить в формате: <b>12:25</b>', parse_mode='html')
        bot.register_next_step_handler(message, check_time_end)
    else:
        bot.send_message(message.chat.id,'Неверный формат времени, введите заново.')
        bot.register_next_step_handler(message, check_time_new)


def check_time_end(message):
    if re.match(r'^[0-2][0-3]:[0-5][0-9]$', message.text):
        bot.send_message(message.chat.id, 'Ок!')
        structure.time_end = message.text
        print(message.from_user.first_name, structure.date,structure.time_begin, structure.time_end)
        db.add(message.from_user.first_name, structure.date,structure.time_begin, structure.time_end)
        bot.send_message(message.chat.id, 'Записано!')
    else:
        bot.send_message(message.chat.id,'Неверный формат времени, введите заново.')
        bot.register_next_step_handler(message, check_time_end)


@bot.message_handler(commands = ['delete'])
def delete(message):
    bot.send_message(message.chat.id,'Список ваших записей:')
    ls = db.get_users_streams(message.from_user.first_name)
    tmp = []
    for i in ls:
        tmp.append((i[1], i[2]))
    if len(tmp)==0:
        bot.send_message(message.chat.id, 'У вас нет активных записей')
        return
    res = ""
    res+='Date             Time\n'
    for i in tmp:
        res+=i[0]+' '+i[1]+'\n'
    bot.send_message(message.chat.id, res)
    bot.send_message(message.chat.id,'Введите дату в формате и время в формате <b>2021/11/25 12:25</b> записи, которую вы хотите удалить',parse_mode='html')
    bot.register_next_step_handler(message, lambda msg: checking_delete(tmp, msg))

def checking_delete(tmp, message):
    if re.match(r'^202\d\/\d[0-2]\/([1-2]?[1-9]|[1-3][0-2])\s[0-2][0-3]:[0-5][0-9]$', message.text):
        print(message.from_user.first_name,message.text.split()[0], message.text.split()[1])
        db.delete(message.from_user.first_name,message.text.split()[0], message.text.split()[1])
        bot.send_message(message.chat.id, 'Запись удалена!')
    else:
        bot.send_message(message.chat.id,'Неверный формат , введите заново.')
        bot.register_next_step_handler(message, lambda msg: checking_delete(tmp, msg))





 

bot.polling(none_stop = True)