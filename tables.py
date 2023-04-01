table_cat = '''CREATE TABLE categories
              (id INTEGER PRIMARY KEY,
              type varchar(20) NOT NULL,
              name varchar(20) NOT NULL)'''

table_curr = '''CREATE TABLE currencies
              (id INTEGER PRIMARY KEY,
              name varchar(3) NOT NULL,
              to_usd REAL)'''

table_rec = '''CREATE TABLE records
              (id INTEGER PRIMARY KEY,
              user_id INTEGER NOT NULL,
              type varchar(20) NOT NULL,
              category varchar(20) NOT NULL,
              date_ts INTEGER NOT NULL,
              comment varchar(100),
              currency varchar(3) NOT NULL,
              amount INTEGER NOT NULL)'''

tables_arr = [ table_cat, table_curr, table_rec ]

default_cats_arr = [['Salary', 'income'], ['Sell', 'income'], ['Other', 'income'], \
                    ['Food', 'expense'], ['Clothes', 'expense'],  ['Fun', 'expense'], ['Other', 'expense']]

default_currs_arr = ['RUR', 'KZT', 'DKK']
