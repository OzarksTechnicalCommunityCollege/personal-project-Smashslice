from django.shortcuts import get_object_or_404, render
from .models import Update
from django.http import Http404
# Create your views here.

# Render post list
def update_list(request):
    updates = Update.published.all()
    
    return render(
        request,
        'changelog/post/list.html',
        {'updates': updates}
    )
    
# Render indivdual post details
def update_detail(request, major_version, current_patch, bug_fix):
    update = get_object_or_404(
        Update,
        major_version=major_version,
        current_patch=current_patch,
        bug_fix=bug_fix,
        status=Update.Status.PUBLISHED
    )
    return render(
        request,
        'changelog/post/detail.html',
        {'update': update}
    )