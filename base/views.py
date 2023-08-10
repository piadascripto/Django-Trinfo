#Python imports
from collections import defaultdict
from datetime import datetime
from itertools import groupby
from pprint import pprint
import plotly.graph_objs as go
import plotly.offline as offline


#Django imports
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm  #, AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import DateField, F
from django.db.models.functions import Cast, TruncDate, TruncMonth, TruncWeek
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import make_aware
#from django.views import View
#Local imports
from .forms import BrokerageForm
from .management.commands.connection_interactive_brokers import connection_interactive_brokers
from .models import Brokerage, Order, Tag, Trade
from .utils import calculate_trades_stats, fetch_stocks_market_data





# Home


def home(request):
    order = Order.objects.all()
    context = {
        'order': order,  # renamed from 'order' to 'orders' for clarity
    }
    return render(request, 'base/home.html', context)


# User authentication


def signin(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            redirect('profile', username=request.user.username)
        else:
            messages.error(request, 'Username or password is wrong')
    context = {}
    return render(request, 'base/signin.html', context)


def signout(request):
    logout(request)
    return redirect('home')


def signup(request):

    if request.user.is_authenticated:
        return redirect('home')

    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    context = {'form': form}
    return render(request, 'base/signup.html', context)


# For authenticated users


def profile(request, username):
    user = User.objects.get(username=username)
    order = Order.objects.filter(user=user)
    brokerage = Brokerage.objects.filter(user=user)

    # Handle the POST request when the "Fetch trades" button is clicked
    if request.method == "POST" and "run_brokerage_connection" in request.POST:
        brokerage_id = request.POST.get("brokerage_id")
        selected_brokerage = Brokerage.objects.get(id=brokerage_id, user=user)
        if selected_brokerage.name == "interactive_brokers":
            connection_interactive_brokers(user.id, 
										   selected_brokerage.id,
                                           selected_brokerage.login,
                                           selected_brokerage.key)
            messages.success(
                request,
                f'Connection successfully executed for brokerage {selected_brokerage.name} - {selected_brokerage.alias}.'
            )
            selected_brokerage.updated = make_aware(datetime.now())
            selected_brokerage.save()
        else:
            messages.error(
                request,
                f'Connection not executed correctly for  {selected_brokerage.get_name_display()} - {selected_brokerage.alias}.'
            )
        #elif selected_brokerage.name == "another_brokerage":
        #connection_another_brokerage(user.id, selected_brokerage.login, selected_brokerage.key)

    context = {'user': user, 'order': order, 'brokerage': brokerage}
    return render(request, 'base/profile.html', context)


@login_required(login_url="signin")
def tradeJournal(request):

    return render(request, 'base/trade_journal.html')


@login_required(login_url="signin")
def order(request, pk):
    order = Order.objects.get(id=pk)
    context = {'order': order}
    return render(request, 'base/order.html', context)


@login_required(login_url="signin")
def tag(request, pk):
    tag = Tag.objects.get(id=pk)
    context = {'tag': tag}
    return render(request, 'base/tag.html', context)


@login_required(login_url="signin")
def brokerage(request, pk):
    brokerage = Brokerage.objects.get(id=pk)

    context = {'brokerage': brokerage}
    return render(request, 'base/brokerage.html', context)


@login_required(login_url="signin")
def addBrokerage(request):
    form = BrokerageForm()
    if request.method == 'POST':
        form = BrokerageForm(request.POST)
        if form.is_valid():
            brokerage = form.save(commit=False)
            brokerage.user = request.user
            brokerage.save()
            return redirect('profile', username=request.user.username)
    context = {'form': form}
    return render(request, 'base/brokerage_form.html', context)


@login_required(login_url="signin")
def updateBrokerage(request, pk):
    brokerage = Brokerage.objects.get(id=pk)
    form = BrokerageForm(instance=brokerage)

    if request.user != brokerage.user:
        return HttpResponse('You can only edit your connected brokerages')

    if request.method == 'POST':
        form = BrokerageForm(request.POST, instance=brokerage)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    context = {'form': form}
    return render(request, 'base/brokerage_form.html', context)


@login_required(login_url="signin")
def deleteBrokerage(request, pk):
    brokerage = Brokerage.objects.get(id=pk)

    if request.user != brokerage.user:
        return HttpResponse('You can only delete your connected brokerages')

    if request.method == 'POST':
        brokerage.delete()
        return redirect('profile', username=request.user.username)
    context = {'obj': brokerage}
    return render(request, 'base/delete.html', context)

# Trades, order, journal, statistics 







def trades_by_timeframe(request, timeframe="day"):
    
    if timeframe == "all":
        trades = Trade.objects.all().order_by('-date_close')
        stats = calculate_trades_stats(trades, None)  # Assuming your function can handle None as the second argument
        grouped_trades_with_stats = [{'date': None, 'trades': list(trades), 'stats': stats}]
    else:
        if timeframe == "day":
            trades = Trade.objects.all().annotate(date_close_truncate=TruncDate('date_close'))
        elif timeframe == "week":
            trades = Trade.objects.all().annotate(date_close_truncate=TruncWeek('date_close'))
        elif timeframe == "month":
            trades = Trade.objects.all().annotate(date_close_truncate=TruncMonth('date_close'))
        else:
            trades = Trade.objects.all().annotate(date_close_truncate=TruncDate('date_close'))
        
        trades = trades.order_by('-date_close_truncate')
        stats_dict = calculate_trades_stats(trades, 'date_close_truncate')
        grouped_trades_with_stats = [{'date': key, 'trades': list(group), 'stats': stats_dict[key]} for key, group in groupby(trades, key=lambda x: x.date_close_truncate)]

    context = {
		'grouped_trades_with_stats': grouped_trades_with_stats,
		'timeframe': timeframe}

    # Use a single template or decide the template based on the timeframe.
    return render(request, 'base/trades.html', context)






def trade(request, trade_id):
    # Your existing code to get trade details
    trade_detail = get_object_or_404(Trade, id=trade_id)
    symbol = trade_detail.symbol
    initial_date = trade_detail.date_open
    end_date = trade_detail.date_close
    time_zone = "UTC"  # TECHNICAL DEBT #trade_detail.orders.first().time_zone  # Get the timezone of the first order

    # Sample bars_data and order_data for demonstration

    try:
        bars_data = fetch_stocks_market_data(symbol, initial_date, end_date, time_zone)
        # DEBUGGING
        #print("========================")
        # print(bars_data)

    except Exception as e:
        print("========================")
        print("Error fetching stock data:", str(e))
    
    order_data = trade_detail.orders.all().values('date_time', 'order_price', 'open_close')

    # Create figure
    fig = go.Figure(data=[go.Candlestick(
        x=[item['t'] for item in bars_data],
        open=[item['o'] for item in bars_data],
        high=[item['h'] for item in bars_data],
        low=[item['l'] for item in bars_data],
        close=[item['c'] for item in bars_data],
    )])
    """
    # Plot orders on the chart
    open_orders = [order for order in order_data if order['open_close'] == 'open']
    close_orders = [order for order in order_data if order['open_close'] == 'close']

    fig.add_trace(go.Scatter(
        x=[order['date_time'] for order in open_orders],
        y=[order['order_price'] for order in open_orders],
        mode='markers',
        marker=dict(color='green', size=8),
        name='Open Orders'
    ))

    # Commented out section starts here
    fig.add_trace(go.Scatter(
         x=[order['date_time'] for order in close_orders],
         y=[order['order_price'] for order in close_orders],
         mode='markers',
         marker=dict(color='red', size=8),
         name='Close Orders'
     ))

    fig.update_layout(
        title=f'{symbol} Stock Price',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False
	)
    """
    # DEBUGGING
    #print("========================")
    #print(trade_detail, bars_data, order_data)
    
    fig.show()

    plot_div = offline.plot(fig, output_type='div', show_link=False)
    
    context = {
        'trade': trade_detail,
        'plot_div': plot_div,
        # ... any other context data
    }

    return render(request, 'base/trade.html', context)
