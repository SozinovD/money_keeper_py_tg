import classes
import db_connector as db

help_msg = '''
This bot helps you to track your money usage
There are commands below:

/help - show this help page
/add_record - add new income or expense record
/show_report - generate report (will be avalible in v2 and above)
'''

def get_help_msg():
  return help_msg

def get_cat_obj_by_name(name):
  '''
  Get category object by category name
  '''
  cats = db.get_cats_arr()
  for cat in cats:
    if cat.name == name:
      return cat
