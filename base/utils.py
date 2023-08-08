from io import StringIO
import logging
import requests
import csv
from django.db import transaction
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Case, When, Value, F, FloatField
from django.db.models.functions import Cast



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



# Calculate sums
def calculate_trades_stats(trades, timeframe):
    stats = trades.values(timeframe).annotate(
        total_trade_result=Sum('trade_result'),
        total_trade_money=Sum('trade_money'),
        total_trade_result_percentage=F('total_trade_result') / F('total_trade_money') * 100,

        total_trade_brokerage_commission=Sum('trade_brokerage_commission'),
        
        total_money_win=Sum(Case(When(trade_result__gt=0, then=F('trade_result')), default=Value(0.0))),
        total_trade_money_when_win=Sum(Case(When(trade_result__gt=0, then=F('trade_money')), default=Value(0.0))),
        total_money_win_percentage=F('total_money_win') / F('total_trade_money_when_win') * 100,
        
        total_money_loss=Sum(Case(When(trade_result__lt=0, then=F('trade_result')), default=Value(0.0))),
        total_trade_money_when_loss=Sum(Case(When(trade_result__lt=0, then=F('trade_money')), default=Value(0.0))),
        total_money_loss_percentage=F('total_money_loss') / F('total_trade_money_when_loss') * 100,
        
        total_of_trades=Count('trade_money'),
        total_of_orders=Sum('quantity_of_orders'),
        total_trades_win=Count(Case(When(trade_result__gt=0, then=1))),
        total_trades_loss=Count(Case(When(trade_result__lt=0, then=1))),
        average_trade_money=F('total_trade_money') / F('total_of_trades'),
        win_rate=Cast(F('total_trades_win'), FloatField()) / F('total_of_trades') * 100


    )

    stats_dict = {
        item[timeframe]: {
            'total_trade_result_percentage': item['total_trade_result_percentage'],
            'total_trade_result': item['total_trade_result'],
            'total_trade_money': item['total_trade_money'],
            'average_trade_money': item['average_trade_money'],
            'total_trade_brokerage_commission': item['total_trade_brokerage_commission'],
            'total_money_win': item['total_money_win'],
            'total_trade_money_when_win': item['total_trade_money_when_win'],
            'total_money_win_percentage': item['total_money_win_percentage'],
            'total_money_loss': item['total_money_loss'],
            'total_trade_money_when_loss': item['total_trade_money_when_loss'],
            'total_money_loss_percentage': item['total_money_loss_percentage'],
            'total_of_trades': item['total_of_trades'],
            'total_of_orders': item['total_of_orders'], 
            'total_trades_win': item['total_trades_win'],
            'total_trades_loss': item['total_trades_loss'],
            'win_rate': item['win_rate']
        } for item in stats
    }
    
    return stats_dict





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

# Maybe change and use lib Arrow (import arrow)
def time_difference_simplifier(initial_date, end_date):
	time_difference = end_date - initial_date
	if time_difference.total_seconds() < 60:  # Less than 60 minutes
		seconds_apart = time_difference.total_seconds()
		time_difference_simplify = str(int(seconds_apart)) + " second" + ("s" if seconds_apart != 1 else "")
	elif time_difference.total_seconds() < 3600:  # Less than 60 minutes
		minutes_apart = time_difference.total_seconds() // 60
		time_difference_simplify = str(int(minutes_apart)) + " minute" + ("s" if minutes_apart != 1 else "")
	elif initial_date.date() == end_date.date():  # Same day
		hours_apart = time_difference.total_seconds() // 3600
		time_difference_simplify = str(int(hours_apart)) + " hour" + ("s" if hours_apart != 1 else "") 
	else:  # Different days
		days_apart = (end_date.date() - initial_date.date()).days
		time_difference_simplify = str(days_apart) + " day" + ("s" if days_apart != 1 else "")

	return time_difference_simplify