from django import forms
from .models import Listing

class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "current_bid", "image", "category"]

class BidForm(forms.Form):
    value = forms.DecimalField(max_digits=17, decimal_places = 2)

class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea())