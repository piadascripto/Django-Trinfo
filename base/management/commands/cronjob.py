from base.models import Order, Brokerage, Trade
from django.contrib.auth.models import User

Order.generate_trades_from_unprocessed_orders()