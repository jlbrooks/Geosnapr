from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User)

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

        # Return the created profile
        return profile,None


class Image(models.Model):
    image = models.ImageField(upload_to="pics")

    lat = models.DecimalField(max_digits=8, decimal_places=6)

    lng = models.DecimalField(max_digits=8, decimal_places=6)

    caption = models.CharField(max_length=100)

    @classmethod
    def create(cls, image, lat, lng, caption):
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

        # Return if we have any errors
        if err:
            return None,err

        # Create the pic object
        pic = cls.objects.create(image=image, lat=lat, lng=lng, caption=caption)
        pic.save()

        return pic,None