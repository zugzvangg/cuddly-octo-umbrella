import sqlite3
from time import strptime
import telebot
import config
from telebot import types
import random
from sql import SQL
import datetime
import re
from Structure import Structure
import json

conf = 'CONFIG_RUS.json'
with open(conf) as jf:
    configuration = json.load(jf)
bot = telebot.TeleBot(config.TOKEN)
db = SQL(configuration['setup']['database'])
structure = Structure() 


@bot.message_handler(commands = [configuration['commands']['start']['name']])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item1 = types.KeyboardButton(configuration['commands']['start']["begin_button"])
    markup.add(item1)
    bot.send_message(message.chat.id,configuration['commands']['start']['hello'].format(message.from_user), parse_mode='html', reply_markup=markup)
    structure.usr = message.from_user.first_name
    


@bot.message_handler(commands=[configuration['commands']["new"]['name']])
def date_new(message):
    keyboard = types.InlineKeyboardMarkup()
    today_button = types.InlineKeyboardButton(text=configuration['commands']["new"]['inline_today'], callback_data=configuration['commands']["new"]['inline_today'])
    tomorrow_button = types.InlineKeyboardButton(text = configuration['commands']["new"]['inline_tomorrow'], callback_data=configuration['commands']["new"]['inline_tomorrow'])
    other_button = types.InlineKeyboardButton(text = configuration['commands']["new"]['inline_other'], callback_data=configuration['commands']["new"]['inline_other'])
    keyboard.add(today_button, tomorrow_button, other_button)
    bot.send_message(message.chat.id,configuration['commands']['new']['start_date'], parse_mode='html', reply_markup=keyboard)
    

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == configuration['commands']["new"]['inline_today']:
            structure.date = datetime.date.today().strftime('%Y/%m/%d')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Registred time for today!", parse_mode="html")
            bot.send_message(call.message.chat.id, configuration['commands']['new']['enter_time_beg'], parse_mode = "html")
            bot.register_next_step_handler(call.message, check_time_new)
        elif call.data == configuration['commands']["new"]['inline_tomorrow']:
            structure.date = (datetime.date.today()+datetime.timedelta(days=1)).strftime('%Y/%m/%d')
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Registred time for tomorrow!", parse_mode="html")
            bot.send_message(call.message.chat.id, configuration['commands']['new']['enter_time_beg'], parse_mode = "html")
            bot.register_next_step_handler(call.message, check_time_new)
        elif call.data == configuration['commands']['new']['inline_other']:
            bot.send_message(call.message.chat.id, configuration['commands']['new']['enter_date'], parse_mode='html')
            bot.register_next_step_handler(call.message, check_date)



def check_date(message):
    if re.match(re.compile(configuration['commands']["new"]['re_date_match']), message.text):
        bot.send_message(message.chat.id, configuration['commands']['new']['check_ok'])
        structure.date = message.text
        bot.send_message(message.chat.id,configuration['commands']['new']['enter_time_beg'],parse_mode='html')
        bot.register_next_step_handler(message, check_time_new)
    else:
        bot.send_message(message.chat.id,configuration['commands']['new']['wrong_date'])
        bot.register_next_step_handler(message, check_date)


def check_time_new(message):
    if re.match(configuration['commands']["new"]['re_time_match'], message.text):
        bot.send_message(message.chat.id, 'Ок!')
        structure.time_begin = message.text
        bot.send_message(message.chat.id,configuration['commands']['new']['enter_time_end'], parse_mode='html')
        bot.register_next_step_handler(message, check_time_end)
    else:
        bot.send_message(message.chat.id,configuration['commands']['new']['wrong_time'])
        bot.register_next_step_handler(message, check_time_new)


def check_time_end(message):
    if re.match(re.compile(configuration['commands']["new"]['re_time_match']), message.text):
        if datetime.datetime.strptime(message.text, "%H:%M") > datetime.datetime.strptime(structure.time_begin, "%H:%M"):
            bot.send_message(message.chat.id, configuration['commands']["new"]["check_ok"])
            structure.time_end = message.text
            print(message.from_user.first_name, structure.date,structure.time_begin, structure.time_end)
            db.add(message.from_user.first_name, structure.date,structure.time_begin, structure.time_end)
            bot.send_message(message.chat.id, configuration['commands']["new"]["written"])
        else:
            bot.send_message(message.chat.id, configuration['commands']["new"]["cant_be_later"])
            bot.register_next_step_handler(message, check_time_end)
    else:
        bot.send_message(message.chat.id,configuration['commands']['new']['wrong_time'])
        bot.register_next_step_handler(message, check_time_end)


@bot.message_handler(commands = [configuration['commands']['delete']['name']])
def delete(message):
    bot.send_message(message.chat.id,configuration['common']['all_user_data'])
    ls = db.get_users_streams(message.from_user.first_name)
    tmp = []
    for i in ls:
        tmp.append((i[2], i[3]))
    if len(tmp)==0:
        bot.send_message(message.chat.id, configuration['common']['no_data'])
        return
    res = ""
    res+='Date             Time\n'
    for i in tmp:
        res+=i[0]+'-'+i[1]+'\n'
    bot.send_message(message.chat.id, res)
    bot.send_message(message.chat.id,configuration['commands']['delete']['enter_time_delete'],parse_mode='html')
    bot.register_next_step_handler(message, lambda msg: checking_delete(tmp, msg))

def checking_delete(tmp, message):
    if re.match(re.compile(configuration['commands']['delete']['re_date_time_match']), message.text):
        db.delete(message.from_user.first_name,message.text.split('-')[0], message.text.split('-')[1])
        bot.send_message(message.chat.id, configuration['commands']['delete']['deleted'])
    else:
        bot.send_message(message.chat.id,configuration['commands']['delete']['wrong_format'])
        bot.register_next_step_handler(message, lambda msg: checking_delete(tmp, msg))


@bot.message_handler(commands = [configuration['commands']['streams']['name']])
def get_streams(message):
    bot.send_message(message.chat.id,configuration['common']['all_user_data'])
    ls = db.get_users_streams(message.from_user.first_name)
    tmp = []
    for i in ls:
        tmp.append((i[2], i[3]))
    if len(tmp)==0:
        bot.send_message(message.chat.id, configuration['common']['no_data'])
        return
    res = ""
    res+='Date             Time\n'
    for i in tmp:
        res+=i[0]+'-'+i[1]+'\n'
    bot.send_message(message.chat.id, res)

@bot.message_handler(commands = [configuration['commands']['today']['name']])
def today(message):
    bot.send_message(message.chat.id,configuration['commands']['today']['streams_for_today'])
    today = datetime.date.today().strftime('%Y/%m/%d')
    ls = db.get_today_streams(today, message.from_user.first_name)
    tmp = []
    for i in ls:
        tmp.append((i[3], i[4]))
    if len(tmp)==0:
        bot.send_message(message.chat.id, configuration['commands']['today']['no_streams_for_today'])
        return
    res = ""
    res+='Begin      End\n'
    for i in tmp:
        res+=i[0]+'  -  '+i[1]+'\n'
    bot.send_message(message.chat.id, res)

@bot.message_handler(commands = ['stat'])
def statistics(message):
    ls = db.get_statistics(streamer=message.from_user.first_name)
    per_month = 0
    summa = 0
    for i in ls:
        print(datetime.datetime.strptime(i[2], "%H:%M"), datetime.datetime.strptime(i[1], "%H:%M"))
        tmp = datetime.datetime.strptime(i[2], "%H:%M")-datetime.datetime.strptime(i[1], "%H:%M")
        print(tmp)
        if datetime.date.today().strftime('%Y/%m/%d').split('/')[1]==i[0].split('/')[1]: 
            per_month+=abs(float(tmp.seconds)/3600)
        summa+=abs(float(tmp.seconds/3600))
    bot.send_message(message.chat.id, configuration['commands']['stat']['pattern'].format(message.from_user.first_name, int(per_month), int(summa)), parse_mode='html')



@bot.message_handler(commands = ['long'])
def add_schedule(message):
    pass

bot.polling(none_stop = True)

