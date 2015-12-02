from django.http import JsonResponse
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from instagram import client, InstagramClientError, InstagramAPIError
from urllib.request import urlopen

def instagram_callback(request):
    # Import here to prevent circularity issues
    from .main import index, main_map

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
            return redirect(main_map)
        else:
            # Return the user information to assist with account creation
            print(user_info)
            return redirect(index)
    except InstagramClientError as e:
        data['error'] = e.error_message
    except InstagramAPIError as e:
        data['error'] = e.error_message

    return redirect(index)

@login_required
def get_insta_images(request):
    data = {}

    access_token = request.user.profile.insta_access_key
    if not access_token:
        data['error'] = "You haven't linked your Geosnapr and Instagram accounts yet."

    try:
        api = client.InstagramAPI(access_token=access_token,
            client_secret=settings.INSTAGRAM_APP_SECRET)

        provided_next = request.GET.get('next')

        if provided_next:
            recent_media, _next = api.user_recent_media(with_next_url=provided_next)
        else:
            recent_media, _next = api.user_recent_media()

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

    if _next:
        data['next_insta_url'] = _next
    else:
        data['next_insta_url'] = ''

    return JsonResponse(data)