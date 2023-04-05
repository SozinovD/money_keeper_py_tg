import sqlite3
import os
from tables import tables_arr, default_cats_arr, default_currs_arr

def check_init(db_filename):
  ''' Connect to db, create if it doesn't exist, return conn obj '''
  try:
    conn = sqlite3.connect(db_filename)
  except Exception as e:
    return 'Error: ' + str(e) 
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
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()

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
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()
  return result

def add_records_to_db(db_filename, table, *fields_arr):
  ''' fields is an array of arrys: [field_name, value]
      'fields_arr' is a list of 'fields' arrs '''
  try:
    request_template = 'INSERT INTO {tbl_name} ({flds}) VALUES ({qstn_marks})'

    for fields in fields_arr:
      field_names = ''
      question_marks = ''
      values = ''
      conn = sqlite3.connect(db_filename)
      c = conn.cursor()
      print('db connected')
      for counter, field in enumerate(fields):
        field_names += field[0]
        question_marks += '?'
        values += str(field[1])
        if counter == len(fields) - 1:
          break
        field_names += ', '
        question_marks += ','
        values +='`'
      values = tuple(values.split('`'))

      request = request_template.format(tbl_name=table, flds=field_names, qstn_marks=question_marks)
      c.execute(request, (values))
    result = conn.commit()

    if result == None:
      result = fields
  except sqlite3.Error as e:
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()
  return result

def del_records_from_db(db_filename, table, filters):
  ''' Delete records from any table in db by filters '''
  try:
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    request = 'DELETE FROM ' + table + ' WHERE '
    for filt in filters:
      request += filt + ' '
    c.execute(request)
    result = conn.commit()
    if result == None:
      result = filters
  except sqlite3.Error as e:
    return 'Error: ' + str(e) 
  finally:
    if conn:
      conn.close()
  return result

def update_record_in_db(db_filename, table, filters, new_data):
  ''' Update records in db by filters '''
  # reference set_amount_usd_all_recs func
  result = 'todo'
  return result

def set_amount_usd_all_recs(db_name):
  try:
    recs = get_recs_all(db_name)
    rec_data = []
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    for rec in recs:
      date_of_rec = datetime.utcfromtimestamp(rec.date_ts).strftime('%Y-%m-%d')
      rec_data = []
      rec_data.append(round(currs_api.get_rate(rec.currency , 'usd', date_of_rec) * rec.amount, 2))
      rec_data.append(rec.id)
      print(rec_data)
      c.execute('Update records set amount_usd = ? where id = ?', (rec_data))
    conn.commit()

  except sqlite3.Error as e:
    return 'Error: ' + str(e)
  finally:
    if conn:
      conn.close()
  return 
