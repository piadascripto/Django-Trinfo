import logging
import csv
import requests
from datetime import datetime as dt
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from io import StringIO
from pprint import pprint
from django.contrib.auth.models import User
from base.models import Order, Brokerage

logging.basicConfig(level=logging.INFO)


def parse_csv_to_dict(csv_string): #move this to utils.py
	csv_file = StringIO(csv_string)
	reader = csv.reader(csv_file)
	unique_rows = set()
	deduped_data = []
	for row in reader:
		if not row:
			continue
		row_tuple = tuple(row)
		if row_tuple not in unique_rows:
			deduped_data.append(row)
			unique_rows.add(row_tuple)
	headers = deduped_data[0]
	
	return [dict(zip(headers, row)) for row in deduped_data[1:]]


def fetch_page_content(url): #move this to utils.py
	try:
		response = requests.get(url)
		response.raise_for_status()
		return response.content, None
	except requests.HTTPError as http_err:
		error_msg = f"HTTP error occurred: {http_err}"
		logging.error(error_msg)
		return None, error_msg
	except Exception as err:
		error_msg = f"An error occurred: {err}"
		logging.error(error_msg)
		return None, error_msg


def connection_interactive_brokers(user_id, brokerage_id, IBKR_user_token, IBKR_user_query):

	def fetch_orders():
		url = f"https://www.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest?t={IBKR_user_token}&q={IBKR_user_query}&v=2"
		page_content, error = fetch_page_content(url)
		if error:
			logging.error(f"Error fetching IBKR data: {error}")
			return
		soup = BeautifulSoup(page_content, "html.parser")
		IBKR_code = soup.find("code").text.strip() if soup.find("code") else None
		if IBKR_code:
			user_query_url = f"https://www.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement?q={IBKR_code}&t={IBKR_user_token}&v=2"
            #DEBUGGING
            #print(user_query_url)
			IBKR_user_orders, error = fetch_page_content(user_query_url)
			if not error and IBKR_user_orders:
				orders_data = parse_csv_to_dict(IBKR_user_orders.decode('utf-8'))
                
				return orders_data
			else:
				logging.error("Error fetching user orders.")
				return None
		else:
			logging.error("Error fetching IBKR code.")
			return None
    
	def process_fetched_data(orders_data):
		processed_data = []
		for record in orders_data:
			required_fields = ['ClientAccountID', 'AssetClass', 'Symbol', 'TradeID', 'Buy/Sell', 'Open/CloseIndicator', 'Quantity', 'CurrencyPrimary', 'TradePrice', 'TradeMoney', 'IBCommission', 'NetCash']
			for field in required_fields:
				if not record.get(field):
					raise ValueError(f'Missing required field: {field}')
            
			date_time_str, timezone = record["DateTime"].rsplit(' ', 1)
			date_time_obj = dt.strptime(date_time_str, '%Y-%m-%d;%H:%M:%S')
            
			try:
				if record['Open/CloseIndicator'] == 'O':
					open_close = 'open'
				elif record['Open/CloseIndicator'] == 'C':
					open_close = 'close'
				elif record['Open/CloseIndicator'] == 'C;O':
					open_close = 'flip'
				else:
					raise ValueError("Invalid value for Open/CloseIndicator. It should be either 'O' for open or 'C' for close or 'Ç;O' for flip")
			except ValueError as e:
				logging.error(f"ValueError occurred: Invalid value for Open/CloseIndicator - {e}")
				raise

			try:
				if record['AssetClass'] == 'STK':
					asset_class = 'stocks'
				elif record['AssetClass'] == 'WAR':
					asset_class = 'warrants'
				elif record['AssetClass'] == 'CASH':
					asset_class = 'forex'
				elif record['AssetClass'] == 'IOPT':
					asset_class = 'index'
				elif record['AssetClass'] == 'FUND': 
					asset_class = 'funds'
				elif record['AssetClass'] == 'RTS': # I guess
					asset_class = 'rights'
				elif record['AssetClass'] == 'OPT': # I guess
					asset_class = 'options'
				elif record['AssetClass'] == 'FUT': # I guess
					asset_class = 'futures'
				elif record['AssetClass'] == 'CPT': # I guess
					asset_class = 'crypto'
				else:
					raise ValueError("Invalid value for AssetClas")
			except ValueError as e:
				logging.error(f"ValueError occurred: Invalid value for AssetClas -  {e}")
				raise

			processed_record = {
				'client_brokerage_account_id': record['ClientAccountID'],
				'listing_exchange': record['ListingExchange'],
				'asset_class': asset_class,
				'symbol': record['Symbol'].upper(),
				'brokerage_order_id': record['TransactionID'],
				'date_time': date_time_obj,
				'timezone': timezone,
				'buy_sell': record['Buy/Sell'].lower(),
				'open_close': open_close,
				'quantity': float(record['Quantity']),
				'currency_primary': record['CurrencyPrimary'].upper(),
				'order_price': float(record['TradePrice']),
				'order_money': float(record['TradeMoney']),
				'brokerage_commission': float(record['IBCommission']),
				'net_money': float(record['NetCash'])
			}
			processed_data.append(processed_record)
        
		return processed_data

	@transaction.atomic
	def save_orders_to_db(user_id, brokerage_id, orders):
		logging.info(f"Saving orders to database for user: {user_id}")
		for record in orders:
			order, created = Order.objects.get_or_create(
				brokerage_order_id=record['brokerage_order_id'],
				defaults={
					'user': User.objects.get(id=user_id), 
					'brokerage': brokerage_id,
					'client_brokerage_account_id': record['client_brokerage_account_id'],
					'listing_exchange': record['listing_exchange'],
					'asset_class': record['asset_class'],
					'symbol': record['symbol'], 
					'date_time': record['date_time'],
					'time_zone': record['timezone'], 
					'buy_sell': record['buy_sell'], 
					'open_close': record['open_close'],
					'quantity': record['quantity'], 
					'currency_primary': record['currency_primary'], 
					'order_price': record['order_price'],
					'order_money': record['order_money'],
					'brokerage_commission': record['brokerage_commission'],
					'net_money': record['net_money'],
				}
			)
			if created:
				logging.info(f"New order created: {order}")

	processed_data = process_fetched_data(fetch_orders())
	save_orders_to_db(user_id, processed_data)
				

class Command(BaseCommand):
	help = 'Fetches data from Interactive Brokers Flex Queries'
	def handle(self, *args, **kwargs):
		user_id = kwargs.get('user_id')
		brokerage_id = kwargs.get('brokerage_id')
		IBKR_user_token = kwargs.get('IBKR_user_token')
		IBKR_user_query = kwargs.get('IBKR_user_query')
		
		if not all([user_id, brokerage_id, IBKR_user_token, IBKR_user_query]):
			self.stdout.write(self.style.ERROR('All parameters: user_id, brokerage_id, IBKR_user_token, and IBKR_user_query are required.'))
			return

		orders_data = connection_interactive_brokers(user_id, brokerage_id, IBKR_user_token, IBKR_user_query)
		
		# Add this line to print out the fetched and processed data
		self.stdout.write(str(orders_data))


#Testing

#data = connection_interactive_brokers(1, 135962967293328323184330, 830297)
#pprint(data)
