import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "frebapps.settings")

from geosnapr.models import User, Album, Image
import django

if __name__ == '__main__':
    django.setup()
    # Get all users
    users = User.objects.all()

    for user in users:
        # Create the default album
        album = Album.get_or_create_default_for_user(username=user.username)

        # Associate all images with the default album
        images = Image.objects.filter(user=user)
        for image in images:
            if image not in album.images.all():
                album.images.add(image)
            album.save()