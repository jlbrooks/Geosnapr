from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.conf import settings
from geosnapr.models import Profile, Album
from .instagram_views import instagram_callback

def index(request):
    if not request.user.is_authenticated():
        return render(request, 'index.html')
    else:
        return main_map(request)

def logout_view(request):
    logout(request)

    return redirect(index)

def login_view(request):
    if request.method != 'POST':
        return redirect(index)

    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request,user)
    else:
        return render(request, 'index.html', {'error':'error'})

    return redirect(index)

def register(request):
    if request.method != 'POST':
        return redirect(index)
    context = {}
    errs = []
    context['errors'] = errs

    username = request.POST.get('username')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')

    if password != confirm_password:
        errs.append('Passwords do not match!')
        return JsonResponse(context)

    # Create the new profile
    profile,errors = Profile.create(username=username, email=email,
        password=password, first_name=first_name, last_name=last_name)

    if errors:
        errs.extend(errors)
        return JsonResponse(context)

    # Login the new user
    user = authenticate(username=username, password=password)
    login(request,user)

    return JsonResponse(context)

@login_required
def main_map(request):
    # Auth url link for instagram
    insta_auth_url = ('https://api.instagram.com/oauth/authorize/' +
        '?client_id=' + settings.INSTAGRAM_APP_ID +
        '&redirect_uri=' + request.build_absolute_uri(reverse(instagram_callback)) +
        '&response_type=code')
    context = {
        'user': request.user,
        'insta_auth_url': insta_auth_url,
        'insta_account_url': 'https://instagram.com/accounts/manage_access/',
        'albums': Album.objects.filter(user=request.user),
        'api_key': request.user.profile.get_or_create_api_key(),
        'error': request.session.get('error')
    }
    # Clear the error
    request.session['error'] = ''

    return render(request, 'map.html', context)

@login_required
def edit_profile(request):
    if request.method != 'POST':
        return redirect(main_map)

    context = {}
    errs = []
    context['errors'] = errs

    username = request.user.username
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    password = request.POST.get('password')
    confirm_password = request.POST.get('confirm_password')

    if password != confirm_password:
        errs.append('Passwords do not match!')
        return JsonResponse(context)

    profile,errors = Profile.update(username=username, email=email,
        password=password, first_name=first_name, last_name=last_name)

    if errors:
        errs.extend(errors)
        print(errors)
        return JsonResponse(context)
    else:
        update_session_auth_hash(request, profile.user)

    context['msg'] = 'Profile successfully updated'
    return JsonResponse(context)

@login_required
def delete_profile(request):
    # Delete the current user
    request.user.delete()
    # Redirect to front page
    return redirect(index)

def handler404(request):
    return render('404.html', {})

def handler500(request):
    return render('500.html', {})
