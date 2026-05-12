from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .models import Update, ChangeRequest, GitHubCommit
from django.http import Http404
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .forms import ChangeRequestForm
from .session_tracker import ChangeRequestTracker
# Post Views


# Render post list
def update_list(request):
    """
    Display a paginated list of published updates and change requests.

    Inputs:
        - request.GET['page']: (optional) page number for pagination
        - request.GET['show_pending']: (optional) show pending requests
        - request.GET['show_denied']: (optional) show denied requests

    Outputs:
        - Renders 'changelog/post/list.html' with:
            - updates: paginated Update objects
            - form: ChangeRequestForm instance
            - requested: filtered ChangeRequest queryset
            - show_pending, show_denied: filter flags
            - viewed_count, viewed_is_high: session stats

    Error Handling:
        - Defaults to first page if page param is invalid.
    """
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
    tracker = ChangeRequestTracker(request)
    for change_request in requested:
        change_request.session_seen = change_request.request_number in tracker
        change_request.session_status_changed = tracker.status_changed(change_request)
        state = tracker.get_state(change_request.request_number)
        change_request.session_last_status = state.get('last_status')

    viewed_count = len(tracker)
    viewed_is_high = tracker > 3
    
    return render(
        request,
        'changelog/post/list.html',
        {
            'updates': updates,
            'form': form,
            'requested': requested,
            'show_pending': show_pending,
            'show_denied': show_denied,
            'viewed_count': viewed_count,
            'viewed_is_high': viewed_is_high,
        }
    )

    
# Render indivdual post details
def update_detail(request, major_version, current_patch, bug_fix):
    """
    Display details for a single published update.

    Inputs:
        - major_version, current_patch, bug_fix: version identifiers (URL params)

    Outputs:
        - Renders 'changelog/post/detail.html' with:
            - update: Update object

    Error Handling:
        - Raises 404 if update not found or not published.
    """
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


def change_request_detail(request, request_number):
    """
    Display details for a single change request, including session-based view state.

    Inputs:
        - request_number: primary key of the ChangeRequest (URL param)

    Outputs:
        - Renders 'changelog/post/change_request_detail.html' with:
            - change_request: ChangeRequest object
            - previous_status: last status seen in session
            - previous_status_label: label for last status
            - previously_seen: whether this request was seen in session
            - status_changed: whether status changed since last view

    Error Handling:
        - Raises 404 if change request not found.
    """
    change_request = get_object_or_404(
        ChangeRequest,
        request_number=request_number
    )
    tracker = ChangeRequestTracker(request)
    try:
        state = tracker[change_request.request_number]
    except KeyError:
        state = {}

    previous_status = state.get('last_status')
    previously_seen = bool(state)
    status_changed = bool(previous_status and previous_status != change_request.status)
    previous_status_label = None
    if previous_status:
        try:
            previous_status_label = ChangeRequest.Status(previous_status).label
        except ValueError:
            previous_status_label = previous_status

    tracker.view(change_request)

    return render(
        request,
        'changelog/post/change_request_detail.html',
        {
            'change_request': change_request,
            'previous_status': previous_status,
            'previous_status_label': previous_status_label,
            'previously_seen': previously_seen,
            'status_changed': status_changed,
        }
    )
    
    
    
@require_POST
def post_change_request(request):
    """
    Handle submission of a new change request via POST.

    Inputs:
        - request.POST: form data for ChangeRequestForm

    Outputs:
        - Renders 'changelog/post/change_request.html' with:
            - form: ChangeRequestForm instance (bound)
            - change_request: newly created ChangeRequest or None if invalid

    Error Handling:
        - If form is invalid, re-renders form with errors.
    """
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
    """
    Staff-only view to update the status of a change request.

    Inputs:
        - request.POST['status']: new status value
        - request.user: must be staff
        - request_number: primary key of ChangeRequest (URL param)

    Outputs:
        - Redirects to changelog:update_list after update

    Error Handling:
        - Raises 404 if not staff, invalid status, or change request not found.
    """
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

def github_commit_list(request):
    """
    Display the 50 most recent synced GitHub commits.

    Inputs:
        - None (GET only)

    Outputs:
        - Renders 'changelog/commits.html' with:
            - commits: list of GitHubCommit objects
    """
    commits = GitHubCommit.objects.order_by('-date')[:50]
    return render(request, 'changelog/commits.html', {'commits': commits})

# Search updates by title, body, or tag label
def update_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = (
            Update.published.filter(
                Q(title__icontains=query) |
                Q(body__icontains=query) |
                Q(tags__label__icontains=query)
            )
            .distinct()
        )
    return render(request, 'changelog/post/search_results.html', {'results': results, 'query': query})