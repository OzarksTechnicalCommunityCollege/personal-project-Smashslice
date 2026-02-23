from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    # path('', include('django.contrib.auth.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit')
]