#!/usr/bin/env python3

import os
import sys
import sqlite3

from dataclasses import dataclass

import telebot
from telebot import types

from config import api_key
from config import admin_id

bot = telebot.TeleBot(api_key)

@dataclass
class Category():
  type: str
  name: str

  def __init__(self, name: str, type: str):
    self.type = str(type)
    self.name = str(name)


@dataclass
class Record:
  seq_num: int
  user_id: int
  type: str
  category: str
  date_ts: int
  currency: str
  amount: int
  comment: str
  
  def __init__(self, seq_num: int):
    self.seq_num = int(seq_num)

  def set_user_id(self, user_id: int):
    self.user_id = int(user_id)

  def set_cat(self, category:Category):
    self.category = str(category.name)
    self.type = str(category.type)

  def set_date(self, date_ts: int):
    self.date_ts = int(date_ts)

  def set_currency(self, currency: str):
    self.currency = str(currency)

  def set_amount(self, amount: int):
    self.amount = int(amount)

  def set_comment(self, comment: str):
    self.comment = str(comment)


help_msg = '''
This bot helps you to track your money usage
There are commands below:

/help - show this help page
/add_record - add new income or expense record
/show_report - generate report (will be avalible in v2 and above)
'''

cat_arr = [['Salary', 'income'], ['Sell', 'income'], ['Other', 'income'], \
            ['Food', 'expence'], ['Clothes', 'expence'],  ['Fun', 'expence'], ['Other', 'expence']]


def get_cats_from_db():
  '''
  Gets categories from db, returns them as array 
  of objects of Category class
  '''
  categories = []
  # todo: connect to db and get categories from there
  for cat in cat_arr:
    c_name = cat[0]
    c_type = cat[1]
    categories.append(Category(c_name, c_type))
  return categories


def get_default_keyboard():
  '''
  Returns default keyboard for /add_record func
  '''
  # get last record number
  new_num = get_new_record_num()
  prefix = 'c_tp' + '\'' + str(new_num) + '\''
  key = types.InlineKeyboardMarkup()
  key.add(types.InlineKeyboardButton(text="Income", callback_data=prefix + 'income'))
  key.add(types.InlineKeyboardButton(text="Expence", callback_data=prefix + 'expence'))
  return key


def do_add_record(message):
  '''
  Adds record to db 
  '''

  new_rec = Record(0)

  for record in rec_arr:
    if record.seq_num == get_last_record_num():
      new_rec = record
      break

  if new_rec.seq_num == 0:
    line = 'Invalid record'
    bot.reply_to(message, line)
    return

  text = message.text
  user_id = message.from_user.id

  amount = text.split(' ')[0:1]
  amount = ''.join(amount)

  try:
    amount = int(amount)
  except Exception:
    line = 'ERROR: Amount is not a number:\n' + amount
    bot.reply_to(message, line)
    del rec_arr[-1]
    return

  if int(amount) != amount:
    line = 'Amount is not a number:\n' + amount
    print(line)
    bot.reply_to(message, line)
    return

  comment = text.split(' ')[1:]  
  comment = ' '.join(comment)

  new_rec.set_user_id(user_id)
  new_rec.set_amount(amount)
  new_rec.set_comment(comment)
  print('Record added:)
  print(new_rec.__dict__)
  line = 'Record added:\n'
  line += str(new_rec.__dict__)
  bot.send_message(message.from_user.id, line)


def get_category_obj_by_name(name):
  '''
  Get category object by category name
  '''
  cats = get_cats_from_db()
  for cat in cats:
    if cat.name == name:
      return cat


def get_last_record_num():
  '''
  Returns curr last record num from db
  '''
  num = len(rec_arr) - 1
  return int(num)


def get_new_record_num():
  '''
  Returns new record num from db
  '''
  num = len(rec_arr)
  return int(num)


@bot.message_handler(content_types=['text'])
def start(message):
  # if str(message.from_user.id) != str(admin_id):
  #   print('Non-admin access attempt, user_id: ' + str(message.from_user.id))
  #   line = 'You are not allowed to use this bot. Your user_id below\n' + str(message.from_user.id)
  #   bot.send_message(message.from_user.id, line)
  #   return
  print('GOT MSG: ' + message.text)
  if message.text == '/help':
    bot.send_message(message.from_user.id, help_msg)
  
  if message.text == '/add_record':
    # show keyboard to choose income\expense
    key = types.InlineKeyboardMarkup()
    key = get_default_keyboard()
    
    bot.send_message(message.from_user.id, 'Choose type of record', reply_markup=key)

  if message.text == '/show_report':
    key = types.InlineKeyboardMarkup()
    key = get_default_keyboard()
    bot.send_message(message.from_user.id, 'Choose how report should look\n(wait for v2, redirecting to /add_record func)', reply_markup=key)
    # bot.register_next_step_handler(message, do_show_report)

  if message.text == '/show_all':
    bot.send_message(message.from_user.id, 'Sending all records, one by one')
    for record in rec_arr:
      bot.send_message(message.from_user.id, str(record.__dict__))


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
  key = types.InlineKeyboardMarkup()
  line = ''
  message = call.message
  call_data = call.data

  data_marker = call_data.split('\'')[0:1]
  data_marker = ''.join(data_marker)
  
  record_num = call_data.split('\'')[1:2]
  record_num = ''.join(record_num)

  data_body = call_data.split('\'')[2:]
  data_body_str = ' '.join(data_body)

  # part for /add_record START
  if data_marker == 'to_start':
    line = 'Choose type of record'
    key = get_default_keyboard()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=line, reply_markup=key)

  if data_marker == 'c_tp':
    line = 'Choose category'
    print('Category type:', record_num, data_body_str)
    categories = get_cats_from_db()

    for category in categories:
      if data_body_str == category.type:
        btn_data = ''
        btn_data = 'cat\'' + record_num + '\'' + category.name
        key.add(types.InlineKeyboardButton(text=category.name, callback_data=btn_data))

    key.add(types.InlineKeyboardButton(text='Back to start', callback_data='to_start'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=line, reply_markup=key)

  if data_marker == 'cat':
    print('Category: ', record_num, data_body_str)
    line = 'Input record info: amount of money you spent (nesessary, no spaces), short comment(optional). Example:\n' \
           '`1234 bananas\n`' \
           'Means \'I just spent (or earned) 1234 of some currency on bananas\''
    new_record = Record(record_num)

    new_cat = get_category_obj_by_name(data_body_str)
    new_record.set_cat(new_cat)

    rec_arr.append(new_record)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=line, parse_mode='Markdown')

    bot.register_next_step_handler(message, do_add_record)
  # part for /add_record END


if __name__ == '__main__':

  cats = get_cats_from_db()

  rec1 = Record(0)
  rec1.set_cat(cats[0])
  rec1.set_amount('100')
  rec1.set_comment('test record 1')

  rec2 = Record(1)
  rec2.set_cat(cats[5])
  rec2.set_amount('450')
  rec2.set_comment('test record 2')

  global rec_arr
  rec_arr = []
  rec_arr.append(rec1)
  rec_arr.append(rec2)

#   for record in rec_arr:
#     if record.seq_num == 1:
# #      record.set_amount(200)
#       print(record.__dict__)

  bot.infinity_polling()
