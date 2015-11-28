from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from instagram import client, InstagramClientError, InstagramAPIError
from urllib.request import urlopen

def instagram_callback(request):
    # Callback URI
    insta_callback_uri = request.build_absolute_uri(reverse(instagram_callback))

    # Config for the base api calls
    instagram_config = {
        'client_id': settings.INSTAGRAM_APP_ID,
        'client_secret': settings.INSTAGRAM_APP_SECRET,
        'redirect_uri': insta_callback_uri,
    }

    # API request object
    unauthenticated_api = client.InstagramAPI(**instagram_config)

    code = request.GET.get('code')
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
            return redirect(main.main_map)
        else:
            # Return the user information to assist with account creation
            print(user_info)
            return redirect(main.main.index)
    except InstagramClientError as e:
        data['error'] = e.error_message
    except InstagramAPIError as e:
        data['error'] = e.error_message

    return redirect(main.index)

@login_required
def get_insta_images(request):
    data = {}

    access_token = request.user.profile.insta_access_key
    if not access_token:
        data['error'] = "You haven't linked your Geosnapr and Instagram accounts yet."

    try:
        api = client.InstagramAPI(access_token=access_token,
            client_secret=settings.INSTAGRAM_APP_SECRET)

        recent_media, next = api.user_recent_media()
        photos = []
        data['photos'] = photos
        for media in recent_media:
            if (media.type != 'video'):
                img = {}
                img['image'] = media.get_standard_resolution_url()
                if hasattr(media, 'location'):
                    img['lat'] = media.location.point.latitude
                    img['lng'] = media.location.point.longitude
                if hasattr(media, 'caption'):
                    if hasattr(media.caption, 'text'):
                        img['caption'] = media.caption.text
                photos.append(img)
    except InstagramClientError as e:
        data['error'] = e.error_message
    except InstagramAPIError as e:
        data['error'] = e.error_message
        request.user.profile.insta_access_key = ''
        request.user.profile.save()

    return JsonResponse(data)