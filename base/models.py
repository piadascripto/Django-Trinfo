from django.contrib.auth.models import User
from base.utils import time_difference_simplifier
from django.db import models

class Brokerage(models.Model):
	
    NAME_CHOICES = (
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
        ('foxbit', 'Foxbit')
        # ... add more names as needed
		# Brokerages are hardcoded as they change infrequently. 
        # If any changes are needed, they will likely be minor (addition or removal of one or two brokerages).
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, choices=NAME_CHOICES)
    alias = models.CharField(max_length=20, null=True)
    login = models.CharField(max_length=100)
    key = models.CharField(max_length=100)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Brokerage: {self.name} - {self.alias}"

class Trade(models.Model):
    symbol = models.CharField(max_length=10)
    long_short = models.CharField(max_length=5)
    win_loss = models.CharField(max_length=5)
    quantity_of_orders = models.IntegerField()
    quantity_trade_asset = models.FloatField()
    trade_money = models.FloatField()
    trade_result = models.FloatField()
    trade_result_percentage = models.FloatField()
    trade_brokerage_commission = models.FloatField()
    date_open = models.DateTimeField()
    date_close = models.DateTimeField()
    holding_time = models.CharField(max_length=20)
	
    class Meta:
        ordering = ['-date_close']
    def __str__(self):
        return f"Trade: {self.symbol}- {self.win_loss}: {self.trade_result} - {self.holding_time}"

class Order(models.Model):
    BUY_SELL_CHOICES = (
        ('buy', 'buy'),
        ('sell', 'sell')
	)
    OPEN_CLOSE_CHOICES = (
        ('open', 'open'),
        ('close', 'close'),
		('flip', 'flip')
	)
    trade = models.ForeignKey(Trade, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    brokerage = models.ForeignKey(Brokerage, on_delete=models.CASCADE)  # turn SET NULL after testing
    client_brokerage_account_id = models.CharField(max_length=20, null=True)
    listing_exchange = models.CharField(max_length=20)
    asset_class = models.CharField(max_length=20)
    symbol = models.CharField(max_length=10)
    brokerage_order_id = models.CharField(max_length=20)
    date_time = models.DateTimeField()
    time_zone = models.CharField(max_length=5)
    buy_sell = models.CharField(max_length=5, choices=BUY_SELL_CHOICES)
    open_close = models.CharField(max_length=5, choices=OPEN_CLOSE_CHOICES)  # binance dont have this :S 
    quantity = models.FloatField()
    currency = models.CharField(max_length=10, null=True)
    order_price = models.FloatField()
    order_money = models.FloatField()
    brokerage_commission = models.FloatField(null=True, default=0.0)
    net_money = models.FloatField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)  # true is already inside a trade

    class Meta:
        ordering = ['-date_time']

    @classmethod
    def generate_trades_from_unprocessed_orders(cls):
        unprocessed_orders = cls.objects.filter(processed=False)
        
        quantity_sum = {}
        orders_within_trade = {}

        for order in unprocessed_orders:
            symbol = order.symbol
            quantity = order.quantity

            if symbol not in quantity_sum:
                quantity_sum[symbol] = 0
                orders_within_trade[symbol] = []

            quantity_sum[symbol] += quantity
            orders_within_trade[symbol].append(order)

            if quantity_sum[symbol] == 0:
                long_short = "long" if orders_within_trade[symbol][0].open_close == "O" and orders_within_trade[symbol][0].buy_sell == "buy" else "short"
                trade_result = sum(o.net_money for o in orders_within_trade[symbol])
                trade_money = sum(abs(o.order_money) for o in orders_within_trade[symbol] if o.open_close == "open")
                quantity_trade_asset = sum(abs(o.quantity) for o in orders_within_trade[symbol] if o.open_close == "open")
                trade_result_percentage = trade_result / trade_money
                win_loss = "win" if trade_result > 0 else "loss"
                trade_brokerage_commission = sum(o.brokerage_commission for o in orders_within_trade[symbol] if o.brokerage_commission)
                date_open = min(o.date_time for o in orders_within_trade[symbol])
                date_close = max(o.date_time for o in orders_within_trade[symbol])

                trade = Trade(
                    symbol=symbol,
                    long_short=long_short,
                    win_loss=win_loss,
					trade_result=trade_result,
					trade_money=trade_money,
                    quantity_of_orders=len(orders_within_trade[symbol]),
                    quantity_trade_asset=quantity_trade_asset,
                    trade_result_percentage=trade_result_percentage,
                    trade_brokerage_commission=trade_brokerage_commission,
                    date_open=date_open,
                    date_close=date_close,
                    holding_time=time_difference_simplifier(date_open, date_close),
                )
                trade.save()

                for o in orders_within_trade[symbol]:
                    o.trade = trade
                    o.save()

                # Reset for next group
                orders_within_trade[symbol] = []

        # After generating trades, mark orders as processed
        unprocessed_orders.update(processed=True)
    
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
