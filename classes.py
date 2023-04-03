from dataclasses import dataclass

@dataclass
class Category():
  ''' Class for income\expense categories '''
  type: str   # income\expense
  name: str   # any name

  def __init__(self, name: str, type: str):
    self.type = str(type)
    self.name = str(name)


@dataclass
class Record:
  ''' Class for db records '''
  id: int           # sequential number
  user_id: int      # user that sent this record
  type: str         # type of record. Usually income or expense
  category: str     # a category name
  date_ts: int      # when record was done
  comment: str      # a comment for record
  currency: str     # tree-letters currency code
  amount: float     # amount for this record
  amount_usd: float # amount for this record

  def __init__(self, id: int):
    self.id = int(id)
    self.user_id = ''
    self.type = ''
    self.category = ''
    self.date_ts = ''
    self.comment = ''
    self.currency = 'USD'
    self.amount = 0
    self.amount_usd = 0

  def set_user_id(self, user_id: int):
    self.user_id = int(user_id)

  def set_cat(self, category:Category):
    self.category = str(category.name)
    self.type = str(category.type)

  def set_date_ts(self, date_ts: int):
    self.date_ts = int(date_ts)

  def set_currency(self, currency: str):
    self.currency = str(currency)

  def set_amount(self, amount: int):
    self.amount = int(amount)

  def set_comment(self, comment: str):
    self.comment = str(comment)

  def get_arr(self):
    arr = []
    # arr.append(int(self.id))
    arr.append(int(self.user_id))
    arr.append(self.type)
    arr.append(self.category)
    arr.append(int(self.date_ts))
    arr.append(self.comment)
    arr.append(self.currency)
    arr.append(int(self.amount))
    return arr