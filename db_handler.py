#!/usr/bin/env python3

import classes
import currency_api_handler as currs_api
from config import db_filename as db_file_name      # for tests

from datetime import datetime
import sqlite3_requests as db_requests

from tables import tables_arr, default_cats_arr, default_currs_arr

import time

def start(db_name):
  ''' Connect to db, create if it doesn't exist, return conn obj '''
  return db_requests.check_init(db_name)


def get_cats_arr(db_name):
  ''' Get categories from db, return them in array '''
  cats_arr = []
  for cat in db_requests.select(db_name, 'categories', 'name, type'):
    new_cat = classes.Category()
    new_cat.set_name(cat[0])
    new_cat.set_type(cat[1])
    cats_arr.append(new_cat)
  return cats_arr

def add_rec(db_name, new_rec):
  ''' Add new record to db, return result '''
  fields_arr = new_rec.get_arr()
  # print(fields_arr)
  result = db_requests.add_record_to_db(db_name, 'records', fields_arr)
  if type(result) == type(list()):
    last_rec = get_last_n_recs(db_name, fields_arr[0][1], 1)[0]
    # print('last_rec', last_rec)
    new_rec.set_id(last_rec.id)
    return new_rec
  else:
    return result

def del_last_rec_1_hour(db_name, user_id, forced = False):
  ''' Delete last record if it was made less then hour ago '''
  last_rec = get_last_n_recs(db_name, user_id, 1)[0]
  # if more than 1 hour passed
  if round(time.time(), 0) - last_rec.date_ts > 3600 or forced != False:
    return 'Can\'t delete record older than 1 hour'
  filters = 'id="' + str(last_rec.id) + '"'
  result = db_requests.del_records_from_db(db_name, 'records', filters)
  if result == filters:
    result = 'Record deleted'
  return result

def get_new_rec_num(db_name):
  ''' Get last record num, return +1 '''
  try:
    last_rec_num = db_requests.select(db_name, 'records')[-1][0]
    new_rec_num = int(last_rec_num) + 1
  except Exception as e:
    new_rec_num = 1
  return new_rec_num

def get_recs_all(db_name):
  ''' Return all records from db in array '''
  rec_all_arr = []
  recs = db_requests.select(db_name, 'records')
  new_rec = classes.Record()
  for rec in recs:
    rec_all_arr.append(new_rec.get_obj_from_arr(rec))
  return rec_all_arr

def get_recs_by_filter(db_name, user_id, filters=None):
  ''' Return record selected by 'field':'value' for one user_id in array '''
  recs_arr = []
  filt = 'user_id="' + str(user_id) + '"'
  if filters != None:
    filt += filters
  recs = db_requests.select(db_name, 'records', '*', filt)
  new_rec = classes.Record()
  for rec in recs:
    recs_arr.append(new_rec.get_obj_from_arr(rec))
  return recs_arr

def get_last_n_recs(db_name, user_id, rec_num):
  recs_arr = []
  min_num = get_new_rec_num(db_name) - rec_num
  recs_arr = get_recs_by_filter(db_name, user_id, 'AND id >= ' + str(min_num))
  return recs_arr


def get_last_rec_currency(db_name, user_id):
  ''' Return currency of last record '''
  filt = 'user_id="' + str(user_id) + '"'
  try:
    result = db_requests.select(db_name, 'records', 'currency', filt)[-1][0]
    return result
  except Exception as e:
    print(e)
    return 'USD'

def get_currs_arr(db_name):
  currs_arr = []
  result = db_requests.select(db_name, 'currencies', 'name')
  for curr in result:
    currs_arr.append(curr[0])
  return currs_arr

def add_curr(db_name, new_curr):
  ''' Add currency into db '''
  new_curr = new_curr.upper()
  if 2 > len(new_curr) or len(new_curr) > 5 :
    return 'Curr identificator must be 2-5 letters'
  if type(currs_api.get_today_rate(new_curr, 'usd')) != float:
    return 'Couldn\'t get new currency rates for: ' + new_curr
  if new_curr in get_currs_arr(db_name):
    return 'Currency already exists in db: ' + new_curr

  fields_arr = [['name', str(new_curr)]]
  result = db_requests.add_record_to_db(db_name, 'currencies', fields_arr)
  if type(result) == type(list()):
    return 'Currency added: ' + result[0][1]
  else:
    return result

def del_curr(db_name, del_curr):
  ''' Delete curr from bd. Don't touch default or if there are records containing it '''
  del_curr = del_curr.upper()
  if not del_curr in get_currs_arr(db_name):
    return 'Currency not found in db: ' + del_curr
  if del_curr in default_currs_arr:
    return 'Can\'t delete default currency'
  used_currs_arr = []
  for rec in get_recs_all(db_name):
    if not rec.currency in used_currs_arr:
      used_currs_arr.append(rec.currency)
  if del_curr in used_currs_arr:
    return 'Can\'t delete currency that is being used in records'
  filters_arr = [ 'name="' + del_curr + '"' ]
  result = db_requests.del_records_from_db(db_name, 'currencies', filters_arr)[0]
  return 'Currency deleted: ' + result.split('"')[1]

def set_amount_usd_all_recs(db_name):
  ''' Helps with old records without such info '''
  recs = get_recs_all(db_name)
  rec_data = []
  for rec in recs:
    date_of_rec = datetime.utcfromtimestamp(rec.date_ts).strftime('%Y-%m-%d')
    amount_usd = round(currs_api.get_rate(rec.currency , 'usd', date_of_rec) * rec.amount, 2)
    db_requests.update_records_in_db(db_name, 'records', 'amount_usd=' + str(amount_usd), 'id=' + str(rec.id))

# if __name__ == '__main__':
  # print(db_requests.update_records_in_db(db_file_name, 'records', 'currency = "BTC"', 'id > 14'))
  # print(set_amount_usd_all_recs(db_file_name))
#   curr_arr = [[['name', 'GBP']], [['name', 'DOGE']], [['name', 'USDT']]]
#   print(db_requests.add_many_records_to_db(db_file_name, 'currencies', curr_arr))
#   print(del_curr(db_requests.db_file_name, 'GBP'))
  # print(db_requests.add_curr(db_file_name, 'KZK'))
#   print(db_requests.get_last_n_recs(db_file_name, 317600836, 3))
#   print(db_requests.get_currs(db_file_name))
  # print(db_requests.get_last_rec_currency(db_file_name, '317600836'))
#   print(db_requests.select(db_file_name, 'records')[-1][0])
#   print(db_requests.select(db_file_name, 'records', '*', 'user_id="123456"'))
#   print(db_requests.get_recs_user(db_file_name, '123456'))
