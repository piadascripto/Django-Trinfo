from django.urls import path
from . import views
from .views import trades_by_timeframe


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
    path('trades/', trades_by_timeframe, name='trades'),
	path('trades/<str:timeframe>/', trades_by_timeframe, name='trades_by_timeframe'),
    path('trade/<int:trade_id>/', views.trade, name='trade'),
	
	path('order/<str:pk>/', views.order, name="order"),
	path('tag/<str:pk>/', views.tag, name="tag"),
	
	path('brokerage/<str:pk>/', views.brokerage, name="brokerage"),
	path('add-brokerage/', views.addBrokerage, name="add-brokerage"),
	path('update-brokerage/<str:pk>/', views.updateBrokerage, name="update-brokerage"),
	path('delete-brokerage/<str:pk>/', views.deleteBrokerage, name="delete-brokerage"),

	
	
]
