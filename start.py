import sqlite3
import threading
from time import strptime
from Structure import Structure
from sql import SQL
import config
import telebot
import random
import calendar
import datetime
import re
import json
from aiogram import Dispatcher, Bot, executor, types
import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import logging
import os
from aiogram.types import InputMediaPhoto, KeyboardButton, ReplyKeyboardMarkup

logging.basicConfig(level=logging.WARNING)
logging.warning('This is a warning message')
logging.error("Error message!")
logging.critical("Critical message!")

# TODO other features
bot = Bot(config.TOKEN)
dp = Dispatcher(bot)
conf = 'CONFIG_ENG.json'
with open(conf) as jf:
        configuration = json.load(jf)
db = SQL(configuration['setup']['database'])
structure = Structure()

while True:
    logging.basicConfig(filename="errors.txt", format='[%(asctime)s] [%(levelname)s] => %(message)s',
                        level=logging.WARNING)
    
    

    @dp.message_handler(commands=[configuration['commands']['discipline']['name']])
    async def set_discipline(message):
        keyboard = types.InlineKeyboardMarkup()
        dota2 = types.InlineKeyboardButton(
            text=configuration['commands']["discipline"]['dota2'], callback_data=configuration['commands']["discipline"]['inline_dota'])
        csgo = types.InlineKeyboardButton(
            text=configuration['commands']["discipline"]['csgo'], callback_data=configuration['commands']["discipline"]['inline_cs'])
        keyboard.add(dota2, csgo)
        await bot.send_message(message.chat.id, configuration['commands']['discipline']['choose'], parse_mode='html', reply_markup=keyboard)
        
        


    @dp.message_handler(commands = [configuration['commands']['start']['name']])
    async def welcome(message):
        markup = types.InlineKeyboardMarkup()
        dota2 = types.InlineKeyboardButton(
            text=configuration['commands']["discipline"]['dota2'], callback_data=configuration['commands']["discipline"]['inline_dota'])
        csgo = types.InlineKeyboardButton(
            text=configuration['commands']["discipline"]['csgo'], callback_data=configuration['commands']["discipline"]['inline_cs'])
        markup.add(dota2, csgo)
        await bot.send_message(message.chat.id, configuration['commands']['start']['hello'].format(message.from_user), parse_mode='html', reply_markup=markup)
        structure.usr = message.from_user.first_name




    @dp.message_handler(commands=[configuration['commands']["new"]['name']])
    async def date_new(message):
        keyboard = types.InlineKeyboardMarkup()
        today_button = types.InlineKeyboardButton(text=configuration['commands']["new"]['inline_today'], callback_data=configuration['commands']["new"]['inline_today'])
        tomorrow_button = types.InlineKeyboardButton(text = configuration['commands']["new"]['inline_tomorrow'], callback_data=configuration['commands']["new"]['inline_tomorrow'])
        other_button = types.InlineKeyboardButton(text = configuration['commands']["new"]['inline_other'], callback_data=configuration['commands']["new"]['inline_other'])
        keyboard.add(today_button, tomorrow_button, other_button)
        await bot.send_message(message.chat.id, configuration['commands']['new']['start_date'], parse_mode='html', reply_markup=keyboard)
        
    @dp.callback_query_handler(lambda call: True)  # inline buttons
    async def callback_inline(call):
        if call.message:
            if call.data == configuration['commands']["new"]['inline_today']:
                structure.date = datetime.date.today().strftime('%Y/%m/%d')
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=configuration['commands']["new"]['reg_for_tod'], parse_mode="html")
                await bot.send_message(call.message.chat.id, configuration['commands']['new']['enter_time_beg'], parse_mode="html")
                await bot.register_next_step_handler(call.message, check_time_new)
            elif call.data == configuration['commands']["new"]['inline_tomorrow']:
                structure.date = (datetime.date.today()+datetime.timedelta(days=1)).strftime('%Y/%m/%d')
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=configuration['commands']["new"]['reg_for_tom'], parse_mode="html")
                await bot.send_message(call.message.chat.id, configuration['commands']['new']['enter_time_beg'], parse_mode="html")
                await bot.register_next_step_handler(call.message, check_time_new)
            elif call.data == configuration['commands']['new']['inline_other']:
                await bot.send_message(call.message.chat.id, configuration['commands']['new']['enter_date'], parse_mode='html')
                await bot.register_next_step_handler(call.message, check_date)
            elif call.data == configuration['commands']["discipline"]['inline_dota']:
                db.change_discipline(call.message.chat.username,configuration['commands']["discipline"]['dota2'])
                await bot.send_message(
                    call.message.chat.id, configuration['commands']['discipline']['discipline_signed'], parse_mode='html')
            elif call.data == configuration['commands']["discipline"]['inline_cs']:
                db.change_discipline(
                    call.message.chat.username, configuration['commands']["discipline"]['csgo'])
                await bot.send_message(call.message.chat.id, configuration['commands']['discipline']['discipline_signed'], parse_mode='html')
            elif call.data in ['0', '1', '2', '3', '4', '5', '6']:
                my_date = datetime.date.today()
                tmp = ((my_date+datetime.timedelta(int(call.data)+1),
                        calendar.day_name[(my_date+datetime.timedelta(int(call.data)+1)).weekday()]))
                await bot.send_message(call.message.chat.id, configuration['commands']['new']['enter_time_beg'], parse_mode='html')
                structure.date = tmp[0].strftime("%Y/%m/%d")
                await bot.register_next_step_handler(call.message, check_time_new)


    async def check_date(message):
        if re.match(re.compile(configuration['commands']["new"]['re_date_match']), message.text):
            await bot.send_message(message.chat.id, configuration['commands']['new']['check_ok'])
            structure.date = message.text
            await bot.send_message(message.chat.id, configuration['commands']['new']['enter_time_beg'], parse_mode='html')
            await bot.register_next_step_handler(message, check_time_new)
        else:
            await bot.send_message(message.chat.id, configuration['commands']['new']['wrong_date'])
            await bot.register_next_step_handler(message, check_date)

    async def check_time_new(message):
        if re.match(configuration['commands']["new"]['re_time_match'], message.text):
            await bot.send_message(message.chat.id, 'Ок!')
            structure.time_begin = message.text
            await bot.send_message(message.chat.id, configuration['commands']['new']['enter_time_end'], parse_mode='html')
            await bot.register_next_step_handler(message, check_time_end)
        else:
            await bot.send_message(message.chat.id, configuration['commands']['new']['wrong_time'])
            await bot.register_next_step_handler(message, check_time_new)

    async def check_time_end(message):
        if re.match(re.compile(configuration['commands']["new"]['re_time_match']), message.text):
            if datetime.datetime.strptime(message.text, "%H:%M") > datetime.datetime.strptime(structure.time_begin, "%H:%M"):
                await bot.send_message(message.chat.id, configuration['commands']["new"]["check_ok"])
                structure.time_end = message.text
                print(message.chat.username, structure.date,
                    structure.time_begin, structure.time_end)
                db.add(message.chat.username, structure.date,structure.time_begin, structure.time_end)
                await bot.send_message(message.chat.id, configuration['commands']["new"]["written"])
            else:
                await bot.send_message(message.chat.id, configuration['commands']["new"]["cant_be_later"])
                await bot.register_next_step_handler(message, check_time_end)
        else:
            await bot.send_message(message.chat.id, configuration['commands']['new']['wrong_time'])
            await bot.register_next_step_handler(message, check_time_end)


    @dp.message_handler(commands = [configuration['commands']['delete']['name']])
    async def delete(message):
        await bot.send_message(message.chat.id, configuration['common']['all_user_data'])
        ls = db.get_users_streams(message.chat.username)
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
        await bot.send_message(message.chat.id, res)
        await bot.send_message(message.chat.id, configuration['commands']['delete']['enter_time_delete'], parse_mode='html')
        await bot.register_next_step_handler(message, lambda msg: checking_delete(tmp, msg))

    async def checking_delete(tmp, message):
        if re.match(re.compile(configuration['commands']['delete']['re_date_time_match']), message.text):
            db.delete(message.chat.username, message.text.split(
                '-')[0], message.text.split('-')[1])
            await bot.send_message(message.chat.id, configuration['commands']['delete']['deleted'])
        else:
            await bot.send_message(message.chat.id, configuration['commands']['delete']['wrong_format'])
            await bot.register_next_step_handler(message, lambda msg: checking_delete(tmp, msg))


    @dp.message_handler(commands = [configuration['commands']['streams']['name']])
    async def get_streams(message):
        await bot.send_message(message.chat.id, configuration['common']['all_user_data'])
        ls = db.get_users_streams(message.chat.username)
        tmp = []
        for i in ls:
        
            if datetime.date.today()<=datetime.date(int(i[2].split('/')[0]), int(i[2].split('/')[1]), int(i[2].split('/')[2])):
                tmp.append((i[2], i[3]))
        if len(tmp)==0:
            bot.send_message(message.chat.id, configuration['common']['no_data'])
            return
        print(tmp)
        res = ""
        res+='Date             Time\n'
        for i in tmp:
            res+=i[0]+'-'+i[1]+'\n'
        await bot.send_message(message.chat.id, res)

    @dp.message_handler(commands = [configuration['commands']['today']['name']])
    async def today(message):
        await bot.send_message(message.chat.id, configuration['commands']['today']['streams_for_today'])
        today = datetime.date.today().strftime('%Y/%m/%d')
        ls = db.get_today_streams(today, message.chat.username)
        tmp = []
        for i in ls:
            tmp.append((i[3], i[4]))
        if len(tmp)==0:
            await bot.send_message(message.chat.id, configuration['commands']['today']['no_streams_for_today'])
            return
        res = ""
        res+='Begin      End\n'
        for i in tmp:
            res+=i[0]+'  -  '+i[1]+'\n'
        await bot.send_message(message.chat.id, res)

    @dp.message_handler(commands = ['stat'])
    async def statistics(message):
        ls = db.get_statistics(streamer=message.chat.username)
        per_month = 0
        summa = 0
        for i in ls:
            print(datetime.datetime.strptime(i[2], "%H:%M"), datetime.datetime.strptime(i[1], "%H:%M"))
            tmp = datetime.datetime.strptime(i[2], "%H:%M")-datetime.datetime.strptime(i[1], "%H:%M")
            print(tmp)
            if datetime.date.today().strftime('%Y/%m/%d').split('/')[1]==i[0].split('/')[1]: 
                per_month+=abs(float(tmp.seconds)/3600)
            summa+=abs(float(tmp.seconds/3600))
        await bot.send_message(message.chat.id, configuration['commands']['stat']['pattern'].format(message.from_user.first_name, int(per_month), int(summa)), parse_mode='html')



    @dp.message_handler(commands = ['timetable'])
    async def add_schedule(message):
        my_date = datetime.date.today()
        ls = []
        for i in range(1, 8):
            ls.append((my_date+datetime.timedelta(i),calendar.day_name[(my_date+datetime.timedelta(i)).weekday()]))
        buttons = []
        for i in range(len(ls)):
            button = types.InlineKeyboardButton(
                text=ls[i][0].strftime("%m/%d/%Y")+"\n"+ls[i][1] , callback_data=str(i))
            buttons.append(button)
        keyboard = types.InlineKeyboardMarkup([[button] for button in buttons])
        bot.send_message(message.chat.id, configuration['commands']['timetable']['choose_days_of_week'], reply_markup=keyboard)

    executor.start_polling(dp)



