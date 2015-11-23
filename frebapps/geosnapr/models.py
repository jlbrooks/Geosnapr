from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from decimal import Decimal

class Profile(models.Model):
    user = models.OneToOneField(User)

    insta_access_key = models.CharField(max_length=100, default='')

    @classmethod
    def create(cls, username, email, password, first_name, last_name):
        err = []

        # Username must exist
        if not username:
            err.append('Username must not be blank')

        # First name must exist
        if not first_name:
            err.append('First name must not be blank')

        # Last name must exist
        if not last_name:
            err.append('Last name must not be blank')

        # Password must exist
        if not password:
            err.append('Password must not be blank')

        # Email must exist
        if not email:
            err.append('Email must not be blank')

        # See if this username or email already exists in the db
        if username and email:
            u = User.objects.filter(username=username)
            if u:
                err.append('Username already exists')
            u = User.objects.filter(email=email)
            if u:
                err.append('Email already exists')

        # Return if we have any errors
        if err:
            return None,err

        # Create user object
        user = User.objects.create_user(username=username, password=password, first_name=first_name,
            last_name=last_name, email=email)
        user.save()

        # Create profile object
        profile = cls.objects.create(user=user)
        profile.save()

        # Create the default album
        Album.get_or_create_default_for_user(username=user.username)

        # Return the created profile
        return profile,None

    @classmethod
    def update(cls, username, email, password, first_name, last_name):
        err = []

        try:
            u = User.objects.get(username=username)
        except:
            err.append('User does not exist')
            return None, err

        # First name must exist
        if first_name:
            u.first_name = first_name

        # Last name must exist
        if last_name:
            u.last_name = last_name

        # Password must exist
        if password:
            u.set_password(password)

        # Email must exist
        if email:
            try:
                other_u = User.objects.get(email=email)
                if u != other_u:
                    err.append('User with that email already exists')
            except:
                u.email = email

        # Return if we have any errors
        if err:
            return None,err

        u.save()

        return u.profile,None


def upload_to(instance, filename):
    # Grab the last part of url filenames
    if '\\' in filename:
        filename = filename.split('\\')[-1]
    if '/' in filename:
        filename = filename.split('/')[-1]
    # Add extension
    if '.' not in filename:
        filename += '.jpg'

    return 'images/%s/%s' % (instance.user.username, filename)

class Image(models.Model):
    user = models.ForeignKey(User)

    image = models.ImageField(upload_to=upload_to)

    lat = models.DecimalField(max_digits=9, decimal_places=6)

    lng = models.DecimalField(max_digits=9, decimal_places=6)

    caption = models.CharField(max_length=100)

    @classmethod
    def create(cls, username, image, lat, lng, caption):
        err = []

        # Image must exist
        if not image:
            err.append('Image must be present')

        # Lat must exist
        if not lat:
            err.append('Latitude must be present')

        # Lat must exist
        if not lng:
            err.append('Longitude must be present')

        # Set caption to empty string if not present
        if not caption:
            caption = ''

        # User must exist
        try:
            user = User.objects.get(username=username)
        except:
            err.append('User does not exist')

        # Return if we have any errors
        if err:
            return None,err

        # Truncate lat and lng
        lat = '%.6f' % float(lat)
        lng = '%.6f' % float(lng)

        # Create the image object
        pic = cls.objects.create(image=image, lat=Decimal(lat), lng=Decimal(lng), caption=caption, user=user)
        pic.save()

        # Add the new image to the users 'all images' album
        album = Album.get_or_create_default_for_user(user.username)
        album.images.add(pic)
        album.save()

        return pic,None

    @classmethod
    def update(cls, im_id, username, lat, lng, caption):
        err = []

        # Image must exist
        try:
            image = Image.objects.get(id=im_id)
        except:
            err.append('Image does not exist')
            return None,err

        # User must exist
        try:
            user = User.objects.get(username=username)
        except:
            err.append('User does not exist')
            return None,err

        # User must own this image
        if image.user != user:
            err.append('User does not own this image')

        # Update lat
        if lat:
            image.lat = Decimal('%.6f' % float(lat))

        # Update lng
        if lng:
            image.lng = Decimal('%.6f' % float(lng))

        # Update caption
        image.caption = caption

        # Save the image
        image.save()

        # Return the new image
        return image,None


class Album(models.Model):
    user = models.ForeignKey(User)

    name = models.CharField(max_length=100)

    images = models.ManyToManyField(Image)

    @classmethod
    def create(cls, username, name):
        err = []

        # Set default name
        if not name:
            name = 'Untitled Album'

        # Make sure the user exists
        try:
            user = User.objects.get(username=username)
        except:
            err.append('User does not exist.')

        # Return if we have errors
        if err:
            return None,err

        # Create the new album
        album = cls.objects.create(user=user, name=name)
        album.save()

        return album,None

    @classmethod
    def get_or_create_default_for_user(cls, username):
        try:
            user = User.objects.get(username=username)
        except:
            return None

        try:
            return cls.objects.get(user=user, name=settings.DEFAULT_ALBUM_NAME)
        except:
            album,errs = cls.create(user.username, settings.DEFAULT_ALBUM_NAME)
            return album
            