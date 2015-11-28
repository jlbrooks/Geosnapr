from geosnapr.models import Image
from django.http import JsonResponse
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

# Refactor into image model
def image_data(image):
    album_ids = image.album_ids()
    albums = []
    for album_id in album_ids:
        a_data = {
            'type': 'album',
            'id': album_id
        }
        albums.append(a_data)

    data = {
        'type': 'image',
        'id': image.id,
        'attributes': {
            'src': image.image,
            'lat': image.lat,
            'lng': image.lng,
            'caption': image.caption
        },
        'relationships': {
            'user': {
                'data': {
                    'type': 'user',
                    'id': image.user.id
                }
            },
            'albums': albums
        }
    }

    return data


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

    if src_type = 'url':
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
        return JsonResponse(image_data(image), status=201)