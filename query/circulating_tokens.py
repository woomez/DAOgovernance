from dotenv import load_dotenv
import os
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

#TODO:get unique blocktime from vote csv, use token address to query circulating token amount

load_dotenv()
cmc_api_key = os.getenv('CMC_API_KEY')

# Replace gitcoin with the slug of the token you are interested in
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/historical?date=2019-10-10'


parameters = {
  'start':'1',
  'limit':'5000',
  'convert':'USD'
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': cmc_api_key,
}

session = Session()
session.headers.update(headers)

try:
  response = session.get(url, params=parameters)
  data = json.loads(response.text)


# Extract the circulating supply data from the response using JMESPath
# Replace data.[*].circulating_supply with the appropriate JMESPath filter for your use case
#   circulating_supply_data = response.json()['data'][0]['quotes'][0]['circulating_supply']
  print(data)
#   print(circulating_supply_data)
except (ConnectionError, Timeout, TooManyRedirects) as e:
  print(e)