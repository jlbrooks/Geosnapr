"""frebapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
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
from geosnapr import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^map$', views.main_map, name='map'),
    url(r'^upload$', views.upload, name='upload'),
    url(r'^edit_image$', views.edit_image, name='edit_image'),
    url(r'^create_album$', views.create_album, name='create_album'),
    url(r'^album/(?P<a_id>[0-9]+)$', views.get_album, name='get_album'),
    url(r'^edit_profile$', views.edit_profile, name='edit_profile'),
    url(r'^delete_profile$', views.delete_profile, name='delete_profile'),
    url(r'^$', views.index, name='index'),
    url(r'^get_images$', views.get_images, name='get_images'),
    url(r'^instagram_callback', views.instagram_callback, name='instagram_callback'),
    url(r'^get_insta_images$', views.get_insta_images, name='get_insta_images'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
