from django.contrib.auth.models import AbstractUser
from django.db import models
from . import categories


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64, default="New Item")
    description = models.CharField(max_length=1500, null=True)
    starting_bid = models.DecimalField(max_digits=17, decimal_places = 2, default = 1)
    image = models.URLField(max_length= 512, null=True)
    category = models.CharField(max_length = 64, choices = categories, null=True)

class Bid(models.Model):
    pass

class Comment(models.Model):
    pass