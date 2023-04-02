#!/usr/bin/env python3

import time

import telebot
from telebot import types

from config import api_key
from config import owner_id
from config import db_filename

import functions as funcs
import db_connector as db

import classes

bot = telebot.TeleBot(api_key)

global new_rec_glob
new_rec_glob = []
new_rec_glob.append(classes.Record(0))

def get_default_keyboard():
  ''' Returns default keyboard for /add_record func  '''
  # get last record number
  new_num = db.get_new_rec_num(db_filename)
  prefix = 'start' + '\'' + str(new_num) + '\''
  key = types.InlineKeyboardMarkup()
  key.add(types.InlineKeyboardButton(text="Income", callback_data=prefix + 'income'))
  key.add(types.InlineKeyboardButton(text="Expence", callback_data=prefix + 'expense'))
  return key

def finalise_new_record(message):
  ''' Finalise new record after before it to db '''

  print(new_rec_glob[0].id)

  if new_rec_glob[0].id == 0:
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
    return

  comment = text.split(' ')[1:]
  comment = ' '.join(comment)

  new_rec_glob[0].set_date_ts(round(time.time(), 0))
  new_rec_glob[0].set_user_id(user_id)
  new_rec_glob[0].set_amount(amount)
  new_rec_glob[0].set_comment(comment)
  line = db.add_rec(db_filename, new_rec_glob[0])
  if not line:
    line = 'Record added'

  bot.send_message(message.from_user.id, line)

@bot.message_handler(content_types=['text'])
def start(message):
  if str(message.from_user.id) != str(owner_id):
    print('Non-admin access attempt, user_id: ' + str(message.from_user.id))
    line = 'You are not allowed to use this bot. Your user_id below\n' + str(message.from_user.id)
    bot.send_message(message.from_user.id, line)
    return
  print('GOT MSG: ' + message.text)
  if message.text == '/help':
    bot.send_message(message.from_user.id, funcs.get_help_msg())

  if message.text == '/add_record':
    # show keyboard to choose income\expense
    key = types.InlineKeyboardMarkup()
    key = get_default_keyboard()

    bot.send_message(message.from_user.id, 'Choose type of record', reply_markup=key)

  if message.text == '/generate_report':
    key = types.InlineKeyboardMarkup()
    key = get_default_keyboard()
    bot.send_message(message.from_user.id, 'Choose how report should look\n(wait for v2, redirecting to /add_record func)', reply_markup=key)
    # bot.register_next_step_handler(message, do_show_report)

  if message.text == '/show_all':
    bot.send_message(message.from_user.id, 'Sending your records, one by one')
    for record in db.get_recs_user(db_filename, message.from_user.id):
      print(record)
      if record == True:
        continue
      if record == False:
        bot.send_message(message.from_user.id, 'You don\'t have records in db')
        return
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
  if data_marker == 'back_to_start':
    line = 'Choose type of record'
    key = get_default_keyboard()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=line, reply_markup=key)

  if data_marker == 'start':
    line = 'Choose category'
    print('Category type:', record_num, data_body_str)
    categories = db.get_cats_arr(db_filename)

    for category in categories:
      if data_body_str == category.type:
        btn_data = ''
        if data_body_str == 'income':
          btn_prefix = 'cat_i'
        if data_body_str == 'expense':
          btn_prefix = 'cat_e'
        btn_data = btn_prefix + '\'' + record_num + '\'' + category.name
        key.add(types.InlineKeyboardButton(text=category.name, callback_data=btn_data))

    key.add(types.InlineKeyboardButton(text='Back to start', callback_data='back_to_start'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=line, reply_markup=key)

  if data_marker == 'cat_i' or data_marker == 'cat_e':
    print('Category: ', record_num, data_body_str)
    line = 'Input record info, example:\n' \
           '`1234 really great bananas!\n`' \
           'Means \'I just spent (or earned) 1234 of some currency on bananas that i really love\''
    new_rec_glob[0] = classes.Record(record_num)

    if data_marker == 'cat_i':
      new_cat_type = 'income'
    if data_marker == 'cat_e':
      new_cat_type = 'expense'
    new_cat = classes.Category(new_cat_type, data_body_str)
    new_rec_glob[0].set_cat(new_cat)

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=line, parse_mode='Markdown')

    bot.register_next_step_handler(message, finalise_new_record)
  # part for /add_record END


if __name__ == '__main__':

  db_started = db.start(db_filename)
  print('Start db:', db_started)

  bot.infinity_polling()
