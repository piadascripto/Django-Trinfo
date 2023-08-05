from django.db import models

# Create your models here.




"""

from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_brokerage_account_id = models.CharField(max_length=20)
    brokerage = models.CharField(max_length=20)
    listing_exchange = models.CharField(max_length=20)
    asset_class = models.CharField(max_length=20)
    symbol = models.CharField(max_length=10)
    brokerage_order_id = models.CharField(max_length=20)
    date_time = models.DateTimeField()
    time_zone = models.CharField(max_length=5)
    buy_sell = models.CharField(max_length=5)
    open_close = models.CharField(max_length=1)
    quantity = models.FloatField()
    currency_primary = models.CharField(max_length=5)
    order_price = models.FloatField()
    order_money = models.FloatField()
    brokerage_commission = models.FloatField()
    net_money = models.FloatField()

    def __str__(self):
        return f"Order {self.id}"

    @classmethod
    def create_trade(cls):
        orders = cls.objects.all()
        trades = []
        quantity_sum = {}
        orders_within_trade = {}

        for order in orders:
            symbol = order.symbol
            quantity = order.quantity

            if symbol not in quantity_sum:
                quantity_sum[symbol] = 0
                orders_within_trade[symbol] = []

            quantity_sum[symbol] += quantity
            orders_within_trade[symbol].append(order)

            if quantity_sum[symbol] == 0:
                long_short = "LONG" if orders_within_trade[symbol][0].open_close == "O" and orders_within_trade[symbol][0].buy_sell == "BUY" else "SHORT"
                trade_result = sum(order.net_money for order in orders_within_trade[symbol])
                trade_amount = sum(abs(order.order_money) for order in orders_within_trade[symbol] if order.open_close == "O")
                trade_shares_quantity = sum(abs(order.quantity) for order in orders_within_trade[symbol] if order.open_close == "O")
                trade_result_percentage = trade_result / trade_amount
                win_loss = "WIN" if trade_result > 0 else "LOSS"
                trade_fee = sum(order.brokerage_commission for order in orders_within_trade[symbol])
                trade_asset = orders_within_trade[symbol][0].asset_class
                trade_enter_date = min(order.date_time for order in orders_within_trade[symbol])
                trade_exit_date = max(order.date_time for order in orders_within_trade[symbol])

                trades.append({
                    "Symbol": symbol,
                    "Asset class": trade_asset,
                    "Long/Short": long_short,
                    "Win/Loss": win_loss,
                    "Number of Orders": len(orders_within_trade[symbol]),
                    "Quantity": quantity_sum[symbol],
                    "Trade Shares/Contracts Quantity": trade_shares_quantity,
                    "Trade Result": trade_result,
                    "Trade Amount": trade_amount,
                    "Trade Result Percentage": trade_result_percentage,
                    "Trade Fee": trade_fee,
                    "Enter Date": trade_enter_date,
                    "Exit Date": trade_exit_date,
                    #"Holding time": time_difference_simplifier(trade_enter_date, trade_exit_date),
                    "Orders": orders_within_trade[symbol],
                })
                # Reset for the next group
                orders_within_trade[symbol] = []

        return trades
"""