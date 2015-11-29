from geosnapr.models import Image
from django.http import JsonResponse
from django.shortcuts import render
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from urllib.request import urlopen

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

# View functions

def swagger(request):
    return render(request, 'swagger.html')

def api_upload(request):
    if request.method != "POST":
        return JsonResponse(wrong_method_error)

    data = request.POST.get('data')

    if not data:
        return JsonResponse(bad_format_errors(["Missing 'data' component of request"]))

    api_key = data.get('api_key')

    lat = data.get('lat')
    lng = data.get('lng')
    caption = data.get('caption')
    album_ids = data.get('album_ids')

    src = data.get('src')
    src_type = data.get('type')

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

    image,errs = Image.create(Profile.user.username, pic, lat, lng, caption, album_ids)

    if errs:
        return JsonResponse(bad_format_errors(errs))
    else:
        # Create response object
        context = {
            'data': image.as_dict(True,True)
        }
        return JsonResponse(context, status=201)

def get_albums(request):
    # Retrieve API key from the GET URL
    api_key = request.GET.get('api_key')

    # Do we have a user with this api key?
    try:
        profile = Profile.objects.get(api_key=api_key)
    except:
        return JsonResponse(bad_api_key_error)

    # Retrieve all albums for this user
    albums = Album.objects.filter(user=profile.user)

    # Create the response object

    album_dicts = [album.as_dict() for album in albums]

    data = {
        'data': album_dicts
    }

    return JsonResponse(data)