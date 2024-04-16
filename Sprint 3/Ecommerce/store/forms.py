from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product
# from .models import Book


class NewUserForm(UserCreationForm):
    ROLE_CHOICES = [
        ('consumer', 'Consumer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class AddBookForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'digital', 'image']


# class BookForm(forms.ModelForm):
#     class Meta:
#         model = Book
#         fields = ['isbn', 'title', 'author', 'genre', 'pages', 'release_date', 'stock']
