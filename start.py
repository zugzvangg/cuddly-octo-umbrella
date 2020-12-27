import sqlite3
import telebot
import config
from telebot import types
import random
from sql import SQL
import datetime


bot = telebot.TeleBot(config.TOKEN)
db = SQL('streamers')
 

@bot.message_handler(commands = ['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item1 = types.KeyboardButton("Начать!")
    markup.add(item1)
    bot.send_message(message.chat.id, """Приветствую, <b>{0.first_name}</b>!\n Это бот, созданный для организации процесса стриминга в нашем проекте. 
    Здесь ты можешь отмечать время, когда ты будешь стримить, а так же выполнять некоторые другие действия.""".format(message.from_user), parse_mode='html', reply_markup=markup)
    global usr
    usr = message.from_user.first_name
    


    

@bot.message_handler(content_types=['text'])
def lalala(message):
    if message.chat.type == 'private':
        if message.text == 'Начать!':
            markup = types.InlineKeyboardMarkup(row_width=3)
            item1 = types.InlineKeyboardButton("Добавить время", callback_data='new')
            item2 = types.InlineKeyboardButton("Удалить время", callback_data='del')
            item3 = types.InlineKeyboardButton("Статистика", callback_data='stat')
            markup.add(item1, item2, item3)
            bot.send_message(message.chat.id, 'Выбери, что ты хочешь сделать:', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Не понимаю тебя😢')
 
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'new':
                bot.send_message(call.message.chat.id, 'Добавляю в базу')
                tm = str(datetime.datetime.now().time()).split(':')[0]+':'+str(datetime.datetime.now().time()).split(':')[1]+':00'
                print(usr, str(datetime.datetime.now().date()), tm, tm)
                db.add(usr, str(datetime.datetime.now().date()), tm, tm)
            elif call.data == 'del':
                bot.send_message(call.message.chat.id, 'Удаляю из базы')
            elif call.data == 'stat':
                bot.send_message(call.message.chat.id, 'Статистика:')

 
 
    except Exception as e:
        print(repr(e)) 

bot.polling(none_stop = True)