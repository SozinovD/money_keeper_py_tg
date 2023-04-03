import classes
import db_connector as db
from telebot import types

help_msg = '''
This bot helps you to track your money usage
There are commands below:

/help - show this help page
/add_record - add new income or expense record
/show_report - generate report (will be avalible in v2 and above)
'''

def get_help_msg():
  ''' Just return help msg '''
  return help_msg

def enc_callback_data(divider, *words):
  ''' Encode data into one line for callback using a divider, return line '''
  call_data = ''
  for word in words:
    call_data += str(word) + str(divider)
  return call_data

def dec_callback_data(divider, call_data):
  ''' Decode data from callback using a divider, return in array '''
  data_arr = []
  for word in call_data.split(divider):
    data_arr.append(word)
  return data_arr

def get_cat_btns_by_type(db_filename, cat_type, divider):
  ''' Return keyboard with needed categories ready to be used in msg '''
  btns_arr = []
  for cat in db.get_cats_arr(db_filename):
    if cat.type == cat_type:
      btn_data = enc_callback_data(divider, cat_type, cat.name)
      btns_arr.append([cat.name, btn_data])
  btns_arr.append(['Back to start', 'back_to_start' + divider])
  return get_keys_in_rows(2, btns_arr)

def get_currency_btns(db_filename, divider, rec_type):
  ''' Return keyboard with currencies ready to be used in msg '''
  btns_arr = []
  for curr in db.get_currs_arr(db_filename):
    btn_data = enc_callback_data(divider, 'curr', curr)
    btns_arr.append([curr, btn_data])
  return get_keys_in_rows(4, btns_arr)

def get_start_rec_add_kbrd(divider, user_id=None):
  ''' Returns default keyboard for /add_record func  '''
  prefix = enc_callback_data(divider, 'start')
  btns_arr = []
  btns_arr.append(['Income', enc_callback_data(divider, 'start', 'income', user_id)])
  btns_arr.append(['Expence', enc_callback_data(divider, 'start', 'expense', user_id)])
  return get_keys_in_rows(2, btns_arr)

def get_keys_in_rows(columns_num, btn_data_arr):
  ''' Return keyboard that is sorted in rows and columns '''
  num = 0
  btn_arr = []
  key = types.InlineKeyboardMarkup()
  for btn in btn_data_arr:
    if int(num) >= int(columns_num):
      num = 0
      key.add(*btn_arr)
      btn_arr = []
    num+=1
    btn_arr.append(types.InlineKeyboardButton(text=btn[0], callback_data=btn[1]))
  if btn_arr:
    key.add(*btn_arr)
  return key