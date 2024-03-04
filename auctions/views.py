from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from . import categories
from .my_forms import BidForm, CommentForm, CreateListingForm
from .models import User, Listing, Bid, Watchlist, Comment


def index(request):
    """Display homepage with list of active listings."""
    listings = Listing.objects.filter(closed="False")
    return render(request, "auctions/index.html", {
        "listings": listings,
        "heading": "Active Listings",
    })


def login_view(request):
    """Display login page and perform login user operation."""
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if not user.watchlist:
                user_watchlist = Watchlist.objects.create(user=user)
                user_watchlist.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    """Perform logout user operation."""
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """Display register page and perform register user operation."""
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


def listing(request, listing_id: str):
    """Display listing page.
    
    Arguments:
    listing_id -- primary key for the listing
    """
    listing = Listing.objects.get(pk=listing_id)
    bidform = BidForm(initial={"value": listing.current_bid})
    if request.user.is_authenticated:
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
        "bid_form": bidform,
        "highest_bid": Bid.objects.get(item=listing, value=listing.current_bid),
        "comment_form": CommentForm,
        "comments": Comment.objects.filter(item=listing),
    })


@login_required
def create_listing(request):
    """Display listing and perform create listing operations."""
    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        else:
            createlistingform = CreateListingForm(request.POST)
            if createlistingform.is_valid():
                title = createlistingform.cleaned_data["title"]
                starting_bid = createlistingform.cleaned_data["current_bid"]
                image = createlistingform.cleaned_data["image"]
                category = createlistingform.cleaned_data["category"]
                description = createlistingform.cleaned_data["description"]
                seller = request.user
                listing = Listing(
                    title = title,
                    description = description,
                    current_bid = starting_bid,
                    image = image,
                    category = category,
                    seller = seller
                )
                breakpoint()
                listing.save()
                bid = Bid(
                    value = starting_bid,
                    item = listing,
                )
                bid.save()
    return render(request, "auctions/create_listing.html", {
        "create_form": CreateListingForm,
    })


@login_required
def watchlist(request):
    """Display user watchlist page."""
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    user_watchlist= Watchlist.objects.get(user=request.user)
    # user_watchlist = request.user.watchlist.all()[0]
    watchlist_listings=[]
    for item in user_watchlist.item.all():
        watchlist_listings.append(item)
    return render(request, "auctions/index.html", {
        "listings": watchlist_listings,
        "heading": "Your Watchlist"
    })


def watchlist_add(request) -> HttpResponseRedirect:
    """Add listing to user's watchlist."""
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    listing_id = request.POST["listing_to_add"]
    listing = Listing.objects.get(pk=listing_id)
    user_watchlist= Watchlist.objects.get(user=request.user)
    user_watchlist.item.add(listing)
    return HttpResponseRedirect(reverse("view_listing", args=[listing.pk]))


@login_required
def watchlist_remove(request):
    """Remove listing from user's watchlist."""
    listing_id = request.POST["listing_to_remove"]
    listing = Listing.objects.get(pk=listing_id)
    user_watchlist = Watchlist.objects.get(user=request.user)
    user_watchlist.item.remove(listing)
    return HttpResponseRedirect(reverse("view_listing", args=[listing.pk]))


def new_bid(request, listing_id):
    """Process new bids.
    
    Arguments:
    listing_id -- primary key for the listing
    """
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    listing = Listing.objects.get(pk=listing_id)
    bid_form = BidForm(request.POST)
    if bid_form.is_valid():
        bid = bid_form.cleaned_data["value"]
        if not bid > listing.current_bid:
            messages.add_message(request, messages.INFO, "You must bid higher than the current bid.")
            return HttpResponseRedirect(reverse("view_listing", args=[listing_id]))
        listing.current_bid = bid
        listing.save()
        new_bid = Bid(
            item=listing,
            bidder=request.user,
            value=bid,
        )
        new_bid.save()
    user_watchlist= Watchlist.objects.get(user=request.user)
    if listing not in user_watchlist:
        user_watchlist.item.add(listing)
    return HttpResponseRedirect(reverse("view_listing", args=[listing_id]))


@login_required
def close_auction(request):
    """Ends the auction."""
    listing_id = request.POST["listing_to_close"]
    listing = Listing.objects.get(pk=listing_id)
    listing.closed="True"
    listing.save()
    return HttpResponseRedirect(reverse("view_listing", args=[listing.pk]))


def add_comment(request, listing_id):
    """Process new comments.
    
    Arguments:
    listing_id -- primary key for the listing
    """
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    listing = Listing.objects.get(pk=listing_id)
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
    """Display category selection page."""
    return render(request, "auctions/select_category.html", {
        "categories": [category[1] for category in categories],
    })


def category(request, category_name):
    """Display listings that fall into a selected category.
    
    Arguments:
    category_name -- selected category to view listings for
    """
    category_listings = Listing.objects.filter(category=category_name)
    return render(request, "auctions/index.html", {
        "listings": category_listings,
        "heading": category_name,
    })