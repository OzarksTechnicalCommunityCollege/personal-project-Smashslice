from django.contrib.auth import views as auth_views
from django.urls import path
# from django.conf.urls import url
from . import views

app_name = 'changelog'

urlpatterns = [
    #update views for list and detail
    path('', views.update_list, name='update_list'),
    path(
        '<int:major_version>.<int:current_patch><str:bug_fix>', views.update_detail, 
        name='update_detail'
    ),
    path('submit_change_request', views.post_change_request, name='change_request_form'),
    # Auth URLs
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout')
]