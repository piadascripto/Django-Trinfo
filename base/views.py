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


# Home


def home(request):
    order = Order.objects.all()
    brokerage = Brokerage.objects.all()
    context = {
        'order': order,       # renamed from 'order' to 'orders' for clarity
        'brokerage': brokerage   # renamed from 'brokerage' to 'brokerages' for clarity
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
            return redirect('home')
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
			messages.error(request, 'Error during registration. Try again.')
	context = {'form': form}
	return render(request, 'base/signup.html', context)


# For authenticated users
def user(request, pk):
	user = User.objects.get(id=pk)

	if request.user != user: # check if this works out
		return HttpResponse ('You can only edit your account')

	context = {'user': user}
	return render(request, 'base/user.html', context)


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
			form.save()
			return redirect('home')
	context = {'form': form}
	return render(request, 'base/brokerage_form.html', context)


@login_required(login_url="signin")
def updateBrokerage(request, pk):
	brokerage = Brokerage.objects.get(id=pk)
	form = BrokerageForm(instance = brokerage)

	if request.user != user.brokerage:
		return HttpResponse ('You can only edit your connected brokerages')

	if request.method == 'POST':
		form = BrokerageForm(request.POST, instance=brokerage)
		if form.is_valid():
			form.save()
			return redirect('home')
	context = {'form': form}
	return render(request, 'base/brokerage_form.html', context)


@login_required(login_url="signin")
def deleteBrokerage(request, pk):
	brokerage = Brokerage.objects.get(id=pk)

	if request.user != user.brokerage:
		return HttpResponse ('You can only delete your connected brokerages')

	if request.method == 'POST':
		brokerage.delete()
		return redirect('home')
	context = {'obj': brokerage}
	return render(request, 'base/delete.html', context)



