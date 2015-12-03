from geosnapr.models import Image, Profile, Album
from django.http import JsonResponse
from django.shortcuts import render
from django.core.files.temp import NamedTemporaryFile
from django.views.decorators.csrf import csrf_exempt
from django.core.files import File
from django.conf import settings
from urllib.request import urlopen
import json

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

# Helper functions

# Getting a resource is similar for both types of objects. Last parameter is the resource class
def get_resource(request, obj_id, Obj):
    # Retrieve API key from the GET URL
    api_key = request.GET.get('api_key')

    # Do we have a user with this api key?
    try:
        profile = Profile.objects.get(api_key=api_key)
    except:
        return JsonResponse(bad_api_key_error, status=403)

    # Try to get object with this id
    try:
        obj = Obj.objects.get(id=obj_id)
    except:
        return JsonResponse(not_found_error("Resource not found"), status=404)

    # If incorrect user, return not found
    if obj.user != profile.user:
        return JsonResponse(not_found_error("Resource not found"), status=404)

    # Return the object data
    context = {
        'data': obj.as_dict(True,True)
    }
    return JsonResponse(context)

# Helper to delete a resource.
def delete_resource(request, obj_id, Obj):
    # Retrieve API key from the GET URL
    api_key = request.GET.get('api_key')

    # Do we have a user with this api key?
    try:
        profile = Profile.objects.get(api_key=api_key)
    except:
        return JsonResponse(bad_api_key_error, status=403)

    # Try to get object with this id
    try:
        obj = Obj.objects.get(id=obj_id)
    except:
        return JsonResponse(not_found_error("Resource not found"), status=404)

    # If incorrect user, return not found
    if obj.user != profile.user:
        return JsonResponse(not_found_error("Resource not found"), status=404)

    # Delete the object
    obj.delete()
    return JsonResponse({})

# View functions

def swagger(request):
    context = {'api_key': ''}
    if request.user.is_authenticated():
        context['api_key'] = request.user.profile.api_key

    return render(request, 'swagger.html', context)

@csrf_exempt
def api_description(request):
    context = {
        "host": settings.HOSTNAME
    }
    return render(request, 'json/geosnapr.json')

@csrf_exempt
def route_image_method(request):
    if request.method == 'POST':
        return post_image(request)
    elif request.method == 'PATCH':
        return patch_image(request)

@csrf_exempt
def post_image(request):
    try:
        data = json.loads(request.body.decode('utf-8')).get('data')
    except:
        return JsonResponse(bad_format_errors(["Could not parse JSON body"]), status=400)

    if not data:
        return JsonResponse(bad_format_errors(["Missing 'data' component of request"]), status=400)

    api_key = request.GET.get('api_key')
    # Does this api key exist?
    try:
        profile = Profile.objects.get(api_key=api_key)
    except:
        return JsonResponse(bad_api_key_error, status=403)


    attributes = data.get('attributes')
    try:
        src = attributes.get('src')
        lat = attributes.get('lat')
        lng = attributes.get('lng')
        caption = attributes.get('caption')
    except:
        return JsonResponse(bad_format_errors(["Missing 'attributes' component of request data"]), status=400)

    relationships = data.get('relationships')
    if relationships:
        album_objects = relationships.get('albums', [])

        try:
            album_ids = [a.get('id') for a in album_objects]
        except:
            return JsonResponse(bad_format_errors(["Malformed 'album' relationship objects"]), status=400)
    else:
        album_ids = []

    src_type = data.get('src_type')

    if src_type == 'url':
        img_temp = NamedTemporaryFile()
        img_temp.write(urlopen(src).read())
        img_temp.flush()
        pic = File(img_temp)
    else:
        return JsonResponse(bad_format_errors(["Invalid src_type parameter"]), status=400)

    image,errs = Image.create(profile.user.username, pic, lat, lng, caption, album_ids)

    if errs:
        return JsonResponse(bad_format_errors(errs), status=400)

    # Create response object
    context = {
        'data': image.as_dict(True,True)
    }
    return JsonResponse(context, status=201)

@csrf_exempt
def patch_image(request):
    try:
        data = json.loads(request.body.decode('utf-8')).get('data')
    except:
        return JsonResponse(bad_format_errors(["Could not parse JSON body"]), status=400)

    if not data:
        return JsonResponse(bad_format_errors(["Missing 'data' component of request"]), status=400)

    api_key = request.GET.get('api_key')
    # Does this api key exist?
    try:
        profile = Profile.objects.get(api_key=api_key)
    except:
        return JsonResponse(bad_api_key_error, status=403)

    image_id = data.get('id')

    # Try to get image with this id
    try:
        image = Image.objects.get(id=image_id)
    except:
        return JsonResponse(not_found_error("Image not found"), status=404)

    # If incorrect user, return not found
    if image.user != profile.user:
        return JsonResponse(not_found_error("Image not found"), status=404)

    # Retrieve attribute data
    attributes = data.get('attributes', {})

    lat = attributes.get('lat')
    lng = attributes.get('lng')
    caption = attributes.get('caption', None)

    # Retrieve new album data
    relationships = data.get('relationships')
    if relationships:
        album_diff = relationships.get('albums', {})
        add = album_diff.get('add', [])
        remove = album_diff.get('remove', [])

        try:
            curr_album_ids = image.album_ids()

            add_ids = [a.get('id') for a in add if a.get('id') not in curr_album_ids]
            remove_ids = [a.get('id') for a in remove]

            # Add new elements to list
            curr_album_ids.extend(add_ids)

            # Remove elements to remove
            album_ids = [x for x in curr_album_ids if x not in remove_ids]
        except:
            return JsonResponse(bad_format_errors(["Malformed 'album' relationship objects"]), status=400)
    else:
        album_ids = image.album_ids()

    image,errs = Image.update(im_id=image_id,
        username=profile.user.username, lat=lat, lng=lng, caption=caption, albums=album_ids)

    if errs:
        return JsonResponse(bad_format_errors(errs), status=400)

    # Create response object
    context = {
        'data': image.as_dict(True,True)
    }
    return JsonResponse(context)


@csrf_exempt
def route_image_id_method(request, image_id):
    if request.method == 'GET':
        return get_image(request, image_id)
    elif request.method == 'DELETE':
        return delete_image(request, image_id)

@csrf_exempt
def get_image(request, image_id):
    return get_resource(request, image_id, Image)

@csrf_exempt
def delete_image(request, image_id):
    return delete_resource(request, image_id, Image)

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
        return JsonResponse(bad_api_key_error, status=403)

    # Retrieve all albums for this user
    albums = Album.objects.filter(user=profile.user)

    # Create the response object

    album_dicts = [album.as_dict(True,False) for album in albums if album.name != settings.DEFAULT_ALBUM_NAME]

    data = {
        'data': album_dicts
    }

    return JsonResponse(data)

@csrf_exempt
def route_album_id_method(request, album_id):
    if request.method == 'GET':
        return get_album(request, album_id)
    elif request.method == 'DELETE':
        return delete_album(request, album_id)

@csrf_exempt
def get_album(request, album_id):
    return get_resource(request, album_id, Album)

@csrf_exempt
def delete_album(request, album_id):
    return delete_resource(request, album_id, Album)

@csrf_exempt
def post_album(request):
    # Retrieve API key from the GET URL
    api_key = request.GET.get('api_key')

    # Do we have a user with this api key?
    try:
        profile = Profile.objects.get(api_key=api_key)
    except Exception as e:
        return JsonResponse(bad_api_key_error, status=403)

    # Try to get the data
    try:
        data = json.loads(request.body.decode('utf-8')).get('data')
    except:
        return JsonResponse(bad_format_errors(["Could not parse JSON body"]), status=400)

    if not data:
        return JsonResponse(bad_format_errors(["Missing 'data' component of request"]), status=400)

    # Retrieve the name
    attributes = data.get('attributes')
    try:
        name = attributes.get('name')
    except:
        return JsonResponse(bad_format_errors(["Missing 'attributes' component of request data"]), status=400)

    # Try to create the album
    album,errs = Album.create(profile.user.username, name)

    if errs:
        return JsonResponse(bad_format_errors(errs), status=400)

    # Create response object
    context = {
        'data': album.as_dict(True,True)
    }
    return JsonResponse(context, status=201)