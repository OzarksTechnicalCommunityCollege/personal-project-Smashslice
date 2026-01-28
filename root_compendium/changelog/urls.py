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
    path('submit_change_request', views.post_change_request, name='change_request_form')
]