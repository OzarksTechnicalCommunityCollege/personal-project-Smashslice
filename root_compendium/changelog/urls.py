from django.urls import path
from . import views

app_name = 'changelog'

urlpatterns = [
    #update views for list and detail
    path('', views.update_list, name='update_list'),
    path('<int:id>/', views.update_detail, name='update_detail'),
]