from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.urlresolvers import reverse_lazy, reverse
from django.conf import settings
from geosnapr.models import Profile, Image
from instagram import client
import json

# Config for the base api calls
instagram_config = {
    'client_id': settings.INSTAGRAM_APP_ID,
    'client_secret': settings.INSTAGRAM_APP_SECRET,
    'redirect_uri': reverse_lazy('instagram_callback'),
}

# API request object
unauthenticated_api = client.InstagramAPI(**instagram_config)

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
        return redirect(index)

    return redirect(index)

def register(request):
    if request.method != 'POST':
        return render(request, 'register.html')
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
        return render(request, 'index.html', context)

    # Create the new profile
    profile,errors = Profile.create(username=username, email=email,
        password=password, first_name=first_name, last_name=last_name)

    if errors:
        errs.extend(errors)
        print(errors)
        return render(request, 'index.html', context)

    # Login the new user
    user = authenticate(username=username, password=password)
    login(request,user)

    return redirect(index)

@login_required
def main_map(request):
    # Auth url link for instagram
    insta_auth_url = ('https://api.instagram.com/oauth/authorize/' +
        '?client_id=' + settings.INSTAGRAM_APP_ID +
        '&redirect_uri=' + request.build_absolute_uri(reverse(instagram_callback)) +
        '&response_type=code')
    context = {
        'user': request.user,
        'insta_auth_url': insta_auth_url
    }

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
    updated_password = True

    if not password and not confirm_password:
        password = request.user.password
        confirm_password = request.user.password
        updated_password = False

    if password != confirm_password:
        errs.append('Passwords do not match!')
        return JsonResponse(context)

    profile,errors = Profile.update(username=username, email=email,
        password=password, first_name=first_name, last_name=last_name)

    if updated_password:
        update_session_auth_hash(request, profile.user)

    if errors:
        errs.extend(errors)
        print(errors)
        return JsonResponse(context)

    context['msg'] = 'Profile successfully updated'
    return JsonResponse(context)

@login_required
def upload(request):
    if request.method != 'POST':
        return redirect(main_map)
    context = {}
    errs = []
    context['errors'] = errs

    pic = request.FILES.get('pic')
    lat = request.POST.get('lat')
    lng = request.POST.get('lng')
    caption = request.POST.get('caption')
    user = request.user

    image,errors = Image.create(username=user.username, image=pic, lat=lat, lng=lng, caption=caption)
    context['image'] = image

    if errors:
        print(errors)
        errs.extend(errors)
    else:
        context['message'] = "Image successfully uploaded!"

    return render(request, 'json/upload_response.json', context, content_type="application/json")

def get_images(request):
    if request.method == "POST":
        user = request.user
        images = Image.objects.filter(user=user)
        response = []
        context = {
            'images': images
        }
        return render(request, 'json/images.json', context, content_type="application/json")
    return JsonResponse({})

# Instagram oauth views

def instagram_callback(request):
    code = request.GET.get(code)
    if not code:
        print(request.GET)
    try:
        access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
        # Is this an authenticated user, or anonymous?
        user = request.user
        if user.is_authenticated():
            # Add the access key to their account
            user.profile.insta_access_key = access_token
            user.profile.save()

            # Return to the map
            return redirect(main_map)
        else:
            # Return the user information to assist with account creation
            print(user_info)
            return redirect(index)
    except Exception as e:
        print(e)