from django.shortcuts import render
from django.db import models
from customer import models as customer_models
from store.models import Product
from customer.models import WishList
from django.db.models import Q, Avg, Sum, Count

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core import serializers
from django.template.loader import render_to_string

# Create your views here.


# To add to wishlist
def add_to_wishlist(request):
    id = request.GET['id']
    product = Product.objects.get(id=id)
    
    context = {}
    
    wishlist_count = WishList.objects.filter(user=request.user, product=product).count()
    print(wishlist_count)
    
    if wishlist_count > 0:
        context = {
            "bool": True,
        }
    else:
        new_wishlist = WishList.objects.create(
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
    wishlist = WishList.objects.filter(user=request.user)

    context = {
        "w" : wishlist,
    }
    return render(request, "core/wishlist.html", context)


# To remove from wishlist
@login_required
def remove_from_wishlist(request):
    pid = request.GET['id']
    wishlist = WishList.objects.filter(user=request.user)
    product = WishList.objects.get(id=pid)
    product.delete()
    
    context = {
        "bool" : True,
        "w": wishlist,
    }
    wishlist_json = serializers.serialize('json', wishlist)
    data = render_to_string("core/async/wishlist-list.html", context)
    return JsonResponse({"data": data, "w": wishlist_json})