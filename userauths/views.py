from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from userauths import forms as userauths_forms
from userauths import models as userauths_models

# Create your views here.
def register_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in!")
        return redirect("/")

    form = userauths_forms.UserRegisterForm(request.POST or None)

    if form.is_valid():
        user = form.save()

        full_name = form.cleaned_data.get("full_name")
        email = form.cleaned_data.get("email")
        mobile = form.cleaned_data.get("mobile")
        password = form.cleaned_data.get("password1")  # ✅ correct field name

        user = authenticate(email=email, password=password)
        if user:
            login(request, user)

            messages.success(request, "Account was created successfully")
            profile = userauths_models.Profile.objects.create(
                full_name=full_name,
                mobile=mobile,
                user=user
            )
            profile.save()

            next_url = request.GET.get("next", "store:index")
            return redirect(next_url)
        else:
            messages.error(request, "Authentication failed. Please try logging in.")

    context = {"form": form}
    return render(request, "userauths/sign-up.html", context)

