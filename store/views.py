from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db.models import Q, Avg, Sum, Count
from django.core import serializers
from .forms import CartOrderRequestForm


from django.contrib.auth.decorators import login_required


from decimal import Decimal
import requests
import stripe
# from plugin.service_fee import calculate_service_fee
import razorpay

# from plugin.paginate_queryset import paginate_queryset
from store import context
from store import models as store_models
from store.models import Category, Order
from customer import models as customer_models
from userauths import models as userauths_models
# from plugin.tax_calculation import tax_calculation
# from plugin.exchange_rate import convert_usd_to_inr, convert_usd_to_kobo, convert_usd_to_ngn, get_usd_to_ngn_rate



def clear_cart_items(request):
    try:
        cart_id = request.session['cart_id']
        store_models.Cart.objects.filter(cart_id=cart_id).delete()
    except:
        pass
    return

def index(request):
    products = store_models.Product.objects.filter(status="Published")
    categories = store_models.Category.objects.all()
    
    context = {
        "products": products,
        "categories": categories,
    }
    return render(request, "store/index.html", context)



# def shop(request):
#     products_list = store_models.Product.objects.filter(status="Published")
#     categories = store_models.Category.objects.all()
#     colors = store_models.VariantItem.objects.filter(variant__name='Color').values('title', 'content').distinct()
#     sizes = store_models.VariantItem.objects.filter(variant__name='Size').values('title', 'content').distinct()
#     item_display = [
#         {"id": "1", "value": 1},
#         {"id": "2", "value": 2},
#         {"id": "3", "value": 3},
#         {"id": "40", "value": 40},
#         {"id": "50", "value": 50},
#         {"id": "100", "value": 100},
#     ]

#     ratings = [
#         {"id": "1", "value": "★☆☆☆☆"},
#         {"id": "2", "value": "★★☆☆☆"},
#         {"id": "3", "value": "★★★☆☆"},
#         {"id": "4", "value": "★★★★☆"},
#         {"id": "5", "value": "★★★★★"},
#     ]

#     prices = [
#         {"id": "lowest", "value": "Highest to Lowest"},
#         {"id": "highest", "value": "Lowest to Highest"},
#     ]


#     print(sizes)

#     products = (request, products_list, 10)

#     context = {
#         "products": products,
#         "products_list": products_list,
#         "categories": categories,
#          'colors': colors,
#         'sizes': sizes,
#         'item_display': item_display,
#         'ratings': ratings,
#         'prices': prices,
#     }
#     return render(request, "store/shop.html", context)

def category(request, id):
    category = store_models.Category.objects.get(id=id)
    products_list = store_models.Product.objects.filter(status="Published", category=category)

    query = request.GET.get("q")
    if query:
        products_list = products_list.filter(name__icontains=query)

    # Annotate each category with the number of published products
    categories = store_models.Category.objects.annotate(
        count=Count('product', filter=Q(product__status='Published'))
    )

    context = {
        "products_list": products_list,
        "category": category,
        "categories": categories,  # ← Pass this to your template
    }
    return render(request, "store/category.html", context)

def product_detail(request, slug):
    product = store_models.Product.objects.get(status="Published", slug=slug)
    product_stock_range = range(1, product.stock + 1)

    related_products = store_models.Product.objects.filter(category=product.category).exclude(id=product.id)

    context = {
        "product": product,
        "product_stock_range": product_stock_range,
        "related_products": related_products
        
    }
    return render(request, "store/product_detail.html", context)

def add_to_cart(request):
    # Get parameters from the request (ID, color, size, quantity, cart_id)
    id = request.GET.get("id")
    qty = request.GET.get("qty")
    color = request.GET.get("color")
    size = request.GET.get("size")
    cart_id = request.GET.get("cart_id")
    
    request.session['cart_id'] = cart_id

    # Validate required fields
    if not id or not qty or not cart_id:
        return JsonResponse({"error": "No id, qty or cart_id"}, status=400)

    # Try to fetch the product, return an error if it doesn't exist
    try:
        product = store_models.Product.objects.get(status="Published", id=id)
    except store_models.Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    # Check if the item is already in the cart
    existing_cart_item = store_models.Cart.objects.filter(cart_id=cart_id, product=product).first()

    # Check if quantity that user is adding exceed item stock qty
    if int(qty) > product.stock:
        return JsonResponse({"error": "Qty exceeds current stock amount"}, status=404)

    cart = None 
    
    # If the item is not in the cart, create a new cart entry
    if not existing_cart_item:
        cart = store_models.Cart()
        cart.product = product
        cart.qty = qty
        cart.price = product.price
        cart.color = color
        cart.size = size
        cart.sub_total = Decimal(product.price) * Decimal(qty)
        cart.shipping = Decimal(product.shipping) * Decimal(qty)
        cart.total = cart.sub_total + cart.shipping
        cart.user = request.user if request.user.is_authenticated else None
        cart.cart_id = cart_id
        cart.save()

        message = "Item added to cart"
    else:
        # If the item exists in the cart, update the existing entry
        existing_cart_item.color = color
        existing_cart_item.size = size
        existing_cart_item.qty = qty
        existing_cart_item.price = product.price
        existing_cart_item.sub_total = Decimal(product.price) * Decimal(qty)
        existing_cart_item.shipping = Decimal(product.shipping) * Decimal(qty)
        existing_cart_item.total = existing_cart_item.sub_total +  existing_cart_item.shipping
        existing_cart_item.user = request.user if request.user.is_authenticated else None
        existing_cart_item.cart_id = cart_id
        existing_cart_item.save()

        message = "Cart updated"

    # Total items count and cart subtotal
    total_cart_items = store_models.Cart.objects.filter(cart_id=cart_id).count()
    cart_sub_total = store_models.Cart.objects.filter(cart_id=cart_id).aggregate(
    sub_total=models.Sum("sub_total")
)['sub_total'] or 0

    # Return safe response
    return JsonResponse({
        "message": message,
        "total_cart_items": total_cart_items,
        "cart_sub_total": "{:,.2f}".format(cart_sub_total),
        "item_sub_total": "{:,.2f}".format(existing_cart_item.sub_total if existing_cart_item else (cart.sub_total if cart else 0)
    )
    })

@login_required
def cart(request):
    # Only show cart items belonging to this user
    items = store_models.Cart.objects.filter(user=request.user)
    cart_sub_total = items.aggregate(sub_total=Sum("sub_total"))['sub_total'] or 0

    try:
        addresses = customer_models.Address.objects.filter(user=request.user)
    except:
        addresses = None

    if not items.exists():
        messages.warning(request, "No item in cart")
        return redirect("store:index")

    context = {
        "items": items,
        "cart_sub_total": cart_sub_total,
        "addresses": addresses
    }
    return render(request, "store/cart.html", context)


@login_required
def delete_cart_item(request):
    id = request.GET.get("id")
    item_id = request.GET.get("item_id")
    cart_id = request.GET.get("cart_id")
    
    # Validate required fields
    if not id and not item_id and not cart_id:
        return JsonResponse({"error": "Item or Product id not found"}, status=400)

    try:
        product = store_models.Product.objects.get(status="Published", id=id)
    except store_models.Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)

    # Check if the item is already in the cart
    item = store_models.Cart.objects.get(product=product, id=item_id)
    item.delete()

    # Count the total number of items in the cart
    total_cart_items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user))
    cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)).aggregate(sub_total = models.Sum("sub_total"))['sub_total']

    return JsonResponse({
        "message": "Item deleted",
        "total_cart_items": total_cart_items.count(),
        "cart_sub_total": "{:,.2f}".format(cart_sub_total) if cart_sub_total else 0.00
    })


from django.urls import reverse  # Add this import

@login_required
def create_order(request):
    customer = request.user
    profile = customer.profile

    cart_id = request.session.get('cart_id')
    items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=customer))

    if not items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("store:cart")

    cart_sub_total = items.aggregate(sub_total=Sum("sub_total"))['sub_total'] or 0
    cart_shipping_total = items.aggregate(shipping=Sum("shipping"))['shipping'] or 0

    if request.method == "POST":
        form = CartOrderRequestForm(request.POST)

        if form.is_valid():
            payment_method = request.POST.get('payment_method')

            order = store_models.Order.objects.create(
                customer=customer,
                sub_total=cart_sub_total,
                shipping=cart_shipping_total,
                tax=Decimal(0),
                service_fee=Decimal(0),
                total=cart_sub_total + cart_shipping_total,
                payment_method=payment_method,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['mobile'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                zip_code=form.cleaned_data['zip_code'],
                note=form.cleaned_data.get('notes', '')
            )

            # Save order items
            for item in items:
                store_models.OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    qty=item.qty,
                    color=item.color,
                    size=item.size,
                    price=item.price,
                    sub_total=item.sub_total,
                    shipping=item.shipping,
                    total=item.total,
                    initial_total=item.total,
                )

            # Update profile
            if not profile.full_name:
                profile.full_name = order.full_name
            if not profile.mobile:
                profile.mobile = order.phone
            profile.save()

            # ✅ Handle payment method flow
            if payment_method == 'bank':
                return redirect('store:confirm_payment', order_id=order.order_id)
            else:
                # COD or Flutterwave
                items.delete()
                messages.success(request, "Your order has been placed successfully.")
                return redirect('store:checkout_success')
        else:
            messages.warning(request, "Please correct the errors in the form.")
    else:
        initial_data = {
            'full_name': profile.full_name,
            'email': profile.user.email,
            'mobile': profile.mobile,
        }
        form = CartOrderRequestForm(initial=initial_data)

    return render(request, "store/checkout.html", {
        'form': form,
        'cart_data': items,
        'cart_total_amount': cart_sub_total,
        'totalcartitems': items.count()
    })


@login_required
def confirm_payment(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if request.method == 'POST':
        order.bank_receipt = request.FILES.get('bank_receipt')
        order.payment_method = request.POST.get("payment_method")
        order.payment_status = 'Pending'
        order.save()

        # Delete cart items now
        store_models.Cart.objects.filter(user=request.user).delete()

        messages.success(request, f"Your order {order.order_id} has been submitted. We'll confirm your payment shortly.")
        return redirect('store:checkout_success')

    return render(request, 'store/confirm_payment.html', {'order': order})


@login_required
def checkout_success(request):
    return render(request, "store/checkout_success.html")


# def checkout(request, order_id):
#     order = store_models.Order.objects.get(order_id=order_id)
    
#     # amount_in_inr = convert_usd_to_inr(order.total)
#     amount_in_kobo = convert_usd_to_kobo(order.total)
#     amount_in_ngn = convert_usd_to_ngn(order.total)

#     try:
#         razorpay_order = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)).order.create({
#             "amount": int(amount_in_inr),
#             "currency": "INR",
#             "payment_capture": "1"
#         })
#     except:
#         razorpay_order = None
#     context = {
#         "order": order,
#         "amount_in_inr":amount_in_inr,
#         "amount_in_kobo":amount_in_kobo,
#         "amount_in_ngn":round(amount_in_ngn, 2),
#         "razorpay_order_id": razorpay_order['id'] if razorpay_order else None,
#         "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
#         "paypal_client_id": settings.PAYPAL_CLIENT_ID,
#         "razorpay_key_id":settings.RAZORPAY_KEY_ID,
#         "paystack_public_key":settings.PAYSTACK_PUBLIC_KEY,
#         "flutterwave_public_key":settings.FLUTTERWAVE_PUBLIC_KEY,
#     }

#     return render(request, "store/checkout.html", context)


    

# def paystack_payment_verify(request, order_id):
#     order = store_models.Order.objects.get(order_id=order_id)
#     reference = request.GET.get('reference', '')

#     if reference:
#         headers = {
#             "Authorization": f"Bearer {settings.PAYSTACK_PRIVATE_KEY}",
#             "Content-Type": "application/json"
#         }

#         # Verify the transaction
#         response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
#         response_data = response.json()

#         if response_data['status']:
#             if response_data['data']['status'] == 'success':
#                 if order.payment_status == "Processing":
#                     order.payment_status = "Paid"
#                     payment_method = request.GET.get("payment_method")
#                     order.payment_method = payment_method
#                     order.save()
#                     clear_cart_items(request)
#                     return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")
#                 else:
#                     return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")
#             else:
#                 # Payment failed
#                 return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")
#         else:
#             return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")
#     else:
#         return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")

# def flutterwave_payment_callback(request, order_id):
#     order = store_models.Order.objects.get(order_id=order_id)

#     payment_id = request.GET.get('tx_ref')
#     status = request.GET.get('status')

#     headers = {
#         'Authorization': f'Bearer {settings.FLUTTERWAVE_PRIVATE_KEY}'
#     }
#     response = requests.get(f'https://api.flutterwave.com/v3/charges/verify_by_id/{payment_id}', headers=headers)

#     if response.status_code == 200:
#         if order.payment_status == "Processing":
#             order.payment_status = "Paid"
#             payment_method = request.GET.get("payment_method")
#             order.payment_method = payment_method
#             order.save()
#             clear_cart_items(request)
#             return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")
#         else:
#             return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")
#     else:
#         return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")

# def payment_status(request, order_id):
#     order = store_models.Order.objects.get(order_id=order_id)
#     payment_status = request.GET.get("payment_status")

#     context = {
#         "order": order,
#         "payment_status": payment_status
#     }
#     return render(request, "store/payment_status.html", context)

# def filter_products(request):
#     products = store_models.Product.objects.all()

#     # Get filters from the AJAX request
#     categories = request.GET.getlist('categories[]')
#     rating = request.GET.getlist('rating[]')
#     sizes = request.GET.getlist('sizes[]')
#     colors = request.GET.getlist('colors[]')
#     price_order = request.GET.get('prices')
#     search_filter = request.GET.get('searchFilter')
#     display = request.GET.get('display')

#     print("categories =======", categories)
#     print("rating =======", rating)
#     print("sizes =======", sizes)
#     print("colors =======", colors)
#     print("price_order =======", price_order)
#     print("search_filter =======", search_filter)
#     print("display =======", display)

   
#     # Apply category filtering
#     if categories:
#         products = products.filter(category__id__in=categories)

#     # Apply rating filtering
#     if rating:
#         products = products.filter(reviews__rating__in=rating).distinct()

    

#     # Apply size filtering
#     if sizes:
#         products = products.filter(variant__variant_items__content__in=sizes).distinct()

#     # Apply color filtering
#     if colors:
#         products = products.filter(variant__variant_items__content__in=colors).distinct()

#     # Apply price ordering
#     if price_order == 'lowest':
#         products = products.order_by('-price')
#     elif price_order == 'highest':
#         products = products.order_by('price')

#     # Apply search filter
#     if search_filter:
#         products = products.filter(name__icontains=search_filter)

#     if display:
#         products = products.filter()[:int(display)]


#     # Render the filtered products as HTML using render_to_string
#     html = render_to_string('partials/_store.html', {'products': products})

#     return JsonResponse({'html': html, 'product_count': products.count()})

# def order_tracker_page(request):
#     if request.method == "POST":
#         item_id = request.POST.get("item_id")
#         return redirect("store:order_tracker_detail", item_id)
    
#     return render(request, "store/order_tracker_page.html")

# def order_tracker_detail(request, item_id):
#     try:
#         item = store_models.OrderItem.objects.filter(models.Q(item_id=item_id) | models.Q(tracking_id=item_id)).first()
#     except:
#         item = None
#         messages.error(request, "Order not found!")
#         return redirect("store:order_tracker_page")
    
#     context = {
#         "item": item,
#     }
#     return render(request, "store/order_tracker.html", context)

# def about(request):
#     return render(request, "pages/about.html")

# def contact(request):
#     if request.method == "POST":
#         full_name = request.POST.get("full_name")
#         email = request.POST.get("email")
#         subject = request.POST.get("subject")
#         message = request.POST.get("message")

#         userauths_models.ContactMessage.objects.create(
#             full_name=full_name,
#             email=email,
#             subject=subject,
#             message=message,
#         )
#         messages.success(request, "Message sent successfully")
#         return redirect("store:contact")
#     return render(request, "pages/contact.html")

# def faqs(request):
#     return render(request, "pages/faqs.html")

# def privacy_policy(request):
#     return render(request, "pages/privacy_policy.html")

# def terms_conditions(request):
#     return render(request, "pages/terms_conditions.html")