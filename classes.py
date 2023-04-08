from dataclasses import dataclass

@dataclass
class Category():
  ''' Class for income\expense categories '''
  type: str   # income\expense
  name: str   # any name
  
  def __init__(self):
    self.name = 'No name'
    self.type = 'No type'

  def set_name(self, name: str):
    self.name = str(name)
  def set_type(self, type: str):
    if type != 'income' and type != 'expense':
      line = 'ERROR: unsupported category type: ' + type
      return line
    self.type = str(type)
  


@dataclass
class Record:
  ''' Class for db records '''
  id: int               # sequential number
  user_id: int          # user that sent this record
  type: str             # type of record. Usually income or expense
  category: Category()  # a category name
  date_ts: int          # when record was done
  comment: str          # a comment for record
  currency: str         # tree-letters currency code
  amount: float         # amount for this record
  amount_usd: float     # amount for this record

  def __init__(self):
    self.id = 0
    self.user_id = ''
    self.type = ''
    self.category = Category()
    self.date_ts = ''
    self.comment = ''
    self.currency = 'USD'
    self.amount = 0
    self.amount_usd = 0

  def set_id(self, id: int):
    self.id = int(id)

  def set_user_id(self, user_id: int):
    self.user_id = int(user_id)

  def set_category(self, category:Category):
    self.category = str(category.name)
    self.type = str(category.type)

  def set_date_ts(self, date_ts: int):
    self.date_ts = int(date_ts)

  def set_currency(self, currency: str):
    self.currency = str(currency)

  def set_amount(self, amount: int):
    self.amount = float(amount)

  def set_amount_usd(self, amount_usd: int):
    self.amount_usd = float(amount_usd)

  def set_comment(self, comment: str):
    self.comment = str(comment)

  def get_arr(self):
    arr = []
    arr.append(['user_id', int(self.user_id)])
    arr.append(['type', self.type])
    arr.append(['category', self.category])
    arr.append(['date_ts', int(self.date_ts)])
    arr.append(['comment', self.comment])
    arr.append(['currency', self.currency])
    arr.append(['amount', float(self.amount)])
    arr.append(['amount_usd', float(self.amount_usd)])
    return arr

  def get_obj_from_arr(self, arr):
    obj = Record()
    obj.set_id(arr[0])
    obj.set_user_id(arr[1])

    cat = Category()
    cat.set_name(arr[2])
    cat.set_type(arr[3])
    
    obj.set_category(cat)
    obj.set_date_ts(arr[4])
    obj.set_comment(arr[5])
    obj.set_currency(arr[6])
    obj.set_amount(arr[7])
    obj.set_amount_usd(arr[8])
    return obj