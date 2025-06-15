from django.shortcuts import render, redirect
from django.db import models
from django.contrib import messages
from customer import models as customer_models
from store import models as store_models
from store.models import Product
from .models import Wishlist
from django.db.models import Q, Avg, Sum, Count
from django.contrib.auth.hashers import check_password

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core import serializers
from django.template.loader import render_to_string

from customer.models import Address

# Create your views here.

@login_required
def dashboard(request):
    orders = store_models.Order.objects.filter(customer=request.user)
    total_spent = store_models.Order.objects.filter(customer=request.user).aggregate(total = models.Sum("total"))["total"]
    notis = customer_models.Notifications.objects.filter(user=request.user, seen=False)
    user_address = Address.objects.filter(user=request.user).first() 
    
    context = {
        "orders" : orders,
        "total_spent": total_spent,
        "notis" : notis,
        'user_address': user_address,
    }
    
    return render(request, "customer/dashboard.html", context)

@login_required
def update_profile(request):
    user = request.user
    profile = user.profile
    address, created = Address.objects.get_or_create(user=user)

    if request.method == 'POST':
        profile.full_name = request.POST.get('full_name')
        profile.mobile = request.POST.get('mobile')

        user.email = request.POST.get('email')
        if 'image' in request.FILES:
            profile.image = request.FILES['image']

        # Update Address fields
        address.address = request.POST.get('address')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.zip_code = request.POST.get('zip_code')
        address.country = request.POST.get('country')
        address.full_name = profile.full_name
        address.email = user.email
        address.mobile = profile.mobile

        # Save everything
        user.save()
        profile.save()
        address.save()

        messages.success(request, "Your account details were updated successfully.")
        return redirect('customer:dashboard')  # Or wherever you want

    return redirect('customer:dashboard')

    

# To add to wishlist
def add_to_wishlist(request):
    id = request.GET['id']
    product = Product.objects.get(id=id)
    
    context = {}
    
    wishlist_count = Wishlist.objects.filter(user=request.user, product=product).count()
    print(wishlist_count)
    
    if wishlist_count > 0:
        context = {
            "bool": True,
        }
    else:
        new_wishlist = Wishlist.objects.create(
            product = product,
            user = request.user
        )
        context ={
            "bool": True,
        }
    
    return JsonResponse(context)

# To view wishlist
@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user)

    context = {
        "w" : wishlist,
    }
    return render(request, "core/wishlist.html", context)


# To remove from wishlist
@login_required
def remove_from_wishlist(request):
    pid = request.GET['id']
    wishlist = Wishlist.objects.filter(user=request.user)
    product = Wishlist.objects.get(id=pid)
    product.delete()
    
    context = {
        "bool" : True,
        "w": wishlist,
    }
    wishlist_json = serializers.serialize('json', wishlist)
    data = render_to_string("core/async/wishlist-list.html", context)
    return JsonResponse({"data": data, "w": wishlist_json})