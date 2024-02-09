from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64, default="New Item")
    description = models.CharField(max_length=1500, null=True)
    starting_bid = models.IntegerField(default = 1)
    image = models.URLField(max_length= 512, null=True)
    categories = [
        ("FD", "Food and Drink"),
        ("HO", "Home"),
        ("EL", "Electronics"),
        ("BT", "Books and TV"),
        ("FA", "Fashion"),
        ("TO", "Toys"),
    ]
    category = models.CharField(max_length = 64, choices = categories, null=True)

class Bid(models.Model):
    pass

class Comment(models.Model):
    pass