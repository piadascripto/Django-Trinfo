from io import StringIO
import logging
import requests
import csv
from django.db import transaction
from django.contrib.auth.models import User
from base.models import Order, Brokerage

@transaction.atomic
def save_orders_to_db(user_id, brokerage_id, orders):
	brokerage = Brokerage.objects.get(id=brokerage_id)
	logging.info(f"Saving orders to database for user {user_id} and brokerage {brokerage_id}")
	for record in orders:
		order, created = Order.objects.get_or_create(
			brokerage_order_id=record['brokerage_order_id'],
			defaults={
				'user': User.objects.get(id=user_id), 
				'brokerage': brokerage,
				'client_brokerage_account_id': record['client_brokerage_account_id'],
				'listing_exchange': record['listing_exchange'],
				'asset_class': record['asset_class'],
				'symbol': record['symbol'], 
				'date_time': record['date_time'],
				'time_zone': record['time_zone'], 
				'buy_sell': record['buy_sell'], 
				'open_close': record['open_close'],
				'quantity': record['quantity'], 
				'currency': record['currency'], 
				'order_price': record['order_price'],
				'order_money': record['order_money'],
				'brokerage_commission': record['brokerage_commission'],
				'net_money': record['net_money'],
			}
		)
		if created:
			logging.info(f"New order created: {order}")

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

