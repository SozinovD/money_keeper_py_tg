#!/usr/bin/env python3

import time

import telebot
from telebot import types

from config import api_key
from config import owner_id
from config import db_filename

import functions as funcs
import db_handler as db

import classes

bot = telebot.TeleBot(api_key)
data_divider_in_callback = '\''

# I tried to use global record, but it simply didn't work
# new_rec_glob[0] is record obj
# new_rec_glob[1] is chat_id
# new_rec_glob[2] is message_id
# new_rec_glob[1] and new_rec_glob[1] are needed to remember message to edit
global new_rec_glob
new_rec_glob = []
new_rec_glob.insert(0, classes.Record(0))

def finalise_new_record(message):
  ''' Finalise new record after before it to db '''

  text = message.text
  user_id = message.from_user.id

  amount = text.split(' ')[0:1]
  amount = ''.join(amount)

  try:
    amount = float(amount)
  except Exception:
    line = 'ERROR: Amount is not a number:\n' + amount
    bot.reply_to(message, line)
    return

  comment = text.split(' ')[1:]
  comment = ' '.join(comment)

  new_rec_glob[0].set_date_ts(round(time.time(), 0))
  new_rec_glob[0].set_user_id(user_id)
  new_rec_glob[0].set_amount(round(amount, 2))
  # new_rec_glob[0].set_amount_usd(round(amount, 2)) # todo: curr convertions
  new_rec_glob[0].set_comment(comment)
  line = db.add_rec(db_filename, new_rec_glob[0])
  if not line:
    line = 'Record added'
  bot.edit_message_text(chat_id=new_rec_glob[1], message_id=new_rec_glob[2], text=line)

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
    key = funcs.get_start_rec_add_kbrd(data_divider_in_callback, message.from_user.id)
    bot.send_message(message.from_user.id, 'Choose type of record', reply_markup=key)

  if message.text == '/generate_report':
    bot.send_message(message.from_user.id, 'Feature is not ready yet')
    # bot.register_next_step_handler(message, do_show_report)  # todo: generate report

  if message.text == '/show_all':
    records = db.get_recs_by_filter(db_filename, message.from_user.id)
    if len(records) < 1:
      bot.send_message(message.from_user.id, 'You do not have records')
    else:
      bot.send_message(message.from_user.id, 'Sending all your records')
    for record in records:
      print(record)
      bot.send_message(message.from_user.id, str(record.__dict__))

  if message.text == '/show_last_3':
    records = db.get_last_n_recs(db_filename, message.from_user.id, 3)
    if len(records) < 1:
      bot.send_message(message.from_user.id, 'You do not have records')
    else:
      bot.send_message(message.from_user.id, 'Sending your 3 last records')
    for record in records:
      print(record)
      bot.send_message(message.from_user.id, str(record.__dict__))

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
  key = types.InlineKeyboardMarkup()
  line = ''
  message = call.message
  new_rec_glob.insert(1, message.chat.id)
  new_rec_glob.insert(2, message.message_id)

  data_arr = funcs.dec_callback_data(data_divider_in_callback, call.data)
  data_marker = data_arr[0]
  data_body_arr = []
  for data in data_arr[1:]:
    data_body_arr.append(data)

  # print(data_body_arr)

  # part for /add_record START
  if data_marker == 'back_to_start':
    line = 'Choose type of record'
    key = funcs.get_start_rec_add_kbrd(data_divider_in_callback)
    bot.edit_message_text(chat_id=new_rec_glob[1], message_id=new_rec_glob[2], text=line, reply_markup=key)

  if data_marker == 'start':
    line = 'Choose category'
    key = funcs.get_cat_btns_by_type(db_filename, data_body_arr[0], data_divider_in_callback)
    new_rec_glob[0].set_currency(db.get_last_rec_currency(db_filename, data_body_arr[1]))
    bot.edit_message_text(chat_id=new_rec_glob[1], message_id=new_rec_glob[2], text=line, reply_markup=key)

  if data_marker == 'income' or data_marker == 'expense' or data_marker == 'curr':
    key = funcs.get_currency_btns(db_filename, data_divider_in_callback, data_marker)
    
    if data_marker == 'curr':
      new_rec_glob[0].set_currency(data_body_arr[0])
    else:
      new_rec_glob[0].set_cat(classes.Category(data_marker, data_body_arr[0]))

    line = 'Input record info, example:\n' \
           '`1234 really great bananas!\n`' \
           'Means \'I just spent (or earned) 1234 ' + new_rec_glob[0].currency + ' on bananas that i really love\''
    try:
      bot.edit_message_text(chat_id=new_rec_glob[1], message_id=new_rec_glob[2], text=line, parse_mode='Markdown', reply_markup=key)
    except Exception as e:
      print(e)

    if data_marker != 'curr':
      bot.register_next_step_handler(message, finalise_new_record)

  # part for /add_record END

if __name__ == '__main__':

  db_started = db.start(db_filename)
  print('Start db:', db_started)

  bot.infinity_polling()
