from django.urls import path
from . import views


#from django.contrib.auth import views as auth_views

urlpatterns = [
	path('', views.home, name="home"),
	path('signin/', views.signin, name="signin"),
	path('signout/', views.signout, name="signout"),
	path('signup/', views.signup, name="signup"),
	path('profile/<str:username>/', views.profile, name="profile"),
	#password_reset
	#password_reset_done
	#password_reset_confirm
	#password_reset_complete
    path('trades/', views.trades, name='trades'),
	path('trades_by_month/', views.trades_by_month, name='trades_by_month'),
	path('trades_by_week/', views.trades_by_week, name='trades_by_week'),
    path('trades/<int:trade_id>/', views.trade, name='trade'),
	
	path('trade-journal/', views.tradeJournal, name="trade-journal"),
	path('order/<str:pk>/', views.order, name="order"),
	path('tag/<str:pk>/', views.tag, name="tag"),
	
	path('brokerage/<str:pk>/', views.brokerage, name="brokerage"),
	path('add-brokerage/', views.addBrokerage, name="add-brokerage"),
	path('update-brokerage/<str:pk>/', views.updateBrokerage, name="update-brokerage"),
	path('delete-brokerage/<str:pk>/', views.deleteBrokerage, name="delete-brokerage"),

	
	
]
