from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from . import categories, CommentForm
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
    listings = Listing.objects.filter(closed="False")
    return render(request, "auctions/index.html", {
        "listings": listings,
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
            user_watchlist = Watchlist.objects.create(user=user)
            user_watchlist.save()
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
                messages.add_message(request, messages.INFO, "You must bid higher than the current bid.")
    if request.user.is_authenticated:
        # user_watchlist = request.user.watchlist.all()[0]
        user_watchlist = Watchlist.objects.get(user=request.user)
        if listing in user_watchlist.item.all():
            in_watchlist=True
        else:
            in_watchlist=False
    else:
        in_watchlist=False
    return render(request, "auctions/listing_page.html", {
        "listing": listing,
        "in_watchlist": in_watchlist,
        "highest_bid": Bid.objects.get(item=listing, value=listing.current_bid),
        "comment_form": CommentForm,
        "comments": Comment.objects.filter(item=listing),
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
    listing = Listing.objects.get(pk=listing_id)
    user_watchlist= Watchlist.objects.get(user=request.user)
    user_watchlist.item.add(listing)
    return HttpResponseRedirect(reverse("view_listing", args=[listing.pk]))

@login_required
def watchlist_remove(request):
    listing_id = request.POST["listing_to_remove"]
    listing = Listing.objects.get(pk=listing_id)
    user_watchlist = Watchlist.objects.get(user=request.user)
    user_watchlist.item.remove(listing)
    return HttpResponseRedirect(reverse("view_listing", args=[listing.pk]))

@login_required
def close_auction(request):
    listing_id = request.POST["listing_to_close"]
    listing = Listing.objects.get(pk=listing_id)
    listing.closed="True"
    listing.save()
    return HttpResponseRedirect(reverse("view_listing", args=[listing.pk]))

@login_required
def add_comment(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.cleaned_data["content"]
            new_comment = Comment(
                commenter=request.user,
                item=listing,
                comment=comment,
                )
            new_comment.save()
    return HttpResponseRedirect(reverse("view_listing", args=[listing_id]))

def select_category(request):
    return render(request, "auctions/select_category.html", {
        "categories": [category[1] for category in categories],
    })

def category(request, category_name):
    category_listings = Listing.objects.filter(category=category_name)
    return render(request, "auctions/index.html", {
        "listings": category_listings,
        "heading": category_name,
    })