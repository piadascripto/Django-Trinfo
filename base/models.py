from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Brokerage(models.Model):
	NAME_CHOICES = [
		('interactive_brokers', 'Interactive Brokers'),
		('tradezero', 'TradeZero'),
		('binance', 'Binance'),
		('coinbase', 'Coinbase'),
		('kucoin', 'KuCoin'),
		('bybit', 'Bybit'),
		('okx', 'OKX'),
		('bitstamp', 'Bitstamp'),
		('bitfinex', 'Bitfinex'),
		('gate_io', 'Gate.io'),
		('gemini', 'Gemini'),
		('bitget', 'Bitget'),
		('huobi', 'Huobi'),
		('mercado_bitcoin', 'Mercado Bitcoin'),
		('foxbit', 'Foxbit'),
		# ... add more names as needed
	]
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=20, choices=NAME_CHOICES)
	alias = models.CharField(max_length=20, null=True)
	login = models.CharField(max_length=100)
	key = models.CharField(max_length=100)
	updated = models.DateTimeField(auto_now=True)
	created = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return f"Brokerage: {self.name} - {self.alias}"

class Order(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	brokerage = models.ForeignKey(Brokerage, on_delete=models.CASCADE) #turn SET NULL after testing
	client_brokerage_account_id = models.CharField(max_length=20, null=True)
	listing_exchange = models.CharField(max_length=20)
	asset_class = models.CharField(max_length=20)
	symbol = models.CharField(max_length=10)
	brokerage_order_id = models.CharField(max_length=20)
	date_time = models.DateTimeField()
	time_zone = models.CharField(max_length=5)
	buy_sell = models.CharField(max_length=5)
	open_close = models.CharField(max_length=5) #binance não tem 
	quantity = models.FloatField()
	currency = models.CharField(max_length=10, null=True)
	order_price = models.FloatField()
	order_money = models.FloatField()
	brokerage_commission = models.FloatField(null=True)
	net_money = models.FloatField()
	updated = models.DateTimeField(auto_now=True)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Order: {self.symbol} {self.date_time} - {self.id}"

class Tag(models.Model):
    name = models.CharField(max_length=50)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
	
"""
class Quotes(models.Model):
    asset_class = models.CharField(max_length=20)
    symbol = models.CharField(max_length=10)
	date = models.DateTimeField()
    currency_primary = models.CharField(max_length=5)
    high_price = models.FloatField()
    low_price = models.FloatField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
"""