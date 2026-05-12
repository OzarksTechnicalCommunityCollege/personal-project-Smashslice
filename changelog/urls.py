from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from .api import UpdateViewSet, ChangeRequestViewSet

app_name = 'changelog'

router = DefaultRouter()
router.register(r'api/updates', UpdateViewSet, basename='update')
router.register(r'api/change-requests', ChangeRequestViewSet, basename='changerequest')

urlpatterns = [
    # update views for list and detail
    path('', views.update_list, name='update_list'),
    path(
        'requests/<int:request_number>/',
        views.change_request_detail,
        name='change_request_detail'
    ),
    path(
        '<int:major_version>.<int:current_patch><str:bug_fix>', views.update_detail, 
        name='update_detail'
    ),
    path('submit_change_request', views.post_change_request, name='change_request_form'),
    path(
        'change-requests/<int:request_number>/status/',
        views.update_change_request_status,
        name='change_request_update_status',
    ),
    path('commits/', views.github_commit_list, name='github_commit_list'),
]

# Add DRF API routes
urlpatterns += router.urls