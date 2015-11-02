from django.db import models

class Image(models.Model):
    image = models.ImageField(upload_to="pics")

    lat = models.DecimalField(max_digits=8, decimal_places=6)

    lng = models.DecimalField(max_digits=8, decimal_places=6)

    caption = models.CharField(max_length=100)