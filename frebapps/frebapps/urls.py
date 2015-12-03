"""frebapps URL Configuration

The `urlpatterns` list routes URLs to  For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from geosnapr.views import main, instagram_views, images, apis

urlpatterns = [
    # Basic urls
    url(r'^$', main.index, name='index'),
    url(r'^login$', main.login_view, name='login'),
    url(r'^logout$', main.logout_view, name='logout'),
    url(r'^register$', main.register, name='register'),
    url(r'^map$', main.main_map, name='map'),
    # Profile urls
    url(r'^edit_profile$', main.edit_profile, name='edit_profile'),
    url(r'^delete_profile$', main.delete_profile, name='delete_profile'),
    # Image urls
    url(r'^upload$', images.upload, name='upload'),
    url(r'^edit_image$', images.edit_image, name='edit_image'),
    url(r'^delete_image$', images.delete_image, name='delete_image'),
    url(r'^get_images$', images.get_images, name='get_images'),
    url(r'^get_public$', images.get_public, name='get_public'),
    # Album urls
    url(r'^create_album$', images.create_album, name='create_album'),
    url(r'^album/(?P<a_id>[0-9]+)$', images.get_album, name='get_album'),
    url(r'^get_album$', images.get_album, name='get_album'),
    # Instagram urls
    url(r'^instagram_callback', instagram_views.instagram_callback, name='instagram_callback'),
    url(r'^get_insta_images$', instagram_views.get_insta_images, name='get_insta_images'),
    # API urls
    url(r'^v1/doc/geosnapr.json$', apis.api_description, name="api_description"),
    url(r'^v1/doc$', apis.swagger, name='swagger'),
    url(r'^v1/image$', apis.route_image_method, name='api_image_method'),
    url(r'^v1/image/(?P<image_id>[0-9]+)$', apis.route_image_id_method, name='api_image_id_method'),
    url(r'^v1/album$', apis.route_album_method, name='api_route_albums'),
    url(r'^v1/album/(?P<album_id>[0-9]+)$', apis.route_album_id_method, name='api_album_id_method'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
