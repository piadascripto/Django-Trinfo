from django.shortcuts import render, redirect
from django import forms
from django.http import HttpResponse
from .models import Order, Tag, Brokerage
from .forms import BrokerageForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm #, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .management.commands.connection_interactive_brokers import connection_interactive_brokers
from datetime import datetime
from django.utils.timezone import make_aware

# Home


def home(request):
    order = Order.objects.all()
    context = {
        'order': order,       # renamed from 'order' to 'orders' for clarity
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

        # Check the name of the brokerage and call the appropriate function
        if selected_brokerage.name == "interactive_brokers":
            connection_interactive_brokers(user.id, selected_brokerage.login, selected_brokerage.key)
            messages.success(request, f'Connection successfully executed for brokerage {selected_brokerage.name} - {selected_brokerage.alias}.')
            # Update the 'updated' timestamp for the brokerage instance
            selected_brokerage.updated = make_aware(datetime.now())
            selected_brokerage.save()
        else:
            messages.error(request, f'Connection not executed correctly for  {selected_brokerage.get_name_display()} - {selected_brokerage.alias}.')
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
	form = BrokerageForm(instance = brokerage)

	if request.user != brokerage.user:
		return HttpResponse ('You can only edit your connected brokerages')

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
		return HttpResponse ('You can only delete your connected brokerages')

	if request.method == 'POST':
		brokerage.delete()
		return redirect('profile', username=request.user.username)
	context = {'obj': brokerage}
	return render(request, 'base/delete.html', context)



