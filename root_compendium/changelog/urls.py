from django.urls import path
from . import views

app_name = 'changelog'

urlpatterns = [
    #post views for list and detail
    path('', views.post_list, name='post_list'),
    path('<int:id>/', views.post_detail, name='post_detail'),
]