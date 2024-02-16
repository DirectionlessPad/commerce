from django import forms

categories = [
    ("FD", "Food and Drink"),
    ("HO", "Home"),
    ("EL", "Electronics"),
    ("BT", "Books and TV"),
    ("FA", "Fashion"),
    ("TO", "Toys"),
]

class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea())