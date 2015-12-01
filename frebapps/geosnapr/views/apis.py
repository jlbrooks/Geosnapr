from geosnapr.models import Image, Profile, Album
from django.http import JsonResponse
from django.shortcuts import render
from django.core.files.temp import NamedTemporaryFile
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from urllib.request import urlopen
import json

# Error response for wrong method type
wrong_method_error = {
    'errors': [{
        'status': '405',
        'detail': 'Method not allowed'
    }]
}

bad_api_key_error = {
    'errors': [{
        'status': '403',
        'detail': 'The API key given is incorrect'
    }]
}

def bad_format_errors(errs):
    errors = []
    for msg in errs:
        struct = {
            'status': '400',
            'detail': msg
        }
        errors.append(struct)
    context = {
        'errors': errors
    }

    return context

def not_found_error(msg):
    context = {
        'errors': [{
            'status': '404',
            'detail': msg
        }]
    }

    return context

# View functions

def swagger(request):
    context = {'api_key': ''}
    if request.user.is_authenticated():
        context['api_key'] = request.user.profile.api_key

    return render(request, 'swagger.html', context)

@csrf_exempt
def api_upload(request):
    if request.method != "POST":
        return JsonResponse(wrong_method_error)

    try:
        data = json.loads(request.body.decode('utf-8')).get('data')
    except:
        return JsonResponse(bad_format_errors(["Could not parse JSON body"]))

    if not data:
        return JsonResponse(bad_format_errors(["Missing 'data' component of request"]))

    api_key = request.GET.get('api_key')
    attributes = data.get('attributes')
    try:
        lat = attributes.get('lat')
        lng = attributes.get('lng')
        caption = attributes.get('caption')
        album_ids = data.get('album_ids', [])
    except:
        return JsonResponse(bad_format_errors(["Missing 'attributes' component of request data"]))

    src = attributes.get('src')
    src_type = data.get('src_type')

    # Does this api key exist?
    try:
        profile = Profile.objects.get(api_key=api_key)
    except:
        return JsonResponse(bad_api_key_error)

    if src_type == 'url':
        img_temp = NamedTemporaryFile()
        img_temp.write(urlopen(src).read())
        img_temp.flush()
        pic = File(img_temp)
    else:
        return JsonResponse(bad_format_errors(["Invalid src_type parameter"]))

    image,errs = Image.create(profile.user.username, pic, lat, lng, caption, album_ids)

    if errs:
        return JsonResponse(bad_format_errors(errs))

    # Create response object
    context = {
        'data': image.as_dict(True,True)
    }
    return JsonResponse(context, status=201)

@csrf_exempt
def get_image(request, image_id):
    # Retrieve API key from the GET URL
    api_key = request.GET.get('api_key')

    # Do we have a user with this api key?
    try:
        profile = Profile.objects.get(api_key=api_key)
    except:
        return JsonResponse(bad_api_key_error)

    # Try to get image with this id
    try:
        image = Image.objects.get(id=image_id)
    except:
        return JsonResponse(not_found_error("Image not found"))

    # If incorrect user, return not found
    if image.user != profile.user:
        return JsonResponse(not_found_error("Image not found"))

    # Return the image data
    context = {
        'data': image.as_dict(True,True)
    }
    return JsonResponse(context)

@csrf_exempt
def route_album_method(request):
    if request.method == 'GET':
        return get_albums(request)
    elif request.method == 'POST':
        return post_album(request)

@csrf_exempt
def get_albums(request):
    # Retrieve API key from the GET URL
    api_key = request.GET.get('api_key')

    # Do we have a user with this api key?
    try:
        profile = Profile.objects.get(api_key=api_key)
    except Exception as e:
        print(e)
        return JsonResponse(bad_api_key_error)

    # Retrieve all albums for this user
    albums = Album.objects.filter(user=profile.user)

    # Create the response object

    album_dicts = [album.as_dict(True,False) for album in albums]

    data = {
        'data': album_dicts
    }

    return JsonResponse(data)

@csrf_exempt
def get_album(request, album_id):
    # Retrieve API key from the GET URL
    api_key = request.GET.get('api_key')

    # Do we have a user with this api key?
    try:
        profile = Profile.objects.get(api_key=api_key)
    except:
        return JsonResponse(bad_api_key_error)

    # Try to get album with this id
    try:
        album = Album.objects.get(id=album_id)
    except:
        return JsonResponse(not_found_error("Album not found"))

    # If incorrect user, return not found
    if album.user != profile.user:
        return JsonResponse(not_found_error("Album not found"))

    # Return the album data
    context = {
        'data': album.as_dict(True,True)
    }
    return JsonResponse(context)

@csrf_exempt
def post_album(request):
    # Retrieve API key from the GET URL
    api_key = request.GET.get('api_key')

    # Do we have a user with this api key?
    try:
        profile = Profile.objects.get(api_key=api_key)
    except Exception as e:
        return JsonResponse(bad_api_key_error)

    # Try to get the data
    try:
        data = json.loads(request.body.decode('utf-8')).get('data')
    except:
        return JsonResponse(bad_format_errors(["Could not parse JSON body"]))

    if not data:
        return JsonResponse(bad_format_errors(["Missing 'data' component of request"]))

    # Retrieve the name
    attributes = data.get('attributes')
    try:
        name = attributes.get('name')
    except:
        return JsonResponse(bad_format_errors(["Missing 'attributes' component of request data"]))

    # Try to create the album
    album,errs = Album.create(profile.user.username, name)

    if errs:
        return JsonResponse(bad_format_errors(errs))

    # Create response object
    context = {
        'data': album.as_dict(True,True)
    }
    return JsonResponse(context, status=201)