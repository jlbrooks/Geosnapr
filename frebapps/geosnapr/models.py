from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User)

    @classmethod
    def create_profile(cls, email, password, first_name, last_name):
        err = []
        # First name must exist
        if not first_name:
            err.append('First name must not be blank')

        # Last name must exist
        if not last_name:
            err.append('Last name must not be blank')

        # Password must exist
        if not password:
            err.append('Password must not be blank')

        # See if this email already exists
        try:
            User.objects.get(email=email)
            err.append('Email already exists')
        except:
            pass

        # Return if we have any errors
        if err:
            return None,err

        # Create user object
        user = User.objects.create(password=password, first_name=first_name,
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