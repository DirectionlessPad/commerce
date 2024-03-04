from django.contrib.auth.models import AbstractUser
from django.db import models
from . import categories


class User(AbstractUser):
    """Registers users.
    
    Attributes:
    listings -- listing objects put up by this user
    bids_placed -- bid objects placed by this user
    watchlist -- watchlist object for listings watched by this user
    comments_left -- comments left by this user on various listing objects
    """
    pass


class Listing(models.Model):
    """Records details of each listing.
    
    Attributes:
    pk -- primary key
    title -- the name of the listing
    description -- a description of the item in the listing
    current_bid -- the highest bid placed on the listing so far
    image -- url for an image (optional)
    category -- category for the listed item (optional)
    seller -- user who listed the item
    closed -- boolean recording open/closed state of the listing
    bids_received -- bid objects placed on this item
    watched_by -- user objects who have this item on their watchlist
    comments -- comment objects left on this item
    """
    title = models.CharField(verbose_name="Title", max_length=64, default="New Item")
    description = models.CharField(verbose_name="Description", max_length=1500, null=True)
    current_bid = models.DecimalField(verbose_name="Starting Bid", max_digits=17, decimal_places = 2, default = 1)
    image = models.URLField(verbose_name="Image", max_length= 512, null=True, blank=True)
    category = models.CharField(verbose_name="Category", max_length = 64, choices = categories, null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    closed = models.BooleanField(default="False")


class Bid(models.Model):
    """Records details of succesful bids.
    
    Attributes:
    item -- listing object the bid was placed on
    bidder -- user object that placed the bid
    value -- monetary value of the bid
    """
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids_received")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids_placed", null=True, blank=True)
    value = models.DecimalField(max_digits=17, decimal_places = 2, default = 1)


class Watchlist(models.Model):
    """Records listings being watched by a user.
    
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    item = models.ManyToManyField(Listing, blank=True, related_name="watched_by")


class Comment(models.Model):
    comment = models.CharField(max_length=1500, null=True)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments_left")