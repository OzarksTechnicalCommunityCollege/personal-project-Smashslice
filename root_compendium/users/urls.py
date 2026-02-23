
    
from django.contrib.auth import views as auth_views
from django.urls import path
# from django.conf.urls import url
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register')
]