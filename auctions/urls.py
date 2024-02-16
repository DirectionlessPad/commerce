from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.create_listing, name="create_listing"),
    path("listing/<str:listing_id>", views.listing, name="view_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist_add", views.watchlist_add, name="watchlist_add"),
    path("watchlist_remove", views.watchlist_remove, name="watchlist_remove"),
]
