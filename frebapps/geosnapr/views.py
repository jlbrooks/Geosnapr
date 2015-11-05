from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from geosnapr.models import Profile, Image

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
    return render(request, 'map.html')

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

    if errors:
        print(errors)
        errs.extend(errors)
    else:
        context['message'] = "Image successfully uploaded!"

    return redirect(index)


