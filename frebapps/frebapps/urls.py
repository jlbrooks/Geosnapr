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
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from geosnapr.views import main, instagram_views, images, apis

urlpatterns = [
    url(r'^login$', main.login_view, name='login'),
    url(r'^logout$', main.logout_view, name='logout'),
    url(r'^register$', main.register, name='register'),
    url(r'^map$', main.main_map, name='map'),
    url(r'^upload$', images.upload, name='upload'),
    url(r'^edit_image$', images.edit_image, name='edit_image'),
    url(r'^delete_image$', images.delete_image, name='delete_image'),
    url(r'^create_album$', images.create_album, name='create_album'),
    url(r'^album/(?P<a_id>[0-9]+)$', images.get_album, name='get_album'),
    url(r'^edit_profile$', main.edit_profile, name='edit_profile'),
    url(r'^delete_profile$', main.delete_profile, name='delete_profile'),
    url(r'^$', main.index, name='index'),
    url(r'^get_images$', images.get_images, name='get_images'),
    url(r'^instagram_callback', instagram_views.instagram_callback, name='instagram_callback'),
    url(r'^get_insta_images$', instagram_views.get_insta_images, name='get_insta_images'),
    url(r'^get_album$', images.get_album, name='get_album'),
    # API urls
    url(r'^v1/doc$', apis.swagger, name='swagger'),
    url(r'^v1/image$', apis.api_upload, name='api_upload'),
    url(r'^v1/image/(?P<image_id>[0-9]+)$', apis.get_image, name='api_get_image'),
    url(r'^v1/album$', apis.get_albums, name='api_get_albums'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
