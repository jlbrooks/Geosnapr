from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from geosnapr.models import Image, Album
from urllib.request import urlopen
from urllib.error import URLError
from .main import index, main_map

@login_required
def upload(request):
    if request.method != 'POST':
        return redirect(main_map)
    context = {}
    errs = []
    context['errors'] = errs

    # Get either external or file pic
    if request.POST.get('external'):
        url = request.POST.get('url')
        img_temp = NamedTemporaryFile()
        try:
            img_temp.write(urlopen(url).read())
            img_temp.flush()
            pic = File(img_temp)
        except URLError as e:
            # Error reading file
            pic = None
    else:
        pic = request.FILES.get('pic')

    # Get lat/lng/caption data
    lat = request.POST.get('lat')
    lng = request.POST.get('lng')
    caption = request.POST.get('caption', '')
    user = request.user
    albums_str = request.POST.get('upload-album')
    # Parse albums string into array of ints
    try:
        albums = [int(s) for s in albums_str.split(',')]
    except:
        albums = []

    # Try to create the image
    image,errors = Image.create(username=user.username,
        image=pic, lat=lat, lng=lng, caption=caption, albums=albums)
    context['image'] = image

    if errors:
        print(errors)
        errs.extend(errors)
    else:
        context['message'] = "Image successfully uploaded!"

    return render(request, 'json/upload_response.json', context, content_type="application/json")

@login_required
def edit_image(request):
    if request.method != 'POST':
        return redirect(main_map)
    context = {}
    errs = []
    context['errors'] = errs

    # Get lat/lng/caption data
    lat = request.POST.get('lat')
    lng = request.POST.get('lng')
    caption = request.POST.get('caption')
    im_id = request.POST.get('img_id')
    albums_str = request.POST.get('edit-album')
    # Parse albums string into array of ints
    try:
        albums = [int(s) for s in albums_str.split(',')]
    except:
        albums = []
    username = request.user.username

    image,errors = Image.update(im_id=im_id,
        username=username, lat=lat, lng=lng, caption=caption, albums=albums)
    context['image'] = image

    if errors:
        print(errors)
        errs.extend(errors)
    else:
        context['message'] = "Image successfully updated!"

    return render(request, 'json/upload_response.json', context, content_type="application/json")

@login_required
def delete_image(request):
    if request.method != "POST":
        return redirect(index)
    im_id = request.POST.get('img_id')
    print(im_id)
    try:
        image = Image.objects.get(id=im_id)
    except Exception as e:
        print(e)
        raise Http404("Image not found for deletion")

    # Is this image associated with the current user?
    if image.user != request.user:
        # Consider changing to 403...
        raise Http404()

    # Delete the image
    image.delete()

    return redirect(index)

@login_required
def create_album(request):
    if request.method != 'POST':
        return redirect(main_map)
    context = {}
    errs = []
    context['errors'] = errs

    # Get new album name
    name = request.POST.get('album_name')

    # Try to create the album
    album, errors = Album.create(request.user.username, name)
    context['album'] = album

    if errors:
        print(errors)
        errs.extend(errors)
    else:
        context['message'] = "Album successfully created!"

    return render(request, 'json/create_album_response.json', context, content_type="application/json")

@login_required
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

@login_required
def get_album(request):
    try:
        if request.POST['a_id']:
            a_id = request.POST['a_id']
            album = Album.objects.get(id=a_id)
    except:
        raise Http404()
    context = {
        'album': album,
        'public': album.public
    }
    return render(request, 'json/album.json', context, content_type="application/json")

@login_required
def get_public(request):
    try:
        images = []
        albums = Album.objects.filter(public=True)
        for album in albums:
            images.extend(album.images.all())

    except:
        raise Http404()
    context = {
        'images': images,
        'public': album.public
    }
    return render(request, 'json/album-public.json', context, content_type="application/json")
