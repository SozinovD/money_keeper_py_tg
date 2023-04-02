#!/usr/bin/env python3

import sqlite3
import classes

import os

from config import db_filename as db_file_name      # for tests
from tables import tables_arr, default_cats_arr, default_currs_arr

def start(db_filename):
  ''' Connect to db, create if it doesn't exist, return conn obj '''
  try:
    conn = sqlite3.connect(db_filename)
  except Exception as e:
    return e
  finally:
    if conn:
      conn.close()

  if os.stat(db_filename).st_size == 0:
    result = init_db(db_filename)
    return result

  return True

def init_db(db_filename):
  ''' Init db, create tables, input default values '''
  print('Init db, filename:\'' + db_filename + '\'')

  try:
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    # create tables
    for table in tables_arr:
      c.execute(table)
    # insert default values
    c.executemany('INSERT INTO categories(type, name) VALUES (?,?)', default_cats_arr)
    for curr in default_currs_arr:
      c.execute('INSERT INTO currencies(name) VALUES (?)', (curr,))

    # make sure changes are permanent
    conn.commit()
    return True
  except sqlite3.Error as e:
    return e
  finally:
    if conn:
      conn.close()

def add_rec(db_filename, new_rec):
  ''' Add new record to db,  return result '''
  try:
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    rec_data_arr = new_rec.get_arr()

    # add record
    c.executemany('INSERT INTO records(user_id, type, category, date_ts, comment, currency, amount) \
                   VALUES (?,?,?,?,?,?,?)', (rec_data_arr,))

    result = c.fetchall()
    # make sure changes are permanent
    conn.commit()

  except sqlite3.Error as e:
    # print(e)
    return e
  finally:
    if conn:
      conn.close()
  return result

def select(db_filename, table, fields='*', filters=None):
  ''' Make SELECT request to db '''
  try:
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    request = 'SELECT ' + fields + ' FROM ' + table
    if not filters == None:
      request += ' WHERE ' + filters
    c.execute(request)

    result = c.fetchall()
  except sqlite3.Error as e:
    # print(e)
    return e
  finally:
    if conn:
      conn.close()
  return result

def get_cats_arr(db_filename):
  ''' Get categories from db, return them in array '''
  cats_arr = []
  for cat in select(db_filename, 'categories'):
    new_cat = classes.Category(cat[1], cat[2])
    cats_arr.append(new_cat)
  return cats_arr

def get_new_rec_num(db_filename):
  ''' Get last record num, return +1 '''
  try:
    last_rec_num = select(db_filename, 'records')[-1][0]
    new_rec_num = int(last_rec_num) + 1
  except Exception as e:
    new_rec_num = 1
  return new_rec_num

def rec_to_obj(rec):
  ''' Get record from db, return Record object '''
  rec_obj = classes.Record(rec[0])
  rec_cat = classes.Category(rec[2], rec[3])
  rec_obj.set_user_id(rec[1])
  rec_obj.set_cat(rec_cat)
  rec_obj.set_date_ts(rec[4])
  rec_obj.set_comment(rec[5])
  rec_obj.set_currency(rec[6])
  rec_obj.set_amount(rec[7])
  return rec_obj

def get_recs_all(db_filename):
  ''' Return all records from db for one user_id in array '''
  rec_all_arr = []
  recs = select(db_filename, 'records')
  for rec in recs:
    rec_all_arr.append(rec_to_obj(rec))
  return rec_all_arr

def get_recs_by_filter(db_filename, user_id, filters=None):
  ''' Return record selected by 'field':'value' for one user_id in array '''
  recs_arr = []
  filt = 'user_id="' + str(user_id) + '"'
  if filters != None:
    filt += filters
  recs = select(db_filename, 'records', '*', filt)
  for rec in recs:
    recs_arr.append(rec_to_obj(rec))
  return recs_arr

def get_last_rec_currency(db_filename, user_id):
  ''' Return currency of last record '''
  filt = 'user_id="' + str(user_id) + '"'
  try:
    result = select(db_filename, 'records', 'currency', filt)[-1][0]
    return result
  except Exception:
    return 'USD'

def get_currs_arr(db_filename):
  currs_arr = []
  result = select(db_filename, 'currencies', 'name')
  for curr in result:
    currs_arr.append(curr[0])
  return currs_arr

def get_last_n_recs(db_filename, user_id, rec_num):
  recs_arr = []
  min_num = get_new_rec_num(db_filename) - rec_num
  recs_arr = get_recs_by_filter(db_filename, user_id, 'AND id >= ' + str(min_num))
  return recs_arr

# if __name__ == '__main__':
  
#   print(get_last_n_recs(db_file_name, 317600836, 3))
#   print(get_currs(db_file_name))
#   print(get_last_rec_currency(db_file_name, 317600836))
#   print(select(db_file_name, 'records')[-1][0])
#   print(select(db_file_name, 'records', '*', 'user_id="123456"'))
#   print(get_recs_user(db_file_name, '123456'))