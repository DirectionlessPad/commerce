from django.contrib.auth.models import AbstractUser
from django.db import models
from . import categories


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64, default="New Item")
    description = models.CharField(max_length=1500, null=True)
    current_bid = models.DecimalField(max_digits=17, decimal_places = 2, default = 1)
    image = models.URLField(max_length= 512, null=True, blank=True)
    category = models.CharField(max_length = 64, choices = categories, null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")


class Bid(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids_received")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids_placed", null=True, blank=True)
    value = models.DecimalField(max_digits=17, decimal_places = 2, default = 1)

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    item = models.ManyToManyField(Listing, blank=True, related_name="watched_by")

class Comment(models.Model):
    comment = models.CharField(max_length=1500, null=True)
    # item = #some Listing
    # commenter = #some User