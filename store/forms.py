from django import forms

class CartOrderRequestForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Full Name**'})
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Town/City**'})
    )
   
    address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Street Address**'})
    )
    apartment = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Apartment, suite, unit, etc (Optional)'})
    )
    mobile = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number**'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address**'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Order notes (optional)', 'rows': 4})
    )
