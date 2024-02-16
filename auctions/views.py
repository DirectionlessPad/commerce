from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from . import categories
from .models import User, Listing, Bid, Watchlist, Comment


def index(request):
    # for listing in Listing.objects.all():
        # bids = listing.bids_received
        # max_bid = bids.all().aggregate(Max('value'))["value__max"]
        # # these lines can probably be removed once I have implemented 
        # # the bidding system as then I can just update the current_bid 
        # # property from there
        # listing.current_bid = max_bid
        # listing.save()
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "heading": "Active Listings",
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        else:
            title = request.POST["title"]
            starting_bid = request.POST["starting_bid"]
            image = request.POST["image"]
            category = request.POST["category"]
            description = request.POST["description"]
            seller = request.user
            listing = Listing(
                title = title,
                description = description,
                current_bid = starting_bid,
                image = image,
                category = category,
                seller = seller
            )
            listing.save()
            bid = Bid(
                value = starting_bid,
                item = listing,
            )
            bid.save()
    return render(request, "auctions/create_listing.html", {
        "categories": [category[1] for category in categories]
    })

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.method =="POST":
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        else:
            new_bid = float(request.POST["new_bid_value"])
            print(listing.current_bid)
            if new_bid > listing.current_bid:
                listing.current_bid = new_bid
                listing.save()
                bid = Bid(
                    value = new_bid,
                    item = listing,
                    bidder = request.user,
                )
                bid.save()
            else:
                pass
    # breakpoint()
    return render(request, "auctions/listing_page.html", {
        "listing": listing,
    })

@login_required
def watchlist(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    user_watchlist = request.user.watchlist.all()[0]
    watchlist_listings=[]
    for item in user_watchlist.item.all():
        watchlist_listings.append(item)
    return render(request, "auctions/index.html", {
        "listings": watchlist_listings,
        "heading": "Your Watchlist"
    })

@login_required
def watchlist_add(request):
    listing_id = request.POST["listing_to_add"]
    listing = Listing.objects.filter(pk=listing_id)[0]
    if not Watchlist.objects.filter(user=request.user, item=listing.pk).exists():
        user_watchlist, created = Watchlist.objects.get_or_create(user=request.user)
        user_watchlist.item.add(listing)
    return HttpResponseRedirect(reverse("view_listing", args=[listing.title]))

def watchlist_remove(request):
    listing = request.POST["listing_to_remove"]
    if Watchlist.objects.filter(user=request.user, item=listing.pk).exists():
        user_watchlist, created = Watchlist.objects.get_or_create(user=request.user)
        user_watchlist.item.remove(listing)
    # next = request.POST.get('next', '/')
    return HttpResponseRedirect(reverse("listing", args=[listing.title]))