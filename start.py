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
    

    
@bot.message_handler(content_types=['text'])
def begin(message):
    if message.chat.type == 'private':
        if message.text == 'Начать!':
            bot.send_message(message.chat.id, """Этот бот поможет тебе выбирать время стрима, отказываться от него, а так же смотреть свою статистику. Функция <b>/new</b> - чтобы выбрать время. Функция <b>/delete</b> - чтобы удалить, <b>/stat</b> - ваша статистика. Введите что угодно.""", parse_mode='html')
            bot.register_next_step_handler(message, mid)

def mid(message):
    bot.send_message(message.chat.id,'Введите команду')
    bot.register_next_step_handler(message, choose)

def choose(message):
    if message.text == "/new":
        bot.register_next_step_handler(message, date_new)
    elif message.text == "/delete":
        bot.register_next_step_handler(message, delete)
    elif message.text == "/stat":
        bot.register_next_step_handler(message, stat)
    else:
        bot.send_message(message.chat.id, "Команда неверна!")
        bot.register_next_step_handler(message, reg)

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
        structure.time_begin = message.text + ':00'
        bot.send_message(message.chat.id,'Введите время, когда закончите стримить в формате: <b>12:25</b>', parse_mode='html')
        bot.register_next_step_handler(message, check_time_end)
    else:
        bot.send_message(message.chat.id,'Неверный формат времени, введите заново.')
        bot.register_next_step_handler(message, check_time_new)


def check_time_end(message):
    if re.match(r'^[0-2][0-3]:[0-5][0-9]$', message.text):
        bot.send_message(message.chat.id, 'Ок!')
        structure.time_end = message.text + ':00'
        print(structure.usr, structure.date,structure.time_begin, structure.time_end)
        db.add(structure.usr, structure.date,structure.time_begin, structure.time_end)
        bot.send_message(message.chat.id, 'Записано!')
        bot.register_next_step_handler(message, mid)
    else:
        bot.send_message(message.chat.id,'Неверный формат времени, введите заново.')
        bot.register_next_step_handler(message, check_time_end)

def delete(message):
    pass



 
    except Exception as e:
        print(repr(e)) 

bot.polling(none_stop = True)