#!/usr/bin/env python3

# this is just genious
# https://github.com/fawazahmed0/currency-api

import requests

base_urls_arr = []
base_urls_arr.append('https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/')
base_urls_arr.append('https://raw.githubusercontent.com/fawazahmed0/currency-api/1/')

suffix_arr = []
suffix_arr.append('.min.json')
suffix_arr.append('.json')

def get_rate(curr1, curr2, date):
  curr1 = curr1.lower()
  curr2 = curr2.lower()
  for base_url in base_urls_arr:
    for suff in suffix_arr:
      url = base_url + date + '/currencies/' + curr1 + '/' + curr2 + suff
      rate = requests.get(url)
      if rate.status_code == 200:
        break
    if rate.status_code == 200:
      break
  if rate.status_code != 200:
    return 'Not found'
  return rate.json()[curr2]

def get_today_rate(curr1, curr2):
  return get_rate(curr1, curr2, 'latest')

# if __name__ == '__main__':
#   print(get_today_rate('aff', 'usd'))