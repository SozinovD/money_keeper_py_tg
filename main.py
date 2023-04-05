#!/usr/bin/env python3

import time

import telebot
from telebot import types

from config import bot_token
from config import owner_id
from config import db_filename as db_name

import functions as funcs
import db_handler as db
import currency_api_handler as currs_api

import classes

bot = telebot.TeleBot(bot_token)
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
  amount_usd = currs_api.get_today_rate(new_rec_glob[0].currency, 'usd') * amount
  new_rec_glob[0].set_amount_usd(round(amount_usd, 2))
  new_rec_glob[0].set_comment(comment)
  line = db.add_rec(db_name, new_rec_glob[0])
  if not line:
    line = 'Record added'
  bot.edit_message_text(chat_id=new_rec_glob[1], message_id=new_rec_glob[2], text=line)

def add_curr_handler(message):
  curr_name = message.text
  bot.send_message(message.from_user.id, db.add_curr(db_name, curr_name))

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
    key = funcs.get_start_rec_add_kbrd(data_divider_in_callback, message.from_user.id)
    bot.send_message(message.from_user.id, 'Choose type of record', reply_markup=key)

  if message.text == '/currs_setup':
    key = funcs.get_curr_setup_kbrd(data_divider_in_callback)
    bot.send_message(message.from_user.id, 'Choose action with currencies', reply_markup=key)

  if message.text == '/generate_report':
    bot.send_message(message.from_user.id, 'Feature is not ready yet')
    # bot.register_next_step_handler(message, do_show_report)  # todo: generate report

  if message.text == '/show_all':
    records = db.get_recs_by_filter(db_name, message.from_user.id)
    if len(records) < 1:
      bot.send_message(message.from_user.id, 'You do not have records')
    else:
      bot.send_message(message.from_user.id, 'Sending all your records')
    for record in records:
      print(record)
      bot.send_message(message.from_user.id, str(record.__dict__))

  if message.text == '/show_last_3':
    records = db.get_last_n_recs(db_name, message.from_user.id, 3)
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

  # print('data_marker', data_marker)
  # print('data_body_arr', data_body_arr)
  # print(data_body_arr)

  # part for /add_record START
  if data_marker == 'back_to_start':
    line = 'Choose type of record'
    key = funcs.get_start_rec_add_kbrd(data_divider_in_callback)
    bot.edit_message_text(chat_id=new_rec_glob[1], message_id=new_rec_glob[2], text=line, reply_markup=key)

  if data_marker == 'start':
    line = 'Choose category'
    key = funcs.get_cat_btns_by_type(db_name, data_body_arr[0], data_divider_in_callback)
    new_rec_glob[0].set_currency(db.get_last_rec_currency(db_name, data_body_arr[1]))
    bot.edit_message_text(chat_id=new_rec_glob[1], message_id=new_rec_glob[2], text=line, reply_markup=key)

  if data_marker == 'income' or data_marker == 'expense' or data_marker == 'a_r_curr':
    key = funcs.get_currency_btns(db_name, data_divider_in_callback, 'a_r_')
    back_btn_callback_data = funcs.enc_callback_data(data_divider_in_callback, 'back_to_start\'')
    key.add(types.InlineKeyboardButton(text='Back to start', callback_data=back_btn_callback_data))
    
    if data_marker == 'a_r_curr':
      new_rec_glob[0].set_currency(data_body_arr[0])
    else:
      new_rec_glob[0].set_category(classes.Category(data_marker, data_body_arr[0]))

    line = '*' + new_rec_glob[0].currency + ' = ' + str(currs_api.get_today_rate(new_rec_glob[0].currency, 'usd')) + ' USD' \
          '*\nInput record info, example:\n' \
          '`1200 really great bananas!\n`' \
          'Means \n\'_I just spent (or earned) 1200 on bananas that i really love_\''
    try:
      bot.edit_message_text(chat_id=new_rec_glob[1], message_id=new_rec_glob[2], text=line, parse_mode='Markdown', reply_markup=key)
    except Exception as e:
      print(e)

    if data_marker != 'a_r_curr':
      bot.register_next_step_handler(message, finalise_new_record)
  # part for /add_record END

  if data_marker == 'curr_setup':
    if data_body_arr[0] == 'add':
      line = 'Input currency identificator, for example\nUSD'
      bot.edit_message_text(chat_id=new_rec_glob[1], message_id=new_rec_glob[2], text=line)
      bot.register_next_step_handler(message, add_curr_handler)
    else:
      key = funcs.get_currency_btns(db_name, data_divider_in_callback, 'del_')
      line = 'Choose currency to delete'
      bot.edit_message_text(chat_id=new_rec_glob[1], message_id=new_rec_glob[2], text=line, reply_markup=key)

  if data_marker == 'del_curr':
    line = db.del_curr(db_name, data_body_arr[0])
    bot.edit_message_text(chat_id=new_rec_glob[1], message_id=new_rec_glob[2], text=line)


if __name__ == '__main__':

  db_started = db.start(db_name)
  print('Start db:', db_started)

  bot.infinity_polling()
