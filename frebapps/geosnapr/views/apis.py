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

    data = json.loads(request.body.decode('utf-8')).get('data')

    print(data)

    if not data:
        return JsonResponse(bad_format_errors(["Missing 'data' component of request"]))

    api_key = request.GET.get('api_key')
    attributes = data.get('attributes')
    lat = attributes.get('lat')
    lng = attributes.get('lng')
    caption = attributes.get('caption')
    album_ids = data.get('album_ids', [])

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
        pic = src

    image,errs = Image.create(profile.user.username, pic, lat, lng, caption, album_ids)

    if errs:
        return JsonResponse(bad_format_errors(errs))
    else:
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