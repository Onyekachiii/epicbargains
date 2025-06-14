from django import forms

class CartOrderRequestForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=20, required=False)
    street_address = forms.CharField(max_length=255)
    apartment = forms.CharField(max_length=255, required=False)
    phone_number = forms.CharField(max_length=20)
    email = forms.EmailField()
    notes = forms.CharField(widget=forms.Textarea, required=False)
