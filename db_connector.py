#!/usr/bin/env python3

import sqlite3
import classes

import os

from config import db_filename
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

def init_db(db_file_name):
  ''' Init db, create tables, input default values '''
  print('Init db, filename:\'' + db_file_name + '\'')

  try:
    conn = sqlite3.connect(db_file_name)
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

    c.executemany('INSERT INTO records(user_id, type, category, date_ts, comment, currency, amount)  \
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

def select(db_file_name, table, fields='*', filters=None):
  ''' Make SELECT request to db '''
  try:
    conn = sqlite3.connect(db_file_name)
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
    last_rec_num = print(select(db_filename, 'records')[-1][0])
    new_rec_num = last_rec_num + 1
  except Exception:
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
  ''' Return all records from db for one user_id in array
      arr[0] will be result (True/False, False if records were not found) '''
  rec_all_arr = [ False ]
  for rec in select(db_filename, 'records'):
    if rec_all_arr[0] == False:
      rec_all_arr[0] = True
    new_rec = rec_to_obj(rec)
    rec_all_arr.append(new_rec)
  return rec_all_arr

def get_recs_user(db_filename, user_id):
  ''' Return record selected by 'field':'value' for one user_id in array
      arr[0] will be result (True/False, False if records were not found) '''
  rec_user_arr = []
  for rec in get_recs_all(db_filename):
    if type(rec) == bool:
      continue
    if rec.user_id == user_id:
      rec_user_arr.append(rec)
  return rec_user_arr

# if __name__ == '__main__':
  # print(select(db_filename, 'records', '*', 'user_id="123456"'))
  # print(get_recs_user(db_filename, '123456'))