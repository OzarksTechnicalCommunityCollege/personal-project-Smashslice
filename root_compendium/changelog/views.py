from django.shortcuts import get_object_or_404, render
from .models import Update, ChangeRequest
from django.http import Http404
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from .forms import ChangeRequestForm




# Render post list
def update_list(request):
    update_list = Update.published.all()
    
    paginator = Paginator(update_list, 5)
    page_number = request.GET.get('page',1)
    updates = paginator.page(page_number)
    
    form = ChangeRequestForm()
    
    requested = ChangeRequest.requested_requests.all()
    
    return render(
        request,
        'changelog/post/list.html',
        {'updates': updates, 'form': form, 'requested': requested}
    )

# class UpdateListView(ListView):
#     queryset = Update.published.all()
#     context_object_name = 'posts'
#     paginate_by = 5
#     template_name = 'changelog/post/list.html'
    
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
    
    
    
@require_POST
def post_change_request(request):
    change_request = None
    form = ChangeRequestForm(data=request.POST)
    
    if form.is_valid():
        change_request = form.save()
    
    return render(
        request,
        'changelog/post/change_request.html',
        {
            'form': form,
            'change_request': change_request
        }
    )
    
    