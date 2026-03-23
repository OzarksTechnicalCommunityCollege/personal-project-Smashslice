from django.shortcuts import get_object_or_404, redirect, render
from .models import Update, ChangeRequest
from django.http import Http404
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .forms import ChangeRequestForm




# Post Views


# Render post list
def update_list(request):
    update_list = Update.published.all()
    
    paginator = Paginator(update_list, 5)
    page_number = request.GET.get('page',1)
    updates = paginator.page(page_number)
    
    form = ChangeRequestForm()

    statuses = [
        ChangeRequest.Status.IN_PROGRESS,
        ChangeRequest.Status.COMPLETED,
    ]

    show_pending = request.GET.get('show_pending') == '1'
    show_denied = request.GET.get('show_denied') == '1'

    if show_pending:
        statuses.append(ChangeRequest.Status.PENDING)
    if show_denied:
        statuses.append(ChangeRequest.Status.DENIED)

    requested = (
        ChangeRequest.objects
        .filter(status__in=statuses)
        .order_by('-updated')
    )
    
    return render(
        request,
        'changelog/post/list.html',
        {
            'updates': updates,
            'form': form,
            'requested': requested,
            'show_pending': show_pending,
            'show_denied': show_denied,
        }
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
    
    
    
@require_POST
def post_change_request(request):
    change_request = None
    form = ChangeRequestForm(data=request.POST)
    
    if form.is_valid():
        change_request = form.save(commit=False)
        if request.user.is_authenticated:
            change_request.requester = request.user
            if not change_request.email:
                change_request.email = request.user.email
        change_request.save()
    
    return render(
        request,
        'changelog/post/change_request.html',
        {
            'form': form,
            'change_request': change_request
        }
    )


@login_required
@require_POST
def update_change_request_status(request, request_number):
    if not request.user.is_staff:
        raise Http404

    change_request = get_object_or_404(ChangeRequest, pk=request_number)
    next_status = request.POST.get('status')

    if next_status not in ChangeRequest.Status.values:
        raise Http404

    if change_request.can_transition_to(next_status):
        change_request.apply_status(next_status)
        change_request._status_changed_by = request.user
        change_request.save()

    return redirect('changelog:update_list')