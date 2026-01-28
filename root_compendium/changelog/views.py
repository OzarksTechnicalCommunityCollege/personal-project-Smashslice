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
def update_detail(request, id):
    update = get_object_or_404(
        Update,
        id=id,
        status=Update.Status.PUBLISHED
    )
    return render(
        request,
        'changelog/post/detail.html',
        {'update': update}
    )