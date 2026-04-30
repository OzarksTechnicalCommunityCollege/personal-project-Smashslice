from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.core.cache import cache
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from changelog.models import ChangeRequestNotification



# Auth Views


def user_login(request):
    """
    Handle user login via POST or display login form via GET.

    Inputs:
        - request.method: 'POST' or 'GET'
        - request.POST: login form data (if POST)

    Outputs:
        - On valid login: returns HttpResponse with success message
        - On invalid login: returns HttpResponse with error message
        - On GET: renders 'users/login.html' with LoginForm

    Error Handling:
        - Returns error messages for invalid or disabled accounts.
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password']
            )
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponse('Authenticated Succesfully')
            else: 
                return HttpResponse('Disabled Account')
        else: 
            return HttpResponse('Invalid Login')
    else:
        form = LoginForm() 
    return render(request, 'users/login.html', {'form': form})


def register(request):
    """
    Handle user registration via POST or display registration form via GET.

    Inputs:
        - request.method: 'POST' or 'GET'
        - request.POST: registration form data (if POST)

    Outputs:
        - On successful registration: renders 'users/register_done.html' with new_user
        - On GET or invalid form: renders 'users/register.html' with UserRegistrationForm
    """
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(
                request,
                'users/register_done.html',
                {'new_user': new_user}
            )
    else:
        user_form = UserRegistrationForm()
    return render(
        request,
        'users/register.html',
        {'user_form': user_form}
    )


@login_required
def dashboard(request):
    """
    Display the user dashboard with recent change request notifications.

    Inputs:
        - request.user: current authenticated user

    Outputs:
        - Renders 'users/dashboard.html' with:
            - section: 'dashboard'
            - notifications: up to 10 recent ChangeRequestNotification objects

    Error Handling:
        - Uses cache to optimize notification queries.
    """
    cache_key = f'user:{request.user.id}:dashboard_notifications'
    notifications = cache.get(cache_key)
    if notifications is None:
        notifications = list(
            ChangeRequestNotification.objects
            .filter(user=request.user)
            .select_related('change_request', 'related_update')[:10]
        )
        cache.set(cache_key, notifications, 60)
    return render(
        request,
        'users/dashboard.html',
        {
            'section': 'dashboard',
            'notifications': notifications,
        }
    )
    
@login_required
def edit(request):
    if request.method =='POST':
        user_form = UserEditForm(
            instance=request.user,
            data=request.POST
        )
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(
        request,
        'users/edit.html',
        {
            'user_form': user_form,
            'profile_form': profile_form
        }
    )
    
def login_modal(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password']
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return JsonResponse({'success': True, 'redirect': '/'})
                else:
                    form.add_error(None, 'This account is disabled.')
            else:
                form.add_error(None, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'partials/_p_login.html', {'form': form})

def logged_out_modal(request):
    return render(request, 'partials/_p_logged_out.html')

def register_modal(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(
                request,
                'partials/_p_register_done.html',
                {'new_user': new_user}
            )
    else:
        user_form = UserRegistrationForm()
    return render(request, 'partials/_p_register.html', {'user_form': user_form})