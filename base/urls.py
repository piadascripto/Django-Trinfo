from django.urls import path
from . import views
#from django.contrib.auth import views as auth_views

urlpatterns = [
	path('', views.home, name="home"),
	path('signin/', views.signin, name="signin"),
	path('signout/', views.signout, name="signout"),
	path('signup/', views.signup, name="signup"),
	#password_reset
	#password_reset_done
	#password_reset_confirm
	#password_reset_complete
	path('trade-journal/', views.tradeJournal, name="trade-journal"),
	path('order/<str:pk>/', views.order, name="order"),
	path('tag/<str:pk>/', views.tag, name="tag"),
	path('user/<str:pk>/', views.user, name="user"),
	path('brokerage/<str:pk>/', views.brokerage, name="brokerage"),
	path('add-brokerage/', views.addBrokerage, name="add-brokerage"),
	path('update-brokerage/<str:pk>/', views.updateBrokerage, name="update-brokerage"),
	path('delete-brokerage/<str:pk>/', views.deleteBrokerage, name="delete-brokerage"),

	
	
]